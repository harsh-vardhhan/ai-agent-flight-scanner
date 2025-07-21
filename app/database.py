import json
from sqlalchemy import create_engine, Column, String, Integer, REAL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 1. Define the Database Model (Table Structure)
Base = declarative_base()

class Flight(Base):
    __tablename__ = 'flights'
    
    uuid = Column(String, primary_key=True)
    airline = Column(String)
    date = Column(String)
    duration = Column(String)
    flightType = Column(String)
    price_inr = Column(Integer)
    origin = Column(String)
    destination = Column(String)
    originCountry = Column(String)
    destinationCountry = Column(String)
    link = Column(String)
    rainProbability = Column(REAL)
    freeMeal = Column(Integer)

def json_to_sqlite(json_file, sqlite_file):
    """
    Reads flight data from JSON and inserts it into a SQLite database using SQLAlchemy.
    """
    # 2. Setup Engine and Session
    engine = create_engine(f'sqlite:///{sqlite_file}')
    Base.metadata.create_all(engine)  # Creates the table if it doesn't exist
    
    Session = sessionmaker(bind=engine)
    session = Session()

    # Load JSON data
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file: {e}")
        return

    # 3. Insert Data using the ORM
    insert_count = 0
    for item in data:
        # Check if the record already exists to avoid trying to insert duplicates
        exists = session.query(Flight).filter_by(uuid=item['uuid']).first()
        if not exists:
            new_flight = Flight(**item) # Unpack dict to model attributes
            session.add(new_flight)
            insert_count += 1
    
    try:
        session.commit()
        print(f"Database operation complete. Inserted {insert_count} new records.")
    except Exception as e:
        print(f"A database error occurred: {e}")
        session.rollback()
    finally:
        session.close()
        print("Database connection closed.")