import json
import sqlite3
from datetime import datetime

def convert_date_to_iso(date_str):
    if date_str:
        day, month = date_str.split()
        day = int(day)
        month = datetime.strptime(month, '%B').month
        return f"{datetime.now().year:04d}-{month:02d}-{day:02d}"
    return None

def json_to_sqlite(json_file, sqlite_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    conn = sqlite3.connect(sqlite_file)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS flights (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        origin TEXT,
                        destination TEXT,
                        price_inr INTEGER,
                        flightType TEXT
                    )''')

    for item in data:
        iso_date = convert_date_to_iso(item['date'])
        price_str = item['price_inr'].replace('₹', '').replace(',', '')
        price_int = int(price_str)

        cursor.execute('''INSERT INTO flights (date, origin, destination, price_inr, flightType)
                           VALUES (?, ?, ?, ?, ?)''',
                       (iso_date, item['origin'], item['destination'], price_int, item['flightType']))

    conn.commit()
    conn.close()