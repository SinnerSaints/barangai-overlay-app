import pyautogui
import base64
from io import BytesIO
import threading
import time
import sys

if sys.platform == "win32":
    import pygetwindow as gw
elif sys.platform == "darwin":
    try:
        from AppKit import NSWorkspace
    except ImportError:
        print("macOS dependencies missing. Run: pip install pyobjc")

# Global variable to store the last app the user was looking at
last_external_window_title = "Initializing..."

def get_active_window_title() -> str:
    if sys.platform == "win32":
        try:
            active_window = gw.getActiveWindow()
            return active_window.title if active_window and active_window.title else ""
        except Exception:
            return ""
            
    elif sys.platform == "darwin":
        try:
            active_app = NSWorkspace.sharedWorkspace().activeApplication()
            return active_app.get('NSApplicationName', "") if active_app else ""
        except Exception:
            return ""
            
    return "Unknown OS"

def window_tracker_daemon():
    """
    Runs continuously in the background. It checks the active window twice a second.
    If the active window is NOT BarangAI, it saves the title to memory.
    """
    global last_external_window_title
    while True:
        try:
            title = get_active_window_title()
            if title and "barangai" not in title.lower():
                last_external_window_title = title
        except Exception:
            pass
        
        time.sleep(0.5)

# Start the background tracker
tracker_thread = threading.Thread(target=window_tracker_daemon, daemon=True)
tracker_thread.start()


def capture_screen() -> dict:
    global last_external_window_title
    
    try:
        # Do a quick check right before capture to ensure context is fresh
        title = get_active_window_title()
        if title and "barangai" not in title.lower():
            last_external_window_title = title

        # PyAutoGUI handles the actual screenshot on both platforms 
        # (Provided macOS has given screen recording permissions)
        screenshot = pyautogui.screenshot()

        buffer = BytesIO()
        screenshot.save(buffer, format="PNG")
        screenshot_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        context = detect_app(last_external_window_title)

        return {
            "screenshot": screenshot_b64,
            "active_window": last_external_window_title,
            "context": context
        }
    except Exception as e:
        print(f"Capture Error: {e}")
        return {"screenshot": None, "active_window": "Unknown", "context": None}


def detect_app(window_title: str) -> str:
    """
    Converts window title into a helpful context string for the AI.
    """
    title_lower = window_title.lower()

    if "word" in title_lower:
        return f"User is working in Microsoft Word. Window: {window_title}"
    elif "excel" in title_lower:
        return f"User is working in Microsoft Excel. Window: {window_title}"
    elif "outlook" in title_lower:
        return f"User is working in Microsoft Outlook. Window: {window_title}"
    elif "powerpoint" in title_lower:
        return f"User is working in Microsoft PowerPoint. Window: {window_title}"
    elif "file explorer" in title_lower:
        return f"User is using File Explorer. Window: {window_title}"
    elif "chrome" in title_lower or "edge" in title_lower or "firefox" in title_lower:
        return f"User is browsing the internet. Window: {window_title}"
    else:
        return f"User is currently using: {window_title}"