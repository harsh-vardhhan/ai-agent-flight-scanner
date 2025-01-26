from langchain.prompts import PromptTemplate

response_prompt = PromptTemplate(
    input_variables=["question", "sql_query", "query_result"],
    template="""
Analyze flight data based on the following:

Query: {question}
SQL Query: {sql_query}
Results: {query_result}

Instructions:
- Create a markdown table ONLY with columns present in the data.
- Format prices with ₹ and comma separators.
- If round-trip data is provided and the total price is specified, calculate outbound and return prices as half the total price (unless explicitly provided).
- Ensure the "Total Price" is displayed accurately and is NOT doubled.
- If only one-way data is available, exclude return and total price columns.
- Highlight the cheapest option in the table using bold formatting for the row.
- Provide a concise summary of key findings.

Response Format:
### Flight Details

If both outbound and return flights are available:
| Date (Outbound) | Date (Return) | Airline | Origin | Destination | Departure Time (Outbound) | Duration (Outbound) | Return Time | Duration (Return) | Outbound Price (₹) | Return Price (₹) | Total Price (₹) |
|------------------|---------------|---------|--------|-------------|---------------------------|---------------------|-------------|-------------------|---------------------|------------------|-----------------|
| ...              | ...           | ...     | ...    | ...         | ...                       | ...                 | ...         | ...               | ₹...,...            | ₹...,...         | ₹...,...         |

If only one-way flights are available:
| Date | Airline | Origin | Destination | Departure Time | Duration | Flight Type | Price (₹) |
|------|---------|--------|-------------|----------------|----------|-------------|-----------|
| ...  | ...     | ...    | ...         | ...            | ...      | ...         | ₹...,...  |

**Summary:** [Concise overview of flight options]
"""
)
