import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageGrab
import os
import sqlite3
import numpy as np
from model import RootAnalyzer
import re
import smtplib
from email.mime.text import MIMEText
import random
import string
from datetime import datetime
import pandas as pd
import openpyxl
from openpyxl import load_workbook
class RootMeasurementView:
    def __init__(self, root, user):
        self.root = root
        self.root.title("Root Measurement App")
        self.root.minsize(1400, 800)
        self.image = None
        self.seuil = 180  # Initial threshold value
        self.ratio = 1  # default ratio returns the number of pixels
        self.user=user
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

        self.crop_button = tk.Button(self.button_frame, text="Crop Image", command=self.open_image_cropper,
                                     width=15, height=2)  # Bind open_image_cropper function
        self.crop_button.pack(fill="x", pady=5)

        self.reset_crop_button = tk.Button(self.button_frame, text="Reset Crop", command=self.reset_cropper,
                                     width=15, height=2)  # Bind open_image_cropper function
        self.reset_crop_button.pack(fill="x", pady=5)

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
        self.cropped_image = None
        self.conn = None
    def open_image_cropper(self):
        # Check if an image is loaded
        if self.image:
            # Open a new window for cropping the image
            crop_window = tk.Toplevel(self.root)
            image_cropper = ImageCropper(self, crop_window)
        else:
            messagebox.showerror("Error", "Please load an image first.")

    def load_image(self):
        image_path = filedialog.askopenfilename(initialdir="/", title="Select Image")#home/hdfixi/Documents/roots-length/src/pfe_jasser
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

    def display_image(self, image):
        if isinstance(image, str):
            image_tk = self.convert_image(image)
        elif isinstance(image, Image.Image):
            image_tk = self.convert_image(image)
        else:
            raise ValueError("Invalid image type. Expected path string or PIL Image.")

        self.image_label.config(image=image_tk)
        self.image_label.image = image_tk

    def convert_image(self, image):
        if isinstance(image, str):
            image_pil = Image.open(image)
        elif isinstance(image, Image.Image):
            image_pil = image.convert("RGBA")
        else:
            raise ValueError("Invalid image type. Expected path string or PIL Image.")
        
        image_tk = ImageTk.PhotoImage(image_pil)
        return image_tk

    def update_threshold(self, value):
        self.seuil = int(value)
        self.root_analyzer.threshold = self.seuil
        if self.image is not None and self.cropped_image is None:
            # Fix the threshold and get the processed image
            self.root_analyzer.load_image(self.image)
            processed_image = self.root_analyzer.fix_threshold(self.seuil)
            # Update the image label with the new image
            self.image_label.config(image=processed_image)
            self.image_label.image = processed_image
            self.thershold_modified = False 
        elif self.cropped_image is not None:
            # Fix the threshold and get the processed image
            self.root_analyzer.load_image(self.cropped_image)
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
        if self.calibrated:
            if self.thershold_modified:
                messagebox.showerror("Threshold not modified", "Please modify threshold")
            else:
                if self.cropped_image is not None:
                    image = self.cropped_image  # Use the cropped image if provided
                elif self.image is not None and self.cropped_image is None:
                    image = self.image  # Use the original image if no cropped image provided
                else:
                    messagebox.showerror("No Image loaded", "Please load an image first")
                    return

                try:
                    # Measure roots and get the Tkinter image with contours
                    self.root_analyzer.load_image(image)
                    root_measurements, processed_image = self.root_analyzer.measure_roots_m()
                    total_length=sum(length*self.ratio for i,length in root_measurements)
                    formatted_length = "{:.2f}".format(total_length)
                    messagebox.showinfo("Total length ",f"Total length of roots:\n {formatted_length} cm")

                    # Update the image label with the new image
                    self.display_image_with_contours(processed_image, root_measurements)

                    # Update the table with root measurements
                    self.update_table(root_measurements)
                    # Save processed image and table data in the database
                    self.save_to_database(processed_image, root_measurements)
                    
                except ValueError as e:
                    if "threshold" in str(e):
                        messagebox.showwarning("Threshold Error",
                                            "Please adjust the threshold value before measuring roots.")
                    else:
                        messagebox.showerror("Error", str(e))
        else:
            messagebox.showerror("Not calibrated ", "No calibration is done !")
    
    def save_to_database(self, processed_image, root_measurements):
        # Specify the directory paths
        image_directory = "processed_images"
        excel_directory = "saved_measurements"
        excel_file = "root_measurements.xlsx"

        # Create the directories if they don't exist
        if not os.path.exists(image_directory):
            os.makedirs(image_directory)
        if not os.path.exists(excel_directory):
            os.makedirs(excel_directory)
            print("Created directory:", excel_directory)
            
        timestamp = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

        # Save the processed image to a file in the specified directory
        image_filename = f"{self.user}_{timestamp}.png"
        image_path = os.path.join(image_directory, image_filename)

        # Convert Tkinter PhotoImage to a canvas
        canvas_width, canvas_height = processed_image.width(), processed_image.height()
        canvas = tk.Canvas(self.root, width=canvas_width, height=canvas_height)
        canvas.create_image((canvas_width, canvas_height), image=processed_image)
        canvas.update() 

        # Save canvas as PNG image
        canvas_img = ImageGrab.grab(bbox=(canvas.winfo_rootx(), canvas.winfo_rooty(), canvas.winfo_rootx() + canvas_width*1.4, canvas.winfo_rooty() + canvas_height*1.4))
        canvas_img.save(image_path, 'PNG')

        # Connect to the SQLite database
        self.conn = sqlite3.connect('users.db')
        cur = self.conn.cursor()

        # Get current user's username
        username = self.user 
        # SQL statements to create tables if they do not exist
        processed_image_table_sql = """
        CREATE TABLE IF NOT EXISTS processed_images_table (
            id INTEGER PRIMARY KEY,
            username TEXT,
            image_path TEXT,
            timestamp TEXT
        )
        """

        root_measurements_table_sql = """
        CREATE TABLE IF NOT EXISTS roots_measurements_table (
            id INTEGER PRIMARY KEY,
            username TEXT,
            measurement_index INTEGER,
            length FLOAT,
            timestamp TEXT
        )
        """

        # Execute SQL statements to create tables
        try:
            cur.execute(processed_image_table_sql)
            cur.execute(root_measurements_table_sql)
            self.conn.commit()
            print("Tables created successfully.")
        except sqlite3.Error as e:
            print("Error creating tables:", e)

        # Insert image path into the database
        cur.execute("INSERT INTO processed_images_table (username, image_path, timestamp) VALUES (?, ?, ?)",
                    (str(username), image_path, timestamp))

        # Insert root measurements into the database
        for index, (contour_array, length) in enumerate(root_measurements, start=1):
            # Save contour_array and length to the database
            cur.execute("INSERT INTO roots_measurements_table (username, measurement_index, length, timestamp) VALUES (?, ?, ?, ?)",
                        (str(username), index, round(length, 2)*self.ratio, timestamp))
            
        self.conn.commit()

        # Extract data from root measurements
        data = {"Time":[],"Measurement Index": [], "Length": [], 'Image path':[]}
        for index, (contour_array, length) in enumerate(root_measurements, start=1):
            data["Measurement Index"].append(index)
            data["Length"].append("{:.2f}".format(length*self.ratio))
            data["Time"].append(timestamp)
            data["Image path"].append(image_path)
        
        # Create a DataFrame from the extracted data
        df = pd.DataFrame(data)
        
        # Create a DataFrame for the separator
        sep = pd.DataFrame({"Time":["-"],"Measurement Index": ["-"], "Length": ["-"],"Image path":["-"]})
        
        # Commit changes to the database
        excel_file = "root_measurements.xlsx"
        # Export the DataFrame to an Excel file in the specified directory
        excel_path = os.path.join(excel_directory, excel_file)

        # Create the Excel file if it doesn't exist
        if not os.path.exists(excel_path):
            df.to_excel(excel_path, index=False)
        else:
            # Load the existing workbook
            wb = load_workbook(excel_path)
            ws = wb.active

            # Add a row of separators
            ws.append(["-", "-", "-", "-"])

            # Add the new data to the worksheet
            for row in df.values:
                ws.append(list(row))

            # Save the changes
            wb.save(excel_path)




    def __del__(self):
        # Close the database connection when the object is destroyed
        self.conn.close()

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
        calibration_window = tk.Toplevel(self.root)
        calibration_window.attributes("-topmost", True)
        calibration_view = CalibrationView(calibration_window, self)
    
    def update_image(self, new_image):
        self.display_image(new_image)
    
    def reset_cropper(self):
        self.cropped_image=None
        self.display_image(self.image)

  

class ImageCropper:
    def __init__(self, root_measurement_view, root):
        self.root_measurement_view = root_measurement_view
        self.root = root
        self.root.title("Image Cropper")
        self.root.minsize(1400, 800)

        self.canvas = tk.Canvas(self.root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.cropped_image=None
        
        self.image = Image.open(root_measurement_view.image)  # Ensure self.image is an Image object, not a string

        self.canvas.bind("<ButtonPress-1>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.track_crop)
        self.canvas.bind("<ButtonRelease-1>", self.end_crop)

        self.image_label = tk.Label(self.root)
        self.image_label.pack(fill=tk.BOTH, expand=True)
        self.display_image(self.image)
        
        # Add confirm and reset buttons
        self.confirm_button = tk.Button(self.root, text="Confirm Crop", command=self.confirm_crop)
        self.confirm_button.pack(side="left", padx=10, pady=10)
        
        self.reset_button = tk.Button(self.root, text="Reset Crop", command=self.reset_crop)
        self.reset_button.pack(side="left", padx=10, pady=10)

    def start_crop(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

    def track_crop(self, event):
        self.end_x = self.canvas.canvasx(event.x)
        self.end_y = self.canvas.canvasy(event.y)
        self.canvas.delete("crop_rect")
        self.canvas.create_rectangle(self.start_x, self.start_y, self.end_x, self.end_y, outline="red", tag="crop_rect")

    def end_crop(self, event):
        self.end_x = self.canvas.canvasx(event.x)
        self.end_y = self.canvas.canvasy(event.y)

        # Convert coordinates to integers and ensure start_x < end_x and start_y < end_y
        x0, x1 = sorted([int(self.start_x), int(self.end_x)])
        y0, y1 = sorted([int(self.start_y), int(self.end_y)])

        # Crop the image and display the cropped region
        cropped_image = self.image.crop((x0, y0, x1, y1))
        self.cropped_image = cropped_image

        # Update the cropped image in the root measurement view
        self.display_image_crop(cropped_image)

    def confirm_crop(self):
        self.root_measurement_view.display_image(self.cropped_image)
        self.root_measurement_view.cropped_image = self.cropped_image
        messagebox.showinfo("Crop Confirmed", "Crop has been confirmed.")
        # Close the window
        self.root.destroy()
        

    def reset_crop(self):
        self.canvas.delete("crop_rect")
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None

        # Redisplay the original image
        self.display_image(self.image)

    def display_image_crop(self, image):
        if isinstance(image, str):
            image_path = image
            image = Image.open(image_path)
        image_tk = ImageTk.PhotoImage(image)
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        image_width = image.width
        image_height = image.height
        
        # Calculate the offsets to center the image
        x_offset = (canvas_width - image_width) // 2
        y_offset = (canvas_height - image_height) // 2

        # Clear previous image on canvas
        self.canvas.delete("image")

        # Create image on canvas
        self.canvas.image = image_tk  # Store a reference to the image to prevent garbage collection
        self.canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=image_tk, tags="image")

        # Bind window resize event to adjust image size
        self.root.bind("<Configure>", self.on_resize)

    def display_image(self, image):
        if isinstance(image, str):
            image_path = image
            image = Image.open(image_path)
        image_tk = ImageTk.PhotoImage(image)
        self.canvas.config(width=image.width, height=image.height)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
        self.canvas.image = image_tk

    def on_resize(self, event):
        # Adjust image coordinates and dimensions when window is resized
        image_width = self.canvas.image.width()
        image_height = self.canvas.image.height()
        canvas_width = event.width
        canvas_height = event.height

        # Calculate new coordinates and dimensions to fit the window
        scale = min(canvas_width / image_width, canvas_height / image_height)
        new_width = int(image_width * scale)
        new_height = int(image_height * scale)
        x_offset = (canvas_width - new_width) // 2
        y_offset = (canvas_height - new_height) // 2

        # Update image coordinates and dimensions
        self.canvas.coords("image", x_offset, y_offset)
        self.canvas.itemconfig("image", width=new_width, height=new_height)

    def convert_image(self, image_path):
        image_pil = Image.open(image_path)
        image_pil = image_pil.convert("RGBA")
        image_tk = ImageTk.PhotoImage(image_pil)
        return image_tk





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
        c_password = self.c_password_entry.get()

        # Verify if username is in email format using regular expression
        if not re.match(r"[^@]+@[^@]+\.[^@]+", username):
            messagebox.showerror("Registration Failed", "Invalid email address")
            return

        # Check if username already exists
        self.cur.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = self.cur.fetchone()

        if existing_user:
            messagebox.showerror("Registration Failed", "Username already exists")
        else:
            if password != c_password:
                messagebox.showerror("Registration Failed", "Password differs ")
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
        self.current_user_username = None

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

        self.forget_password_button = tk.Button(self.root, text="Forget Password", command=self.open_forget_password_window)
        self.forget_password_button.pack()
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
        # Get username and password from entry fields
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Check if username and password are not empty
        if not username or not password:
            messagebox.showerror("Login Failed", "Please enter both username and password")
            return

        # Perform authentication here (check username and password)
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()

        if user:
            # Call the callback function to indicate successful login
            self.current_user_username = username
            self.on_login()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def open_forget_password_window(self):
        forget_password_window = tk.Toplevel(self.root)
        forget_password_view = ForgetPasswordView(forget_password_window)

    def get_current_user_username(self):
        # Return the current user's username
        return self.current_user_username
    
    def __del__(self):
        # Close the database connection when the object is destroyed
        self.conn.close()

class ForgetPasswordView:
    def __init__(self, root):
        self.root = root

        self.root.title("Forget Password")
        self.root.geometry("300x150")

        self.email_label = tk.Label(self.root, text="Enter your email:")
        self.email_label.pack()

        self.email_entry = tk.Entry(self.root)
        self.email_entry.pack()

        self.send_button = tk.Button(self.root, text="Send Reset Email", command=self.send_reset_email)
        self.send_button.pack()

    def send_reset_email(self):
        email = self.email_entry.get()
        # Generate a temporary password
        temporary_password = generate_random_password()

        # Send email with temporary password
        self.send_email(email, temporary_password)

        messagebox.showinfo("Email Sent", "Please check your email for instructions to reset your password.")

    def send_email(self, email, temporary_password):
        # Configure email settings
        sender_email = "jasserayed54@gmail.com"  # Replace with your email address
        password = "Jasser@27102001"  # Replace with your email password

         # Compose message
        message = MIMEText(f"Your temporary password is: {temporary_password}")
        message["Subject"] = "Password Reset"
        message["From"] = sender_email
        message["To"] = email

        try:
            # Connect to SMTP server and send email
            with smtplib.SMTP("smtp.google.com", 465) as server:  # Replace with your SMTP server and port
                server.starttls()  # Use TLS encryption
                server.login(sender_email, password)
                server.send_message(message)
            print("Email sent successfully")
        except Exception as e:
            print(f"Failed to send email: {e}")

def generate_random_password():
    # Generate a random password of length 8
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


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
        image_path = filedialog.askopenfilename(initialdir="/", title="Select Image",parent=self.root)#home/hdfixi/Documents/roots-length/src/pfe_jasser
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
        self.root_measurement_view.calibrated = True
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
#     user=login_view.get_current_user_username()
#     login_window.destroy()
#     root = tk.Tk()
#     view = RootMeasurementView(root,user)
#     icon_path = "/home/hdfixi/Documents/roots-length/src/pfe_jasser/roots.png"
#     if os.path.exists(icon_path):
#         root.iconphoto(True, tk.PhotoImage(file=icon_path))
#     root.mainloop()

# #Create a Tkinter window for login
# icon_path = "/home/hdfixi/Documents/roots-length/src/pfe_jasser/roots.png"
# login_window = tk.Tk()
# login_window.iconphoto(True, tk.PhotoImage(file=icon_path))
# login_view = LoginView(login_window, login_success)
# login_window.mainloop()