import questionary
import queries
from decimal import Decimal, InvalidOperation

"""
https://questionary.readthedocs.io/en/stable/pages/quickstart.html
"""

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


class Screen:
    def __init__(self, app):
        self.app = app

    def show(self):
        raise RuntimeError("Do not implement.")

class TemplateScreen(Screen):
    def show(self):
        return "login"

class WelcomeScreen(Screen):
    def show(self):
        res = questionary.select(
            "Auction Site V1.0",
            choices=[
                "Login",
                "Register",
                "Close Program"
            ]).ask()
        # Returns either "login" or "register"
        if res == "Close Program":
            return "exit"
        return res.lower()

class RegisterScreen(Screen):
    def show(self):
        questionary.print("Registration", style="bold")

        login = questionary.text("Enter Login: ").ask()

        # Check if login already exists
        res = self.app.esql.execute_query(
            queries.CHECK_LOGIN_EXISTS,
            (login,)
        )

        if res:
            questionary.print(
                "\nThat login already exists. Please choose another one.\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()
            return "register"

        pw = questionary.password("Enter Password: ").ask()
        confirm_pw = questionary.password("Confirm Password: ").ask()

        if pw != confirm_pw:
            questionary.print(
                "\nPasswords do not match. Please try again.\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()
            return "register"

        phone_num = questionary.text("Enter Phone Number: ").ask()
        address = questionary.text("Enter Address: ").ask()
        favorite_category = questionary.text(
            "Enter Favorite Category: "
        ).ask()

        try:
            self.app.esql.execute_update(
                queries.INSERT_USER,
                (
                    login,
                    pw,
                    phone_num,
                    address,
                    "Buyer",
                    favorite_category
                )
            )

            questionary.print(
                "\nRegistration successful! You can now log in.\n",
                style="bold fg:green"
            )
            questionary.press_any_key_to_continue().ask()

            return "welcome"

        except Exception as e:
            questionary.print(
                f"\nRegistration failed: {e}\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()

            return "register"
        
class LoginScreen(Screen):
    def show(self):
        login = questionary.text("Login: ").ask()
        pw = questionary.password("Password: ").ask()

        # Determine login success and user role
        res = self.app.esql.execute_query(queries.GET_USER_ROLE, (login, pw))
        if not res.empty():
            # There was a user with this login + pass. Login successful.
            self.app.current_user = login
            self.app.current_role = res[0][0]
            return "home"
        
        # No match, invalid
        questionary.print("\n\n Incorrect Credentials. Please try again.", style = "bold fg:red", end = "\n\n")

        questionary.press_any_key_to_continue().ask()
        
        return "login"
    
class HomeScreen(Screen):
    def show(self):
        questionary.print(f"Welcome, {self.app.current_user}.", style="bold")

        choices = {
            "Browse Items" : "browse_items",
            "Search Auctions" : "search_auction",
            "Make Payments" : "make_payment",
            "See Active Bids" : "active_bid",
            "Edit Profile" : "edit_profile",
        }

        role = self.app.current_role
        if role == "Seller":
            choices["Seller Dashboard"] = "sell_dashboard"

        if role == "Admin":
            choices["Admin Dashboard"] = "admin_dashboard"
        
        choices["Exit"] = "exit"

        res = questionary.select(
            "Home",
            choices=list(choices.keys())
        ).ask()

        return choices[res]

class EditProfileScreen(Screen):
    def show(self):
        questionary.print("Edit Profile", style="bold")
        login = self.app.current_user

        res = self.app.esql.execute_query(
            queries.GET_USER_INFO,
            (login,)
        )

        phone_num, address, favorite_category, password = res[0]

        new_phone_num = questionary.text(
            "Phone Number:",
            default=phone_num
        ).ask()

        new_address = questionary.text(
            "Address:",
            default=address
        ).ask()

        new_favorite_category = questionary.text(
            "Favorite Category:",
            default=favorite_category if favorite_category is not None else ""
        ).ask()

        new_password = questionary.text(
            "Password:",
            default=password
        ).ask()

        self.app.esql.execute_update(
            queries.UPDATE_USER_INFO,
            (
                new_phone_num,
                new_address,
                new_favorite_category,
                new_password,
                login
            )
        )

        questionary.print(
            "\nProfile updated successfully!\n",
            style="bold fg:green"
        )
        questionary.press_any_key_to_continue().ask()
        return "home"

class DebugScreen(Screen):
    def show(self):
        questionary.print("Debug: Success")
        print(f"Current User: {self.app.current_user}")
        print(f"Current Role: {self.app.current_role}")
        x = input()
        
        return ""

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
            choice_dict[choice_text] = payment_id

        choices.append("Return")

        selected = questionary.select(
            "Select a payment to complete:",
            choices=choices
        ).ask()

        if selected == "Return" or selected is None:
            return "home"

        payment_id = choice_dict[selected]

        confirm = questionary.confirm(
            f"Pay for payment ID {payment_id} (${amount})?"
        ).ask()

        if not confirm:
            return "home"

        self.app.esql.execute_update(
            queries.SET_PAYMENT_STATUS_COMPLETED,
            (payment_id,)
        )

        questionary.print(
            "\nPayment successfully completed!\n",
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

        print()

        for auction_id, item_id, item_name, category, starting_price, current_highest_bid, seller_login in res:
            print(
                f"Auction ID: {auction_id} | "
                f"Item: {item_name} | "
                f"Category: {category} | "
                f"Starting: ${starting_price} | "
                f"Current Bid: ${current_highest_bid}"
            )

        print()

        questionary.press_any_key_to_continue().ask()
        return "home"
    
