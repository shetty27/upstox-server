import requests
import os
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase Initialize (यह पहले से set होना चाहिए)
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_credentials.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# 🔹 Firestore में Saved Tokens को Retrieve करने का Function
def get_saved_tokens():
    doc_ref = db.collection("tokens").document("upstox")
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None

# 🔹 Firestore में Token Update करने का Function
def update_tokens(access_token, refresh_token):
    doc_ref = db.collection("tokens").document("upstox")
    doc_ref.set({
        "access_token": access_token,
        "refresh_token": refresh_token
    })

# 🔹 Access Token को Auto Refresh करने वाला Function
def refresh_access_token():
    tokens = get_saved_tokens()
    if not tokens:
        return None

    refresh_token = tokens["refresh_token"]
    client_id = os.getenv("UPSTOX_CLIENT_ID")
    client_secret = os.getenv("UPSTOX_CLIENT_SECRET")
    redirect_uri = os.getenv("UPSTOX_REDIRECT_URI")

    url = "https://api.upstox.com/login/refresh-token"
    data = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "redirect_uri": redirect_uri
    }

    response = requests.post(url, data=data)
    if response.status_code == 200:
        new_tokens = response.json()
        update_tokens(new_tokens["access_token"], new_tokens["refresh_token"])
        return new_tokens["access_token"]
    
    return None
