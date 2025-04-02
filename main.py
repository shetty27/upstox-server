from fastapi import FastAPI
from upstox_api import fetch_stock_data
from database import save_to_firebase

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Stock Prediction API is Running with Firebase!"}

@app.get("/fetch/{symbol}")
def get_stock(symbol: str):
    price = fetch_stock_data(symbol)
    if price:
        save_to_firebase(symbol, price)
        return {"symbol": symbol, "price": price}
    return {"error": "Failed to fetch data"}
