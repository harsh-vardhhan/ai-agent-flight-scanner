from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
import os

def get_llm():
    model = "OLLAMA"
    if model == 'GROQ':
        return ChatGroq(
            temperature=1,
            model_name="llama-3.3-70b-versatile",
            groq_api_key=os.environ["GROQ_API_KEY"]
        )
    elif model == 'OLLAMA':
        return ChatOllama(
            model="phi4:latest",
            temperature=1,
        )