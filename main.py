from fastapi import FastAPI
import requests
from upstox_auth import refresh_access_token, get_saved_tokens
from firebase_config import save_to_firebase
import uvicorn

app = FastAPI()

# 🔹 Upstox API से Data Fetch करने वाला Function
def fetch_stock_data(symbol):
    access_token = refresh_access_token()
    if not access_token:
        return {"error": "Failed to get access token"}

    url = f"https://api.upstox.com/market-quote/{symbol}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        save_to_firebase(symbol, data["last_price"])
        return {"symbol": symbol, "price": data["last_price"]}
    
    return {"error": "Failed to fetch data"}

# 🔹 API Routes
@app.get("/")
def home():
    return {"message": "Stock Prediction API is Running with Upstox!"}

@app.get("/fetch/{symbol}")
def get_stock(symbol: str):
    return fetch_stock_data(symbol)

# ✅ Server को Start करने के लिए Uvicorn का Use करो
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
