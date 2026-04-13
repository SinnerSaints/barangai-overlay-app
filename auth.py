from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QColor
from api_client import login


class LoginWorker(QThread):
    login_done = pyqtSignal(dict)

    def __init__(self, email, password):
        super().__init__()
        self.email = email
        self.password = password

    def run(self):
        result = login(self.email, self.password)
        self.login_done.emit(result)


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("BarangAI")
        self.setFixedSize(360, 480)

        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.width() // 2 - 180,
            screen.height() // 2 - 240
        )

        self.setStyleSheet("""
            QWidget {
                background-color: #0f1923;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit {
                background-color: #1a2535;
                color: #ffffff;
                border: 1px solid #2a3a4a;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #4ade80;
            }
            QLineEdit::placeholder {
                color: #6b7280;
            }
            QPushButton#loginBtn {
                background-color: #4ade80;
                color: #0f1923;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#loginBtn:hover {
                background-color: #22c55e;
            }
            QPushButton#loginBtn:pressed {
                background-color: #16a34a;
            }
            QPushButton#loginBtn:disabled {
                background-color: #2a3a4a;
                color: #6b7280;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/logo.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(
                logo_pixmap.scaled(
                    60, 60,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
        else:
            logo_label.setText("BarangAI")
            logo_label.setStyleSheet("""
                color: #4ade80;
                font-size: 22px;
                font-weight: bold;
            """)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        welcome = QLabel("Welcome back")
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome.setStyleSheet("font-size: 22px; font-weight: bold; color: #ffffff;")
        layout.addWidget(welcome)

        subtitle = QLabel("Login to your BarangAI account")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 13px; color: #6b7280;")
        layout.addWidget(subtitle)

        layout.addSpacing(8)

        email_label = QLabel("Email")
        email_label.setStyleSheet("font-size: 13px; color: #9ca3af;")
        layout.addWidget(email_label)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        self.email_input.setFixedHeight(46)
        layout.addWidget(self.email_input)

        password_label = QLabel("Password")
        password_label.setStyleSheet("font-size: 13px; color: #9ca3af;")
        layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(46)
        self.password_input.returnPressed.connect(self.handle_login)
        layout.addWidget(self.password_input)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 12px; color: #ef4444;")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.login_btn = QPushButton("Login")
        self.login_btn.setObjectName("loginBtn")
        self.login_btn.setFixedHeight(46)
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)

        layout.addStretch()

        self.setLayout(layout)

    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            self.status_label.setText("Please enter your email and password.")
            return

        self.login_btn.setEnabled(False)
        self.email_input.setEnabled(False)
        self.password_input.setEnabled(False)
        self.status_label.setStyleSheet("font-size: 12px; color: #4ade80;")
        self.status_label.setText("Logging in...")

        self.worker = LoginWorker(email, password)
        self.worker.login_done.connect(self.handle_result)
        self.worker.start()

    def handle_result(self, result: dict):
        if result["success"]:
            self.is_logged_in = True # 1. MUST set this to True BEFORE calling close
            self.on_login_success(result["access_token"], result["user_id"])
            self.close()
        else:
            self.status_label.setStyleSheet("font-size: 12px; color: #ef4444;")
            self.status_label.setText(result["message"])
            self.login_btn.setEnabled(True)
            self.email_input.setEnabled(True)
            self.password_input.setEnabled(True)
    
    def closeEvent(self, event):
        """
        If the login window is closed manually (not via self.close() after success),
        shut down the entire application.
        """
        if not getattr(self, 'is_logged_in', False):
            QApplication.instance().quit()
        event.accept()