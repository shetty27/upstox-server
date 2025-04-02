import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# Load Firebase Credentials from ENV
firebase_creds = json.loads(os.getenv("FIREBASE_CREDENTIALS"))

# Initialize Firebase App
cred = credentials.Certificate(firebase_creds)
firebase_admin.initialize_app(cred)

db = firestore.client()

def save_to_firebase(symbol, price):
    doc_ref = db.collection("stock_data").document(symbol)
    doc_ref.set({
        "symbol": symbol,
        "price": price,
        "timestamp": firestore.SERVER_TIMESTAMP
    })
