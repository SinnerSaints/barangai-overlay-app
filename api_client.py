import requests
import os
from dotenv import load_dotenv

load_dotenv()

SERVER_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8002") # Adjusted to point to AI service endpoint


def login(email: str, password: str) -> dict:
    """
    Runs login and token fetch at the same time.
    Returns token if both succeed.
    """
    try:
        # Step 1 — authenticate use
        login_response = requests.post(
            f"{SERVER_URL}/accounts/login/",
            json={
                "email": email,
                "password": password
            },
            timeout=10
        )

        if login_response.status_code != 200:
            return {
                "success": False,
                "message": "Invalid email or password."
            }

        # Step 2 — get token immediately after login
        token_response = requests.post(
            f"{SERVER_URL}/accounts/token/",
            json={
                "email": email,
                "password": password
            },
            timeout=10
        )

        if token_response.status_code != 200:
            return {
                "success": False,
                "message": "Authentication failed. Please try again."
            }

        token_data = token_response.json()

        return {
            "success": True,
            "access_token": token_data.get("access"),
            "user_id": login_response.json().get("id"),  # adjust key based on your actual response
        }

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "Cannot connect to server. Check your internet connection."
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"An unexpected error occurred: {str(e)}"
        }


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
    
