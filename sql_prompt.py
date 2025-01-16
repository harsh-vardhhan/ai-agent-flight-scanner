from langchain.prompts import PromptTemplate

sql_prompt = PromptTemplate(
    input_variables=["input", "top_k", "table_info"],
    template="""Given the following input: {input}

Known cities and their variations:
Mumbai (bombay, bom)
New Delhi (delhi, del)
Da Nang (danang, dng)
Ho Chi Minh City (saigon, hcmc)
Hanoi (hanoi, han)
Phu Quoc (phuquoc, pq)

When processing flight search queries:
1. Match city names using the variations above
2. Convert all inputs to standard names
3. Handle case-insensitive matching
4. Handle partial matching
5. Handle common abbreviations
6. Handle common misspellings
7. Handle common aliases
9. Handle common short forms
10. Handle common acronyms
11. Handle common initials

For example:
- "bombay" should be treated as "Mumbai"
- "hcmc" should be treated as "Ho Chi Minh City"
- "delhi" should be treated as "New Delhi"

For the database with the following schema:
{table_info}

Generate a SQL query that:
1. Is valid SQLite syntax
2. Returns at most {top_k} results
3. ALWAYS explicitly specify columns instead of using *
4. ALWAYS include price_inr column when price information is relevant
5. Use a consistent column order: date, origin, destination, price_inr, flightType
6. Keep price_inr as raw integer values without any formatting
7. DO NOT modify or transform price values in the query
8. DO NOT introduce typos like 'price_inn' or any other variations. Only use 'price_inr'.
9. Returns **only the raw SQL query** without any explanation, formatting, or markdown.

When handling one-way flight queries:
1. The query should ONLY consider the requested direction (e.g., `origin` to `destination`).
2. DO NOT include logic for return flights.

When handling round-trip flight queries:
1. Always use a WITH clause to handle outbound and return flights separately
2. Always use DATE() function for calculating minimum return date
3. Always use UNION ALL to combine results
4. Always limit to exactly one flight in each direction
5. Always order by price_inr ASC

Ensure that:
- For one-way flights, there is no mention of return flights.
- For round-trip flights, both outbound and return flights are included as per the rules above.

Output ONLY the SQL query and nothing else.
"""
)

