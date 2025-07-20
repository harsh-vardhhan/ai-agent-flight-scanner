from langchain.prompts import PromptTemplate

response_prompt = PromptTemplate(
    input_variables=["question", "sql_query", "query_result"],
    template="""
Analyze flight data based on the following:

User Query: {question}
SQL Query Generated: {sql_query}
SQL Query Result: {query_result}

Instructions:
- First, check if 'query_result' is empty or None. If it is, respond with "No flight data available for this query." and nothing else.
- If data exists, format the results as a series of cards, with each card representing one flight. Separate cards with a horizontal rule (`---`).
- Format prices with a '₹' symbol and comma separators (e.g., ₹32,621).
- For the 'freeMeal' column, display "Yes" if the value is 1/True and "No" if it is 0/False.
- For the 'rainProbability' column, display the value as a percentage (e.g., 52.58%).
- For the 'link' column, create a clickable markdown link with the text "Book Now".
- Highlight the single cheapest option by adding "**(Cheapest)**" next to the airline and bolding the price.
- Provide a concise summary of the key findings (like the cheapest flight, availability of meals, or weather conditions) ONLY if data exists.

Response Format:

If no data is found:
No flight data available for this query.

---

If data exists (example for one-way flights):
### Flight Options

---
**✈️ [Airline Name]**
- **Route:** [Origin] → [Destination]
- **Date:** [Date]
- **Price:** ₹[Price]
- **Duration:** [Duration]
- **Details:** [Flight Type], Free Meal ([Yes/No])
- **Weather:** [value]% chance of rain
- **[Book Now]([link])**
---
**✈️ [Airline Name] (Cheapest)**
- **Route:** [Origin] → [Destination]
- **Date:** [Date]
- **Price:** **₹[Price]**
- **Duration:** [Duration]
- **Details:** [Flight Type], Free Meal ([Yes/No])
- **Weather:** [value]% chance of rain
- **[Book Now]([link])**
---

**Summary:** [Your concise overview of the flight options, highlighting the best choice based on the user's query. For example: "The cheapest flight is with Vietnam Airlines on July 21st for ₹32,621. This is a direct flight and includes a free meal, though there is a 52% chance of rain."]

Note: All data displayed must be exclusively from the 'query_result'. Do not show any placeholder or example data in the final response.
"""
)
