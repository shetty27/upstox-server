import os
import requests
import time
from firebase_admin import firestore

# Firestore Database Init
db = firestore.client()

# 🔹 Firestore से Token लाने का Function
def get_saved_tokens():
    doc_ref = db.collection("upstox_tokens").document("tokens")
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None

# 🔹 Firestore में Token Save करने का Function
def save_tokens(access_token, expiry_time):
    doc_ref = db.collection("upstox_tokens").document("tokens")
    doc_ref.set({
        "access_token": access_token,
        "access_token_expiry": expiry_time,
        "last_updated": int(time.time())
    })

# 🔹 Access Token Auto Refresh करने का Function
def refresh_access_token():
    tokens = get_saved_tokens()
    if not tokens:
        return None

    access_token_expiry = tokens.get("access_token_expiry", 0)
    
    # 🔥 अगर Token Expire हो गया है, तो नया Generate करो
    if int(time.time()) >= access_token_expiry:
        print("🔄 Access Token Expired! Generating New Token...")

        url = "https://api.upstox.com/v2/login/authorization/token"
        payload = {
            "client_id": os.getenv("UPSTOX_API_KEY"),
            "client_secret": os.getenv("UPSTOX_API_SECRET"),
            "grant_type": "password",
            "username": os.getenv("UPSTOX_USERNAME"),
            "password": os.getenv("UPSTOX_PASSWORD")
        }
        
        response = requests.post(url, data=payload)
        
        if response.status_code == 200:
            new_token_data = response.json()
            access_token = new_token_data.get("access_token")
            expires_in = new_token_data.get("expires_in", 3600)
            expiry_time = int(time.time()) + expires_in
            
            save_tokens(access_token, expiry_time)
            return access_token
        else:
            print("❌ Failed to Refresh Token:", response.json())
            return None
    else:
        return tokens.get("access_token")
