import logging
from llm import get_llm
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase

# LLM setup
PLATFORM_NAME = 'GROQ'
MODEL_NAME = 'deepseek-r1-distill-llama-70b'
llm = get_llm(model_name=MODEL_NAME, platform_name=PLATFORM_NAME)

# Database setup
URL = 'sqlite:///flights.db'
engine = create_engine(URL, echo=False)
db = SQLDatabase(engine)

# Maximum number of SQL generation attempts
MAX_ATTEMPTS = 3

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
