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
        # Get table info for the prompt
        table_info = db.get_table_info()
        
        # Print the complete SQL generation prompt
        print("\n=== SQL Generation Prompt ===")
        formatted_sql_prompt = sql_prompt.format(
            input=question,
            top_k=5,  # or whatever your default top_k value is
            table_info=table_info
        )
        print(formatted_sql_prompt)
        
        sql_chain = create_sql_query_chain(llm=llm, db=db, prompt=sql_prompt)
        sql_query = await sql_chain.ainvoke({"question": question})
        
        print("\n=== Generated SQL Query ===")
        print(sql_query)

        def validate_sql_query(sql_query, expected_columns):
            for col in expected_columns:
                if col not in sql_query:
                    raise ValueError(f"Invalid SQL query: Missing column '{col}'")
            return sql_query

        expected_columns = ["date", "origin", "destination", "price_inr", "flightType"]
        cleaned_query = validate_sql_query(sql_query.strip('`').replace('sql\n', '').strip(), expected_columns)

        if cleaned_query:
            query_result = db.run(cleaned_query)
            
            # Print the SQL query results
            print("\n=== SQL Query Results ===")
            if isinstance(query_result, list):
                if len(query_result) == 0:
                    print("No results found")
                else:
                    # Print column headers
                    if isinstance(query_result[0], dict):
                        headers = list(query_result[0].keys())
                        print("Columns:", headers)
                        
                        # Print each row
                        print("\nRows:")
                        for row in query_result:
                            print(row)
                    else:
                        print("Raw results:", query_result)
            else:
                print("Raw results:", query_result)
            
            response_input = {
                "question": question,
                "sql_query": cleaned_query,
                "query_result": query_result
            }
            
            # Print the response generation prompt
            print("\n=== Response Generation Prompt ===")
            formatted_response_prompt = response_prompt.format(**response_input)
            print(formatted_response_prompt)
            
            response = await llm.ainvoke(formatted_response_prompt)
            print("\n=== LLM Response ===")
            print(response.content)
        else:
            print("No SQL query was generated.")

    except Exception as e:
        print(f"An error occurred: {e}")
        # Print more detailed error information
        import traceback
        print("\nDetailed error traceback:")
        print(traceback.format_exc())

if __name__ == "__main__":
    import asyncio

    # Initialize the database outside the loop
    json_to_sqlite('flight_data.json', 'flights.db')

    # Create a single event loop for the entire session
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        while True:
            # Run the query in the existing event loop
            loop.run_until_complete(process_flight_query())
            
            if input("\nDo you want to ask another question? (y/n): ").lower() != 'y':
                break
    finally:
        # Clean up the event loop when done
        loop.close()