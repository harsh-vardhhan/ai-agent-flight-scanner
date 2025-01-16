from sqlite import json_to_sqlite
from query_chain import query_chain


if __name__ == "__main__":
    import asyncio

    # Initialize the database outside the loop
    json_to_sqlite('./data/flight_data.json', 'flights.db')

    # Create a single event loop for the entire session
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        while True:
            # Run the query in the existing event loop
            loop.run_until_complete(query_chain())
            
            if input("\nDo you want to ask another question? (y/n): ").lower() != 'y':
                break
    finally:
        # Clean up the event loop when done
        loop.close()