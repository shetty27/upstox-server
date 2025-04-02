import firebase_admin
from firebase_admin import credentials, firestore
import requests
import json
import os
from datetime import datetime, timedelta

# Firebase Initialization (Only Once)
if not firebase_admin._apps:
    firebase_credentials = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Upstox API Credentials from Environment Variables
UPSTOX_API_KEY = os.getenv("UPSTOX_API_KEY")
UPSTOX_API_SECRET = os.getenv("UPSTOX_API_SECRET")

# Function to Get & Refresh Access Token
def get_access_token():
    doc_ref = db.collection("tokens").document("upstox")
    token_data = doc_ref.get().to_dict()

    if not token_data:
        print("❌ Error: No token data found in Firestore!")
        return None

    access_token = token_data.get("access_token")
    last_updated = token_data.get("last_updated")

    # Convert last_updated to datetime
    last_updated_dt = datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%S")

    # Check if Token Expired (Validity: 12 Hours)
    if datetime.utcnow() - last_updated_dt > timedelta(hours=12):
        print("🔄 Access Token Expired! Getting a new one...")

        auth_url = "https://api.upstox.com/v2/login/authorization/token"
        payload = {
            "apiKey": UPSTOX_API_KEY,
            "apiSecret": UPSTOX_API_SECRET
        }

        response = requests.post(auth_url, json=payload)
        new_token_data = response.json()

        if "access_token" in new_token_data:
            new_access_token = new_token_data["access_token"]

            # Save New Token in Firestore
            doc_ref.set({
                "access_token": new_access_token,
                "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
            })

            print("✅ New Access Token Saved!")
            return new_access_token
        else:
            print("❌ Error: Failed to refresh token!")
            return None
    else:
        print("✅ Access Token is still valid!")
        return access_token

# Function to Fetch Market Data from Upstox
def fetch_market_data():
    access_token = get_access_token()
    if not access_token:
        print("❌ Error: Unable to fetch valid Access Token!")
        return

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    market_data_url = "https://api.upstox.com/v2/market-quote/stocks/NSE/RELIANCE"
    response = requests.get(market_data_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("📊 Market Data:", json.dumps(data, indent=4))
    else:
        print("❌ Error Fetching Market Data:", response.status_code, response.text)

# Run the Market Data Fetching
if __name__ == "__main__":
    fetch_market_data()
