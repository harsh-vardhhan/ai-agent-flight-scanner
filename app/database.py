import sqlite3
import json

def json_to_sqlite(json_file, sqlite_file):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return

    conn = sqlite3.connect(sqlite_file)
    cursor = conn.cursor()

    try:
        # Create the table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS flights (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            airline TEXT,
                            time TEXT,
                            date TEXT,
                            duration TEXT,
                            flightType TEXT,
                            price_inr INTEGER,
                            origin TEXT,
                            destination TEXT,
                            originCountry TEXT,
                            destinationCountry TEXT
                        )''')
        print("Table created (or already exists).")
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")
        conn.close()
        return

    try:
        # Insert data into the table
        for item in data:
            cursor.execute('''INSERT INTO flights (
                                airline, time, date, duration, flightType,
                                price_inr, origin, destination,
                                originCountry, destinationCountry
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (item['airline'], item['time'], item['date'],
                             item['duration'], item['flightType'], item['price_inr'],
                             item['origin'], item['destination'],
                             item['originCountry'], item['destinationCountry']))
        conn.commit()
        print(f"Inserted {len(data)} records into 'flights' table.")
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
    finally:
        conn.close()
