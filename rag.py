import json
import sqlite3
from sqlalchemy import create_engine
from langchain_community.llms import Ollama
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
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

# Initialize the LLM with Ollama
llm = Ollama(
    model="llama3.2:3b",
    temperature=0.1
)

# Define custom prompt template for SQL queries with schema information
sql_prompt = PromptTemplate(
    input_variables=["input"],
    template="""Given this input: {input}, generate only the SQL query to answer it from the flights database:
    Schema:
    - flights table with columns: id, date, origin, destination, price, flightType, percentage
    Ensure you include both the date and the price when relevant. Do not include any markdown, comments, or explanations. Output only plain SQL.""",
)



# Build a chain
db_chain = SQLDatabaseChain.from_llm(
    llm=llm,
    db=db,
    prompt=sql_prompt,
    verbose=False
)

# Query flights function using the invoke method
def query_flights():
    question = input("Enter your question about flights: ")

    try:
        # Use invoke method with the correct input key
        result = db_chain.invoke({"query": question})  # Use 'query' as the key

        # Retrieve and print the query result
        sql_query = result['result']  # Assuming the generated SQL is stored in 'result'
        print(f"Generated SQL Query: {sql_query}")

        # Execute the SQL query
        result_from_query = db.run(sql_query)
        print(f"Query Result: {result_from_query}")

    except Exception as e:
        print(f"An error occurred: {e}")


# Main execution
if __name__ == "__main__":
    while True:
        query_flights()
        if input("Do you want to query again? (y/n): ").lower() != 'y':
            break
