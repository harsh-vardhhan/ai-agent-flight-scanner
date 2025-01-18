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

Known countries and their variations:
India (ind, in)
Vietnam (viet, vn)

When processing flight search queries:
1. Match city names using the variations above
2. Match country names using the variations above
3. Convert all inputs to standard names
4. Handle case-insensitive matching
5. Handle partial matching
6. Handle common abbreviations
7. Handle common misspellings
8. Handle common aliases
9. Handle common short forms
10. Handle common acronyms
11. Handle common initials

For example:
- "bombay" should be treated as "Mumbai"
- "hcmc" should be treated as "Ho Chi Minh City"
- "delhi" should be treated as "New Delhi"
- "ind" should be treated as "India"
- "viet" should be treated as "Vietnam"

For the database with the following schema:
{table_info}

Generate a SQL query that:
1. Is valid SQLite syntax
2. Returns at most {top_k} results
3. ALWAYS explicitly specify columns instead of using *
4. Include ALL relevant columns: date, time, duration, airline, origin, destination, originCountry, destinationCountry, price_inr, flightType
5. Use a consistent column order: date, time, duration, airline, origin, destination, originCountry, destinationCountry, price_inr, flightType
6. Keep price_inr as raw integer values without any formatting
7. DO NOT modify or transform price values in the query
8. DO NOT introduce typos in column names
9. Returns **only the raw SQL query** without any explanation, formatting, or markdown

When handling time-based queries:
1. Use proper time comparison with the 'time' column
2. Handle time ranges appropriately (morning: 06:00-12:00, afternoon: 12:00-18:00, evening: 18:00-24:00, night: 00:00-06:00)
3. Use proper duration parsing when filtering by flight duration

When handling one-way flight queries:
1. The query should ONLY consider the requested direction (e.g., `origin` to `destination`)
2. DO NOT include logic for return flights
3. Allow filtering by:
   - Specific dates or date ranges
   - Time of day preferences
   - Maximum duration
   - Specific airlines
   - Direct flights vs connections
   - Price ranges
   - Countries

When handling round-trip flight queries:
1. Always use a WITH clause to handle outbound and return flights separately
2. Always use DATE() function for calculating minimum return date
3. Always use UNION ALL to combine results
4. Always limit to exactly one flight in each direction
5. Always order by total price (sum of outbound and return price_inr) ASC
6. Ensure matching countries in both directions
7. Allow all the same filters as one-way flights

Additional Requirements:
1. When filtering by airline, use case-insensitive matching
2. When filtering by flight type, handle both "Direct" and "X Stop" variations
3. When comparing dates, always use DATE() function
4. When filtering by duration, parse the duration string properly
5. When filtering by country, check both originCountry and destinationCountry
6. When sorting by multiple criteria, always include price_inr as the final tiebreaker

Output ONLY the SQL query and nothing else.
"""
)