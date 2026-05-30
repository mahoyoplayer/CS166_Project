import questionary
import queries
"""
https://questionary.readthedocs.io/en/stable/pages/quickstart.html
"""

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

