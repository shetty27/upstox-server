from fastapi import FastAPI, Request
import requests
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# Firestore Setup
if not firebase_admin._apps:
    firebase_credentials = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# FastAPI Setup
app = FastAPI()

# Upstox API Base URL
UPSTOX_API_BASE = "https://api.upstox.com/v2/market-quote/ltp"

# ✅ Firestore से Access Token लेना
def get_access_token():
    doc_ref = db.collection("tokens").document("upstox")
    token_data = doc_ref.get().to_dict()
    if token_data:
        return token_data.get("access_token")
    else:
        return None

# ✅ LTP Fetch API (POST Method)
@app.post("/ltp")
async def get_ltp(request: Request):
    access_token = get_access_token()
    if not access_token:
        return {"error": "Access Token not found in Firestore!"}

    data = await request.json()
    instrument_keys = data.get("instrument_keys", [])

    headers = {
        "Authorization": f"Bearer {access_token}",
        
        "Content-Type": "application/json"
    }

    url = UPSTOX_API_BASE
    payload = {"instrument_keys": instrument_keys}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch LTP", "status_code": response.status_code, "message": response.text}

# ✅ Health Check Route
@app.get("/")
def home():
    return {"message": "Server is running!"}

@app.get("/ping")
@app.head("/ping")
def ping():
    return {"status": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=True)
