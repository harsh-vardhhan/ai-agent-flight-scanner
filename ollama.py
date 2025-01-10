import json
import sqlite3
from sqlalchemy import create_engine
from langchain_community.chat_models import ChatOllama
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain.prompts import PromptTemplate
from datetime import datetime

def is_flight_related_query(query):
    """
    Check if the query is related to flight data by looking for relevant keywords
    """
    flight_keywords = {
        'flight', 'flights', 'air', 'airline', 'airport', 'travel',
        'destination', 'origin', 'route', 'price', 'fare',
        'departure', 'arrive', 'arriving', 'departing', 'connection',
        '₹', 'type', 'date', 'cost', 'expensive', 'cheap'
    }

    # Convert query to lowercase for case-insensitive matching
    query_words = set(query.lower().split())

    # Check if any flight-related keyword is present in the query
    return bool(query_words.intersection(flight_keywords))

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
                    )''')

    for item in data:
        iso_date = convert_date_to_iso(item['date'])
        price_str = item['price'].replace('₹', '').replace(',', '')
        price_int = int(price_str)

        cursor.execute('''INSERT INTO flights (date, origin, destination, price, flightType)
                           VALUES (?, ?, ?, ?, ?, ?)''',
                       (iso_date, item['origin'], item['destination'], price_int, item['flightType']))

    conn.commit()
    conn.close()

# Database and LLM setup
url = 'sqlite:///flights.db'
engine = create_engine(url, echo=False)
db = SQLDatabase(engine)

llm = ChatOllama(
    model="qwen2.5-coder:3b",
    temperature=1,
)

sql_prompt = PromptTemplate(
    input_variables=["input", "top_k", "table_info"],
    template="""Given the following input: {input}

For the database with the following schema:
{table_info}

Generate a SQL query that:
1. Is valid SQLite syntax
2. Returns at most {top_k} results
3. Returns only the raw SQL query without any formatting or markdown

Query:"""
)

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
5. Price should be denominated in Indian currency ₹ and
6. Price should use Indian number system
7. Provide data in tabular format if possible

Response:"""
)

async def process_flight_query():
    question = input("Enter your question about flights: ")

    # First, verify if the query is flight-related
    if not is_flight_related_query(question):
        print("\nQuery not related to flight data. Please ask a question about flights, prices, routes, or travel dates.")
        return

    try:
        # Get the table info from the database
        table_info = db.get_table_info()

        # Create the input dictionary for the SQL prompt
        prompt_input = {
            "input": question,
            "top_k": 5,
            "table_info": table_info
        }

        # Print the complete SQL generation prompt
        print("\nComplete SQL Generation Prompt:")
        print("-" * 50)
        print(sql_prompt.format(**prompt_input))
        print("-" * 50)

        # Create the SQL chain
        sql_chain = create_sql_query_chain(llm=llm, db=db, prompt=sql_prompt)

        # Generate SQL query and clean it
        sql_query = await sql_chain.ainvoke({"question": question})
        # Clean the query by removing any markdown formatting
        cleaned_query = sql_query.strip('`').replace('sql\n', '').strip()
        print(f"\nGenerated SQL Query: {cleaned_query}")

        # Execute query and get results
        if cleaned_query:
            query_result = db.run(cleaned_query)

            # Print the complete response generation prompt
            print("\nComplete Response Generation Prompt:")
            print("-" * 50)
            response_input = {
                "question": question,
                "sql_query": cleaned_query,
                "query_result": query_result
            }
            print(response_prompt.format(**response_input))
            print("-" * 50)

            # Generate natural language response
            response = await llm.ainvoke(response_prompt.format(**response_input))
            print("\nFinal Response:")
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
