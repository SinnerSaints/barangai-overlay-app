from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton,
    QLabel, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint
from PyQt6.QtGui import QIcon, QFont


class AIWorker(QThread):
    response_ready = pyqtSignal(str)

    def __init__(self, message, token):
        super().__init__()
        self.message = message
        self.token = token

    def run(self):
        self.response_ready.emit(f"This is a test response for: '{self.message}'")


class FloatingButton(QWidget):
    """
    Small floating button that stays on screen when overlay is hidden.
    Click it to bring the overlay back.
    """
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.drag_position = QPoint()

    def setup_ui(self):
        # no window border, always on top, no taskbar entry
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )

        # transparent background so only button is visible
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # the floating button itself
        self.btn = QPushButton("💬")
        self.btn.setFixedSize(55, 55)
        self.btn.setToolTip("Open BarangAI Assistant")
        self.btn.setFont(QFont("Arial", 20))
        self.btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 27px;
                border: 2px solid #388E3C;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        self.btn.clicked.connect(self.clicked.emit)
        layout.addWidget(self.btn)

        self.setLayout(layout)
        self.setFixedSize(55, 55)

        # position on bottom-right of screen
        self.position_button()

    def position_button(self):
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - 75
        y = screen.height() - 150
        self.move(x, y)

    # allow dragging the floating button
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)


class OverlayWindow(QWidget):
    def __init__(self, token: str):
        super().__init__()
        self.token = token

        # create floating button
        self.floating_btn = FloatingButton()
        self.floating_btn.clicked.connect(self.show_overlay)

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("BarangAI Assistant")
        self.setFixedSize(350, 520)

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.position_window()

        layout = QVBoxLayout()

        # header
        header_layout = QHBoxLayout()

        header = QLabel("💬 BarangAI Assistant")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(header)

        # minimize button
        minimize_btn = QPushButton("—")
        minimize_btn.setFixedSize(30, 30)
        minimize_btn.setToolTip("Minimize")
        minimize_btn.clicked.connect(self.hide_to_button)
        header_layout.addWidget(minimize_btn)

        # close/quit button
        quit_btn = QPushButton("✕")
        quit_btn.setFixedSize(30, 30)
        quit_btn.setToolTip("Quit BarangAI")
        quit_btn.setStyleSheet("QPushButton { color: red; }")
        quit_btn.clicked.connect(self.quit_app)
        header_layout.addWidget(quit_btn)

        layout.addLayout(header_layout)

        # chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        # input row
        input_layout = QHBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask me anything...")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)

        layout.addLayout(input_layout)

        # status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        self.display_message(
            "BarangAI",
            "Hello! I am your BarangAI assistant. How can I help you today?"
        )

    def position_window(self):
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - 350 - 20
        y = screen.height() - 520 - 60
        self.move(x, y)

    def hide_to_button(self):
        # hide overlay, show floating button
        self.hide()
        self.floating_btn.show()

    def show_overlay(self):
        # hide floating button, show overlay
        self.floating_btn.hide()
        self.position_window()
        self.show()
        self.raise_()
        self.activateWindow()

    def quit_app(self):
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate() # Force the thread to stop
            self.worker.wait()      # Wait for it to actually vanish
    
        self.floating_btn.close()
        QApplication.quit()

    def send_message(self):
        user_message = self.input_field.text().strip()
        if not user_message:
            return

        self.display_message("You", user_message)
        self.input_field.clear()
        self.input_field.setEnabled(False)
        self.status_label.setText("BarangAI is typing...")

        self.worker = AIWorker(user_message, self.token)
        self.worker.response_ready.connect(self.handle_response)
        self.worker.start()

    def handle_response(self, response: str):
        self.status_label.setText("")
        self.input_field.setEnabled(True)
        self.input_field.setFocus()
        self.display_message("BarangAI", response)

    def display_message(self, sender: str, message: str):
        if sender == "You":
            color = "#2196F3"
        elif sender == "BarangAI":
            color = "#4CAF50"
        else:
            color = "#FF9800"

        self.chat_display.append(
            f'<b style="color:{color}">{sender}:</b> {message}<br>'
        )
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )