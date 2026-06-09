from screen import Screen
import questionary
import queries
from screen_helper import *


class BuyerDashboardScreen(Screen):
    def show(self):
        questionary.print(
            f"Welcome, {self.app.current_user}.",
            style="bold"
        )

        choices = {
            "Browse Items": "browse_items",
            "Search Auctions": "search_auction",
            "See Active Bids": "active_bid",
            "See Previously Won Auctions": "won_auction",
            "Make Payments": "make_payment",
            "See Ongoing Item Shipments": "confirm_delivery",
            "Edit Profile": "edit_profile",
            "Log Out": "exit"
        }

        res = questionary.select(
            "Buyer Dashboard",
            choices=list(choices.keys())
        ).ask()

        if res is None:
            return "home"

        return choices[res]
    
class MakePaymentScreen(Screen):
    def show(self):
        questionary.print("Make Payment:", style="bold")

        res = self.app.esql.execute_query(
            queries.GET_PENDING_PAYMENTS,
            (self.app.current_user,)
        )

        if res.empty():
            questionary.print(
                "\nYou have no pending payments.\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()
            return "home"

        choice_dict = {}
        choices = []

        for payment_id, auction_id, item_name, amount in res:
            choice_text = (
                f"Payment ID: {payment_id} | "
                f"Auction ID: {auction_id} | "
                f"Item: {item_name} | "
                f"Amount: ${amount}"
            )

            choices.append(choice_text)

            choice_dict[choice_text] = (
                payment_id,
                auction_id,
                amount
            )

        choices.append("Return")

        selected = questionary.select(
            "Select a payment to complete:",
            choices=choices
        ).ask()

        if selected == "Return" or selected is None:
            return "home"

        payment_id, auction_id, amount = choice_dict[selected]

        confirm = questionary.confirm(
            f"Pay for payment ID {payment_id} (${amount})?"
        ).ask()

        if not confirm:
            return "home"

        # Complete payment
        self.app.esql.execute_update(
            queries.SET_PAYMENT_STATUS_COMPLETED,
            (payment_id,)
        )

        # Get buyer address
        address_res = self.app.esql.execute_query(
            queries.FIND_ADDRESS_BY_LOGIN,
            (self.app.current_user,)
        )

        if address_res.empty():
            questionary.print(
                "\nPayment completed, but could not find your address for shipment.\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()
            return "home"

        address = address_res[0][0]

        # Create shipment
        self.app.esql.execute_update(
            queries.INSERT_SHIPMENT,
            (auction_id, address)
        )

        questionary.print(
            "\nPayment successfully completed! The seller will ship the item soon.\n",
            style="bold fg:green"
        )
        questionary.press_any_key_to_continue().ask()

        return "home"
    
class SearchAuctionScreen(Screen):
    def show(self):
        curr_login = self.app.current_user

        questionary.print("Explore Active Auctions:", style="bold")

        search_term = questionary.text(
            "Search item name, or enter -1 to cancel: "
        ).ask()

        if search_term is None:
            return "home"

        search_term = search_term.strip()

        if search_term == "-1":
            return "home"

        if search_term == "":
            questionary.print(
                "\nSearch term cannot be blank.\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()
            return "home"

        res = self.app.esql.execute_query(
            queries.FIND_AUCTION_BY_ITEM_NAME,
            (f"%{search_term}%", curr_login, curr_login)
        )

        if res.empty():
            questionary.print(
                "\nNo active auctions found for that item name.\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()
            return "home"

        choice_dict = {}
        choices = []

        for auction_id, item_id, current_highest_bid, starting_price, item_name, category, seller_login in res:
            choice_text = (
                f"{item_name} ({category}) | "
                f"Current Highest Bid: ${current_highest_bid} | "
                f"Starting Price: ${starting_price}"
            )

            choices.append(choice_text)
            choice_dict[choice_text] = (
                auction_id,
                item_id,
                Decimal(str(current_highest_bid)),
                Decimal(str(starting_price)),
                item_name
            )

        choices.append("Return")

        selected = questionary.select(
            "Select an auction to bid on:",
            choices=choices
        ).ask()

        if selected == "Return" or selected is None:
            return "home"

        auction_id, item_id, current_highest_bid, starting_price, item_name = choice_dict[selected]

        item_res = self.app.esql.execute_query(
            queries.GET_ITEM_INFO,
            (item_id,)
        )

        if item_res.empty():
            questionary.print(
                "\nCould not find item information.\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()
            return "home"

        (
            item_id,
            item_name,
            category,
            item_starting_price,
            image_url,
            item_condition,
            description,
            seller_login
        ) = item_res[0]

        def show_value(value):
            if value is None or value == "":
                return "N/A"
            return value

        print("\n" + "-" * 40)
        questionary.print("Full Item Information", style="bold")
        print(f"Item ID: {item_id}")
        print(f"Name: {item_name}")
        print(f"Category: {category}")
        print(f"Starting Price: ${item_starting_price}")
        print(f"Current Highest Bid: ${current_highest_bid}")
        print(f"Seller: {seller_login}")
        print(f"Condition: {show_value(item_condition)}")
        print(f"Image URL: {show_value(image_url)}")
        print(f"Description: {show_value(description)}")
        print("-" * 40 + "\n")

        min_bid = max(current_highest_bid, starting_price)

        while True:
            bid_amount_input = questionary.text(
                f"Enter bid amount greater than ${min_bid}, or -1 to cancel: "
            ).ask()

            if bid_amount_input is None:
                return "home"

            bid_amount_input = bid_amount_input.strip()

            if bid_amount_input == "-1":
                return "home"

            if is_valid_price(bid_amount_input):
                bid_amount = Decimal(bid_amount_input)

                if bid_amount > min_bid:
                    break

            questionary.print(
                f"Invalid bid. Bid must be greater than ${min_bid}.",
                style="bold fg:red"
            )

        confirm = questionary.confirm(
            f"Place bid of ${bid_amount} on '{item_name}'?"
        ).ask()

        if not confirm:
            return "home"

        self.app.esql.execute_update(
            queries.INSERT_BID,
            (auction_id, curr_login, bid_amount)
        )

        self.app.esql.execute_update(
            queries.UPDATE_CURR_HIGHEST_BID,
            (bid_amount, auction_id)
        )

        questionary.print(
            "\nBid successfully placed!\n",
            style="bold fg:green"
        )
        questionary.press_any_key_to_continue().ask()

        return "home"
    
class ActiveBidsScreen(Screen):
    def show(self):
        questionary.print("Active Winning Bids:", style="bold")

        res = self.app.esql.execute_query(
            queries.GET_ACTIVE_BIDS,
            (self.app.current_user,)
        )
        
        # Check for no winning bids
        if res.empty():
            questionary.print(
                "\nYou are not currently winning any active auctions.\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()
            return "home"
        
        # User is winning in at least one auction, so output them.
        print()
        for auction_id, item_name, category, current_highest_bid in res:
            print(
                f"Auction ID: {auction_id} | "
                f"Item: {item_name} | "
                f"Category: {category} | "
                f"Your Bid: ${current_highest_bid}"
            )
        print()
        questionary.press_any_key_to_continue().ask()
        return "home"

class BrowseItemsScreen(Screen):
    def show(self):
        questionary.print("Recently Posted Items:", style="bold")

        res = self.app.esql.execute_query(
            queries.BROWSE_ITEMS,
            (self.app.current_user,)
        )

        if res.empty():
            questionary.print(
                "\nThere are no active auction items right now.\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()
            return "home"

        choice_dict = {}
        choices = []

        for auction_id, item_id, item_name, category, starting_price, current_highest_bid, seller_login in res:
            choice_text = (
                f"{item_name} ({category}) | "
                f"Starting: ${starting_price} | "
                f"Current Bid: ${current_highest_bid}"
            )
            choices.append(choice_text)
            choice_dict[choice_text] = (
                auction_id,
                item_id,
                Decimal(str(current_highest_bid)),
                Decimal(str(starting_price)),
                item_name
            )

        choices.append("Return")

        selected = questionary.select(
            "Select an item to bid on, or Return to go back:",
            choices=choices
        ).ask()

        if selected == "Return" or selected is None:
            return "home"

        auction_id, item_id, current_highest_bid, starting_price, item_name = choice_dict[selected]

        min_bid = max(current_highest_bid, starting_price)

        while True:
            bid_amount_input = questionary.text(
                f"Enter bid amount greater than ${min_bid}, or -1 to cancel: "
            ).ask()

            if bid_amount_input is None:
                return "home"

            bid_amount_input = bid_amount_input.strip()

            if bid_amount_input == "-1":
                return "home"

            if is_valid_price(bid_amount_input):
                bid_amount = Decimal(bid_amount_input)
                if bid_amount > min_bid:
                    break

            questionary.print(
                f"Invalid bid. Bid must be greater than ${min_bid}.",
                style="bold fg:red"
            )

        confirm = questionary.confirm(
            f"Place bid of ${bid_amount} on '{item_name}'?"
        ).ask()

        if not confirm:
            return "home"

        self.app.esql.execute_update(
            queries.INSERT_BID,
            (auction_id, self.app.current_user, bid_amount)
        )

        self.app.esql.execute_update(
            queries.UPDATE_CURR_HIGHEST_BID,
            (bid_amount, auction_id)
        )

        questionary.print(
            "\nBid successfully placed!\n",
            style="bold fg:green"
        )
        questionary.press_any_key_to_continue().ask()
        return "home"
    
class WonAuctionsScreen(Screen):
    def show(self):
        questionary.print("Won Auctions:", style="bold")

        res = self.app.esql.execute_query(
            queries.FIND_WON_AUCTIONS,
            (self.app.current_user,)
        )

        if res.empty():
            questionary.print(
                "\nYou have not won any auctions yet.\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()
            return "home"

        def show_value(value):
            return "N/A" if value is None or value == "" else value

        print()

        for auction_id, item_name, category, description, winning_price, auction_status in res:
            print("-" * 50)
            print(f"Auction ID: {auction_id}")
            print(f"Item: {item_name}")
            print(f"Category: {category}")
            print(f"Winning Price: ${winning_price}")
            print(f"Description: {show_value(description)}")

        print("-" * 50)

        questionary.press_any_key_to_continue().ask()
        return "home"
    
class ConfirmDeliveryScreen(Screen):
    def show(self):
        questionary.print("Confirm Delivery:", style="bold")

        res = self.app.esql.execute_query(
            queries.FIND_SHIPMENTS_ACTIVE,
            (self.app.current_user,)
        )

        if res.empty():
            questionary.print(
                "\nThere are no packages currently being shipped to you.\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()
            return "home"

        choice_dict = {}
        choices = []

        for shipment_id, item_name, tracking_number in res:
            tracking = tracking_number if tracking_number is not None else "N/A"

            choice_text = (
                f"Shipment ID: {shipment_id} | "
                f"Item: {item_name} | "
                f"Tracking: {tracking}"
            )

            choices.append(choice_text)
            choice_dict[choice_text] = shipment_id

        choices.append("Return")

        selected = questionary.select(
            "Select a shipment to mark as delivered:",
            choices=choices
        ).ask()

        if selected == "Return" or selected is None:
            return "home"

        shipment_id = choice_dict[selected]

        confirm = questionary.confirm(
            f"Mark shipment {shipment_id} as delivered?"
        ).ask()

        if not confirm:
            return "home"

        self.app.esql.execute_update(
            queries.SET_SHIPMENT_DELIVERED,
            (shipment_id,)
        )

        questionary.print(
            "\nShipment marked as delivered! Thank you for your cooperation!\n",
            style="bold fg:green"
        )
        questionary.press_any_key_to_continue().ask()

        return "home"
    
