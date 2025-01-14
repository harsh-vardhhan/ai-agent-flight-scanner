from langchain.prompts import PromptTemplate

sql_prompt = PromptTemplate(
    input_variables=["input", "top_k", "table_info"],
    template="""Given the following input: {input}

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
8. **DO NOT introduce typos like 'price_inn' or any other variations. Only use 'price_inr'.**
9. Returns only the raw SQL query without any formatting or markdown

Example queries:
Good: SELECT date, origin, destination, price_inr, flightType FROM flights WHERE price_inr < 10000
Bad: SELECT date, origin, destination, price_inr/100 as price, flightType FROM flights

When handling round-trip flight queries:
1. Always use a WITH clause to handle outbound and return flights separately
2. Always use DATE() function for calculating minimum return date
3. Always use UNION ALL to combine results
4. Always limit to exactly one flight in each direction
5. Always order by price_inr ASC

Query:"""
)
