from langchain.prompts import PromptTemplate

sql_prompt = PromptTemplate(
    input_variables=["input", "top_k", "table_info"],
    template="""
Convert the user's flight search request into a precise SQL query:

User Input: {input}
Top Results to Retrieve: {top_k}

Allowed Routes:
- New Delhi ↔ Phu Quoc
- New Delhi ↔ Da Nang
- New Delhi ↔ Hanoi
- New Delhi ↔ Ho Chi Minh City
- Mumbai ↔ Phu Quoc
- Mumbai ↔ Da Nang
- Mumbai ↔ Hanoi
- Mumbai ↔ Ho Chi Minh City

Database Schema:
{table_info}

Query Generation Rules:
1. Validate route exists in allowed routes
2. Apply all user-specified filters
3. If "cheapest" mentioned, sort by price ascending
4. Limit to {top_k} results

Provide ONLY the SQL query that fully addresses the requirements.
"""
)
