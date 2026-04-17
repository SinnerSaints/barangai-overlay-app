import os
import sys
import keyring

SERVICE_NAME = "BarangAI"

def get_resource_path(filename):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
        
    return os.path.join(base_path, filename)

def save_auth_data(token: str, user_id: int, user_name: str, user_role: str, preferred_language: str):
    """Saves the token and user ID to the OS native secure vault."""
    keyring.set_password(SERVICE_NAME, "access_token", token)
    keyring.set_password(SERVICE_NAME, "user_id", str(user_id))
    keyring.set_password(SERVICE_NAME, "user_name", user_name)
    keyring.set_password(SERVICE_NAME, "user_role", user_role)
    keyring.set_password(SERVICE_NAME, "preferred_language", preferred_language)

def load_auth_data():
    """Retrieves the token, ID, Name, and Role from the OS vault."""
    token = keyring.get_password(SERVICE_NAME, "access_token")
    user_id_str = keyring.get_password(SERVICE_NAME, "user_id")
    user_name = keyring.get_password(SERVICE_NAME, "user_name")
    user_role = keyring.get_password(SERVICE_NAME, "user_role")
    preferred_language = keyring.get_password(SERVICE_NAME, "preferred_language")
    
    if token and user_id_str:
        final_name = user_name if user_name else "Barangay Official"
        final_role = user_role if user_role else "OFFICIAL"
        final_lang = preferred_language if preferred_language else "Default"
        return token, int(user_id_str), final_name, final_role, final_lang
    return None, None, None, None, "Default"

def clear_auth_data():
    """Deletes all credentials from the vault on logout."""
    try:
        keyring.delete_password(SERVICE_NAME, "access_token")
        keyring.delete_password(SERVICE_NAME, "user_id")
        keyring.delete_password(SERVICE_NAME, "user_name")
        keyring.delete_password(SERVICE_NAME, "user_role")
        keyring.delete_password(SERVICE_NAME, "preferred_language")
    except keyring.errors.PasswordDeleteError:
        pass