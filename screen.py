import questionary as q

class Screen:
    def __init__(self, app):
        self.app = app

    def show(self):
        raise RuntimeError("Do not implement.")

class LoginScreen(Screen):
    def show(self):
        login = q.text("Login: ").ask()
        pw = q.password("Password: ").ask()


        # Determine login success and user type
        if login == "a" and pw == "a":
            self.app.running = False
            return "next_window"
        
        # No match, invalid
        q.print("\n\nIncorrect Credentials. Please try again.", style = "bold fg:red", end = "\n\n")

        q.press_any_key_to_continue().ask()
        
        return "login"

