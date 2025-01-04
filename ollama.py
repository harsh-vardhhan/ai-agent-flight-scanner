import json
import sqlite3
from sqlalchemy import create_engine
from langchain_community.chat_models import ChatOllama
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain.prompts import PromptTemplate
from datetime import datetime

# Previous date conversion and database setup functions remain the same
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

# Database and LLM setup
url = 'sqlite:///flights.db'
engine = create_engine(url, echo=False)
db = SQLDatabase(engine)

llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0.1
)

# SQL query generation prompt
sql_prompt = PromptTemplate(
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

# New prompt template for natural language response generation
response_prompt = PromptTemplate(
    input_variables=["question", "sql_query", "query_result"],
    template="""Given the user's question: {question}

The SQL query used: {sql_query}

And the query results: {query_result}

Please provide a natural language response that:
1. Directly answers the user's question
2. Includes relevant specific details from the query results
3. Provides context when helpful
4. Uses a clear and conversational tone

Response:"""
)

# Create the SQL chain
sql_chain = create_sql_query_chain(llm=llm, db=db, prompt=sql_prompt)

async def process_flight_query():
    question = input("Enter your question about flights: ")

    try:
        # Generate SQL query
        sql_query = await sql_chain.ainvoke({"question": question})
        # print(f"\nGenerated SQL Query: {sql_query}")

        # Execute query and get results
        if sql_query:
            query_result = db.run(sql_query)
            # print(f"\nRaw Query Result: {query_result}")

            # Generate natural language response
            response_input = {
                "question": question,
                "sql_query": sql_query,
                "query_result": query_result
            }
            
            response = await llm.ainvoke(response_prompt.format(**response_input))
            print(response.content)
        else:
            print("No SQL query was generated.")

    except Exception as e:
        print(f"An error occurred: {e}")

# Main execution
if __name__ == "__main__":
    import asyncio
    
    # Initialize database
    json_to_sqlite('flight_data.json', 'flights.db')
    
    while True:
        asyncio.run(process_flight_query())
        if input("\nDo you want to ask another question? (y/n): ").lower() != 'y':
            break