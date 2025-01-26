from langchain.prompts import PromptTemplate

response_prompt = PromptTemplate(
    input_variables=["question", "sql_query", "query_result"],
    template="""
Analyze flight data based on the following:

Query: {question}
SQL Query: {sql_query}
Results: {query_result}

Instructions:
- Create a markdown table ONLY with columns present in the data
- Format prices with ₹ and comma separators
- Highlight the cheapest option
- Provide a concise summary of key findings

Response Format:
### Flight Details

| Date | Airline | Origin | Destination | Origin Country | Destination Country | Departure Time | Duration | Flight Type | Price (₹) |
|------|---------|--------|-------------|---------------|---------------------|----------------|----------|-------------|------------|
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Summary:** [Concise overview of flight options]
"""
)