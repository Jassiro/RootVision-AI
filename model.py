import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev

class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name

    # Autres méthodes du gestionnaire de base de données...

    def process_image(self, image_path):
        image_path="C:/Users/R I B/Desktop/pfe_jasser/471.tif"
        # Chargement de l'image
        image = cv2.imread(image_path)

        # Conversion en niveau de gris
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Segmentation de l'image (exemple de seuillage)
        seuil = 135
        _, binary_image = cv2.threshold(gray_image, seuil, 255, cv2.THRESH_BINARY)

        # Complément de l'image
        binary_image = cv2.bitwise_not(binary_image)

        # Fermeture morphologique
        kernel = np.ones((5, 5), np.uint8)
        closing = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)

        # Initialisation de la longueur totale des racines
        total_length = 0

        # Initialisation du compteur de racines traitées
        roots_processed = 0

        # Tant qu'il y a des racines dans l'image et que k est inférieur à m
        while True:
            # Trouver les contours dans l'image
            contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # S'il n'y a plus de contours ou que k est égal à m, sortir de la boucle
            if not contours or roots_processed == len(contours):
                break

            # Sélectionner le contour le plus grand (la plus grande racine)
            largest_contour = max(contours, key=cv2.contourArea)

            # Convert contour to NumPy array
            contour_array = largest_contour.squeeze()

            if len(contour_array) < 3:
                roots_processed += 1
                continue

            # Perform spline interpolation
            tck, u = splprep([contour_array[:, 0], contour_array[:, 1]], u=None, s=0.0, per=1, k=3)
            u_new = np.linspace(u.min(), u.max(), 1000)
            x_new, y_new = splev(u_new, tck)

            # Calculer la longueur de la racine
            length = np.sum(np.sqrt(np.diff(x_new) ** 2 + np.diff(y_new) ** 2))

            # Accumuler la longueur de la racine à la longueur totale
            total_length += length

            # Affichage du résultat de la mesure pour cette racine
            print("Longueur de la Racine (pixels):", length)

            # cm
            total_length_cm = length * (10 / 1069.66)
            print("Longueur de la Racine (cm):", total_length_cm)

            # Affichage des étapes intermédiaires (à des fins de vérification)
            plt.figure(figsize=(6, 6))
            plt.imshow(binary_image, cmap='gray')
            plt.plot(contour_array[:, 0], contour_array[:, 1], 'r', linewidth=2, label='Contour')
            plt.plot(x_new, y_new, 'g--', linewidth=2, label='Courbe Interpolée')
            plt.title('Traitement de la Racine')
            plt.axis('off')
            plt.legend()
            plt.show()

            # Créer un masque pour la zone sélectionnée
            mask = np.zeros_like(binary_image)
            cv2.drawContours(mask, [largest_contour], -1, (255), -1)

            # Retirer la zone sélectionnée de l'image
            binary_image = cv2.bitwise_and(binary_image, cv2.bitwise_not(mask))

            # Mise à jour de l'image après avoir retiré la racine traitée
            closing = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)

            # Incrémenter le compteur de racines traitées
            roots_processed += 1

        # Conversion de la longueur totale de pixels en centimètres
        total_length_cm = total_length * (10 / 1069.66)

        # Affichage du résultat total en pixels et en centimètres
        print("Longueur totale des Racines (pixels):", total_length)
        print("Longueur totale des Racines (centimètres):", total_length_cm)
