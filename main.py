from fastapi import FastAPI
import requests
import os
from firebase_config import save_to_firebase

app = FastAPI()

# 🔹 Upstox API Key
UPSTOX_API_KEY = os.getenv("UPSTOX_API_KEY")

# 🔹 Upstox से Data Fetch करने वाला Function
def fetch_stock_data(symbol):
    url = f"https://api.upstox.com/market-quote/{symbol}"
    headers = {"Authorization": f"Bearer {UPSTOX_API_KEY}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data["last_price"]
    return None

# 🔹 Home Route
@app.get("/")
def home():
    return {"message": "Stock Prediction API is Running with Firebase!"}

# 🔹 Stock Data Fetch करने वाला API Route
@app.get("/fetch/{symbol}")
def get_stock(symbol: str):
    price = fetch_stock_data(symbol)
    if price:
        save_to_firebase(symbol, price)
        return {"symbol": symbol, "price": price}
    return {"error": "Failed to fetch data"}
