from screen import Screen
import questionary
import queries
from decimal import Decimal
from screen_helper import *

class SellerDashboardScreen(Screen):
    def show(self):
        questionary.print(
            f"Welcome, {self.app.current_user}.",
            style="bold"
        )

        choices = {
            "Create Item": "create_item",
            "Update Item": "update_item",
            "My Auctions" : "auctions_by_seller",
            "Start Auction": "start_auction",
            "End Auction": "end_auction",
            "Ship Sold Items" : "ship_items",
            "Edit Profile" : "edit_profile",
            "Log Out": "exit"
        }

        res = questionary.select(
            "Seller Dashboard",
            choices=list(choices.keys())
        ).ask()

        return choices[res]
    
class AuctionsBySellerScreen(Screen):
    def show(self):
        questionary.print("My Recent Auctions:", style="bold")

        res = self.app.esql.execute_query(
            queries.GET_RECENT_AUCTIONS_BY_SELLER,
            (self.app.current_user,)
        )

        if res.empty():
            questionary.print(
                "\nThere are no records of you having created an auction yet.\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()
            return "sell_dashboard"

        print()

        for auction_id, item_name, current_highest_bid, auction_status in res:
            bid_count_res = self.app.esql.execute_query(
                queries.GET_BID_COUNT,
                (auction_id,)
            )

            bid_count = bid_count_res[0][0]

            print("-" * 50)
            print(f"Auction ID: {auction_id}")
            print(f"Item: {item_name}")
            print(f"Status: {auction_status}")
            print(f"Number of Bids: {bid_count}")

            if bid_count > 0:
                print(f"Current Highest Bid: ${current_highest_bid}")
            else:
                print("Current Highest Bid: N/A")

        print("-" * 50)

        questionary.press_any_key_to_continue().ask()
        return "sell_dashboard"

class StartAuctionScreen(Screen):
    def show(self):
        seller_login = self.app.current_user

        questionary.print("Start Auction:", style="bold")

        res = self.app.esql.execute_query(
            queries.GET_POSS_ITEMS,
            (seller_login,)
        )

        if res.empty():
            questionary.print(
                "\nYou have no available items to start an auction.\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()
            return "sell_dashboard"

        choice_dict = {}
        choices = []

        for item_id, item_name in res:
            choice_text = f"Item ID: {item_id} | Item Name: {item_name}"
            choices.append(choice_text)
            choice_dict[choice_text] = item_id

        choices.append("Return")

        selected = questionary.select(
            "Select an item to start an auction:",
            choices=choices
        ).ask()

        if selected == "Return" or selected is None:
            return "sell_dashboard"

        item_id = choice_dict[selected]

        confirm = questionary.confirm(
            f"Start auction for item {item_id}?"
        ).ask()

        if not confirm:
            return "sell_dashboard"

        self.app.esql.execute_update(
            queries.INSERT_AUCTION,
            (item_id, seller_login)
        )

        questionary.print(
            "\nAuction successfully started!\n",
            style="bold fg:green"
        )
        questionary.press_any_key_to_continue().ask()

        return "sell_dashboard"

class UpdateItemScreen(Screen):
    def show(self):
        seller_login = self.app.current_user

        questionary.print("Update Item:", style="bold")

        # Get all items from current seller
        res = self.app.esql.execute_query(
            queries.GET_POSS_ITEMS_ACTIVE,
            (seller_login,)
        )

        if res.empty():
            questionary.print(
                "\nYou have no items to update.\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()
            return "sell_dashboard"

        choice_dict = {}
        choices = []

        for item_id, item_name in res:
            choice_text = f"Item ID: {item_id} | Item Name: {item_name}"
            choices.append(choice_text)
            choice_dict[choice_text] = item_id

        choices.append("Return")

        selected = questionary.select(
            "Select an item to update:",
            choices=choices
        ).ask()

        if selected == "Return" or selected is None:
            return "sell_dashboard"

        item_id = choice_dict[selected]

        # Load old item values
        item_res = self.app.esql.execute_query(
            queries.GET_ITEM_BY_ID_FOR_SELLER,
            (item_id, seller_login)
        )

        if item_res.empty():
            questionary.print(
                "\nItem not found or you do not own this item.\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()
            return "sell_dashboard"

        old_item_name, old_category, old_starting_price, old_image_url, old_item_condition, old_description = item_res[0]

        # Ask for new values, with current values as defaults
        item_name = questionary.text(
            "New Item Name:",
            default=str(old_item_name)
        ).ask()

        if item_name is None:
            return "sell_dashboard"

        item_name = item_name.strip()

        if item_name == "":
            questionary.print("\nItem name cannot be blank.\n", style="bold fg:red")
            questionary.press_any_key_to_continue().ask()
            return "sell_dashboard"

        category = questionary.text(
            "New Item Category:",
            default=str(old_category)
        ).ask()

        if category is None:
            return "sell_dashboard"

        category = category.strip()

        if category == "":
            questionary.print("\nCategory cannot be blank.\n", style="bold fg:red")
            questionary.press_any_key_to_continue().ask()
            return "sell_dashboard"

        while True:
            starting_price_input = questionary.text(
                "New Item Starting Price:",
                default=str(old_starting_price)
            ).ask()

            if starting_price_input is None:
                return "sell_dashboard"

            if is_valid_price(starting_price_input):
                starting_price = Decimal(starting_price_input)
                break

            questionary.print(
                "Invalid starting price. Enter a non-negative number with at most 2 decimals.",
                style="bold"
            )

        image_url = optional_text(
            questionary.text(
                "New Item Image Url (Optional, Leave blank to skip):",
                default="" if old_image_url is None else str(old_image_url)
            ).ask()
        )

        item_condition = optional_text(
            questionary.text(
                "New Item Condition (Optional, Leave blank to skip):",
                default="" if old_item_condition is None else str(old_item_condition)
            ).ask()
        )

        description = optional_text(
            questionary.text(
                "New Item Description (Optional, Leave blank to skip):",
                default="" if old_description is None else str(old_description)
            ).ask()
        )

        confirm = questionary.confirm(
            f"Are you sure you want to update item {item_id}?"
        ).ask()

        if not confirm:
            return "sell_dashboard"

        self.app.esql.execute_update(
            queries.UPDATE_ITEM,
            (
                item_name,
                category,
                starting_price,
                image_url,
                item_condition,
                description,
                item_id,
                seller_login
            )
        )

        questionary.print(
            "\nItem successfully updated!\n",
            style="bold fg:green"
        )
        questionary.press_any_key_to_continue().ask()

        return "sell_dashboard"

class CreateItemScreen(Screen):
    def show(self):
        questionary.print("Create Item:", style="bold")

        item_name = required_text("New Item Name: ")
        if item_name is None:
            return "sell_dashboard"

        category = required_text("New Item Category: ")
        if category is None:
            return "sell_dashboard"

        while True:
            starting_price_input = questionary.text("New Item Starting Price: ").ask()

            if starting_price_input is None:
                return "sell_dashboard"

            if is_valid_price(starting_price_input):
                starting_price = Decimal(starting_price_input.strip())
                break

            questionary.print(
                "Invalid starting price. Enter a non-negative number with at most 2 decimals.",
                style="bold fg:red"
            )

        image_url = optional_text(
            questionary.text(
                "New Item Image Url (Optional, Leave blank to skip): "
            ).ask()
        )

        item_condition = optional_text(
            questionary.text(
                "New Item Condition (Optional, Leave blank to skip): "
            ).ask()
        )

        description = optional_text(
            questionary.text(
                "New Item Description (Optional, Leave blank to skip): "
            ).ask()
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

        return "sell_dashboard"
    
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
            return "sell_dashboard"

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
            return "sell_dashboard"

        auction_id = choice_dict[selected]

        confirm = questionary.confirm(
            f"Are you sure you want to close auction {auction_id}?"
        ).ask()

        if not confirm:
            return "sell_dashboard"

        self.handle_end_auction(auction_id)

        questionary.print(
            "\nAuction succesfully closed .\n",
            style="bold fg:green"
        )
        questionary.press_any_key_to_continue().ask()

        return "sell_dashboard"
    
class ShipItemsScreen(Screen):
    def show(self):
        questionary.print("Ship Sold Items:", style="bold")

        res = self.app.esql.execute_query(
            queries.FIND_SHIPMENTS_PENDING,
            (self.app.current_user,)
        )

        if res.empty():
            questionary.print(
                "\nYou have no items that were recently bought by others to ship.\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()
            return "sell_dashboard"

        choice_dict = {}
        choices = []

        for shipment_id, item_name in res:
            choice_text = (
                f"Shipment ID: {shipment_id} | "
                f"Item: {item_name}"
            )

            choices.append(choice_text)
            choice_dict[choice_text] = shipment_id

        choices.append("Return")

        selected = questionary.select(
            "Select an item to ship:",
            choices=choices
        ).ask()

        if selected == "Return" or selected is None:
            return "sell_dashboard"

        shipment_id = choice_dict[selected]

        tracking_number = questionary.text(
            "Enter tracking number, or leave blank if unavailable: "
        ).ask()

        if tracking_number is None:
            return "sell_dashboard"

        tracking_number = tracking_number.strip()

        if tracking_number == "":
            tracking_number = None

        confirm = questionary.confirm(
            f"Mark shipment {shipment_id} as shipped?"
        ).ask()

        if not confirm:
            return "sell_dashboard"

        self.app.esql.execute_update(
            queries.UPDATE_SHIPMENT,
            (tracking_number, shipment_id)
        )

        questionary.print(
            "\nShipment marked as shipped!\n",
            style="bold fg:green"
        )
        questionary.press_any_key_to_continue().ask()

        return "sell_dashboard"
