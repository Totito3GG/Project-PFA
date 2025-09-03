from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QWidget, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
import os

from app.db import add_user
from app.auth import hash_password, login as auth_login


class BaseLoginDialog(QDialog):
    """Base class for all login dialogs"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Project & Expense Management System")
        self.setFixedSize(1280, 720)
        self.setStyleSheet("QDialog { background-color: #f7f7f7; }")
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setModal(True)
        self.center_on_screen()

    def center_on_screen(self):
        """Center the dialog on the screen"""
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

    def create_logo(self):
        """Logo widget (bigger now)"""
        logo = QLabel()
        logo.setFixedSize(120, 120)  # bigger logo
        logo_path = r"C:\Users\mosta\OneDrive\Bureau\Project\v0.1\Images\logo.jpg"
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo.setPixmap(pixmap)
        else:
            logo.setText("🏠")
            logo.setFont(QFont("Arial", 60))
            logo.setAlignment(Qt.AlignCenter)
        return logo

    def create_input_field(self, placeholder, is_password=False):
        """Styled input field (smaller now)"""
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        if is_password:
            field.setEchoMode(QLineEdit.Password)
        field.setFixedHeight(40)  # smaller height
        field.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d0d0d0;
                border-radius: 20px;
                padding: 0 12px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #c17a5e;
            }
        """)
        return field

    def create_primary_button(self, text):
        """Primary button"""
        button = QPushButton(text)
        button.setFixedHeight(45)
        button.setStyleSheet("""
            QPushButton {
                background-color: #c17a5e;
                color: white;
                border-radius: 22px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #b06951; }
            QPushButton:pressed { background-color: #9f5e47; }
        """)
        return button

    def create_secondary_button(self, text):
        """Secondary button"""
        button = QPushButton(text)
        button.setFixedHeight(45)
        button.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
                border-radius: 22px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #d0d0d0; }
        """)
        return button


class SignUpDialog(BaseLoginDialog):
    """Sign Up dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        center = QWidget()
        vbox = QVBoxLayout(center)
        vbox.setAlignment(Qt.AlignCenter)
        vbox.setSpacing(20)

        vbox.addWidget(self.create_logo(), alignment=Qt.AlignCenter)
        title = QLabel("Sign Up")
        title.setFont(QFont("Arial", 26, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        vbox.addWidget(title)

        self.name_edit = self.create_input_field("Full Name")
        self.email_edit = self.create_input_field("Email")
        self.password_edit = self.create_input_field("Password", True)
        self.confirm_password_edit = self.create_input_field("Confirm Password", True)

        for w in [self.name_edit, self.email_edit, self.password_edit, self.confirm_password_edit]:
            vbox.addWidget(w)

        hbox = QHBoxLayout()
        self.signup_btn = self.create_primary_button("Sign Up")
        self.signup_btn.clicked.connect(self.handle_signup)
        hbox.addWidget(self.signup_btn)

        self.cancel_btn = self.create_secondary_button("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        hbox.addWidget(self.cancel_btn)
        vbox.addLayout(hbox)

        signin_link = QLabel('<a href="#">Already have an account? <b>Sign In</b></a>')
        signin_link.setStyleSheet("color: #c17a5e; font-size: 13px;")
        signin_link.setAlignment(Qt.AlignCenter)
        signin_link.linkActivated.connect(self.show_signin)
        vbox.addWidget(signin_link)

        layout.addWidget(center)

    def handle_signup(self):
        name = self.name_edit.text().strip()
        email = self.email_edit.text().strip()
        password = self.password_edit.text().strip()
        confirm_password = self.confirm_password_edit.text().strip()

        if not name or not email or not password:
            QMessageBox.warning(self, "Error", "Fill all fields")
            return
        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords don’t match")
            return
        if len(password) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters")
            return
        try:
            user_id = add_user(name, hash_password(password), "Employé")
            if user_id:
                QMessageBox.information(self, "Success", "Account created successfully!")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Email already exists")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def show_signin(self):
        self.reject()


class ForgotPasswordDialog(BaseLoginDialog):
    """Forgot Password dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        center = QWidget()
        vbox = QVBoxLayout(center)
        vbox.setAlignment(Qt.AlignCenter)
        vbox.setSpacing(20)

        vbox.addWidget(self.create_logo(), alignment=Qt.AlignCenter)
        title = QLabel("Forgot Password")
        title.setFont(QFont("Arial", 26, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        vbox.addWidget(title)

        instruction = QLabel("Enter your email address and we'll send you a link\nto reset your password.")
        instruction.setFont(QFont("Arial", 13))
        instruction.setStyleSheet("color: #555;")
        instruction.setAlignment(Qt.AlignCenter)
        instruction.setWordWrap(True)
        vbox.addWidget(instruction)

        self.email_edit = self.create_input_field("Email")
        vbox.addWidget(self.email_edit)

        hbox = QHBoxLayout()
        self.reset_btn = self.create_primary_button("Reset Password")
        self.reset_btn.clicked.connect(self.handle_reset)
        hbox.addWidget(self.reset_btn)

        self.cancel_btn = self.create_secondary_button("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        hbox.addWidget(self.cancel_btn)
        vbox.addLayout(hbox)

        signin_link = QLabel('<a href="#"><b>Sign In</b></a>')
        signin_link.setStyleSheet("color: #c17a5e; font-size: 13px;")
        signin_link.setAlignment(Qt.AlignCenter)
        signin_link.linkActivated.connect(self.show_signin)
        vbox.addWidget(signin_link)

        layout.addWidget(center)

    def handle_reset(self):
        email = self.email_edit.text().strip()
        if not email:
            QMessageBox.warning(self, "Error", "Enter your email")
            return
        QMessageBox.information(self, "Reset Link Sent", f"Reset link sent to {email}")
        self.accept()

    def show_signin(self):
        self.reject()


class SignInDialog(BaseLoginDialog):
    """Sign In dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        center = QWidget()
        vbox = QVBoxLayout(center)
        vbox.setAlignment(Qt.AlignCenter)
        vbox.setSpacing(20)

        vbox.addWidget(self.create_logo(), alignment=Qt.AlignCenter)
        title = QLabel("Sign In")
        title.setFont(QFont("Arial", 26, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        vbox.addWidget(title)

        self.username_edit = self.create_input_field("Username")
        self.password_edit = self.create_input_field("Password", True)
        vbox.addWidget(self.username_edit)
        vbox.addWidget(self.password_edit)

        self.remember_checkbox = QCheckBox("Remember me")
        self.remember_checkbox.setStyleSheet("font-size: 13px; color: #555;")
        vbox.addWidget(self.remember_checkbox)

        hbox = QHBoxLayout()
        self.signin_btn = self.create_primary_button("Sign In")
        self.signin_btn.clicked.connect(self.handle_signin)
        hbox.addWidget(self.signin_btn)

        self.cancel_btn = self.create_secondary_button("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        hbox.addWidget(self.cancel_btn)
        vbox.addLayout(hbox)

        forgot_link = QLabel('<a href="#"><b>Forgot Password?</b></a>')
        forgot_link.setStyleSheet("color: #c17a5e; font-size: 13px;")
        forgot_link.setAlignment(Qt.AlignCenter)
        forgot_link.linkActivated.connect(self.show_forgot_password)
        vbox.addWidget(forgot_link)

        create_link = QLabel('<a href="#"><b>Create New Account</b></a>')
        create_link.setStyleSheet("color: #c17a5e; font-size: 13px;")
        create_link.setAlignment(Qt.AlignCenter)
        create_link.linkActivated.connect(self.show_signup)
        vbox.addWidget(create_link)

        layout.addWidget(center)

    def handle_signin(self):
        try:
            username = self.username_edit.text().strip()
            password = self.password_edit.text().strip()
            if not username or not password:
                QMessageBox.warning(self, "Error", "Enter username and password")
                return
            
            user = auth_login(username, password)
            
            if user:
                QMessageBox.information(self, "Success", f"Welcome {user[1]}!")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Invalid credentials")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Login failed: {str(e)}")

    def show_signup(self):
        self.hide()
        signup = SignUpDialog(self)
        if signup.exec_() == signup.Accepted:
            self.accept()
        else:
            self.show()

    def show_forgot_password(self):
        self.hide()
        forgot = ForgotPasswordDialog(self)
        forgot.exec_()
        self.show()


# ✅ Wrapper for backward compatibility with main.py
class LoginSignupDialog(SignInDialog):
    """Wrapper so main.py can still import LoginSignupDialog"""
    pass


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = LoginSignupDialog()
    dialog.show()
    sys.exit(app.exec_())
