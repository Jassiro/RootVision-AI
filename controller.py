import tkinter as tk
from view import LoginView , RootMeasurementView
import os

def login_success():
    # Close the login window and open the main application window
    login_window.destroy()
    root = tk.Tk()
    view = RootMeasurementView(root)
    icon_path = "./roots.png"
    if os.path.exists(icon_path):
        root.iconphoto(True, tk.PhotoImage(file=icon_path))
    root.mainloop()

# Create a Tkinter window for login
icon_path = "./roots.png"
login_window = tk.Tk()
login_window.iconphoto(True, tk.PhotoImage(file=icon_path))
login_view = LoginView(login_window, login_success)
login_window.mainloop()