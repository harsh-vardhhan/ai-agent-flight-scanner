import logging
from llm import get_llm
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase

# LLM setup
flight_llm = get_llm(model_name='deepseek-r1-distill-llama-70b', platform_name='GROQ')
luggage_llm = get_llm(model_name='llama3.2:3b', platform_name='OLLAMA')

# Database setup
URL = 'sqlite:///flights.db'
engine = create_engine(URL, echo=False)
db = SQLDatabase(engine)

# Maximum number of SQL generation attempts
MAX_ATTEMPTS = 3

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
