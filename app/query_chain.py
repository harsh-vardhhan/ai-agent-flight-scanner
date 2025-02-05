import re
import json
import asyncio
from typing import AsyncGenerator
from sqlite3 import Error as SQLiteError
from sqlalchemy.exc import SQLAlchemyError
from langchain_core.messages import AIMessage
from query_validator import is_flight_related_query, is_luggage_related_query
from luggage_extractor import extract_luggage_query
from fastapi import HTTPException
from response_prompt import response_prompt
from generate_and_verify_sql import generate_sql
from config import flight_llm, db, logger
from vector_db import search_policy
from util import parse_tuple_list
from airlines import VALID_AIRLINES

async def stream_response(question: str) -> AsyncGenerator[str, None]:
    try:
        if not is_flight_related_query(question):
            yield json.dumps({
                "type": "error",
                "content": "Query not related to flight data. Please ask about flights, prices, routes, or travel dates."
            })
            return

        # Step 1: Generate and verify SQL query
        cleaned_query = await generate_sql(question)

        # Step 2: Stream SQL query in chunks
        sql_chunks = [cleaned_query[i:i+10] for i in range(0, len(cleaned_query), 10)]
        for chunk in sql_chunks:
            yield json.dumps({
                "type": "sql",
                "content": chunk
            })
            await asyncio.sleep(0.05)

        # Step 3: Execute SQL query
        query_results_str = await execute_query(cleaned_query)

        # Step 4: Parse query results
        flight_data = parse_tuple_list(query_results_str)

        if not flight_data:
            yield json.dumps({
                "type": "error",
                "content": "No flights found for the given route."
            })
            return

        # Step 5: Extract valid airline names
        airline_names = {flight[1] for flight in flight_data if flight[1] in VALID_AIRLINES}

        # Step 6: Handle luggage-related queries
        luggage_policies = {}
        if is_luggage_related_query(question):
            luggage_query = await extract_luggage_query(question)
            if luggage_query:
                for airline in airline_names:
                    policy = await search_policy(airline, luggage_query)
                    luggage_policies[airline] = f"{policy} ({airline})"

        # Step 7: Generate response using streaming
        response_input = {
            "question": question,
            "sql_query": cleaned_query,
            "query_result": flight_data,
            "luggage_policies": luggage_policies
        }
        formatted_response_prompt = response_prompt.format(**response_input)

        buffer = ""
        current_think = False

        # Step 8: Stream AI-generated response
        async for chunk in flight_llm.astream(formatted_response_prompt):
            if isinstance(chunk, AIMessage):
                content = chunk.content
            else:
                content = str(chunk)

            if "<think>" in content:
                current_think = True
                continue
            elif "</think>" in content:
                current_think = False
                continue

            if current_think:
                continue

            buffer += content

            if re.search(r'[.,!?\s]$', buffer):
                if buffer.strip():
                    yield json.dumps({"type": "answer", "content": buffer})
                buffer = ""

        # Step 9: Append luggage policy at the end
        if luggage_policies:
            luggage_info = "\n\nLuggage Policies:\n" + "\n".join(
                [f"- {policy}" for policy in luggage_policies.values()]
            )
            yield json.dumps({"type": "answer", "content": luggage_info})

        # Send any remaining buffered content
        if buffer.strip():
            yield json.dumps({"type": "answer", "content": buffer})

    except Exception as e:
        logger.error("Error in stream_response: %s", str(e))
        yield json.dumps({"type": "error", "content": str(e)})

async def execute_query(query: str):
    """Execute SQL query and return results"""
    try:
        return db.run(query)
    except (SQLAlchemyError, SQLiteError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"SQL execution error: {str(e)}"
        ) from e