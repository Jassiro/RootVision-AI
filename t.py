import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

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

        self.crop_button = tk.Button(self.button_frame, text="Crop Image", command=self.crop_image,
                                     width=15, height=2)
        self.crop_button.pack(fill="x", pady=5)

        self.canvas = tk.Canvas(self.root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.crop_rect = None

    def load_image(self):
        image_path = filedialog.askopenfilename(title="Select Image")
        if image_path:
            try:
                with Image.open(image_path) as img:
                    self.image = img
                    self.display_image(img)
            except Exception as e:
                messagebox.showerror("Error", "Selected file is not a valid image.")

    def display_image(self, image):
        if isinstance(image, str):
            image_path = image
            image = Image.open(image_path)
        image_tk = ImageTk.PhotoImage(image)
        self.canvas.config(width=image.width, height=image.height)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
        self.canvas.image = image_tk

    def update_threshold(self, value):
        self.seuil = int(value)
        # Update the image with the new threshold

    def process_image(self):
        pass  # Placeholder for processing image functionality

    def calibrate(self):
        pass  # Placeholder for calibration functionality

    def clear_image(self):
        self.canvas.delete("all")
        self.image = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.crop_rect = None

    def crop_image(self):
        if self.start_x is not None and self.end_x is not None and self.start_y is not None and self.end_y is not None:
            x0, y0 = self.start_x, self.start_y
            x1, y1 = self.end_x, self.end_y
            if x0 > x1:
                x0, x1 = x1, x0
            if y0 > y1:
                y0, y1 = y1, y0
            cropped_image = self.image.crop((x0, y0, x1, y1))
            self.display_image(cropped_image)

    def start_crop(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

    def track_crop(self, event):
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
        self.end_x = self.canvas.canvasx(event.x)
        self.end_y = self.canvas.canvasy(event.y)
        self.crop_rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.end_x, self.end_y, outline="red")

    def end_crop(self, event):
        self.end_x = self.canvas.canvasx(event.x)
        self.end_y = self.canvas.canvasy(event.y)
        self.crop_image()

root = tk.Tk()
app = RootMeasurementView(root)
app.canvas.bind("<ButtonPress-1>", app.start_crop)
app.canvas.bind("<B1-Motion>", app.track_crop)
app.canvas.bind("<ButtonRelease-1>", app.end_crop)
root.mainloop()
