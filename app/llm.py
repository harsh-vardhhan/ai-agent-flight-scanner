import os
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

def get_llm(model_name, platform_name="OLLAMA"):
    if platform_name == "OLLAMA":
        return ChatOllama(
            model=model_name,
            temperature=0.2,
        )
    elif platform_name == "GROQ":
        return ChatGroq(
            temperature=1,
            model=model_name,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
