from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from query_validator import is_flight_related_query
from llm import get_llm
from sql_prompt import sql_prompt
from response_prompt import response_prompt
from sqlite3 import Error as SQLiteError
from fastapi import FastAPI, HTTPException
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from models import QueryRequest, QueryResponse
import logging

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)


# Database and LLM setup
url = 'sqlite:///flights.db'
engine = create_engine(url, echo=False)
db = SQLDatabase(engine)
llm = get_llm()

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a flight-related query and return structured response including intermediate steps
    """
    if not request.question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    if not is_flight_related_query(request.question):
        raise HTTPException(
            status_code=400,
            detail="Query not related to flight data. Please ask about flights, prices, routes, or travel dates."
        )

    try:
        # Get table info and generate SQL prompt
        table_info = await get_table_info()
        formatted_sql_prompt = sql_prompt.format(
            input=request.question,
            top_k=5,
            table_info=table_info
        )

        # Generate SQL query
        sql_chain = create_sql_query_chain(llm=llm, db=db, prompt=sql_prompt)
        sql_query = await sql_chain.ainvoke({"question": request.question})

        # Validate and clean SQL query
        cleaned_query = validate_sql_query(
            sql_query.strip('`').replace('sql\n', '').strip(),
            ["date", "origin", "destination", "price_inr", "flightType"]
        )

        # Execute query
        query_results = await execute_query(cleaned_query)

        # Format results
        if isinstance(query_results, list) and len(query_results) == 0:
            formatted_results = "NONE"
        else:
            formatted_results = query_results

        # Generate natural language response
        response_input = {
            "question": request.question,
            "sql_query": cleaned_query,
            "query_result": formatted_results
        }
        formatted_response_prompt = response_prompt.format(**response_input)
        response = await llm.ainvoke(formatted_response_prompt)

        return QueryResponse(
            final_response=response.content
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except (SQLAlchemyError, SQLiteError) as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

async def get_table_info():
    """Get database schema information"""
    try:
        return db.get_table_info()
    except (SQLAlchemyError, SQLiteError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error accessing database schema: {str(e)}"
        )

async def execute_query(query: str):
    """Execute SQL query and return results"""
    try:
        return db.run(query)
    except (SQLAlchemyError, SQLiteError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"SQL execution error: {str(e)}"
        )

def validate_sql_query(sql_query: str, expected_columns: List[str]) -> str:
    """Validate SQL query for safety and completeness"""
    if not sql_query:
        raise ValueError("Empty SQL query received")
    
    sql_lower = sql_query.lower()
    forbidden_operations = ['insert', 'update', 'delete', 'drop', 'truncate']
    if any(keyword in sql_lower for keyword in forbidden_operations):
        raise ValueError("SQL query contains forbidden operations")
        
    for col in expected_columns:
        if col not in sql_query:
            raise ValueError(f"Invalid SQL query: Missing column '{col}'")
            
    return sql_query