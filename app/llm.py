import os
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_openai.chat_models.base import BaseChatOpenAI
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
    elif platform_name == 'DEEPSEEK':
        return BaseChatOpenAI(
            model=model_name,
            openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
            openai_api_base='https://api.deepseek.com',
            max_tokens=1024
        )
