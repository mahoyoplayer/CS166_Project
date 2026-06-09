
import os
import subprocess
from esql_final import EmbeddedSQL

from screen import *
import buyer_screen as buy_scr
import admin_screen as adm_scr
import seller_screen as sell_scr

dbname = "cs166_final" #sys.argv[1]
dbport = 5432#sys.argv[2]
user = "ryan" #sys.argv[3]
password = "ryan123"

DEBUG = False

def clear_console() -> None:
    clear_command = "cls" if os.name == "nt" else "clear"
    subprocess.run(clear_command, shell=True, check=False)

class App:
    def __init__(self):
        self.running = True
        self.current_user = None
        self.current_role = None
        self.esql = EmbeddedSQL(dbname, dbport, user, password)

        self.screen_map = {
            # General Screens
            "welcome" : WelcomeScreen(self),
            "login" : LoginScreen(self),
            "register" : RegisterScreen(self),
            "home" : buy_scr.BuyerDashboardScreen(self),
            "edit_profile": EditProfileScreen(self),
            "debug": DebugScreen(self),
            "make_payment" : MakePaymentScreen(self),
            "search_auction" : SearchAuctionScreen(self),
            "active_bid" : ActiveBidsScreen(self),
            "browse_items" : BrowseItemsScreen(self),
            "won_auction" : WonAuctionsScreen(self),
            "confirm_delivery" : ConfirmDeliveryScreen(self),

            # Buyer Screens
            "buyer_dashboard" : buy_scr.BuyerDashboardScreen(self),

            # Seller Screens
            "sell_dashboard" : sell_scr.SellerDashboardScreen(self),
            "create_item" : sell_scr.CreateItemScreen(self),
            "end_auction" : sell_scr.EndAuctionScreen(self),
            "update_item" : sell_scr.UpdateItemScreen(self),
            "start_auction" : sell_scr.StartAuctionScreen(self),
            "ship_items" : sell_scr.ShipItemsScreen(self),
            "auctions_by_seller" : sell_scr.AuctionsBySellerScreen(self),

            # Admin Screens
            "admin_dashboard" : adm_scr.AdminDashboardScreen(self),
            "change_user_role" : adm_scr.ChangeRoleScreen(self),
            "view_analytics" : adm_scr.ViewAnalyticsScreen(self),
            "remove_item" : adm_scr.RemoveItemScreen(self),
            "view_shipments_recent" : adm_scr.ViewShipmentsRecentScreen(self),
            "view_payments_recent" : adm_scr.ViewPaymentsRecentScreen(self)
        }
        
        
    def run(self):
        if DEBUG:
            # Buyer account
            curr_screen="home"
            self.current_user="seller1"
            self.current_role="Admin"
        else:
            curr_screen = "welcome"

        while self.running and curr_screen != "exit":
            clear_console()
            if curr_screen not in self.screen_map:
                print(f"Error: unknown screen '{curr_screen}'")
                return     
            curr_screen = self.screen_map[curr_screen].show()
        clear_console()

            
