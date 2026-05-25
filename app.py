from screen import *
import os
import subprocess

def clear_console() -> None:
    clear_command = "cls" if os.name == "nt" else "clear"
    subprocess.run(clear_command, shell=True, check=False)

class App:
    def __init__(self):
        self.running = True
        self.screens = {
            "login" : LoginScreen(self)
        }
        
    def run(self):
        # Initial Screen
        curr_screen = "login"
        while self.running:
            clear_console()
            curr_screen = self.screens[curr_screen].show()
        clear_console()
            
