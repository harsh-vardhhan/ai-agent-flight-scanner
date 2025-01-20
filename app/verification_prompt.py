from langchain.prompts import PromptTemplate

# Define the prompt template
verification_prompt = PromptTemplate(
    input_variables=["question", "sql_query"],
    template="""
    Analyze if this SQL query would provide information that reasonably answers the user's question. The query doesn't need to be perfect - it just needs to return data that would help answer the question.

    User's Question: "{question}"
    Generated SQL Query: {sql_query}

    Respond with VALID if SQL query is reasonable and would help answer the user's question.

    Respond with INVALID if SQL query is not reasonable or would not help answer the user's question.

    First explain your reasoning, then on a new line write either VALID or INVALID.
    """
)