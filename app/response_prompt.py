from langchain.prompts import PromptTemplate

response_prompt = PromptTemplate(
    input_variables=["question", "sql_query", "query_result"],
    template="""
Analyze flight data based on the following:

Query: {question}
SQL Query: {sql_query}
Results: {query_result}

Instructions:
- Create a markdown table with columns:
  1. Outbound Date
  2. Outbound Airline
  3. Origin
  4. Destination
  5. Outbound Departure Time
  6. Outbound Duration
  7. Return Date
  8. Return Airline
  9. Return Origin
  10. Return Destination
  11. Return Departure Time
  12. Return Duration
  13. Outbound Price (₹)
  14. Return Price (₹)
  15. Total Trip Price (₹)
- Format prices with ₹ and comma separators
- Highlight the cheapest option
- Provide a concise summary of key findings

Response Format:
### Flight Details

| Outbound Date | Outbound Airline | Origin | Destination | Outbound Departure | Outbound Duration | Return Date | Return Airline | Return Origin | Return Destination | Return Departure | Return Duration | Outbound Price (₹) | Return Price (₹) | Total Trip Price (₹) |
|--------------|-----------------|--------|-------------|-------------------|-------------------|-------------|---------------|--------------|---------------------|-----------------|-----------------|-------------------|-----------------|---------------------|
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Summary:** [Concise overview of flight options]
"""
)