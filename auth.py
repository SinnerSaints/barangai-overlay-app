from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from api_client import login


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        # callback function called after successful login
        self.on_login_success = on_login_success
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("BarangAI - Login")
        self.setFixedSize(300, 280)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        # logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/logo.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(
                logo_pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio)
            )
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(logo_label)

        # title
        title = QLabel("BarangAI Assistant")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Login with your BarangAI account")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        # password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        # login button
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.handle_login)
        # allow pressing Enter to login
        self.password_input.returnPressed.connect(self.handle_login)
        layout.addWidget(self.login_btn)

        # status label for errors
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        # basic validation
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password.")
            return

        # disable button while logging in
        self.login_btn.setEnabled(False)
        self.status_label.setText("Logging in...")

        result = login(username, password)

        if result["success"]:
            # pass token to main.py and close login window
            self.on_login_success(result["token"])
            self.close()
        else:
            self.status_label.setText(result["message"])
            self.login_btn.setEnabled(True)