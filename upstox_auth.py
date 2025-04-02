import os
import json
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# 🔹 Firebase Initialization
firebase_creds = os.getenv("FIREBASE_CREDENTIALS")
if not firebase_creds:
    raise ValueError("Firebase credentials not found in environment variables.")

firebase_creds_dict = json.loads(firebase_creds)
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_creds_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 🔹 Upstox API Credentials
UPSTOX_API_KEY = os.getenv("UPSTOX_API_KEY")
UPSTOX_API_SECRET = os.getenv("UPSTOX_API_SECRET")
UPSTOX_REDIRECT_URI = os.getenv("UPSTOX_REDIRECT_URI")

FIRESTORE_DOC_PATH = "upstox/tokens"


def get_saved_tokens():
    """Retrieve stored access token from Firestore"""
    doc = db.document(FIRESTORE_DOC_PATH).get()
    if doc.exists:
        return doc.to_dict()
    return None


def save_tokens(access_token):
    """Save access token to Firestore"""
    db.document(FIRESTORE_DOC_PATH).set({"access_token": access_token}, merge=True)


def refresh_access_token():
    """Refresh Upstox Access Token"""
    saved_tokens = get_saved_tokens()
    if not saved_tokens or "access_token" not in saved_tokens:
        raise ValueError("No valid access token found in Firestore.")
    
    access_token = saved_tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.upstox.com/v2/user/profile", headers=headers)
    
    if response.status_code == 401:
        raise ValueError("Access Token Expired! Manual re-authentication required.")
    elif response.status_code == 200:
        print("✅ Access Token is still valid.")
        return access_token
    else:
        print("⚠️ Unknown response from Upstox API", response.json())
        return None
