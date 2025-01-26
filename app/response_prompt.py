from langchain.prompts import PromptTemplate

response_prompt = PromptTemplate(
    input_variables=["question", "sql_query", "query_result"],
    template="""
Analyze flight data based on the following:

Query: {question}
SQL Query: {sql_query}
Results: {query_result}

Instructions:
- Create a markdown table with ALL these columns:
  1. Date
  2. Airline
  3. Origin
  4. Destination
  5. Origin Country
  6. Destination Country
  7. Departure Time
  8. Duration
  9. Flight Type
  10. Price (₹)
- Format prices with ₹ and comma separators
- For round trips, show both outbound and return flight details
- Highlight the cheapest option if applicable
- Provide a concise summary of key findings

Response Format:
### Flight Details

| Date | Airline | Origin | Destination | Origin Country | Destination Country | Departure Time | Duration | Flight Type | Price (₹) |
|------|---------|--------|-------------|---------------|---------------------|----------------|----------|-------------|------------|
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Summary:** [Concise overview of flight options]
"""
)
