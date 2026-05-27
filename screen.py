import questionary
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
                "Register"
            ]).ask()
        return res.lower()

class RegisterScreen(Screen):
    def show(self):
        questionary.print("Registration")

        login = questionary.text("Enter Login: ").ask()
        pw = questionary.password("Enter Password: ").ask()
        print("Run stored procedure")
        x = input()
        return "welcome"
        return "register"
        


class LoginScreen(Screen):
    def show(self):
        
        login = questionary.text("Login: ").ask()
        pw = questionary.password("Password: ").ask()

        # Determine login success and user type
        if login == "a" and pw == "a":
            self.app.running = False
            return "next_window"
        
        # No match, invalid
        questionary.print("\n\n Incorrect Credentials. Please try again.", style = "bold fg:red", end = "\n\n")

        questionary.press_any_key_to_continue().ask()
        
        return "login"
    
