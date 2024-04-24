import cv2
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev

class RootAnalyzer:
    def __init__(self):
        self.image = None
        self.threshold=180
        self.total_length = 0

    def load_image(self, image_path_or_image):
        if isinstance(image_path_or_image, str):  # If input is a path
            image_path = image_path_or_image
            self.image = cv2.imread(image_path)
        else:  # If input is an Image object
            image = np.array(image_path_or_image)
            self.image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    def fix_threshold(self, seuil):
       
            gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            _, binary_image = cv2.threshold(gray_image, seuil, 255, cv2.THRESH_BINARY)
            # Convert the thresholded image to a format compatible with Tkinter
            pil_image = Image.fromarray(binary_image)
            tk_image = ImageTk.PhotoImage(pil_image)
            return tk_image
       


    def measure_roots(self):
        if self.image is None:
            print("Veuillez charger une image avant de mesurer les racines.")
            return [], None

        gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        _, binary_image = cv2.threshold(gray_image, self.threshold, 255, cv2.THRESH_BINARY)
        binary_image = cv2.bitwise_not(binary_image)

        kernel = np.ones((5, 5), np.uint8)
        closing = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)

        root_image = np.zeros_like(self.image)  # Create an empty image for drawing contours
        root_measurements = []

        while True:
            contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                break

            largest_contour = max(contours, key=cv2.contourArea)
            contour_array = largest_contour.squeeze()

            if len(contour_array) < 10:
                break

            try:
                tck, u = splprep([contour_array[:, 0], contour_array[:, 1]], u=None, s=0.0, per=1, k=3)
            except TypeError as e:
                if "m > k must hold" in str(e):
                    print("Skipping contour due to m > k condition.")
                    break

            u_new = np.linspace(u.min(), u.max(), 1000)
            x_new, y_new = splev(u_new, tck)
            length = np.sum(np.sqrt(np.diff(x_new) ** 2 + np.diff(y_new) ** 2))

            print("Longueur de la Racine (pixels):", length, "position: ", contour_array[0])

            root_measurements.append((contour_array[0], length))

            # Draw contours on the root_image with red color
            cv2.drawContours(root_image, [largest_contour], -1, (0, 0, 255), 2)

            mask = np.zeros_like(binary_image)
            cv2.drawContours(mask, [largest_contour], -1, (255), -1)
            binary_image = cv2.bitwise_and(binary_image, cv2.bitwise_not(mask))
            closing = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)

        # Convert the image with contours to a PIL Image
        pil_image = Image.fromarray(cv2.cvtColor(root_image, cv2.COLOR_BGR2RGB))
        # Convert PIL Image to Tkinter PhotoImage
        tk_image = ImageTk.PhotoImage(pil_image)

        return root_measurements, tk_image

    def measure_roots_m(self):
        if self.image is None:
            print("Please load an image before measuring roots.")
            return [], None

        gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        _, binary_image = cv2.threshold(gray_image, self.threshold, 255, cv2.THRESH_BINARY)
        binary_image = cv2.bitwise_not(binary_image)

        kernel = np.ones((5, 5), np.uint8)
        closing = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)

        root_image = np.zeros_like(self.image)  # Create an empty image for drawing contours
        root_measurements = []
        root_counter = 1  # Counter for numbering the roots

        while True:
            contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                break

            largest_contour = max(contours, key=cv2.contourArea)
            contour_array = largest_contour.squeeze()

            if len(contour_array) < 10:
                break

            try:
                tck, u = splprep([contour_array[:, 0], contour_array[:, 1]], u=None, s=0.0, per=1, k=3)
            except TypeError as e:
                if "m > k must hold" in str(e):
                    print("Skipping contour due to m > k condition.")
                    break

            u_new = np.linspace(u.min(), u.max(), 1000)
            x_new, y_new = splev(u_new, tck)
            length = np.sum(np.sqrt(np.diff(x_new) ** 2 + np.diff(y_new) ** 2))

            print("Root Length (pixels):", length, "Position:", contour_array[0])

            root_measurements.append((contour_array, length))

            # Draw contours on the root_image with red color
            cv2.drawContours(root_image, [largest_contour], -1, (0, 0, 255), 2)

            # Add root number on top of the red contour
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.7
            thickness = 2
            text_size = cv2.getTextSize(str(root_counter), font, font_scale, thickness)[0]
            text_x = max(contour_array[0][0] - text_size[0] // 2, 0)  # Ensure text doesn't go beyond the left edge
            text_x = min(text_x, root_image.shape[1] - text_size[0])  # Ensure text doesn't go beyond the right edge
            text_y = max(contour_array[0][1] - 10, text_size[1])  # Ensure text doesn't go beyond the top edge
            cv2.putText(root_image, str(root_counter), (text_x, text_y), font, font_scale, (255, 255, 255), thickness)

            # Draw a dot at the root position
            cv2.circle(root_image, tuple(contour_array[0]), 3, (255, 255, 255), -1)

            mask = np.zeros_like(binary_image)
            cv2.drawContours(mask, [largest_contour], -1, (255), -1)
            binary_image = cv2.bitwise_and(binary_image, cv2.bitwise_not(mask))
            closing = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)

            root_counter += 1

        # Convert the image with contours to a PIL Image
        pil_image = Image.fromarray(cv2.cvtColor(root_image, cv2.COLOR_BGR2RGB))
        # Convert PIL Image to Tkinter PhotoImage
        tk_image = ImageTk.PhotoImage(pil_image)

        return root_measurements, tk_image


    
    def calibrate_roots_mesurment(self):
        if self.image is None:
            print("Veuillez charger une image avant de mesurer les racines.")
            return None, None

        gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        _, binary_image = cv2.threshold(gray_image, self.threshold, 255, cv2.THRESH_BINARY)
        binary_image = cv2.bitwise_not(binary_image)
        kernel = np.ones((5,5), np.uint8)
        closing = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)
        
        total_length = 0
        contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return 0, False

        largest_contour = max(contours, key=cv2.contourArea)
        contour_array = largest_contour.squeeze()
        if len(contour_array) < 3:
            return 0, False

        tck, u = splprep([contour_array[:,0], contour_array[:,1]], u=None, s=0.0, per=1, k=3)
        u_new = np.linspace(u.min(), u.max(), 1000)
        x_new, y_new = splev(u_new, tck)
        length = np.sum(np.sqrt(np.diff(x_new)**2 + np.diff(y_new)**2))
        total_length = length
        
        return total_length, True
