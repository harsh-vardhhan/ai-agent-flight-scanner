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

Return Flight Query Strategy:
1. If return flight requested, find:
   - Outbound route price (A to B)
   - Return route price (B to A)
2. Ensure flight exists in both directions
3. Match countries between routes
4. Allow date range for return flight

Query Generation Rules:
1. Validate both outbound and return routes
2. Apply all user-specified filters
3. If "cheapest" mentioned, sort by:
   - Outbound route price
   - Return route price
   - Total trip price
4. Limit to {top_k} total results
5. Prefer flights with similar characteristics

Display Requirements:
- Show separate prices for:
  1. Outbound flight (A to B)
  2. Return flight (B to A)
  3. Total trip price

Provide ONLY SQL query.
"""
)