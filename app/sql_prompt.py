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

Query Generation Rules:
1. Default to one-way flight search unless round-trip is explicitly requested
2. Only generate round-trip queries when the user explicitly mentions:
   - "round trip"
   - "return flight"
   - "both ways"
   - Specifies both departure and return dates
3. For one-way flights:
   - Include: flight ID, airline, departure time, date, duration, and price
   - Do not join with return flights
4. For round-trip requests only:
   - Include details for both outbound and return flights
   - Calculate total price as sum of both flights
5. Apply any user-specified filters (e.g., sort by price if "cheapest" mentioned)
6. Limit results to {top_k}

Strictly only output SQL.
"""
)