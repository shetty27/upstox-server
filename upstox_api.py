import requests
from config import UPSTOX_API_KEY

UPSTOX_API_URL = "https://api.upstox.com/v2/market/quote"

def fetch_stock_data(symbol):
    headers = {"Authorization": f"Bearer {UPSTOX_API_KEY}"}
    params = {"symbol": symbol}

    response = requests.get(UPSTOX_API_URL, headers=headers, params=params)
    data = response.json()

    if "data" in data:
        return data["data"]["last_price"]
    return None
