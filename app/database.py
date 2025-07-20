import sqlite3
import json

def json_to_sqlite(json_file, sqlite_file):
    """
    Reads flight data from a JSON file and inserts it into a SQLite database.

    This function handles a specific JSON structure containing flight details,
    creates a 'flights' table if it doesn't exist, and populates it.
    The 'uuid' from the JSON is used as the primary key to prevent duplicates.

    Args:
        json_file (str): The path to the input JSON file.
        sqlite_file (str): The path to the output SQLite database file.
    """
    try:
        # Attempt to read and parse the JSON file
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        print(f"Successfully loaded {len(data)} records from {json_file}.")
    except FileNotFoundError:
        print(f"Error: The file {json_file} was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_file}. Please check its format.")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading the JSON file: {e}")
        return

    conn = None  # Initialize connection to None
    try:
        # Establish a connection to the SQLite database
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()

        # Create the table with the new schema if it doesn't already exist.
        # Using 'uuid' as the PRIMARY KEY is a good practice for unique identification.
        # Added rainProbability (REAL for float) and freeMeal (INTEGER for boolean).
        cursor.execute('''CREATE TABLE IF NOT EXISTS flights (
                            uuid TEXT PRIMARY KEY,
                            airline TEXT,
                            date TEXT,
                            duration TEXT,
                            flightType TEXT,
                            price_inr INTEGER,
                            origin TEXT,
                            destination TEXT,
                            originCountry TEXT,
                            destinationCountry TEXT,
                            link TEXT,
                            rainProbability REAL,
                            freeMeal INTEGER
                        )''')
        print("Table 'flights' created or already exists.")

        # Insert or ignore data into the table
        # Using INSERT OR IGNORE to avoid errors if a UUID already exists.
        insert_count = 0
        for item in data:
            # Ensure all required keys are present in the item before insertion
            required_keys = [
                'uuid', 'airline', 'date', 'duration', 'flightType', 
                'price_inr', 'origin', 'destination', 'originCountry', 
                'destinationCountry', 'link', 'rainProbability', 'freeMeal'
            ]
            if not all(key in item for key in required_keys):
                print(f"Skipping record due to missing keys: {item.get('uuid', 'N/A')}")
                continue

            # Execute the insertion with the new fields
            cursor.execute('''INSERT OR IGNORE INTO flights (
                                uuid, airline, date, duration, flightType,
                                price_inr, origin, destination,
                                originCountry, destinationCountry, link,
                                rainProbability, freeMeal
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (item['uuid'], item['airline'], item['date'],
                             item['duration'], item['flightType'], item['price_inr'],
                             item['origin'], item['destination'],
                             item['originCountry'], item['destinationCountry'], item['link'],
                             item['rainProbability'], item['freeMeal']))
            if cursor.rowcount > 0:
                insert_count += 1
        
        # Commit the changes to the database
        conn.commit()
        print(f"Database operation complete. Inserted {insert_count} new records into 'flights' table.")

    except sqlite3.Error as e:
        print(f"A database error occurred: {e}")
        if conn:
            conn.rollback() # Rollback changes on error
    except KeyError as e:
        print(f"A key error occurred. A record might be missing the key: {e}")
    finally:
        # Ensure the database connection is closed
        if conn:
            conn.close()
            print("Database connection closed.")
