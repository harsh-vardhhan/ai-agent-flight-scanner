from langchain.prompts import PromptTemplate

luggage_prompt = PromptTemplate(
    input_variables=["airline", "query", "relevant_text"],
    template="""
Based on the airline's official policy, here is the answer to the user's question:

Airline: {airline}
Policy Information: {relevant_text}

Response:
Provide only the relevant policy details in a direct and concise manner.
Do not include unnecessary introductions, explanations, or meta commentary.
Simply restate the policy information in a clear, user-friendly way.
"""
)
