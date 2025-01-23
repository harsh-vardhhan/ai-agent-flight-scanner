import logging
from typing import List, Tuple
from sqlite3 import Error as SQLiteError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from query_validator import is_flight_related_query
from llm import get_llm
from sql_prompt import sql_prompt
from response_prompt import response_prompt
from verification_prompt import verification_prompt
from fastapi import FastAPI, HTTPException
from models import QueryRequest, QueryResponse
from clean_sql_query import clean_sql_query

app = FastAPI()



# Database and LLM setup
URL = 'sqlite:///flights.db'
engine = create_engine(URL, echo=False)
db = SQLDatabase(engine)
llm = get_llm('qwen2.5-coder:14b', platform_name='OLLAMA')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Maximum number of SQL generation attempts
MAX_ATTEMPTS = 3

async def verify_sql_query(question: str, sql_query: str) -> Tuple[bool, str]:
    """
    Use LLM to verify if the generated SQL query reasonably answers the user's question.
    Returns a tuple of (is_valid, explanation)
    """
    # Format the verification prompt
    formatted_prompt = verification_prompt.format(question=question, sql_query=sql_query)

    # Get the response from the LLM
    response = await llm.ainvoke(formatted_prompt)

    # Extract the decision and explanation
    lines = response.content.split('\n')
    explanation = '\n'.join(line for line in lines if not line.strip().upper() in ['VALID', 'INVALID'])
    is_valid = any('VALID' in line.upper() and not 'INVALID' in line.upper() for line in lines)

    return is_valid, explanation.strip()


class LoggingSQLChain:
    def __init__(self, chain, db):
        self.chain = chain
        self.db = db

    async def ainvoke(self, inputs):
        # Get the actual table info from the database
        table_info = self.db.get_table_info()
        
        # Format the prompt with all variables
        formatted_prompt = sql_prompt.format(
            input=inputs["question"],
            top_k=10,  # or whatever default you want
            table_info=table_info
        )
        
        # Log the fully formatted prompt
        logger.info("\n=== RUNTIME SQL PROMPT ===\n")
        logger.info(formatted_prompt)
        logger.info("\n=== END RUNTIME SQL PROMPT ===\n")
        
        return await self.chain.ainvoke(inputs)

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
        # Initialize SQL generation chain with logging wrapper
        sql_chain = create_sql_query_chain(llm=llm, db=db, prompt=sql_prompt)
        logging_chain = LoggingSQLChain(sql_chain, db)

        # Attempt SQL query generation with verification
        attempt = 0
        while attempt < MAX_ATTEMPTS:
            # Generate SQL query using logging chain
            sql_query = await logging_chain.ainvoke({"question": request.question})

            cleaned_query = validate_sql_query(
                clean_sql_query(sql_query),
                ["date", "origin", "destination", "price_inr", "flightType"]
            )

            # Verify the generated query
            is_valid, explanation = await verify_sql_query(request.question, cleaned_query)
            print(is_valid, attempt)

            if is_valid:
                break

            logging.warning("SQL validation failed (attempt %d/%d): %s", attempt + 1, MAX_ATTEMPTS, explanation)
            attempt += 1

            if attempt == MAX_ATTEMPTS:
                raise ValueError(f"Failed to generate valid SQL query after {MAX_ATTEMPTS} attempts. Last explanation: {explanation}")

        # Execute validated query
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
            final_response=response.content,
            sql_query=cleaned_query,
            validation_explanation=explanation
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except (SQLAlchemyError, SQLiteError) as e:
        logging.error("Database error: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") from e
    except Exception as e:
        logging.error("Internal server error: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e

async def get_table_info():
    """Get database schema information"""
    try:
        return db.get_table_info()
    except (SQLAlchemyError, SQLiteError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error accessing database schema: {str(e)}"
        ) from e

async def execute_query(query: str):
    """Execute SQL query and return results"""
    try:
        return db.run(query)
    except (SQLAlchemyError, SQLiteError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"SQL execution error: {str(e)}"
        ) from e

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
