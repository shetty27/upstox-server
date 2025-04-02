import os
import json
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# 🔹 Firebase Credentials को Environment Variable से Load करो
firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")

if firebase_credentials:
    cred_dict = json.loads(firebase_credentials)
    cred = credentials.Certificate(cred_dict)

    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
else:
    raise ValueError("❌ Firebase Credentials Not Found in Environment Variables!")

# 🔹 Firestore Database Access
db = firestore.client()

# 🔹 Upstox API Credentials (Render के Env Variables से)
UPSTOX_API_KEY = os.getenv("UPSTOX_API_KEY")
UPSTOX_API_SECRET = os.getenv("UPSTOX_API_SECRET")
UPSTOX_REDIRECT_URI = os.getenv("UPSTOX_REDIRECT_URI")

# 🔹 Firebase से Tokens Fetch करने का Function
def get_saved_tokens():
    doc_ref = db.collection("upstox_tokens").document("auth")
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None

# 🔹 Access Token Refresh करने का Function
def refresh_access_token():
    tokens = get_saved_tokens()
    if not tokens or "refresh_token" not in tokens:
        print("❌ No Refresh Token Found in Firebase!")
        return None

    refresh_token = tokens["refresh_token"]

    url = "https://api.upstox.com/login/authorization/token"
    payload = {
        "client_id": UPSTOX_API_KEY,
        "client_secret": UPSTOX_API_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "redirect_uri": UPSTOX_REDIRECT_URI
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        new_access_token = data.get("access_token")
        new_refresh_token = data.get("refresh_token")

        if new_access_token and new_refresh_token:
            # 🔹 Firebase में Updated Tokens Save करो
            db.collection("upstox_tokens").document("auth").set({
                "access_token": new_access_token,
                "refresh_token": new_refresh_token
            })

            print("✅ Access Token Refreshed Successfully!")
            return new_access_token
    else:
        print("❌ Failed to Refresh Access Token!", response.text)
    
    return None
