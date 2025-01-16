import json
import sqlite3

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
        cursor.execute('''INSERT INTO flights (date, origin, destination, price_inr, flightType)
                           VALUES (?, ?, ?, ?, ?)''',
                       (item['date'], item['origin'], item['destination'], item['price_inr'], item['flightType']))

    conn.commit()
    conn.close()