import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import os
import cv2
import sqlite3
import io
import numpy as np
from model import RootAnalyzer

class RegisterView:
    def __init__(self, root, on_register):
        self.root = root
        self.on_register = on_register

        self.root.title("Register")
        self.root.geometry("300x200")

        self.username_label = tk.Label(self.root, text="Username:")
        self.username_label.pack()

        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        self.password_label = tk.Label(self.root, text="Password:")
        self.password_label.pack()

        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        self.password_label = tk.Label(self.root, text="Confirm Password:")
        self.password_label.pack()

        self.c_password_entry = tk.Entry(self.root, show="*")
        self.c_password_entry.pack()

        self.register_button = tk.Button(self.root, text="Register", command=self.register)
        self.register_button.pack()
        # Connect to the SQLite database
        self.conn = sqlite3.connect('users.db')
        self.cur = self.conn.cursor()

    def register(self):
        # Get username and password from entry fields
        username = self.username_entry.get()
        password = self.password_entry.get()
        c_password=self.c_password_entry.get()
        


        # Check if username already exists
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            messagebox.showerror("Registration Failed", "Username already exists")
        else:
            if password!= c_password:
                messagebox.showerror("Registration Failed", "Password differs ")
            # Insert new user into the database
            else:
                # Insert new user into the database
                self.cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                self.conn.commit()  # Commit the changes to the database
                messagebox.showinfo("Registration Successful", "You have been registered successfully")
                self.on_register()
                self.root.destroy()  # Close the register window after successful registration

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

        self.register_button = tk.Button(self.root, text="Register", command=self.open_register_window)
        self.register_button.pack()

        # Connect to the SQLite database
        self.conn = sqlite3.connect('users.db')
        global cur
        cur = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # Create a table for users if it does not exist
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE,
                        password TEXT
                        )''')
        self.conn.commit()

    def open_register_window(self):
        register_window = tk.Toplevel(self.root)
        register_view = RegisterView(register_window, self.on_register)

    def on_register(self):
        # Handle actions after successful registration
        messagebox.showinfo("Registration Success", "You can now login with your new account.")

    def login(self):
        # Perform authentication here (check username and password)
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Check if username and password match
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()

        if user:
            # Call the callback function to indicate successful login
            self.on_login()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def __del__(self):
        # Close the database connection when the object is destroyed
        self.conn.close()

class RootMeasurementView:
    def __init__(self, root):
        self.root = root
        self.root.title("Root Measurement App")
        self.root.minsize(1400, 800)
        self.image = None
        self.seuil = 180  # Initial threshold value
        self.ratio = 1  # default ratio returns the number of pixels

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create a frame to contain the buttons
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(side="right", fill="y")

        self.load_button = tk.Button(self.button_frame, text="Load Image", command=self.load_image,
                                     width=15, height=2)
        self.load_button.pack(fill="x", pady=5)

        self.threshold_label = tk.Label(self.button_frame, text="Threshold:")
        self.threshold_label.pack()

        self.threshold_slider = tk.Scale(self.button_frame, from_=0, to=255, orient="horizontal",
                                         command=self.update_threshold)
        self.threshold_slider.set(self.seuil)
        self.threshold_slider.pack()

        self.process_button = tk.Button(self.button_frame, text="Process Image", command=self.process_image,
                                        width=15, height=2)
        self.process_button.pack(fill="x", pady=5)

        self.calibrate_button = tk.Button(self.button_frame, text="Calibrate", command=self.calibrate,
                                          width=15, height=2)
        self.calibrate_button.pack(fill="x", pady=5)

        self.clear_button = tk.Button(self.button_frame, text="Clear Image", command=self.clear_image,
                                      width=15, height=2)
        self.clear_button.pack(fill="x", pady=5)

        self.image_label = tk.Label(self.main_frame)
        self.image_label.pack(side="left", fill="both", expand=True)

        self.table_frame = tk.Frame(self.main_frame)
        self.table_frame.pack(side="right", fill="y")

        self.treeview = ttk.Treeview(self.table_frame, columns=("Length",))
        self.treeview.heading("#0", text="Index")
        self.treeview.heading("Length", text="Length in cm")
        self.treeview.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.treeview.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.treeview.configure(yscrollcommand=self.scrollbar.set)

        # Create an instance of the RootAnalyzer class
        self.root_analyzer = RootAnalyzer()
        self.first_update = True
        self.calibrated = False
        self.thershold_modified = True

    def load_image(self):
        image_path = filedialog.askopenfilename(initialdir="/", title="Select Image")
        if image_path:
            # Check if the file is an image
            try:
                with Image.open(image_path) as img:
                    # If opening the image succeeds, display it
                    self.display_image(image_path)
                    self.image = image_path  # Update the self.image attribute
            except Exception as e:
                # If opening the image fails, show a messagebox
                messagebox.showerror("Error", "Selected file is not a valid image.")

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
            self.root_analyzer.load_image(self.image)
            processed_image = self.root_analyzer.fix_threshold(self.seuil)
            # Update the image label with the new image
            self.image_label.config(image=processed_image)
            self.image_label.image = processed_image
            self.thershold_modified = False 
        else:
            if not self.first_update:
                messagebox.showerror("No Image loaded", "Please load an image first")
            self.first_update = False

    def process_image(self):
        if self.calibrated :
            if  self.thershold_modified:
                messagebox.showerror("Threshold not modified", "Please modify threshold")
            if self.image is not None:
                try:
                    # Measure roots and get the Tkinter image with contours
                    self.root_analyzer.load_image(self.image)
                    root_measurements, processed_image = self.root_analyzer.measure_roots_m()

                    # Update the image label with the new image
                    self.display_image_with_contours(processed_image, root_measurements)

                    # Update the table with root measurements
                    self.update_table(root_measurements)
                except ValueError as e:
                    if "threshold" in str(e):
                        messagebox.showwarning("Threshold Error",
                                            "Please adjust the threshold value before measuring roots.")
                    else:
                        messagebox.showerror("Error", str(e))
            else:
                messagebox.showerror("No Image loaded", "Please load an image first")
        else :
            messagebox.showerror("Not calibrated ", "No calibration is done !")

    def display_image_with_contours(self, processed_image, root_measurements):
        # Display the processed image with contours
        self.image_label.config(image=processed_image)
        self.image_label.image = processed_image

        # Bind mouse click event to the image label
        #self.image_label.bind("<Button-1>", lambda event: self.display_root_length(event, root_measurements))

    def display_root_length(self, event, root_measurements):
        x, y = event.x, event.y

        # Clear existing length labels
        for label in self.image_label.place_slaves():
            label.destroy()

        closest_distance = float('inf')
        closest_point = None
        root_length = None

        # Find the closest point to the click
        for point, length in root_measurements:
            distance = np.linalg.norm(np.array(point) - np.array([x, y]))
            if distance < closest_distance:
                closest_distance = distance
                closest_point = point
                root_length = length

        if closest_point is not None:
            if isinstance(closest_point, np.ndarray):
                # If closest_point is an array, choose the first coordinate
                closest_point = closest_point[0]

            # Extract x and y coordinates from closest_point
            closest_x, closest_y = closest_point

            # Add a label next to the point to display the root length
            label = tk.Label(self.image_label, text=f"Length: {root_length*self.ratio}")
            label.place(x=closest_x, y=closest_y, anchor="center")

            # Increase the font size when the label is clicked
            def increase_font_size(_event):
                label.config(font=("Arial", 12, "bold"))  # Increase font size to 12 and make it bold
                label.unbind("<Button-1>")  # Unbind the event to prevent further clicks

            label.bind("<Button-1>", increase_font_size)
        else:
            messagebox.showerror("Error", "No root measurement found at this position.")

    def update_table(self, root_measurements):
        # Clear previous entries in the table
        for row in self.treeview.get_children():
            self.treeview.delete(row)

        # Insert new entries for root measurements
        for idx, (_, root_length) in enumerate(root_measurements, start=1):
            root_length_cm=root_length*self.ratio
            self.treeview.insert("", "end", text=str(idx), values=(f"{root_length_cm:.2f} cm"))

    def clear_image(self):
        # Clear length labels
        for label in self.image_label.place_slaves():
            label.destroy()

        # Clear table
        for row in self.treeview.get_children():
            self.treeview.delete(row)

        # Clear image
        self.image_label.config(image=None)
        self.image_label.image = None

    def calibrate(self):
        # Open a new window for calibration
        self.calibrated = True
        calibration_window = tk.Toplevel(self.root)
        calibration_view = CalibrationView(calibration_window, self)




class CalibrationView:
    def __init__(self, root, root_measurement_view):
        self.root = root
        self.root.title("Calibration")
        self.root.geometry("1400x800")
        self.root_measurement_view = root_measurement_view
        self.image = None
        self.ratio = tk.DoubleVar(self.root, 127)
        self.seuil = 127

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side="right", fill="y")

        self.load_button = tk.Button(self.button_frame, text="Load Image", command=self.load_image,
                                     width=15, height=2)
        self.load_button.pack(fill="x", pady=5)

        self.threshold_slider = tk.Scale(self.button_frame, from_=0, to=255, orient="horizontal", label="Threshold",
                                         command=self.update_threshold)
        self.threshold_slider.set(self.seuil)
        self.threshold_slider.pack(fill="x", pady=5)

        self.calibrate_button = tk.Button(self.button_frame, text="Calibrate Length", command=self.calibrate_length,
                                          width=15, height=2)
        self.calibrate_button.pack(fill="x", pady=5)


        self.image_label = tk.Label(self.root)
        self.image_label.pack(side="left", fill="both", expand=True)

        # Create an instance of the RootAnalyzer class
        self.root_analyzer = RootAnalyzer()
        self.first_update = True

    def load_image(self):
        image_path = filedialog.askopenfilename(initialdir="/", title="Select Image")
        if image_path:
            # Check if the file is an image
            try:
                with Image.open(image_path) as img:
                    # If opening the image succeeds, display it
                    self.display_image(image_path)
                    self.image = image_path
            except Exception as e:
                # If opening the image fails, show a messagebox
                messagebox.showerror("Error", "Selected file is not a valid image.",parent=self.root)
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
        if self.root_analyzer:
            self.root_analyzer.threshold = self.seuil
        if self.image is not None:
            self.root_analyzer.load_image(self.image)
            # Fix the threshold and get the processed image
            processed_image = self.root_analyzer.fix_threshold(self.seuil)
            # Update the image label with the new image
            self.image_label.config(image=processed_image)
            self.image_label.image = processed_image
            self.first_update = False
        else:
            if not self.first_update:
                messagebox.showerror("No Image loaded", "Please load an image first",parent=self.root)

    def update_ratio(self,ratio):
        self.root_measurement_view.ratio = ratio
    
    def calibrate_length(self):
        length_cm = simpledialog.askfloat("Calibrate Length", "Enter the length in centimeters:", parent=self.root)
        if length_cm is not None and length_cm > 0:
            if self.image is not None:
                self.root_analyzer.load_image(self.image)
                length, valide = self.root_analyzer.calibrate_roots_mesurment()
                if valide:
                    self.ratio = length_cm / length
                    self.update_ratio(self.ratio)
                    print(length)
                    print(self.ratio)
                    # Show success message
                    messagebox.showinfo("Calibration Successful", "Calibration was successfully done.", parent=self.root)
                    self.root.destroy()
                else:
                    messagebox.showerror("Error", "Couldn't detect the contours. Try another image.", parent=self.root)
            else:
                messagebox.showerror("No Image loaded", "Load an image first ", parent=self.root)
        else:
            messagebox.showerror("Calibration Failed", "Invalid length entered", parent=self.root)



# def login_success():
#     # Close the login window and open the main application window
#     login_window.destroy()
#     root = tk.Tk()
#     view = RootMeasurementView(root)
#     icon_path = "/home/hdfixi/Documents/roots-length/src/pfe_jasser/roots.png"
#     if os.path.exists(icon_path):
#         root.iconphoto(True, tk.PhotoImage(file=icon_path))
#     root.mainloop()

# Create a Tkinter window for login
# login_window = tk.Tk()
# login_view = LoginView(login_window, login_success)
# login_window.mainloop()