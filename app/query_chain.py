import re
import json
from typing import AsyncGenerator
import asyncio
from sqlite3 import Error as SQLiteError
from sqlalchemy.exc import SQLAlchemyError
from langchain_core.messages import AIMessage
from query_validator import is_flight_related_query
from fastapi import HTTPException
from response_prompt import response_prompt
from generate_and_verify_sql import generate_sql
from config import llm, db, logger

"""
from vector_db import process_documents, search_policy, documents

# Run the async function
processed_data = asyncio.run(process_documents(documents))

query_result = asyncio.run(
    search_policy(
        "VietJet Air", 
        "which is the cheapest flight from New Delhi to Hanoi which allows most luggage?")
    )
"""

async def stream_response(question: str) -> AsyncGenerator[str, None]:
    try:
        if not is_flight_related_query(question):
            yield json.dumps({
                "type": "error",
                "content": "Query not related to flight data. Please ask about flights, prices, routes, or travel dates."
            })
            return

        # Generate and verify SQL query
        cleaned_query = await generate_sql(question)

        # Stream SQL query in chunks
        sql_chunks = [cleaned_query[i:i+10] for i in range(0, len(cleaned_query), 10)]
        for chunk in sql_chunks:
            yield json.dumps({
                "type": "sql",
                "content": chunk
            })
            await asyncio.sleep(0.05)  # Add small delay between chunks

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
