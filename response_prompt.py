from langchain.prompts import PromptTemplate

response_prompt = PromptTemplate(
    input_variables=["question", "sql_query", "query_result"],
    template="""Given the user's question: {question}

The SQL query used: {sql_query}

And the query results: {query_result}

IMPORTANT FORMATTING REQUIREMENTS:

1. Empty Result Handling:
   - If query_result is empty or nothing ([] or ""), respond with:
     "No flights found matching your search criteria."
   - Do not generate any table or analysis for empty results
   - Do not hallucinate or make up any flight data

2. Table Format (ONLY if results exist):
   - ALWAYS use markdown table format with | separators
   - Include header row and separator row
   - Right-align price column
   Example:
   | Date | Origin | Destination | Price (₹) | Type |
   |------|--------|------------|----------:|------|
   | 2024-01-15 | Delhi | Mumbai | ₹5,000 | Direct |

3. Price Formatting Rules (when results exist):
   - Format raw price_inr values as follows:
     * For 4 digits (1000-9999): ₹X,XXX (e.g., 5000 → ₹5,000)
     * For 5 digits (10000-99999): ₹XX,XXX (e.g., 15000 → ₹15,000)
     * For 6 digits (100000-999999): ₹X,XX,XXX (e.g., 150000 → ₹1,50,000)
   - DO NOT add extra digits or commas
   - Examples of correct formatting:
     * 9852 → ₹9,852 (not ₹9,85,252)
     * 98520 → ₹98,520 (not ₹9,85,200)
   - Use exact values from price_inr without modification

4. Column Order (when results exist):
   - Date (YYYY-MM-DD format)
   - Origin
   - Destination
   - Price (₹)
   - Type

5. Response Structure:
   - For results found:
     * Brief answer first
     * Data table
     * Concise analysis of prices, dates, and flight types
     * Clear and conversational tone
   - For empty results:
     * Only the "No flights found" message
     * Optional: Suggest checking alternative dates or routes if appropriate

Remember:
- NEVER create fake data when no results are found
- Keep raw price values exactly as provided
- Double-check price formatting
- Never add extra digits to prices
- Verify table format before responding
- Only include table and analysis when actual results exist

Response:"""
)