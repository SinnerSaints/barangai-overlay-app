from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton,
    QLabel, QApplication, QMessageBox, 
    QStackedWidget, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint, QSize
from PyQt6.QtGui import QIcon, QPixmap
from screen_capture import capture_screen
from api_client import send_message
from utils import get_resource_path, clear_auth_data
import ctypes
import platform # added to check OS 
import sys
import os

DARK_BG       = "#0f1923"
DARK_CARD     = "#1a2535"
DARK_BORDER   = "#2a3a4a"
GREEN_PRIMARY = "#4ade80"
GREEN_HOVER   = "#22c55e"
TEXT_PRIMARY  = "#ffffff"
TEXT_MUTED    = "#6b7280"
TEXT_LABEL    = "#9ca3af"
RED_ERROR     = "#ef4444"


class AIWorker(QThread):
    response_ready = pyqtSignal(dict)

    def __init__(self, message, screen_data, user_id, session_uuid, token):
        super().__init__()
        self.message = message
        self.screen_data = screen_data
        self.user_id = user_id
        self.session_uuid = session_uuid
        self.token = token

    def run(self):
        screenshot_b64 = self.screen_data.get("screenshot")

        # FOR DEBUG PURPOSES
        print("\n" + "="*40)
        print(f"USER MESSAGE : {self.message}")
        print(f"ACTIVE WINDOW: {self.screen_data['active_window']}")
        print(f"AI CONTEXT   : {self.screen_data['context']}")
        print("="*40 + "\n")

        # Simulate a tiny 1-second "thinking" delay
        QThread.msleep(1000)
        
        result = send_message(
            message=self.message,
            screenshot_b64=screenshot_b64,
            user_id=self.user_id,
            session_uuid=self.session_uuid,
            token=self.token
        )

        '''
        # 3. Send a fake response back to the GUI so it doesn't freeze. FOR TESTING
        dummy_result = {
            "success": True,
            "response": f"System Test OK! I detected you were looking at: <b>{self.screen_data['active_window']}</b>",
            "session_uuid": self.session_uuid
        }
        '''

        self.response_ready.emit(result)

class FloatingButton(QWidget):
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.drag_position = QPoint()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        hwnd = int(self.winId())
        # ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 0x11) - Changed it so I can run it ony Mac
        if platform.system() == "Windows":
            hwnd = int(self.winId())
            ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 0x11)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        icon_path = get_resource_path("assets/icon.png")
        
        self.btn = QPushButton()
        self.btn.setFixedSize(55, 55)

        self.btn.setIcon(QIcon(icon_path))
        self.btn.setIconSize(QSize(40, 40)) # Adjust this (35-45) to fit your taste
        
        self.btn.setToolTip("Open BarangAI Assistant")

        self.btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; /* No more green box */
                border: none;                 /* No more border */
                border-radius: 27px;
                outline: none;
            }
            QPushButton:hover {
                background-color: transparent;
            }
            QPushButton:pressed {
                background-color: transparent;
            }
        """)
        
        self.btn.clicked.connect(self.clicked.emit)
        layout.addWidget(self.btn)

        self.setLayout(layout)
        self.setFixedSize(55, 55)
        self.position_button()

    def position_button(self):
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - 75
        y = screen.height() - 150
        self.move(x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(
                event.globalPosition().toPoint() - self.drag_position
            )


class OverlayWindow(QWidget):
    logout_requested = pyqtSignal() # Signal for logout

    def __init__(self, token: str, user_id: int, user_name: str, user_role: str):
        super().__init__()
        self.token = token
        self.user_id = user_id
        self.user_name = user_name
        self.user_role = user_role
        self.session_uuid = None
        self.drag_position = QPoint()

        self.floating_btn = FloatingButton()
        self.floating_btn.clicked.connect(self.show_overlay)

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("BarangAI")
        self.setFixedSize(370, 580)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.position_window()

        # outer container — handles border radius and background
        container = QWidget(self)
        container.setGeometry(0, 0, 370, 580)
        container.setObjectName("container")
        container.setStyleSheet(f"""
            QWidget#container {{
                background-color: {DARK_BG};
                border-radius: 16px;
                border: 1px solid {DARK_BORDER};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)

        # main layout — no margins, no spacing so sections fill edge to edge
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── HEADER ──────────────────────────────────────────
        header_widget = QWidget()
        header_widget.setObjectName("header")
        header_widget.setFixedHeight(56)
        header_widget.setStyleSheet(f"""
            QWidget#header {{
                background-color: {DARK_CARD};
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
                border-bottom: 1px solid {DARK_BORDER};
            }}
        """)

        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(16, 0, 12, 0)
        header_layout.setSpacing(8)

        # green dot
        dot = QLabel("●")
        dot.setFixedWidth(14)
        dot.setStyleSheet(f"color: {GREEN_PRIMARY}; font-size: 10px;")
        header_layout.addWidget(dot)

        # title
        self.header_title = QLabel("BarangAI Assistant")
        self.header_title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 14px;
            font-weight: bold;
        """)
        header_layout.addWidget(self.header_title)

        # setting button
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(28, 28)
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.setStyleSheet(f"""
            QPushButton {{ background-color: transparent; color: {TEXT_MUTED}; border: none; font-size: 16px; }}
            QPushButton:hover {{ color: {TEXT_PRIMARY}; }}
        """)
        self.settings_btn.clicked.connect(self.toggle_settings)
        header_layout.addWidget(self.settings_btn)

        # minimize button
        minimize_btn = QPushButton("—")
        minimize_btn.setFixedSize(28, 28)
        minimize_btn.setToolTip("Minimize")
        minimize_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_MUTED};
                border: none;
                border-radius: 6px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {DARK_BORDER};
                color: {TEXT_PRIMARY};
            }}
        """)
        minimize_btn.clicked.connect(self.hide_to_button)
        header_layout.addWidget(minimize_btn)

        # close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setToolTip("Quit BarangAI")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_MUTED};
                border: none;
                border-radius: 6px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: #450a0a;
                color: {RED_ERROR};
            }}
        """)
        close_btn.clicked.connect(self.quit_app)
        header_layout.addWidget(close_btn)

        layout.addWidget(header_widget)

        # Stack widget
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # ── CHAT DISPLAY ─────────────────────────────────────
        chat_page = QWidget()
        chat_layout = QVBoxLayout(chat_page)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: {DARK_BG};
                color: {TEXT_PRIMARY};
                border: none;
                padding: 8px 10px;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {DARK_BORDER};
                border-radius: 3px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        chat_layout.addWidget(self.chat_display, stretch=1)

        # ── STATUS LABEL ──────────────────────────────────────
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFixedHeight(18)
        self.status_label.setStyleSheet(f"""
            color: {TEXT_MUTED};
            font-size: 11px;
            background-color: {DARK_BG};
            font-family: 'Segoe UI', Arial, sans-serif;
        """)
        chat_layout.addWidget(self.status_label)

        # ── INPUT AREA ────────────────────────────────────────
        input_widget = QWidget()
        input_widget.setObjectName("inputArea")
        input_widget.setFixedHeight(62)
        input_widget.setStyleSheet(f"""
            QWidget#inputArea {{
                background-color: {DARK_CARD};
                border-top: 1px solid {DARK_BORDER};
                border-bottom-left-radius: 16px;
                border-bottom-right-radius: 16px;
            }}
        """)

        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(12, 10, 12, 10)
        input_layout.setSpacing(8)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask me anything...")
        self.input_field.setFixedHeight(40)
        self.input_field.returnPressed.connect(self.send_message)
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {DARK_BG};
                color: {TEXT_PRIMARY};
                border: 1px solid {DARK_BORDER};
                border-radius: 20px;
                padding: 0 14px;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QLineEdit:focus {{
                border: 1px solid {GREEN_PRIMARY};
            }}
        """)
        input_layout.addWidget(self.input_field)

        self.send_btn = QPushButton("➤")
        self.send_btn.setFixedSize(40, 40)
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {GREEN_PRIMARY};
                color: {DARK_BG};
                border: none;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {GREEN_HOVER};
            }}
            QPushButton:pressed {{
                background-color: #16a34a;
            }}
            QPushButton:disabled {{
                background-color: {DARK_BORDER};
                color: {TEXT_MUTED};
            }}
        """)
        input_layout.addWidget(self.send_btn)

        chat_layout.addWidget(input_widget)
        self.stacked_widget.addWidget(chat_page) # Add chat to page 0

        # ── SETTINGS INTERFACE ───────────────────────
        settings_page = QWidget()
        settings_layout = QVBoxLayout(settings_page)
        settings_layout.setContentsMargins(24, 32, 24, 24)
        settings_layout.setSpacing(20)

        # Settings Header
        settings_title = QLabel("Account Preferences")
        settings_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold;")
        settings_layout.addWidget(settings_title)
        
        # Profile Card
        profile_card = QWidget()
        profile_card.setObjectName("profileCard")
        profile_card.setStyleSheet(f"""
            QWidget#profileCard {{
                background-color: {DARK_CARD};
                border-radius: 12px;
                border: 1px solid {DARK_BORDER};
            }}
        """)
        profile_layout = QVBoxLayout(profile_card)
        profile_layout.setContentsMargins(16, 16, 16, 16)
        profile_layout.setSpacing(6)
        
        lbl_logged = QLabel("Logged in as")
        lbl_logged.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; background: transparent;")
        profile_layout.addWidget(lbl_logged)

        name_role_layout = QHBoxLayout()
        name_role_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_name = QLabel(self.user_name)
        lbl_name.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: bold; background: transparent;")
        name_role_layout.addWidget(lbl_name)
        
        # The Role Badge
        role_badge = QLabel(self.user_role)
        role_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if self.user_role == "CAPTAIN":
            text_color = "#60a5fa" # Soft Blue
        elif self.user_role == "ADMIN":
            text_color = "#a78bfa" # Soft Purple
        else:
            text_color = GREEN_PRIMARY
            
        role_badge.setStyleSheet(f"""
            background-color: {DARK_BG};
            color: {text_color};
            border: 1px solid {DARK_BORDER};
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 0.5px;
        """)
        name_role_layout.addWidget(role_badge)
        name_role_layout.addStretch() 
        
        profile_layout.addLayout(name_role_layout)
        settings_layout.addWidget(profile_card)

        # Language Placeholder
        lang_card = QWidget()
        lang_card.setObjectName("langCard")
        lang_card.setStyleSheet(f"""
            QWidget#langCard {{
                background-color: {DARK_CARD};
                border-radius: 12px;
                border: 1px solid {DARK_BORDER};
            }}
        """)
        lang_layout = QVBoxLayout(lang_card)
        lang_layout.setContentsMargins(16, 16, 16, 16)
        lang_layout.setSpacing(10)

        lbl_lang_title = QLabel("AI Language")
        lbl_lang_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 14px; font-weight: bold; background: transparent;")
        lang_layout.addWidget(lbl_lang_title)

        lbl_lang_desc = QLabel("Set the default language you want the assistant to reply in.")
        lbl_lang_desc.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; background: transparent;")
        lbl_lang_desc.setWordWrap(True)
        lang_layout.addWidget(lbl_lang_desc)

        # The Interactive Dropdown
        self.lang_dropdown = QComboBox()
        self.lang_dropdown.addItems(["English", "Cebuano", "Tagalog"])
        self.lang_dropdown.setFixedHeight(38)
        self.lang_dropdown.setStyleSheet(f"""
            QComboBox {{
                background-color: {DARK_BG};
                color: {TEXT_PRIMARY};
                border: 1px solid {DARK_BORDER};
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 13px;
            }}
            QComboBox:focus {{
                border: 1px solid {GREEN_PRIMARY};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {DARK_BG};
                color: {TEXT_PRIMARY};
                selection-background-color: {DARK_BORDER};
                border: 1px solid {DARK_BORDER};
                outline: none;
            }}
        """)
        # Connect to a placeholder function for future database updates
        self.lang_dropdown.currentTextChanged.connect(self.on_language_changed)
        lang_layout.addWidget(self.lang_dropdown)

        settings_layout.addWidget(lang_card)
        settings_layout.addStretch()
        
        # Logout Button
        logout_btn = QPushButton("Log Out")
        logout_btn.setFixedHeight(46)
        logout_btn.setStyleSheet(f"""
            QPushButton {{ 
                background-color: transparent; 
                color: {RED_ERROR}; 
                border: 1px solid {RED_ERROR}; 
                border-radius: 8px; 
                font-size: 14px; 
                font-weight: bold; 
            }}
            QPushButton:hover {{ 
                background-color: #450a0a; 
            }}
            QPushButton:pressed {{
                background-color: #7f1d1d;
                color: {TEXT_PRIMARY};
            }}
        """)
        logout_btn.clicked.connect(self.perform_logout)
        settings_layout.addWidget(logout_btn)

        self.stacked_widget.addWidget(settings_page) # Add settings to page 1

        # welcome message
        self.display_message(
            "BarangAI",
            "Hello! I am your BarangAI assistant. How can I help you today?"
        )

        self.check_macos_permissions()

    def toggle_settings(self):
        """Flips between the Chat View (Index 0) and Settings View (Index 1)."""
        if self.stacked_widget.currentIndex() == 0:
            self.stacked_widget.setCurrentIndex(1)
            self.header_title.setText("Settings")
        else:
            self.stacked_widget.setCurrentIndex(0)
            self.header_title.setText("BarangAI Assistant")

    def perform_logout(self):
        """Clears the secure vault and tells main.py to show the login screen."""
        clear_auth_data()
        self.logout_requested.emit()

    def on_language_changed(self, selected_language: str):
        """
        Placeholder function for future update.
        Fires automatically whenever the user picks a new language.
        """
        print(f"User changed language preference to: {selected_language}")
        
        # In the future, you will trigger an API call here to save this 
        # to the database so it syncs with the web app!

    # ── DRAGGING THE OVERLAY ─────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(
                event.globalPosition().toPoint() - self.drag_position
            )

    # ── WINDOW MANAGEMENT ────────────────────────────────────
    def position_window(self):
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - 370 - 20
        y = screen.height() - 580 - 60
        self.move(x, y)

    def hide_to_button(self):
        self.hide()
        self.floating_btn.show()

    def show_overlay(self):
        self.floating_btn.hide()
        self.show()
        self.raise_()
        self.activateWindow()

    def quit_app(self):
        self.floating_btn.hide()
        QApplication.quit()

    # ── MESSAGING ────────────────────────────────────────────
    def send_message(self):
        user_message = self.input_field.text().strip()
        if not user_message:
            return

        self.display_message("You", user_message)
        self.input_field.clear()
        self.input_field.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.status_label.setText("BarangAI is looking at your screen...")

        screen_data = capture_screen() 

        self.worker = AIWorker(
            message=user_message,
            screen_data=screen_data, 
            user_id=self.user_id,
            session_uuid=self.session_uuid,
            token=self.token
        )
        self.worker.response_ready.connect(self.handle_response)
        self.worker.start()

    def handle_response(self, result: dict):
        self.status_label.setText("")
        self.input_field.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.input_field.setFocus()

        if not result["success"]:
            if result["response"] == "SESSION_EXPIRED":
                clear_auth_data()
                self.display_message(
                    "System",
                    "Your session has expired. Please restart and login again."
                )
            else:
                self.display_message("System", result["response"])
            return

        if result.get("session_uuid"):
            self.session_uuid = result["session_uuid"]

        self.display_message("BarangAI", result["response"])

    def display_message(self, sender: str, message: str):
        if sender == "You":
            # Right-aligned table for user messages
            self.chat_display.append(f"""
                <table width="100%" style="margin: 4px 0;">
                    <tr>
                        <td width="20%"></td> <td align="right">
                            <table style="background-color: #14532d; border-radius: 8px;">
                                <tr>
                                    <td style="padding: 8px 12px; color: #4ade80; font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px;">
                                        {message}
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            """)

        elif sender == "BarangAI":
            # Left-aligned table for AI messages
            self.chat_display.append(f"""
                <table width="100%" style="margin: 4px 0;">
                    <tr>
                        <td align="left">
                            <div style="color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; margin-bottom: 2px; letter-spacing: 0.5px;">
                                BarangAI
                            </div>
                            <table style="background-color: {DARK_CARD}; border-radius: 8px; border: 1px solid {DARK_BORDER};">
                                <tr>
                                    <td style="padding: 8px 12px; color: {TEXT_PRIMARY}; font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px;">
                                        {message}
                                    </td>
                                </tr>
                            </table>
                        </td>
                        <td width="20%"></td> </tr>
                </table>
            """)
        else:
            # Centered system/error messages using the Table method
            self.chat_display.append(f"""
                <table width="100%" style="margin: 6px 0;">
                    <tr>
                        <td align="center">
                            <table style="background-color: #450a0a; border-radius: 10px; border: 1px solid #7f1d1d;">
                                <tr>
                                    <td style="padding: 6px 14px; color: {RED_ERROR}; font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; font-weight: bold;">
                                        ⚠️ {message}
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            """)

        # Auto scroll to latest message
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )

    def check_macos_permissions(self):
        if sys.platform == "darwin":
            try:
                import Quartz
                
                has_access = Quartz.CGPreflightScreenCaptureAccess()
                
                if not has_access:
                    msg = QMessageBox(self)
                    msg.setWindowTitle("Action Required: Screen Access")
                    
                    # --- NEW IMAGE CODE ---
                    # Load the image using your resource path helper
                    tutorial_image = QPixmap(get_resource_path("mac_toggle_tutorial.png"))
                    
                    # Check if the image loaded successfully
                    if not tutorial_image.isNull():
                        msg.setIconPixmap(tutorial_image.scaledToWidth(300))
                    else:
                        # Fallback if the image is missing from the assets folder
                        msg.setIcon(QMessageBox.Icon.Warning)
                    # ----------------------
                    
                    msg.setText("BarangAI needs your permission to see the screen.")
                    msg.setInformativeText(
                        "Click 'OK' to open your computer settings.\n\n"
                        "Please find 'BarangAI' (or your Terminal) in the list and click the switch to turn it ON.\n\n"
                        "After that, you may need to restart this app."
                    )
                    msg.exec()
                    
                    # This triggers the native macOS popup if it's their very first time
                    Quartz.CGRequestScreenCaptureAccess()
                    
                    # Opens the exact Settings page for them
                    os.system('open "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture"')
                    
            except ImportError:
                print("Quartz module not found. Cannot check macOS permissions.")
            except AttributeError:
                pass