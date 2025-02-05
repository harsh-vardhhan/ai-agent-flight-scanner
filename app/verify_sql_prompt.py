from langchain.prompts import PromptTemplate

# Define luggage-related keywords for reference in the prompt
LUGGAGE_KEYWORDS = [
    'luggage', 'baggage', 'bag', 'suitcase', 'carry-on',
    'carry on', 'check-in', 'checked bag', 'hand baggage',
    'weight', 'kg', 'kilos', 'pounds', 'lbs',
    'dimensions', 'size', 'allowance', 'restriction',
    'prohibited', 'forbidden', 'allowed', 'limit',
    'overweight', 'excess', 'cabin', 'hold', 'storage',
    'pack', 'bring', 'carry', 'transport', 'stow'
]

# Pre-format the luggage keywords string
LUGGAGE_KEYWORDS_STR = ", ".join(LUGGAGE_KEYWORDS)

verify_sql_prompt = PromptTemplate(
    input_variables=["question", "sql_query"],
    template=f"""
Given a user question and a generated SQL query, verify if the query correctly answers the flight-related aspects of the question.
Note: Luggage-related information (including {LUGGAGE_KEYWORDS_STR}) is stored in a separate system and should be ignored for SQL validation.

Follow these steps:
1. Identify if the question contains both flight and luggage-related queries
2. For validation, focus ONLY on the flight-related aspects:
   - Flight routes, schedules, prices, airlines
   - Ignore all luggage-related requirements as they're handled separately

Consider:
1. Does the query select all necessary flight-related information to answer the question?
   Example: If user asks "What's the cheapest flight from Delhi to Mumbai with baggage allowance?",
   only validate if the query gets flight price, route, and airline information.
   
2. Are the table joins and conditions correct for flight data?

3. Will the query return the flight data in a format that answers the user's question?
   Note: Luggage information will be added later from a different source.

User Question: {{question}}
Generated SQL Query: {{sql_query}}

Respond with either:
"VALID" if the query correctly answers the flight-related aspects of the question
OR
"INVALID: <reason>" if the query does not correctly answer the flight-related components.

Think carefully about your response.
"""
)