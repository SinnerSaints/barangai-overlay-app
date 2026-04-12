import requests
import os
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env file


BACKEND_URL = os.getenv("BACKEND_URL")
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL")

def login(username: str, password: str) -> dict:
    """
    Logs in through Django backend.
    Same login as the web app.
    Returns token if successful.
    """
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/token/",  # change to your actual login endpoint
            json={
                "username": username,
                "password": password
            },
            timeout=10
        )

        if response.status_code == 200:
            return {
                "success": True,
                "token": response.json().get("access")  # JWT token from Django
            }
        else:
            return {
                "success": False,
                "message": "Invalid username or password."
            }

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "Cannot connect to server. Check your internet connection."
        }
    except Exception as e:
        return {
            "success": False,
            "message": "An unexpected error occurred."
        }


def send_message(message: str, context: str, token: str) -> str:
    """
    Sends user message + context to FastAPI AI service.
    Returns AI response as a string.
    """
    try:
        response = requests.post(
            f"{AI_SERVICE_URL}/chat/",
            json={
                "message": message,
                "context": context,
            },
            headers={
                "Authorization": f"Bearer {token}"
            },
            timeout=30
        )

        if response.status_code == 200:
            return response.json().get("response", "Sorry, I could not get a response.")
        elif response.status_code == 401:
            return "SESSION_EXPIRED"
        else:
            return "Sorry, something went wrong. Please try again."

    except requests.exceptions.ConnectionError:
        return "Cannot connect to BarangAI service. Please check your internet."
    except requests.exceptions.Timeout:
        return "Response took too long. Please try again."
    except Exception as e:
        return "An unexpected error occurred."