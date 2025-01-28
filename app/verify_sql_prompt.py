from langchain.prompts import PromptTemplate

verify_sql_prompt = PromptTemplate(
    input_variables=["question", "sql_query"],
    template="""
Given a user question and a generated SQL query, verify if the query correctly answers the question.
Consider:
1. Does the query select all necessary information to answer the question?
2. Are the table joins and conditions correct?
3. Will the query return the data in a format that answers the user's question?

User Question: {question}
Generated SQL Query: {sql_query}

Respond with either:
"VALID" if the query correctly answers the question
OR
"INVALID: <reason>" if the query does not correctly answer the question.

Think carefully about your response.
""",
)
