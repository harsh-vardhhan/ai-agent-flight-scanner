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
1. Strictly match user-specified route
2. For A to B return:
   - Find flights from A to B
   - Find corresponding return flights from B to A
3. Do NOT search for alternate route combinations

Query Generation Rules:
1. Validate route existence
2. Apply user-specified filters
3. If "cheapest" mentioned, sort by price
4. Limit to {top_k} total results
5. Ensure chronological date order

Advanced Filtering:
- Enforce unique flight combinations
- Ensure minimum/maximum date gaps if specified
- Prioritize direct routes

Provide ONLY the complete SQL query addressing all requirements.
"""
)