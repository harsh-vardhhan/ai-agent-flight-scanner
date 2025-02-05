from typing import Optional
from config import luggage_llm

async def extract_luggage_query(user_query: str) -> Optional[str]:
    """
    Extract the specific luggage-related question from a user query using LLM.
    Returns None if no luggage-related question is found.
    """
    prompt = f"""
    Extract the specific luggage-related question from the following query. 
    If there's no luggage-related question, return "NONE".
    Focus on aspects like weight limits, size restrictions, prohibited items, or general baggage policies.
    
    Example inputs and outputs:
    Input: "What's the price of flights from Delhi to Mumbai and what's the baggage allowance?"
    Output: "what's the baggage allowance"
    
    Input: "How much does a ticket cost from Bangkok to Hanoi?"
    Output: "NONE"
    
    Input: "Can I bring a 25kg suitcase on VietJet Air?"
    Output: "Can I bring a 25kg suitcase"
    
    Now process this query: {user_query}
    Return only the extracted question or "NONE", without any additional text or explanation.
    """

    response = await luggage_llm.ainvoke(prompt)
    extracted = response.content.strip()

    return None if extracted == "NONE" else extracted
