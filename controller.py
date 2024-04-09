from PyQt5.QtWidgets import QMessageBox
from model import DatabaseManager

class LoginController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.login_command = self.login
        self.view.register_command = self.register

    def login(self):
        username = self.view.get_username()
        password = self.view.get_password()
        if username and password:
            user = self.model.verify_user(username, password)
            if user:
                QMessageBox.information(None, 'Success', 'Login successful!')
            else:
                QMessageBox.critical(None, 'Error', 'Invalid username or password.')
        else:
            QMessageBox.critical(None, 'Error', 'Username and password are required.')

    def register(self):
        username = self.view.get_username()
        password = self.view.get_password()
        if username and password:
            self.model.register_user(username, password)
            QMessageBox.information(None, 'Success', 'Registration successful!')
        else:
            QMessageBox.critical(None, 'Error', 'Username and password are required.')
