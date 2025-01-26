from langchain.prompts import PromptTemplate
sql_prompt = PromptTemplate(
    input_variables=["input", "top_k", "table_info"],
    template="""
Convert the user's flight search request into a comprehensive SQL query:

User Input: {input}
Top Results to Retrieve: {top_k}

Required Output Columns:
1. airline
2. departure_time
3. date
4. duration
5. flight_type
6. price_inr
7. origin
8. destination
9. origin_country
10. destination_country

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

Flight Query Strategy:
1. Distinguish between one-way and round-trip requests
2. If one-way flight requested:
   - Return outbound route details
3. If round-trip explicitly mentioned:
   - Find outbound route (A to B)
   - Find return route (B to A)

Query Generation Rules:
1. Validate route existence
2. Apply all user-specified filters
3. If "cheapest" mentioned, sort by price
4. Limit to {top_k} total results
5. Ensure all specified columns are returned

Keywords to Detect Round Trip:
- "round trip"
- "return flight"
- "both ways"

Provide ONLY the complete SQL query addressing all requirements.
"""
)