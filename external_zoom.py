import jwt
import os
import requests
import time
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()

API_KEY = os.getenv("ZOOM_API_KEY")
API_SECRET = os.getenv("ZOOM_API_SECRET")
USER_ID = os.getenv("ZOOM_USER_ID", "me")

def generate_jwt():
    payload = {
        'iss': API_KEY,
        'exp': time.time() + 3600  # valid for 1 hour
    }
    token = jwt.encode(payload, API_SECRET, algorithm='HS256')
    return token

def schedule_zoom_meeting(topic="Test Meeting", start_time=None, duration=60):
    if start_time is None:
        start_time = (datetime.now(timezone.utc) + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")

    headers = {
        'authorization': f'Bearer {generate_jwt()}',
        'content-type': 'application/json'
    }

    payload = {
        "topic": topic,
        "type": 2,  # Scheduled meeting
        "start_time": start_time,
        "duration": duration,
        "timezone": "UTC",
        "settings": {
            "join_before_host": True,
            "mute_upon_entry": True,
            "waiting_room": False
        }
    }

    response = requests.post(
        f'https://api.zoom.us/v2/users/{USER_ID}/meetings',
        headers=headers,
        json=payload
    )

    if response.status_code == 201:
        meeting = response.json()
        print("Meeting created successfully!")
        print("Join URL:", meeting["join_url"])
        print("Start URL:", meeting["start_url"])
    else:
        print("Error:", response.status_code)
        print(response.text)

if __name__ == "__main__":
    # Example usage
    schedule_zoom_meeting(topic="Project Sync", duration=45)
