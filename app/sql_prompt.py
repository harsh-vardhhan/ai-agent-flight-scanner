from langchain.prompts import PromptTemplate

sql_prompt = PromptTemplate(
    input_variables=["input", "top_k", "table_info"],
    template="""
Convert the user's flight search request into a comprehensive SQL query:

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

Query Generation Strategy:
1. Default to one-way flight search
2. ONLY generate round-trip query when EXPLICITLY requested with:
   - "round trip"
   - "return flight"
   - "both ways"

Query Generation Rules:
1. Validate route existence
2. Apply user-specified filters
3. If "cheapest" mentioned, sort by price
4. Limit to {top_k} total results
5. Strictly follow query type specification

Provide ONLY the complete SQL query addressing all requirements.
"""
)