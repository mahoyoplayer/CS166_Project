from screen import Screen
import questionary
import queries
from decimal import Decimal, InvalidOperation

class CreateItemScreen(Screen):
    def show(self):
        def is_valid_price(value):
            if value is None:
                return False

            value = value.strip()

            try:
                price = Decimal(value)
            except InvalidOperation:
                return False

            # Reject NaN and Infinity
            if not price.is_finite():
                return False

            # Must be positive
            if price < Decimal("0"):
                return False

            exponent = price.as_tuple().exponent

            # Makes Pylance happy
            if not isinstance(exponent, int):
                return False

            # Must have at most 2 decimal places
            if exponent < -2:
                return False

            # Must fit NUMERIC(10,2)
            if price > Decimal("99999999.99"):
                return False

            return True
        
        def optional_text(value):
            if value is None:
                return None

            value = value.strip()
            return value if value else None

        def required_text(prompt):
            while True:
                value = questionary.text(prompt).ask()

                if value is None:
                    return None

                value = value.strip()

                if value:
                    return value

                questionary.print("This field is required.", style="bold")

        questionary.print("Create Item:", style="bold")

        item_name = required_text("New Item Name: ")
        if item_name is None:
            return "home"

        category = required_text("New Item Category: ")
        if category is None:
            return "home"

        while True:
            starting_price_input = questionary.text("New Item Starting Price: ").ask()

            if is_valid_price(starting_price_input):
                starting_price = Decimal(starting_price_input)
                break

            questionary.print(
                "Invalid starting price. Enter a non-negative number with at most 2 decimals.",
                style="bold"
            )

        image_url = optional_text(
            questionary.text("New Item Image Url (Optional, Leave blank to skip): ").ask()
        )

        item_condition = optional_text(
            questionary.text("New Item Condition (Optional, Leave blank to skip): ").ask()
        )

        description = optional_text(
            questionary.text("New Item Description (Optional, Leave blank to skip): ").ask()
        )

        self.app.esql.execute_update(
            queries.INSERT_ITEM,
            (
                item_name,
                category,
                starting_price,
                image_url,
                item_condition,
                description,
                self.app.current_user
            )
        )

        questionary.print(
            "\nItem successfully created!\n",
            style="bold fg:green"
        )
        questionary.press_any_key_to_continue().ask()

        return "home"

class UpdateItemScreen(Screen):
    pass  

class EndAuctionScreen(Screen):
    def handle_end_auction(self, auction_id):
        res = self.app.esql.execute_query(
            queries.FIND_AUCTION_WINNER,
            (auction_id,auction_id)
        )
        if res.empty():
            # Close auction id
            self.app.esql.execute_update(
                queries.CLOSE_AUCTION_ID, 
                (None, auction_id)
            )
            # No need to make payment
        else:
            winner_login, winning_bid = res[0]

            # Close auction id
            self.app.esql.execute_update(
                queries.CLOSE_AUCTION_ID, 
                (winner_login, auction_id)
            )

            # Create payment
            self.app.esql.execute_update(
                queries.INSERT_PAYMENT, 
                (auction_id, winner_login, winning_bid)
            )



    def show(self):
        res = self.app.esql.execute_query(
            queries.GET_CURRENT_AUCTIONS,
            (self.app.current_user,)
        )

        if res.empty():
            questionary.print(
                "\n You have no auctions that are open.\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()
            return "home"

        choice_dict = {}
        choices = []

        for auction_id, item_name in res:
            choice_text = f"Auction ID: {auction_id} | Item Name: {item_name}"
            choices.append(choice_text)
            choice_dict[choice_text] = auction_id

        choices.append("Return")

        selected = questionary.select(
            "Select an auction to close:",
            choices=choices
        ).ask()

        if selected == "Return" or selected is None:
            return "home"

        auction_id = choice_dict[selected]

        confirm = questionary.confirm(
            f"Are you sure you want to close auction {auction_id}?"
        ).ask()

        if not confirm:
            return "home"

        self.handle_end_auction(auction_id)

        questionary.print(
            "\nAuction succesfully closed .\n",
            style="bold fg:green"
        )
        questionary.press_any_key_to_continue().ask()

        return "home"