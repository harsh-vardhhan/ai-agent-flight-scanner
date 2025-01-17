# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import json_to_sqlite
from query_chain import process_query
from models import QueryRequest, QueryResponse
import uvicorn
from pathlib import Path

app = FastAPI(title="Flight Query API")

# Allow all origins (you can limit this to specific domains in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or list specific URLs like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Or limit to methods like ["GET", "POST"]
    allow_headers=["*"],  # Allow any headers
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup if it doesn't exist"""
    db_path = Path('flights.db')
    if not db_path.exists():
        print("Initializing database...")
        json_to_sqlite('./data/flight_data.json', 'flights.db')
        print("Database initialization complete")

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """Process a flight-related query"""
    return await process_query(request)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)