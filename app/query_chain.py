from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from query_validator import is_flight_related_query
from llm import get_llm
from sql_prompt import sql_prompt
from response_prompt import response_prompt
from sqlalchemy.exc import SQLAlchemyError
from sqlite3 import Error as SQLiteError

# Database and LLM setup
url = 'sqlite:///flights.db'
engine = create_engine(url, echo=False)
db = SQLDatabase(engine)
llm = get_llm()

async def query_chain():
    question = input("Enter your question about flights: ")

    if not is_flight_related_query(question):
        print("\nQuery not related to flight data. Please ask a question about flights, prices, routes, or travel dates.")
        return

    try:
        # Get table info for the prompt
        try:
            table_info = db.get_table_info()
        except (SQLAlchemyError, SQLiteError) as e:
            print(f"\nError accessing database schema: {str(e)}")
            return
        
        # Print the complete SQL generation prompt
        print("\n=== SQL Generation Prompt ===")
        formatted_sql_prompt = sql_prompt.format(
            input=question,
            top_k=5,
            table_info=table_info
        )
        print(formatted_sql_prompt)
        
        try:
            sql_chain = create_sql_query_chain(llm=llm, db=db, prompt=sql_prompt)
            sql_query = await sql_chain.ainvoke({"question": question})
        except Exception as e:
            print(f"\nError generating SQL query: {str(e)}")
            return
        
        print("\n=== Generated SQL Query ===")
        print(sql_query)

        def validate_sql_query(sql_query, expected_columns):
            if not sql_query:
                raise ValueError("Empty SQL query received")
            
            sql_lower = sql_query.lower()
            if any(keyword in sql_lower for keyword in ['insert', 'update', 'delete', 'drop', 'truncate']):
                raise ValueError("SQL query contains forbidden operations")
                
            for col in expected_columns:
                if col not in sql_query:
                    raise ValueError(f"Invalid SQL query: Missing column '{col}'")
            return sql_query

        try:
            expected_columns = ["date", "origin", "destination", "price_inr", "flightType"]
            cleaned_query = validate_sql_query(sql_query.strip('`').replace('sql\n', '').strip(), expected_columns)
        except ValueError as e:
            print(f"\nSQL validation error: {str(e)}")
            return

        if cleaned_query:
            try:
                query_result = db.run(cleaned_query)
            except (SQLAlchemyError, SQLiteError) as e:
                print(f"\nSQL execution error: {str(e)}")
                print("\nThe generated SQL query may be invalid or incompatible with the database schema.")
                return
            
            # Print the SQL query results
            print("\n=== SQL Query Results ===")
            if isinstance(query_result, list):
                if len(query_result) == 0:
                    query_result = "NONE"
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
            
            try:
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
            except Exception as e:
                print(f"\nError generating response: {str(e)}")
        else:
            print("No SQL query was generated.")

    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        # Print more detailed error information in development environment only
        import traceback
        print("\nDetailed error traceback:")
        print(traceback.format_exc())