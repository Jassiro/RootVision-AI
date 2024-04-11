import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev

class RootAnalyzer:
    def __init__(self):
        self.image = None
        self.total_length = 0

    def load_image(self, image_path):
        self.image = cv2.imread(image_path)

    def measure_roots(self):
        if self.image is None:
            print("Veuillez charger une image avant de mesurer les racines.")
            return
        gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        seuil=180
        _, binary_image = cv2.threshold(gray_image, seuil, 255, cv2.THRESH_BINARY)

        binary_image = cv2.bitwise_not(binary_image)

        kernel = np.ones((5,5), np.uint8)

        closing = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)

        total_length = 0
        
        while True:
            contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                break
            
            largest_contour = max(contours, key=cv2.contourArea)
            contour_array = largest_contour.squeeze()
            
            if len(contour_array) < 3:
                continue
            
            tck, u = splprep([contour_array[:,0], contour_array[:,1]], u=None, s=0.0, per=1, k=3)
            u_new = np.linspace(u.min(), u.max(), 1000)
            x_new, y_new = splev(u_new, tck)
            length = np.sum(np.sqrt(np.diff(x_new)**2 + np.diff(y_new)**2))
            total_length += length

            plt.figure(figsize=(6, 6))
            plt.imshow(binary_image, cmap='gray')
            plt.plot(contour_array[:, 0], contour_array[:, 1], 'r', linewidth=2, label='Contour')
            plt.plot(x_new, y_new, 'g--', linewidth=2, label='Courbe Interpolée')
            plt.title('Traitement de la Racine')
            plt.axis('off')
            plt.legend()
            plt.show()

            print("Longueur de la Racine (pixels):", length)
            total_length_cm = length * (10 / 1069.66)
            print("Longueur de la Racine (cm):", total_length_cm)
            
            mask = np.zeros_like(binary_image)
            cv2.drawContours(mask, [largest_contour], -1, (255), -1)
            binary_image = cv2.bitwise_and(binary_image, cv2.bitwise_not(mask))
            closing = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)
        
        total_length_cm = total_length * (10 / 1069.66)
        print("Longueur totale des Racines (pixels):", total_length)
        print("Longueur totale des Racines (centimètres):", total_length_cm)

        return total_length, total_length_cm
