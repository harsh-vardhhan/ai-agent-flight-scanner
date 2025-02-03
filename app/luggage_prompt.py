from langchain.prompts import PromptTemplate

luggage_prompt = PromptTemplate(
    input_variables=["airline", "query", "relevant_text"],
    template="""
Given the following airline policy information and user question, generate a clear, 
concise, and friendly response. Focus only on answering the specific question asked.

Airline: {airline}
User Question: {query}
Policy Information: {relevant_text}

Instructions:
1. Answer directly and conversationally
2. Include only relevant information from the policy
3. If specific numbers or limits are mentioned in the policy, include them
4. If any information is missing, acknowledge that
5. Keep the response concise but complete

Response:
"""
)
