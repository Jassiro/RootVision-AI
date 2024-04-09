import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class LoginView:
    def __init__(self, login_command, register_command):
        self.root = tk.Tk()
        self.root.title('Login Page')
        # Ajouter des éléments GUI pour la vue de connexion
        bg_image = ImageTk.PhotoImage(Image.open("C:/Users/R I B/Pictures/oolive.jpg"))
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
        btn_login = tk.Button(self.root, text='Login', command=login_command, font=('Helvetica', 14))
        btn_login.place(relx=0.35, rely=0.65, anchor='center')
        btn_register = tk.Button(self.root, text='Register', command=register_command, font=('Helvetica', 14))
        btn_register.place(relx=0.65, rely=0.65, anchor='center')
        self.root.geometry(f"{bg_image.width()}x{bg_image.height()}")

    def show(self):
        self.root.mainloop()
