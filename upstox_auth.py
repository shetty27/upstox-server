import requests
import os
import json
from firebase_config import db  # Firestore से Connect करने के लिए

# 🔹 Upstox API Credentials
UPSTOX_API_KEY = os.getenv("UPSTOX_API_KEY")
UPSTOX_API_SECRET = os.getenv("UPSTOX_API_SECRET")
UPSTOX_REDIRECT_URI = os.getenv("UPSTOX_REDIRECT_URI")

# 🔹 Firestore Database में Token Save करने वाला Function
def save_token(access_token, refresh_token):
    doc_ref = db.collection("upstox_tokens").document("tokens")
    doc_ref.set({
        "access_token": access_token,
        "refresh_token": refresh_token
    })

# 🔹 Firestore से Token Fetch करने वाला Function
def get_saved_tokens():
    doc_ref = db.collection("upstox_tokens").document("tokens").get()
    if doc_ref.exists:
        return doc_ref.to_dict()
    return None

# 🔹 Upstox से New Access Token Generate करने वाला Function
def get_new_access_token(auth_code):
    url = "https://api.upstox.com/login/authorize"
    data = {
        "client_id": UPSTOX_API_KEY,
        "client_secret": UPSTOX_API_SECRET,
        "redirect_uri": UPSTOX_REDIRECT_URI,
        "code": auth_code,
        "grant_type": "authorization_code"
    }
    
    response = requests.post(url, data=data)
    if response.status_code == 200:
        token_data = response.json()
        save_token(token_data["access_token"], token_data["refresh_token"])
        return token_data["access_token"]
    return None

# 🔹 Refresh Token का Use करके नया Access Token Generate करने वाला Function
def refresh_access_token():
    tokens = get_saved_tokens()
    if not tokens:
        return None
    
    refresh_token = tokens["refresh_token"]
    url = "https://api.upstox.com/login/refresh-token"
    data = {
        "client_id": UPSTOX_API_KEY,
        "client_secret": UPSTOX_API_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    
    response = requests.post(url, data=data)
    if response.status_code == 200:
        token_data = response.json()
        save_token(token_data["access_token"], token_data["refresh_token"])
        return token_data["access_token"]
    return None
