import os
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_openai.chat_models.base import BaseChatOpenAI

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
    elif platform_name == 'DEEPSEEK':
        return BaseChatOpenAI(
            model=model_name,
            openai_api_key=os.environ["OPENAI_API_KEY"],
            openai_api_base='https://api.deepseek.com',
            max_tokens=1024
        )
