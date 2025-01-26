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
1. Default to one-way flight search.
2. ONLY generate round-trip query when EXPLICITLY requested with:
   - "round trip"
   - "return flight"
   - "both ways"

Query Generation Rules:
1. Validate the route existence (e.g., New Delhi ↔ Hanoi).
2. Apply user-specified filters, including price sorting if "cheapest" is mentioned.
3. If "round trip" or "both ways" is mentioned, ensure both outbound and return flight details are retrieved.
4. Display each individual column for the outbound and return flights:
    - Outbound Flight:
      - ID, Airline, Time, Date, Duration, Price (Price of the outbound flight)
    - Return Flight:
      - ID, Airline, Time, Date, Duration, Price (Price of the return flight)
    - Total Price: Sum of outbound and return flight prices.
    - Display separate columns for the **departure time** and **departure date** for both outbound and return flights.
5. Limit the number of results to {top_k} as specified by the user.

Provide ONLY the complete SQL query addressing all requirements. The SQL query should:
- Fetch the outbound and return flight details (ID, airline, time, date, duration, price).
- Show both outbound and return flight prices individually.
- Calculate the total price as the sum of both outbound and return flight prices.
- Include separate columns for the departure times and dates of both the outbound and return flights.
"""
)
