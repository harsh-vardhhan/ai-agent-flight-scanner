import sqlite3
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from database import json_to_sqlite
from query_chain import process_query
from models import QueryRequest, QueryResponse

# Initialize the FastAPI app
app = FastAPI(title="Flight Query API")

# Allow all origins (you can limit this to specific domains in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or list specific URLs like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Or limit to methods like ["GET", "POST"]
    allow_headers=["*"],  # Allow any headers
)

# Event handlers for startup and shutdown
@app.on_event("startup")
async def startup_event():
    db_path = Path('./flights.db')
    # Check if database file exists and is empty
    if is_database_empty(db_path):
        json_to_sqlite('./data/flight_data.json', './flights.db')

def is_database_empty(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if flights table exists first
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='flights'")
        table_exists = cursor.fetchone() is not None

        if not table_exists:
            return True

        # If table exists, check number of rows
        cursor.execute("SELECT COUNT(*) FROM flights")
        row_count = cursor.fetchone()[0]

        return row_count == 0

    except sqlite3.Error as e:
        print(f"Error checking database: {e}")
        return True
    finally:
        conn.close()

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """Process a flight-related query"""
    return await process_query(request)

if __name__ == "__main__":
    # Run the application using uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
