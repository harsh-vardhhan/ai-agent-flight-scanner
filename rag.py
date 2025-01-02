import json
from langchain_groq import ChatGroq

# Initialize Groq LLM with LangChain
llm = ChatGroq(
    model_name="llama-3.2-3b-preview",  # Replace with the model you're using
    temperature=0.7
)

# Load the JSON data from file
with open('flight_data.json', 'r') as file:
    flight_data = json.load(file)

# Initial message with flight data
initial_message = [
    {
        "role": "system",
        "content": f"Here's some flight data to consider for your queries: {json.dumps(flight_data)}"
    }
]

# Interactive loop
while True:
    user_input = input("Enter your prompt (or 'exit' to end): ")

    if user_input.lower() == 'exit':
        print("Exiting the program.")
        break

    # Add user's prompt to the initial message
    messages = initial_message + [
        {
            "role": "user",
            "content": user_input
        }
    ]

    # Get the response from the LLM
    response = llm.invoke(messages)

    # Print the response
    print(f"LLM Response: {response.content}\n")
