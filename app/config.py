import logging
from llm import get_llm
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase

# LLM setup
flight_llm = get_llm(model_name='qwen/qwen3-32b', platform_name='GROQ')
luggage_llm = get_llm(model_name='llama-3.1-8b-instant', platform_name='GROQ')

# Database setup
URL = 'sqlite:///flights.db'
engine = create_engine(URL, echo=False)
db = SQLDatabase(engine)

# Maximum number of SQL generation attempts
MAX_ATTEMPTS = 3

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
