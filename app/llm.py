import os
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

def get_llm(model_name, platform_name="OLLAMA"):
    if platform_name == "GROQ":
        return ChatGroq(
            temperature=1,
            model=model_name,
            groq_api_key=os.environ["GROQ_API_KEY"]
        )
    elif platform_name == "OLLAMA":
        return ChatOllama(
            model=model_name,
            temperature=0.2,
        )
