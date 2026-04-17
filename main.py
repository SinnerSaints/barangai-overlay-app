import sys
import os
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QStyle, QSplashScreen
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from overlay import OverlayWindow
from auth import LoginWindow 
from utils import get_resource_path, load_auth_data

class BeautifulSplash(QSplashScreen):
    def __init__(self, pixmap):
        super().__init__(pixmap, Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(300, 350)

        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
    def drawContents(self, painter):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QColor("#0f1923")) 
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)

        icon_pixmap = self.pixmap().scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        x = (self.width() - icon_pixmap.width()) // 2
        y = (self.height() - icon_pixmap.height()) // 2 - 30
        painter.drawPixmap(x, y, icon_pixmap)

        painter.setPen(QColor("#4ade80"))
        font = painter.font()
        font.setPointSize(18)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.rect().adjusted(0, 80, 0, 0), Qt.AlignmentFlag.AlignCenter, "BarangAI")

        painter.setPen(QColor("#9ca3af"))
        font.setPointSize(10)
        font.setBold(False)
        painter.setFont(font)
        painter.drawText(self.rect().adjusted(0, 0, 0, -25), Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, "Initializing Services...")

class BarangAIApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.icon_path = get_resource_path("assets/icon.png")
        if os.path.exists(self.icon_path):
            self.app_icon = QIcon(self.icon_path)
            splash_pixmap = QPixmap(self.icon_path)
        else:
            self.app_icon = self.app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
            splash_pixmap = self.app_icon.pixmap(200, 200)
        
        self.app.setWindowIcon(self.app_icon)

        self.splash = BeautifulSplash(splash_pixmap)
        self.splash.show()

        self.overlay_window = None
        self.tray_icon = None
        self.login_window = None

        self.app.processEvents()

        QTimer.singleShot(4000, self.fade_out_splash)

    def fade_out_splash(self):
        self.opacity_anim = QPropertyAnimation(self.splash, b"windowOpacity")
        self.opacity_anim.setDuration(1000) # 1 second fade
        self.opacity_anim.setStartValue(1.0)
        self.opacity_anim.setEndValue(0.0)
        self.opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.opacity_anim.finished.connect(self.show_login_after_splash)
        self.opacity_anim.start()

    def show_login_after_splash(self):
        saved_token, saved_user_id, saved_name, saved_role, saved_lang = load_auth_data()

        if saved_token and saved_user_id:
            self.start_overlay(saved_token, saved_user_id, saved_name, saved_role, saved_lang)
            self.splash.finish(self.overlay_window)
        else:
            self.login_window = LoginWindow(on_login_success=self.start_overlay)
            self.login_window.show()
            self.splash.finish(self.login_window)

    def start_overlay(self, token, user_id, user_name="Guest - Default", user_role="OFFICIAL", pref_lang="Default"):
        self.overlay_window = OverlayWindow(token=token, user_id=user_id, user_name=user_name, user_role=user_role, preferred_language=pref_lang)
        self.overlay_window.logout_requested.connect(self.handle_logout)
        self.overlay_window.show()
        self.setup_tray()

    def handle_logout(self):
        self.overlay_window.close()
        self.overlay_window = None
        self.tray_icon.hide()

        self.login_window = LoginWindow(on_login_success=self.start_overlay)
        self.login_window.show()
        self.splash.finish(self.login_window)

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self.app_icon, self.app)
        self.tray_icon.setToolTip("BarangAI Assistant")

        menu = QMenu()
        show_action = menu.addAction("Show Assistant")
        show_action.triggered.connect(self.overlay_window.show_overlay)
        
        quit_action = menu.addAction("Exit BarangAI")
        quit_action.triggered.connect(self.app.quit)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

        self.tray_icon.activated.connect(
            lambda reason: self.overlay_window.show_overlay() 
            if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None
        )

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app_instance = BarangAIApp()
    sys.exit(app_instance.app.exec())