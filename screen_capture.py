import pygetwindow as gw
import pyautogui
import base64
from io import BytesIO
import threading
import time

# Global variable to store the last app the user was looking at
last_external_window_title = "Initializing..."

def window_tracker_daemon():
    """
    Runs continuously in the background. It checks the active window twice a second.
    If the active window is NOT BarangAI, it saves the title to memory.
    """
    global last_external_window_title
    while True:
        try:
            active_window = gw.getActiveWindow()
            if active_window and active_window.title:
                title = active_window.title
                # Only update the memory if the user is NOT looking at our overlay
                if "barangai" not in title.lower():
                    last_external_window_title = title
        except Exception:
            pass # Ignore temporary OS errors if a window is closing
        
        time.sleep(0.5) # Check twice a second

# Start the background tracker the moment this file is imported
tracker_thread = threading.Thread(target=window_tracker_daemon, daemon=True)
tracker_thread.start()


def capture_screen() -> dict:
    global last_external_window_title
    
    try:
        current_active = gw.getActiveWindow()

        if current_active and current_active.title:
            if "barangai" not in current_active.title.lower():
                last_external_window_title = current_active.title

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