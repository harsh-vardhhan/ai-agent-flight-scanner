import logging
import re
from typing import List, Union
from sqlite3 import Error as SQLiteError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_core.messages import AIMessage
from query_validator import is_flight_related_query
from llm import get_llm
from sql_prompt import sql_prompt
from response_prompt import response_prompt
from fastapi import FastAPI, HTTPException
from models import QueryRequest, QueryResponse
from clean_sql_query import clean_sql_query

app = FastAPI()

# LLM setup
PLATFORM_NAME = 'GROQ'
MODEL_NAME = 'deepseek-r1-distill-llama-70b'
llm = get_llm(model_name=MODEL_NAME, platform_name=PLATFORM_NAME)

# Database setup
URL = 'sqlite:///flights.db'
engine = create_engine(URL, echo=False)
db = SQLDatabase(engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Maximum number of SQL generation attempts
MAX_ATTEMPTS = 3

def strip_think_tags(response: Union[str, AIMessage]) -> str:
    """
    Remove <think> tags and their content from the response
    Handles both string and AIMessage type responses
    """
    # If response is an AIMessage, extract its content
    if isinstance(response, AIMessage):
        response_content = response.content
    elif isinstance(response, str):
        response_content = response
    else:
        response_content = str(response)

    # Remove <think> tags and their content using regex
    clean_content = re.sub(r'<think>.*?</think>', '', response_content, flags=re.DOTALL).strip()

    return clean_content

class LoggingSQLChain:
    def __init__(self, chain, _db):
        self.chain = chain
        self.db = _db

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
    if not request.question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    if not is_flight_related_query(request.question):
        raise HTTPException(
            status_code=400,
            detail="Query not related to flight data." \
            "Please ask about flights, prices, routes, or travel dates."
        )

    try:
        # Initialize SQL generation chain with logging wrapper
        sql_chain = create_sql_query_chain(llm=llm, db=db, prompt=sql_prompt)
        logging_chain = LoggingSQLChain(sql_chain, db)
        sql_query_response = await logging_chain.ainvoke({"question": request.question})

        print('=== SQL QUERY RESPONSE ===')
        print(sql_query_response)

        # Ensure SQL query is stripped of any potential <think> tags
        sql_query = strip_think_tags(sql_query_response)

        print('=== SQL QUERY ===')
        print(sql_query)

        cleaned_query = clean_sql_query(sql_query)

        print('=== CLEANED QUERY ===')
        print(cleaned_query)

        # Execute validated query
        query_results = await execute_query(cleaned_query)

        print('=== QUERY RESULTS ===')
        print(query_results)

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

        # Strip <think> tags from the response
        cleaned_response_content = strip_think_tags(response)

        return QueryResponse(
            final_response=cleaned_response_content,
            sql_query=cleaned_query,
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
