from screen import Screen


class AdminMainScreen(Screen):
    def show(self):
        questionary.print(f"Admin Dashboard", style="bold")

        default_choices = {
            "Change User Role" : "browse_items",
            "Monitor Auctions" : "monitor_auctions",
            "Manage Items" : "edit_profile",
            "Mana" : "exit"
        }

        choices = default_choices
        res = questionary.select(
            "Home",
            choices=list(choices.keys())
        ).ask()

        # Returns either "login" or "register"
        return choices[res]