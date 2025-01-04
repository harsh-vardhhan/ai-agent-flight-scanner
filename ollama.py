import json
import sqlite3
from sqlalchemy import create_engine
from langchain_community.chat_models import ChatOllama
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain.prompts import PromptTemplate
from datetime import datetime

# Date conversion function
def convert_date_to_iso(date_str):
    if date_str:
        day, month = date_str.split()
        day = int(day)
        month = datetime.strptime(month, '%B').month
        return f"{datetime.now().year:04d}-{month:02d}-{day:02d}"
    return None

# JSON to SQLite conversion
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
                        price INTEGER,
                        flightType TEXT,
                        percentage REAL
                    )''')

    for item in data:
        iso_date = convert_date_to_iso(item['date'])
        price_str = item['price'].replace('₹', '').replace(',', '')
        price_int = int(price_str)

        cursor.execute('''INSERT INTO flights (date, origin, destination, price, flightType, percentage)
                           VALUES (?, ?, ?, ?, ?, ?)''',
                       (iso_date, item['origin'], item['destination'], price_int, item['flightType'], float(item['percentage'])))

    conn.commit()
    conn.close()

# Convert JSON to SQLite
json_to_sqlite('flight_data.json', 'flights.db')

# Connect to SQLite database
url = 'sqlite:///flights.db'
engine = create_engine(url, echo=False)
db = SQLDatabase(engine)

# Initialize ChatOllama
llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0.1
)

# Define custom prompt template for SQL queries
prompt = PromptTemplate(
    input_variables=["input", "top_k", "table_info"],
    template="""Given the following input: {input}

For the database with the following schema:
{table_info}

Generate a SQL query that:
1. Is valid SQLite syntax
2. Returns at most {top_k} results
3. Only includes the SQL query without any explanations

SQL Query:"""
)

# Create the SQL chain
chain = create_sql_query_chain(llm=llm, db=db, prompt=prompt)

# Query flights function
async def query_flights():
    question = input("Enter your question about flights: ")

    try:
        # Generate SQL query using the chain
        sql_query = await chain.ainvoke({"question": question})
        print(f"Generated SQL Query: {sql_query}")

        # Execute the query and get results
        if sql_query:
            result = db.run(sql_query)
            print(f"Query Result: {result}")
        else:
            print("No SQL query was generated.")

    except Exception as e:
        print(f"An error occurred: {e}")

# Main execution
if __name__ == "__main__":
    import asyncio
    
    while True:
        asyncio.run(query_flights())
        if input("Do you want to query again? (y/n): ").lower() != 'y':
            break