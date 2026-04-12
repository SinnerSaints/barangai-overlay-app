import sys
from PyQt6.QtWidgets import QApplication
from overlay import OverlayWindow


def main():
    app = QApplication(sys.argv)
    # prevents app from closing when overlay window is hidden
    app.setQuitOnLastWindowClosed(False)

    overlay_window = OverlayWindow(token="dummy_token")
    overlay_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()