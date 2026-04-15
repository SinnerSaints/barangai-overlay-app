import requests
import os
from dotenv import load_dotenv

load_dotenv()

SERVER_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8002") # Adjusted to point to AI service endpoint


import requests
import os
from dotenv import load_dotenv

load_dotenv()

SERVER_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8001")

def login(email: str, password: str) -> dict:
    try:
        # Hit the Login Endpoint to get user details
        login_response = requests.post(
            f"{SERVER_URL}/accounts/login/",
            json={"email": email, "password": password},
            timeout=10
        )

        if login_response.status_code != 200:
            return {"success": False, "message": "Invalid email or password."}

        login_data = login_response.json()

        print("\n=== DEBUG: BACKEND LOGIN RESPONSE ===")
        print(f"Type: {type(login_data)}")
        print(f"Data: {login_data}")
        print("=====================================\n")

        # Hit the Token Endpoint to get the actual JWT
        token_response = requests.post(
            f"{SERVER_URL}/accounts/token/",
            json={"email": email, "password": password},
            timeout=10
        )
        
        if token_response.status_code != 200:
            return {"success": False, "message": "Login succeeded, but failed to retrieve access token."}
            
        token_data = token_response.json()

        # EXTRACT DATA SAFELY
        user_id = login_data.get("id", 0)
        first_name = login_data.get("first_name", "")
        last_name = login_data.get("last_name", "")
        user_role = login_data.get("role", "OFFICIAL").upper()

        if first_name or last_name:
            display_name = f"{first_name} {last_name}".strip()
        else:
            display_name = login_data.get("user", "Barangay Official")

        return {
            "success": True,
            "access_token": token_data.get("access"),
            "user_id": user_id,
            "user_name": display_name,
            "user_role": user_role
        }

    except requests.exceptions.ConnectionError:
        return {"success": False, "message": "Cannot connect to server. Check your internet connection."}
    except Exception as e:
        return {"success": False, "message": f"An unexpected error occurred: {str(e)}"}

def send_message(
    message: str,
    screenshot_b64: str,
    user_id: int,
    session_uuid: str,
    token: str
) -> dict:
    """
    Sends message + screenshot to FastAPI chat endpoint.
    Returns full response dict.
    """
    try:
        payload = {
            "message": message,
            "user_id": int(user_id),
            "screenshot": screenshot_b64,
        }

        if session_uuid:
            payload["session_uuid"] = session_uuid

        response = requests.post(
            f"{SERVICE_URL}/chat/",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}"
            },
            timeout=30
        )

        if response.status_code == 200:
            return {
                "success": True,
                "response": response.json().get("response"),
                "session_uuid": response.json().get("session_uuid"),
            }
        elif response.status_code == 401:
            return {"success": False, "response": "SESSION_EXPIRED"}
        elif response.status_code == 404:
            return {"success": False, "response": "User not found."}
        else:
            return {"success": False, "response": "Sorry, something went wrong. Please try again."}

    except requests.exceptions.ConnectionError:
        return {"success": False, "response": "Cannot connect to BarangAI service."}
    except requests.exceptions.Timeout:
        return {"success": False, "response": "Response took too long. Please try again."}
    except Exception as e:
        return {"success": False, "response": f"Unexpected error: {str(e)}"}
    
