from langchain.prompts import PromptTemplate

# Define the prompt template
verification_prompt = PromptTemplate(
    input_variables=["question", "sql_query"],
    template="""
    Compare the user's question with the generated SQL query and determine if executing this query would provide the information the user is asking for.

    User's Question: "{question}"
    Generated SQL Query: {sql_query}

    Think through this step by step:
    1. What specific information is the user asking for?
    2. What data would this SQL query return?
    3. Would the query results directly answer the user's question?

    If there's ANY mismatch between what the user wants to know and what this query would return, respond with INVALID.
    Only respond with VALID if executing this query would give exactly the information needed to answer the user's question.

    First explain your reasoning, then on a new line write either VALID or INVALID.
    """
)
