from langchain.prompts import PromptTemplate

response_prompt = PromptTemplate(
    input_variables=["question", "sql_query", "query_result"],
    template="""
Analyze flight data based on the following:

Query: {question}
SQL Query: {sql_query}
Results: {query_result}

Instructions:
- If results exist, create a markdown table which informs Date, Origin, Destination, Price, FlightType of outbound and return flights
- Format prices with ₹ and comma separators
- Provide a brief summary of the results

Response:"""
)