import sqlite3

conn = sqlite3.connect("stocks.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS stock_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT,
    price REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

def save_to_db(symbol, price):
    cursor.execute("INSERT INTO stock_data (symbol, price) VALUES (?, ?)", (symbol, price))
    conn.commit()
