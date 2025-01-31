import re
from typing import Union
from langchain_core.messages import AIMessage

def strip_think_tags(response: Union[str, AIMessage]) -> str:
    """
    Remove <think> tags and their content from the response
    Handles both string and AIMessage type responses
    """
    # If response is an AIMessage, extract its content
    if isinstance(response, AIMessage):
        response_content = response.content
    elif isinstance(response, str):
        response_content = response
    else:
        response_content = str(response)

    # Remove <think> tags and their content using regex
    clean_content = re.sub(r'<think>.*?</think>', '', response_content, flags=re.DOTALL).strip()

    return clean_content
