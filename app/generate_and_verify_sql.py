from typing import Tuple
from langchain.chains import create_sql_query_chain # pylint: disable=no-name-in-module
from clean_sql_query import clean_sql_query
from sql_prompt import sql_prompt
from verify_sql_prompt import verify_sql_prompt
from strip_think_tags import strip_think_tags
from config import flight_llm, db, MAX_ATTEMPTS, logger

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

async def verify_sql(question: str, sql_query: str) -> Tuple[bool, str]:
    # Generate natural language response
    sql_verify_input = {
        "question": question,
        "sql_query": sql_query,
    }
    verification_prompt = verify_sql_prompt.format(**sql_verify_input)
    verification_response = await flight_llm.ainvoke(verification_prompt)
    response_text = strip_think_tags(verification_response).strip().upper()

    if response_text.startswith("VALID"):
        return True, ""
    else:
        # Extract reason after "INVALID:"
        if ":" in response_text:
            reason = response_text.split(":", 1)[1].strip()
        else:
            reason = "Query does not correctly answer the question"
        return False, reason

async def generate_sql(question: str, attempt: int = 1) -> str:
    if attempt > MAX_ATTEMPTS:
        raise ValueError(f"Failed to generate valid SQL query after {MAX_ATTEMPTS} attempts")

    # Initialize SQL generation chain with logging wrapper
    sql_chain = create_sql_query_chain(llm=flight_llm, db=db, prompt=sql_prompt)
    logging_chain = LoggingSQLChain(sql_chain, db)

    # Generate SQL query
    sql_query_response = await logging_chain.ainvoke({"question": question})
    sql_query = strip_think_tags(sql_query_response)
    cleaned_query = clean_sql_query(sql_query)

    # Verify the query
    is_valid, reason = await verify_sql(question, cleaned_query)

    if is_valid:
        logger.info("Valid SQL query generated on attempt %d", attempt)
        return cleaned_query
    else:
        logger.warning("Invalid SQL query on attempt %d. Reason: %s", attempt, reason)
        return await generate_sql(question, attempt + 1)
