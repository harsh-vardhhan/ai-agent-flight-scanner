from langchain.prompts import PromptTemplate

response_prompt = PromptTemplate(
    input_variables=["question", "sql_query", "query_result"],
    template="""Given the user's question: {question}

The SQL query used: {sql_query}

And the query results: {query_result}

IMPORTANT FORMATTING REQUIREMENTS:

1. Table Format:
   - ALWAYS use markdown table format with | separators
   - Include header row and separator row
   - Right-align price column
   Example:
   | Date | Origin | Destination | Price (₹) | Type |
   |------|--------|------------|----------:|------|
   | 2024-01-15 | Delhi | Mumbai | ₹5,000 | Direct |

2. Price Formatting Rules:
   - Format raw price_inr values as follows:
     * For 4 digits (1000-9999): ₹X,XXX (e.g., 5000 → ₹5,000)
     * For 5 digits (10000-99999): ₹XX,XXX (e.g., 15000 → ₹15,000)
     * For 6 digits (100000-999999): ₹X,XX,XXX (e.g., 150000 → ₹1,50,000)
   - DO NOT add extra digits or commas
   - Examples of correct formatting:
     * 9852 → ₹9,852 (not ₹9,85,252)
     * 98520 → ₹98,520 (not ₹9,85,200)
   - Use exact values from price_inr without modification

3. Column Order:
   - Date (YYYY-MM-DD format)
   - Origin
   - Destination
   - Price (₹)
   - Type

4. Response Structure:
   - Brief answer first
   - Data table
   - Concise analysis of prices, dates, and flight types
   - Clear and conversational tone

Remember:
- Keep raw price values exactly as provided
- Double-check price formatting
- Never add extra digits to prices
- Verify table format before responding

Response:"""
)