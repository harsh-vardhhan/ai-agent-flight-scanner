from langchain.prompts import PromptTemplate

response_prompt = PromptTemplate(
    input_variables=["question", "sql_query", "query_result"],
    template="""Given the user's question: {question}

The SQL query used: {sql_query}

query_result used: {query_result}

Follow these steps exactly to create your response:

STEP 1: CREATE TABLE
Copy and use exactly this table format:
| Date | Time | Duration | Airline | Origin (Country) | Destination (Country) | Price (₹) | Type |
|------|------|----------|---------|-----------------|---------------------|----------:|------|

STEP 2: ADD FLIGHT DATA
For each flight row:
1. Date: Use YYYY-MM-DD format
2. Time: Use HH:MM - HH:MM format
3. Duration: Use XXh XXm format
4. Airline: Copy exactly as provided
5. Origin: Add country in brackets - Example: Delhi (India)
6. Destination: Add country in brackets - Example: Hanoi (Vietnam)
7. Price: Format the number with commas:
   - If price is 1000-9999: Add one comma - Example: ₹8,187
   - If price is 10000-99999: Add one comma - Example: ₹98,520
   - If price is 100000-999999: Add two commas - Example: ₹1,50,000
8. Type: Copy exactly as provided
9. Do not distort Price values in any way
"""
)