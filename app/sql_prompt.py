from langchain.prompts import PromptTemplate

sql_prompt = PromptTemplate(
    input_variables=["input", "top_k", "table_info"],
    template="""Given the following input: {input}

Known cities and their variations:
Mumbai (bombay, bom)
New Delhi (delhi, del)
Da Nang (danang, dng)
Ho Chi Minh City (saigon, hcmc)
Hanoi (hanoi, han)
Phu Quoc (phuquoc, pq)

Known countries and their variations:
India (ind, in)
Vietnam (viet, vn)

For the database with the following schema:
{table_info}

Generate a SQL query that:
1. Is valid SQLite syntax.
2. ONLY includes SQL code without any additional explanation, formatting, or natural language text.
3. Returns at most {top_k} results.
4. Always explicitly specifies columns instead of using *.
5. Includes the following columns in this order: id, airline, time, date, duration, flightType, price_inr, origin, destination, originCountry, destinationCountry.
6. Does NOT modify or format `price_inr` values.
7. Properly matches inputs like origin, destination, and other filters using case-insensitive comparisons.
8. Properly handles partial matches for city or country variations.

### Examples

1. For "What is the cheapest flight from New Delhi to Hanoi?":
   SELECT id, airline, time, date, duration, flightType, price_inr, origin, destination, originCountry, destinationCountry
   FROM flights
   WHERE origin = 'New Delhi' AND destination = 'Hanoi'
   ORDER BY price_inr ASC
   LIMIT 1;

2. For "Find the cheapest return flight between New Delhi and Hanoi with at least 7 days gap?":
   WITH outbound AS (
       SELECT id, airline, time, date, duration, flightType, price_inr, origin, destination, originCountry, destinationCountry
       FROM flights
       WHERE origin = 'New Delhi' AND destination = 'Hanoi'
   ),
   return_flight AS (
       SELECT id, airline, time, date, duration, flightType, price_inr, origin, destination, originCountry, destinationCountry
       FROM flights
       WHERE origin = 'Hanoi' AND destination = 'New Delhi' AND DATE(date) >= DATE(outbound.date, '+7 days')
   )
   SELECT 
       outbound.id AS outbound_id, outbound.airline AS outbound_airline, outbound.time AS outbound_time, 
       outbound.date AS outbound_date, outbound.duration AS outbound_duration, outbound.flightType AS outbound_flightType,
       outbound.price_inr AS outbound_price,
       return_flight.id AS return_id, return_flight.airline AS return_airline, return_flight.time AS return_time, 
       return_flight.date AS return_date, return_flight.duration AS return_duration, return_flight.flightType AS return_flightType,
       return_flight.price_inr AS return_price,
       (outbound.price_inr + return_flight.price_inr) AS total_price
   FROM outbound
   JOIN return_flight
   ON outbound.destination = return_flight.origin
   ORDER BY total_price ASC
   LIMIT {top_k};

3. For "List all round trips between Mumbai and Phu Quoc?":
   WITH outbound AS (
       SELECT id, airline, time, date, duration, flightType, price_inr, origin, destination, originCountry, destinationCountry
       FROM flights
       WHERE origin = 'Mumbai' AND destination = 'Phu Quoc'
   ),
   return_flight AS (
       SELECT id, airline, time, date, duration, flightType, price_inr, origin, destination, originCountry, destinationCountry
       FROM flights
       WHERE origin = 'Phu Quoc' AND destination = 'Mumbai'
   )
   SELECT 
       outbound.id AS outbound_id, outbound.airline AS outbound_airline, outbound.time AS outbound_time, 
       outbound.date AS outbound_date, outbound.duration AS outbound_duration, outbound.flightType AS outbound_flightType,
       outbound.price_inr AS outbound_price,
       return_flight.id AS return_id, return_flight.airline AS return_airline, return_flight.time AS return_time, 
       return_flight.date AS return_date, return_flight.duration AS return_duration, return_flight.flightType AS return_flightType,
       return_flight.price_inr AS return_price,
       (outbound.price_inr + return_flight.price_inr) AS total_price
   FROM outbound
   JOIN return_flight
   ON outbound.destination = return_flight.origin
   ORDER BY total_price ASC
   LIMIT {top_k};

Output ONLY the SQL query and nothing else.
"""
)
