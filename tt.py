import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

from model import RootAnalyzer

class LoginView:
    def __init__(self, root, on_login):
        self.root = root
        self.on_login = on_login

        self.root.title("Login")
        self.root.geometry("300x200")

        self.username_label = tk.Label(self.root, text="Username:")
        self.username_label.pack()

        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        self.password_label = tk.Label(self.root, text="Password:")
        self.password_label.pack()

        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        self.login_button = tk.Button(self.root, text="Login", command=self.login)
        self.login_button.pack()

    def login(self):
        # Perform authentication here (check username and password)
        # For simplicity, let's just check if the username is "admin" and password is "password"
        if self.username_entry.get() == "a" and self.password_entry.get() == "p":
            # Call the callback function to indicate successful login
            self.on_login()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

class RootMeasurementView:
    def __init__(self, root):
        self.root = root
        self.root.title("Root Measurement App")
        self.root.minsize(1400, 800)
        self.image=None
        self.seuil = 180  # Initial threshold value

        # Create a frame to contain the buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side="right", fill="y")

        self.load_button = tk.Button(self.button_frame, text="Load Image", command=self.load_image,
                                     width=15, height=2)
        self.load_button.pack(fill="x", pady=5)

        self.threshold_label = tk.Label(self.button_frame, text="Threshold:")
        self.threshold_label.pack()

        self.threshold_slider = tk.Scale(self.button_frame, from_=0, to=255, orient="horizontal", command=self.update_threshold)
        self.threshold_slider.set(self.seuil)
        self.threshold_slider.pack()

        self.process_button = tk.Button(self.button_frame, text="Process Image", command=self.process_image,
                                        width=15, height=2)
        self.process_button.pack(fill="x", pady=5)

        self.clear_button = tk.Button(self.button_frame, text="Clear Image", command=self.clear_image,
                                      width=15, height=2)
        self.clear_button.pack(fill="x", pady=5)

        self.image_label = tk.Label(self.root)
        self.image_label.pack(side="left", fill="both", expand=True)

        # Create an instance of the RootAnalyzer class
        self.root_analyzer = RootAnalyzer()

    def load_image(self):
        image_path = filedialog.askopenfilename(initialdir="/home/hdfixi/Documents/roots-length", title="Select Image")
        if image_path:
            self.display_image(image_path)
            self.image=image_path
            self.root_analyzer.load_image(self.image)

    def display_image(self, image_path):
        image_tk = self.convert_image(image_path)
        self.image_label.config(image=image_tk)
        self.image_label.image = image_tk

    def convert_image(self, image_path):
        image_pil = Image.open(image_path)
        image_pil = image_pil.convert("RGBA")
        image_tk = ImageTk.PhotoImage(image_pil)
        return image_tk

    def update_threshold(self, value):
        self.seuil = int(value)
        self.root_analyzer.threshold = self.seuil
        if self.image is not None:
            # Fix the threshold and get the processed image
            processed_image = self.root_analyzer.fix_threshold(self.seuil)
            # Update the image label with the new image
            self.image_label.config(image=processed_image)
            self.image_label.image = processed_image
        else:
            messagebox.showerror("No Image loaded", "Please load an image first")


    def process_image(self):
        
        if self.image!=None:
            # Perform processing and get the processed image
            total_length, total_length_cm = self.root_analyzer.measure_roots()
            # Display the processed image
        else:
            messagebox.showerror("No Image loaded", "Please load an image first")

    def clear_image(self):
        self.image_label.config(image=None)
        self.image_label.image = None
class CalibrationView:
    def __init__(self, root):
        self.root = root
        self.root.title("Calibration")
        self.root.geometry("400x300")

def login_success():
    # Close the login window and open the main application window
    login_window.destroy()
    root = tk.Tk()
    view = RootMeasurementView(root)
    icon_path = "/home/hdfixi/Documents/roots-length/src/pfe_jasser/roots.png"
    if os.path.exists(icon_path):
        root.iconphoto(True, tk.PhotoImage(file=icon_path))
    root.mainloop()

# Create a Tkinter window for login
login_window = tk.Tk()
login_view = LoginView(login_window, login_success)
login_window.mainloop()