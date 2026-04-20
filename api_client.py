import requests
import os
from dotenv import load_dotenv

load_dotenv()

SERVER_URL = os.getenv("BACKEND_URL", "https://barangaibackend-production.up.railway.app/")
SERVICE_URL = os.getenv("AI_SERVICE_URL",  "https://barangai-service-openai-production.up.railway.app/")

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
        preferred_language = login_data.get("preferred_language", "Default")

        if first_name or last_name:
            display_name = f"{first_name} {last_name}".strip()
        else:
            display_name = login_data.get("user", "Barangay Official")

        return {
            "success": True,
            "access_token": token_data.get("access"),
            "user_id": user_id,
            "user_name": display_name,
            "user_role": user_role,
            "preferred_language": preferred_language
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
    token: str,
    user_name: str,
    preferred_language: str,
) -> dict:
    """
    Sends message + screenshot to FastAPI chat endpoint.
    Returns full response dict.
    """
    try:
        if callable(user_id):
            return {"success": False, "response": "Local Error: user_id is a function, not a number. Check self.user_id in overlay.py"}

        payload = {
            "message": message,
            "user_id": int(user_id),
            "screenshot": screenshot_b64,
            "user_name": user_name,
            "preferred_language": preferred_language,
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
            data = response.json()
            detected_intent = data.get("nlp_analysis", {}).get("detected_intent", "unknown")
            
            return {
                "success": True,
                "response": data.get("response"),
                "session_uuid": data.get("session_uuid"),
                "detected_intent": detected_intent
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
    
def update_user_preference(token: str, user_id: int, preferred_language: str) -> bool:
    """Uses the existing UpdateUserView to sync the language."""
    try:
        url = f"{SERVER_URL}/accounts/users/{user_id}/update/" 
        
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"preferred_language": preferred_language}

        response = requests.patch(url, json=payload, headers=headers, timeout=10)

        print(payload)
        
        return response.status_code == 200
    except Exception as e:
        print(f"API Error: {e}")
        return False

def save_system_log(token: str, task_type: str, time_taken: float, errors: int, help_requests: int) -> bool:
    """Sends the completed task metrics to the Django backend."""
    try:
        url = f"{SERVER_URL}/logs/create/"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "task_type": task_type,
            "time_taken_seconds": round(time_taken, 2),
            "error_count": errors,
            "help_requests_count": help_requests
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 201:
            print(f"Successfully saved system log: {task_type}")
            return True
        else:
            print(f"Failed to save log. Status: {response.status_code}, Msg: {response.text}")
            return False
            
    except Exception as e:
        print(f"API Error saving log: {e}")
        return False

def get_latest_session(user_id: int, token: str) -> dict:
    """Fetches the user's most recent chat session to resume."""
    try:
        response = requests.get(
            f"{SERVICE_URL}/sessions/",
            params={"user_id": user_id},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 401:
            return {"success": False, "error": "SESSION_EXPIRED"}
            
        if response.status_code == 200:
            sessions = response.json()
            if sessions:
                return {"success": True, "session": sessions[0]}
            return {"success": True, "session": None}
            
        return {"success": False, "error": f"Server returned {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_session_messages(session_uuid: str, token: str) -> dict:
    """Fetches all messages belonging to a specific session."""
    try:
        response = requests.get(
            f"{SERVICE_URL}/sessions/{session_uuid}/messages?limit=15",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 401:
            return {"success": False, "error": "SESSION_EXPIRED"}
            
        if response.status_code == 200:
            return {"success": True, "messages": response.json()}
            
        return {"success": False, "error": f"Server returned {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}