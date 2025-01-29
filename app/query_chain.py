import logging
import re
import json
from typing import List, Union, Tuple, AsyncGenerator
from sqlite3 import Error as SQLiteError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_core.messages import AIMessage
from query_validator import is_flight_related_query
from llm import get_llm
from fastapi import FastAPI, HTTPException
from clean_sql_query import clean_sql_query
from sql_prompt import sql_prompt
from verify_sql_prompt import verify_sql_prompt
from response_prompt import response_prompt

app = FastAPI()

# LLM setup
PLATFORM_NAME = 'GROQ'
MODEL_NAME = 'deepseek-r1-distill-llama-70b'
llm = get_llm(model_name=MODEL_NAME, platform_name=PLATFORM_NAME)

# Database setup
URL = 'sqlite:///flights.db'
engine = create_engine(URL, echo=False)
db = SQLDatabase(engine)

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Maximum number of SQL generation attempts
MAX_ATTEMPTS = 3

async def verify_sql_query(question: str, sql_query: str) -> Tuple[bool, str]:
    # Generate natural language response
    sql_verify_input = {
        "question": question,
        "sql_query": sql_query,
    }
    verification_prompt = verify_sql_prompt.format(**sql_verify_input)
    verification_response = await llm.ainvoke(verification_prompt)
    response_text = strip_think_tags(verification_response).strip().upper()

    if response_text.startswith("VALID"):
        return True, ""
    else:
        # Extract reason after "INVALID:"
        reason = response_text.split(":", 1)[1].strip() if ":" in response_text else "Query does not correctly answer the question"
        return False, reason

async def generate_and_verify_sql(question: str, attempt: int = 1) -> str:
    if attempt > MAX_ATTEMPTS:
        raise ValueError(f"Failed to generate valid SQL query after {MAX_ATTEMPTS} attempts")

    # Initialize SQL generation chain with logging wrapper
    sql_chain = create_sql_query_chain(llm=llm, db=db, prompt=sql_prompt)
    logging_chain = LoggingSQLChain(sql_chain, db)

    # Generate SQL query
    sql_query_response = await logging_chain.ainvoke({"question": question})
    sql_query = strip_think_tags(sql_query_response)
    cleaned_query = clean_sql_query(sql_query)

    # Verify the query
    is_valid, reason = await verify_sql_query(question, cleaned_query)

    if is_valid:
        logger.info("Valid SQL query generated on attempt %d", attempt)
        return cleaned_query
    else:
        logger.warning("Invalid SQL query on attempt %d. Reason: %s", attempt, reason)
        return await generate_and_verify_sql(question, attempt + 1)

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


async def stream_response(question: str) -> AsyncGenerator[str, None]:
    try:
        if not is_flight_related_query(question):
            yield json.dumps({
                "type": "error",
                "content": "Query not related to flight data. Please ask about flights, prices, routes, or travel dates."
            })
            return

        # Generate and verify SQL query
        cleaned_query = await generate_and_verify_sql(question)

        # Stream SQL query first
        yield json.dumps({
            "type": "sql",
            "content": cleaned_query
        })

        # Execute query
        query_results = await execute_query(cleaned_query)

        # Generate response using streaming
        response_input = {
            "question": question,
            "sql_query": cleaned_query,
            "query_result": query_results
        }
        formatted_response_prompt = response_prompt.format(**response_input)

        buffer = ""
        current_think = False

        # Stream the response chunks
        async for chunk in llm.astream(formatted_response_prompt):
            if isinstance(chunk, AIMessage):
                content = chunk.content
            else:
                content = str(chunk)

            # Check for think tags
            if '<think>' in content:
                current_think = True
                continue
            elif '</think>' in content:
                current_think = False
                continue

            # Skip content if we're inside think tags
            if current_think:
                continue

            # Add the chunk to buffer
            buffer += content

            # Check if we have complete words or punctuation
            if re.search(r'[.,!?\s]$', buffer):
                # Send the buffered content
                if buffer.strip():
                    yield json.dumps({
                        "type": "answer",
                        "content": buffer
                    })
                buffer = ""

        # Send any remaining buffered content
        if buffer.strip():
            yield json.dumps({
                "type": "answer",
                "content": buffer
            })

    except Exception as e:
        logger.error("Error in stream_response: %s", str(e))
        yield json.dumps({
            "type": "error",
            "content": str(e)
        })


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
