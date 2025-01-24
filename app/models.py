# models.py
from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    final_response: str
    sql_query: str
