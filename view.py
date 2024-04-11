import sys
import os
import sqlite3
import tkinter as tk
from tkinter import messagebox
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QTextEdit
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image, ImageTk

class LoginApp:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.root = tk.Tk()
        self.root.title('Login Page')
        bg_image = ImageTk.PhotoImage(Image.open(os.path.join(os.getcwd(), 'C:/Users/R I B/Pictures/oolive.jpg')))
        bg_label = tk.Label(self.root, image=bg_image)
        bg_label.place(relwidth=1, relheight=1)
        label_username = tk.Label(self.root, text='Username:', font=('Helvetica', 14), bg='#99cc99')
        label_username.place(relx=0.2, rely=0.45, anchor='center')
        self.entry_username = tk.Entry(self.root, font=('Helvetica', 14))
        self.entry_username.place(relx=0.5, rely=0.45, anchor='center')
        label_password = tk.Label(self.root, text='Password:', font=('Helvetica', 14), bg='#99cc99')
        label_password.place(relx=0.2, rely=0.55, anchor='center')
        self.entry_password = tk.Entry(self.root, show='*', font=('Helvetica', 14))
        self.entry_password.place(relx=0.5, rely=0.55, anchor='center')
        btn_login = tk.Button(self.root, text='Login', command=self.login, font=('Helvetica', 14))
        btn_login.place(relx=0.35, rely=0.65, anchor='center')
        btn_register = tk.Button(self.root, text='Register', command=self.register_user, font=('Helvetica', 14))
        btn_register.place(relx=0.65, rely=0.65, anchor='center')
        self.root.geometry(f"{bg_image.width()}x{bg_image.height()}")
        self.root.mainloop()

    def register_user(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        if username and password:
            self.db_manager.register_user(username, password)
            messagebox.showinfo('Success', 'Registration successful!')
        else:
            messagebox.showerror('Error', 'Username and password are required.')

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        if username and password:
            user = self.db_manager.verify_user(username, password)
            if user:
                self.root.destroy()  # Close the login window
                app = QApplication(sys.argv)
                window = ImageProcessingApp(username, self.db_manager)
                window.show()
                sys.exit(app.exec_())
            else:
                messagebox.showerror('Error', 'Invalid username or password.')
        else:
            messagebox.showerror('Error', 'Username and password are required.')

class ImageProcessingApp(QMainWindow):
    def __init__(self, username, db_manager):
        super().__init__()
        self.setWindowTitle('Image Processing App')
        self.username = username
        self.db_manager = db_manager
        self.initUI()

    def initUI(self):
        # Layout principal
        layout = QVBoxLayout()

        # Étiquette de bienvenue
        welcome_label = QLabel(f"Welcome, {self.username}!", self)
        layout.addWidget(welcome_label)

        # Zone de texte pour afficher les informations traitées
        self.processed_info_textedit = QTextEdit(self)
        self.processed_info_textedit.setReadOnly(True)  # Rendre le texte non éditable
        layout.addWidget(self.processed_info_textedit)

        # Bouton pour déclencher un traitement d'image
        process_image_button = QPushButton("Process Image", self)
        layout.addWidget(process_image_button)

        # Connecter le bouton à une méthode de traitement d'image
        process_image_button.clicked.connect(self.process_image)

        # Créer un widget pour contenir le layout principal
        central_widget = QWidget(self)
        central_widget.setLayout(layout)

        # Définir le widget central de la fenêtre principale
        self.setCentralWidget(central_widget)

    def process_image(self):
        # Implémenter ici la logique de traitement de l'image
        # Par exemple, charger une image, effectuer un traitement et afficher le résultat
        self.processed_info_textedit.append("Image processed successfully!")
