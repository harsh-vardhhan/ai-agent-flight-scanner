from langchain.prompts import PromptTemplate

sql_prompt = PromptTemplate(
    input_variables=["input", "top_k", "table_info"],
    template="""
Convert the user's flight search request into a comprehensive SQL query based on the rules below.

User Input: {input}
Top Results to Retrieve: {top_k}

Allowed Routes:
- New Delhi ↔ Hanoi
- New Delhi ↔ Ho Chi Minh City
- Mumbai ↔ Hanoi
- Mumbai ↔ Ho Chi Minh City
- Bangalore ↔ Ho Chi Minh City
- Kolkata ↔ Hanoi
- Kolkata ↔ Ho Chi Minh City
- Ahmedabad ↔ Hanoi
- Ahmedabad ↔ Ho Chi Minh City
- Ahmedabad ↔ Da Nang

Database Schema:
{table_info}

Query Generation Rules:
1.  **Column Selection:** Always select all available columns: `uuid, airline, date, duration, flightType, price_inr, origin, destination, link, rainProbability, freeMeal`.
2.  **Trip Type:** Default to a one-way flight search unless a round-trip is explicitly requested (e.g., "round trip," "return flight," "both ways"). For round-trip queries, you will need to construct two separate queries or a more complex join, but for this task, focus on generating the query for the outbound flight first.
3.  **Free Meal Filter:** If the user asks for a "free meal" or "included meal," add the condition `WHERE freeMeal = 1`.
4.  **Weather Filter:** If the user specifies a condition on rain or weather (e.g., "low chance of rain"), use the `rainProbability` column. For example, for a low chance of rain, you might use `WHERE rainProbability < 40`.
5.  **Direct Flights:** For "direct" or "non-stop" flight requests, match ANY of these values in the `flightType` column: 'Nonstop', 'Direct', 'Non-stop', 'Non stop', 'Direct flight'.
6.  **Sorting:** If the user asks for the "cheapest" or "best price," add `ORDER BY price_inr ASC`.
7.  **Limit:** Always limit the number of results to `{top_k}`.

STRICTLY output only the SQL query. Do not include any additional information, comments, or explanations.
"""
)
