from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from sqlite import json_to_sqlite
from query_validator import is_flight_related_query
from llm import get_llm
from sql_prompt import sql_prompt
from response_prompt import response_prompt

# Database and LLM setup
url = 'sqlite:///flights.db'
engine = create_engine(url, echo=False)
db = SQLDatabase(engine)
llm = get_llm()


async def process_flight_query():
    question = input("Enter your question about flights: ")

    if not is_flight_related_query(question):
        print("\nQuery not related to flight data. Please ask a question about flights, prices, routes, or travel dates.")
        return

    try:
        sql_chain = create_sql_query_chain(llm=llm, db=db, prompt=sql_prompt)
        sql_query = await sql_chain.ainvoke({"question": question})

        def validate_sql_query(sql_query, expected_columns):
            for col in expected_columns:
                if col not in sql_query:
                    raise ValueError(f"Invalid SQL query: Missing column '{col}'")
            return sql_query

        expected_columns = ["date", "origin", "destination", "price_inr", "flightType"]
        cleaned_query = validate_sql_query(sql_query.strip('`').replace('sql\n', '').strip(), expected_columns)
        print(f"\nGenerated SQL Query: {cleaned_query}")

        if cleaned_query:
            query_result = db.run(cleaned_query)
            response_input = {
                "question": question,
                "sql_query": cleaned_query,
                "query_result": query_result
            }
            response = await llm.ainvoke(response_prompt.format(**response_input))
            print("\nFinal Response:")
            print(response.content)
        else:
            print("No SQL query was generated.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    import asyncio
    json_to_sqlite('flight_data.json', 'flights.db')
    while True:
        asyncio.run(process_flight_query())
        if input("\nDo you want to ask another question? (y/n): ").lower() != 'y':
            break