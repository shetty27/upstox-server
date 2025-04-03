from fastapi import FastAPI
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import json
import os
from datetime import datetime, timedelta

app = FastAPI()

# Firebase Initialization (Only Once)
if not firebase_admin._apps:
    firebase_credentials = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Upstox API Credentials from Environment Variables
UPSTOX_API_KEY = os.getenv("UPSTOX_API_KEY")
UPSTOX_API_SECRET = os.getenv("UPSTOX_API_SECRET")
REDIRECT_URI = "YOUR_REDIRECT_URL"  # 🔹 Upstox में सेट किया हुआ Redirect URL डालो

# Function to Get & Refresh Access Token
def get_access_token():
    doc_ref = db.collection("tokens").document("upstox")
    token_data = doc_ref.get().to_dict()

    if not token_data:
        print("❌ Error: No token data found in Firestore!")
        return None

    access_token = token_data.get("access_token")
    auth_code = token_data.get("authorization_code")  # ✅ Authorization Code Firebase से लो
    last_updated = token_data.get("last_updated")

    # Convert last_updated to datetime
    last_updated_dt = datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%S")

    # Check if Token Expired (Validity: 12 Hours)
    if datetime.utcnow() - last_updated_dt > timedelta(hours=12):
        print("🔄 Access Token Expired! Getting a new one...")

        auth_url = "https://api.upstox.com/v2/login/authorization/token"
        payload = {
            "code": auth_code,
            "apiKey": UPSTOX_API_KEY,
            "apiSecret": UPSTOX_API_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(auth_url, json=payload, headers=headers)

        new_token_data = response.json()
        
        if "access_token" in new_token_data:
            new_access_token = new_token_data["access_token"]

            # Save New Token in Firestore
            doc_ref.set({
                "access_token": new_access_token,
                "authorization_code": auth_code,  # ✅ Authorization Code फिर से Save करो
                "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
            })

            print("✅ New Access Token Saved!")
            return new_access_token
        else:
            print("❌ Error: Failed to refresh token!")
            print("🔍 API Response:", new_token_data)  # Debugging के लिए
            return None
    else:
        print("✅ Access Token is still valid!")
        return access_token

# Fetch Last Traded Price (LTP) from Upstox
@app.get("/ltp/{instrument_key}")
def get_ltp(instrument_key: str):
    access_token = get_access_token()
    if not access_token:
        return {"error": "Access Token Fetch Failed!"}

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    url = "https://api.upstox.com/v2/market-quote/ltp"
    payload = {"instrument_keys": [instrument_key]}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch LTP", "status_code": response.status_code, "message": response.text}

# Fetch Full Market Quotes from Upstox
@app.get("/quotes/{instrument_key}")
def get_quotes(instrument_key: str):
    access_token = get_access_token()
    if not access_token:
        return {"error": "Access Token Fetch Failed!"}

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    url = "https://api.upstox.com/v2/market-quote/quotes"
    payload = {"instrument_keys": [instrument_key]}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch market quotes", "status_code": response.status_code, "message": response.text}

@app.get("/")
def home():
    return {"message": "Server is running!"}

@app.get("/ping")
@app.head("/ping")
def ping():
    return {"status": "OK"}

# ✅ Server को Start करने के लिए Uvicorn का Use करो (Render के लिए ज़रूरी)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
