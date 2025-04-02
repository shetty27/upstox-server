import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# 🔹 Firebase Credentials को ENV से Load करो
firebase_creds = json.loads(os.getenv("FIREBASE_CREDENTIALS"))

# 🔹 Firebase Initialize करो
cred = credentials.Certificate(firebase_creds)
firebase_admin.initialize_app(cred)

# 🔹 Firestore Database का Client Object
db = firestore.client()

# 🔹 Data को Firestore में Save करने का Function
def save_to_firebase(symbol, price):
    doc_ref = db.collection("stock_data").document(symbol)
    doc_ref.set({
        "symbol": symbol,
        "price": price,
        "timestamp": firestore.SERVER_TIMESTAMP
    })
