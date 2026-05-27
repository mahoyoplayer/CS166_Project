from screen import *
import os
import subprocess

def clear_console() -> None:
    clear_command = "cls" if os.name == "nt" else "clear"
    subprocess.run(clear_command, shell=True, check=False)

class App:
    def __init__(self):
        self.running = True
        self.current_user = None
        self.current_role = None
        self.screen_map = {
            "welcome" : WelcomeScreen(self),
            "login" : LoginScreen(self),
            "register" : RegisterScreen(self)
        }
        
    def run(self):
        # Initial Screen
        curr_screen = "welcome"
        while self.running:
            clear_console()
            curr_screen = self.screen_map[curr_screen].show()
        clear_console()

            
