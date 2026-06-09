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
            "Return": "home"
        }

        res = questionary.select(
            "Buyer Dashboard",
            choices=list(choices.keys())
        ).ask()

        if res is None:
            return "home"

        return choices[res]