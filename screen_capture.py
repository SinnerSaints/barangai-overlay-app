import pygetwindow as gw


def get_active_window_context() -> str:
    """
    Detects the currently active window
    and returns a helpful context string for the AI.
    """
    try:
        active_window = gw.getActiveWindow()

        if not active_window:
            return None

        window_title = active_window.title
        return detect_app(window_title)

    except Exception as e:
        return None


def detect_app(window_title: str) -> str:
    """
    Converts window title into a context string.

    Examples:
    "Document1 - Microsoft Word" → "User is working in Microsoft Word"
    "Book1 - Microsoft Excel"    → "User is working in Microsoft Excel"
    """
    title_lower = window_title.lower()

    if "word" in title_lower:
        return f"User is working in Microsoft Word. Window title: {window_title}"
    elif "excel" in title_lower:
        return f"User is working in Microsoft Excel. Window title: {window_title}"
    elif "outlook" in title_lower:
        return f"User is working in Microsoft Outlook (Email). Window title: {window_title}"
    elif "file explorer" in title_lower:
        return f"User is using File Explorer. Window title: {window_title}"
    elif "chrome" in title_lower or "firefox" in title_lower or "edge" in title_lower:
        return f"User is browsing the internet. Window title: {window_title}"
    elif "barangai" in title_lower:
        # ignore our own app window
        return None
    else:
        return f"User is currently using: {window_title}"