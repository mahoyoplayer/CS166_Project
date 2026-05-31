from screen import Screen
import questionary
import queries


class RemoveItemScreen(Screen):
    def show(self):
        questionary.print("Remove Item:", style="bold")

        item_id_input = questionary.text(
            "Enter item ID to remove, or -1 to cancel: "
        ).ask()

        if item_id_input is None:
            return "admin_dashboard"

        item_id_input = item_id_input.strip()

        if item_id_input == "-1":
            return "admin_dashboard"

        if not item_id_input.isdigit():
            questionary.print(
                "\nInvalid item ID. Please enter a number.\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()
            return "admin_dashboard"

        item_id = int(item_id_input)

        res = self.app.esql.execute_query(
            queries.GET_ITEM_DELETE_INFO,
            (item_id,)
        )

        if res.empty():
            questionary.print(
                f"\nNo item found with ID {item_id}.\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()
            return "admin_dashboard"

        item_id, item_name, category, seller_login, has_auction = res[0]

        if has_auction:
            questionary.print(
                "\nThis item cannot be deleted because it has auction history.\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()
            return "admin_dashboard"

        questionary.print(
            f"\nItem found:\n"
            f"Item Name: {item_name}\n"
            f"Item Category: {category}\n"
            f"Item Seller: {seller_login}\n",
            style="bold"
        )

        confirm = questionary.confirm(
            f"Are you sure you want to permanently delete item {item_id}?"
        ).ask()

        if not confirm:
            return "admin_dashboard"

        self.app.esql.execute_update(
            queries.DELETE_ITEM,
            (item_id,)
        )

        questionary.print(
            "\nItem successfully removed.\n",
            style="bold fg:green"
        )
        questionary.press_any_key_to_continue().ask()

        return "admin_dashboard"
    
class ViewAnalyticsScreen(Screen):
    def show(self):
        questionary.print(
            "Site Analytics",
            style="bold"
        )
        print("-" * 30)

        # Basic counts
        user_count_res = self.app.esql.execute_query(
            queries.GET_USER_COUNT
        )
        num_bids_today_res = self.app.esql.execute_query(
            queries.GET_NUM_BIDS_TODAY
        )
        num_auction_res = self.app.esql.execute_query(
            queries.GET_NUM_AUCTION
        )
        num_active_auction_res = self.app.esql.execute_query(
            queries.GET_NUM_AUCTION_ACTIVE
        )

        user_count = user_count_res[0][0]
        num_bids_today = num_bids_today_res[0][0]
        num_auction = num_auction_res[0][0]
        num_active_auction = num_active_auction_res[0][0]

        questionary.print(f"Total Users: {user_count}", style="bold")
        questionary.print(f"Bids Today: {num_bids_today}", style="bold")
        questionary.print(f"Total Auctions: {num_auction}", style="bold")
        questionary.print(f"Active Auctions: {num_active_auction}", style="bold")

        print("\n" + "-" * 30)
        questionary.print("Most Bidded Auctions", style="bold")

        most_bidded_res = self.app.esql.execute_query(
            queries.GET_MOST_BIDDED_AUCTIONS
        )

        if most_bidded_res.empty():
            print("No auction bid data available.")
        else:
            for auction_id, item_name, num_bids in most_bidded_res:
                print(f"Auction ID: {auction_id} | Item: {item_name} | Bids: {num_bids}")

        print("\n" + "-" * 30)
        questionary.print("Top Categories By Bids", style="bold")

        top_categories_res = self.app.esql.execute_query(
            queries.GET_TOP_CATEGORIES_BY_BIDS
        )

        if top_categories_res.empty():
            print("No category bid data available.")
        else:
            for category, num_bids in top_categories_res:
                print(f"Category: {category} | Bids: {num_bids}")

        print("\n" + "-" * 30)
        questionary.print("Top Sellers By Auctions", style="bold")

        top_sellers_res = self.app.esql.execute_query(
            queries.GET_TOP_SELLERS_BY_AUCTIONS
        )

        if top_sellers_res.empty():
            print("No seller auction data available.")
        else:
            for seller_login, num_auctions in top_sellers_res:
                print(f"Seller: {seller_login} | Auctions: {num_auctions}")

        print("-" * 30)

        questionary.press_any_key_to_continue().ask()
        return "admin_dashboard"

class AdminDashboardScreen(Screen):
    def show(self):
        questionary.print(
            f"Welcome, {self.app.current_user}.",
            style="bold"
        )

        choices = {
            "Delete User That are not Buyers": "create_item",
            "Remove Items" : "remove_item", 
            "Change User Roles" : "change_user_role",
            "View Analytics" : "view_analytics",
            "Return": "home"
        }

        res = questionary.select(
            "Admin Dashboard",
            choices=list(choices.keys())
        ).ask()

        return choices[res]
    
class ChangeRoleScreen(Screen):
    def show(self):
        questionary.print("Change User Role:", style="bold")

        login = questionary.text("Enter user login: ").ask()

        if login is None:
            return "admin_dashboard"

        login = login.strip()

        if login == "":
            questionary.print(
                "\nLogin cannot be blank.\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()
            return "admin_dashboard"

        # Check if user exists
        res = self.app.esql.execute_query(
            queries.GET_USER_BY_LOGIN,
            (login,)
        )

        if res.empty():
            questionary.print(
                f"\nUser '{login}' does not exist.\n",
                style="bold fg:red"
            )
            questionary.press_any_key_to_continue().ask()
            return "admin_dashboard"

        user_login, current_role = res[0]

        questionary.print(
            f"\nCurrent role for {user_login}: {current_role}\n",
            style="bold"
        )

        role_choices = ["Buyer", "Seller", "Admin", "Return"]

        new_role = questionary.select(
            "Select new role:",
            choices=role_choices
        ).ask()

        if new_role == "Return" or new_role is None:
            return "admin_dashboard"

        confirm = questionary.confirm(
            f"Change {user_login}'s role from {current_role} to {new_role}?"
        ).ask()

        if not confirm:
            return "admin_dashboard"

        self.app.esql.execute_update(
            queries.SET_USER_ROLE,
            (new_role, user_login)
        )

        questionary.print(
            f"\nSuccessfully changed {user_login}'s role to {new_role}.\n",
            style="bold fg:green"
        )
        questionary.press_any_key_to_continue().ask()

        return "admin_dashboard"
    
