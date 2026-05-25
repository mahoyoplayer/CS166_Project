# https://github.com/mahoyoplayer/CS166_Project
import customtkinter as ctk
import tkinter as tk

class HomePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        label = ctk.CTkLabel(self, text="Home Page", font=("Arial", 24))
        label.pack(pady=20)

        button = ctk.CTkButton(
            self,
            text="Go to Settings",
            command=lambda: master.show_page("settings")
        )
        button.pack(pady=10)


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        label = ctk.CTkLabel(self, text="Settings Page", font=("Arial", 24))
        label.pack(pady=20)

        button = ctk.CTkButton(
            self,
            text="Back to Home",
            command=lambda: master.show_page("home")
        )
        button.pack(pady=10)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Multi-page CustomTkinter App")
        self.geometry("1000x1000")

        self.pages = {}

        self.pages["home"] = HomePage(self)
        self.pages["settings"] = SettingsPage(self)

        for page in self.pages.values():
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_page("home")

    def show_page(self, page_name):
        page = self.pages[page_name]
        page.tkraise()


if __name__ == "__main__":
    app = App()
    app.mainloop()