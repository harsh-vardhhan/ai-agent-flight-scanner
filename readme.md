# RAG on Google Flights Data

![carbon](https://github.com/user-attachments/assets/25622d31-be95-4f45-b66a-74a3073f600d)

## Technical spec

| Spec                            |           |
|----------------------------------------- |-----------|
| Platform to run LLM                      | Ollama    |
| LLM                                      | Phi4      |
| AI agent framework                       | LangChain |
| Database                                 | SQLite    |

## Application architecture
<img width="1141" alt="application-architecture" src="https://github.com/user-attachments/assets/35b3843d-f748-4a86-a8ba-34725819a44b" />

## Running application

```
python3 app/main.py
```

## Prompt testing
### Basic Price Queries (India to Vietnam)

| Prompt                                                                                       | Phi4 14B | Llama 3.3 70B |
|---------------------------------------------------------------------------------------------|------|----------------|
| What is the cheapest flight from New Delhi to Hanoi?                                        | ✅   |    ✅            |
| Find the lowest price flight from Mumbai to Ho Chi Minh City                                | ✅   |    ✅            |
| Show me the cheapest flight from New Delhi to Da Nang                                       | ✅   |    ✅            |
| What is the lowest fare from Mumbai to Phu Quoc?                                            | ✅   |    ✅            |

### Basic Price Queries (Vietnam to India)

| Prompt                                                                                       | Phi4 14B | Llama 3.3 70B |
|---------------------------------------------------------------------------------------------|------|----------------|
| What is the cheapest flight from Hanoi to New Delhi?                                        | ✅   |    ✅            |
| Find the lowest price flight from Ho Chi Minh City to Mumbai                                | ✅   |    ✅            |
| Show me the cheapest flight from Da Nang to New Delhi                                       | ✅   |    ✅            |
| What is the lowest fare from Phu Quoc to Mumbai?                                            | ✅   |    ✅            |

### Price Range Queries (Generic)

| Prompt                                                                                       | Phi4 14B | Llama 3.3 70B |
|---------------------------------------------------------------------------------------------|------|----------------|
| Show me flights from New Delhi to Hanoi ordered by price                                    | ✅   |   ✅             |
| List all flights from Ho Chi Minh City to Mumbai from lowest to highest price              | ✅   |    ✅            |
| What are the available flights from Mumbai to Da Nang sorted by fare?                      | ✅   |    ✅            |
| Find flights from Phu Quoc to New Delhi ordered by cost                                    | ✅   |    ✅            |

### Flight Type Specific

| Prompt                                                                                       | Phi4 14B | Llama 3.3 70B |
|---------------------------------------------------------------------------------------------|------|----------------|
| Show me all direct flights from New Delhi to Ho Chi Minh City                              | ✅   |   ✅              |
| List connecting flights from Hanoi to Mumbai                                               |      |       ❌         |
| What types of flights are available from New Delhi to Da Nang?                             | ✅   |                |
| Find direct flights from Phu Quoc to Mumbai                                               | ✅   |                |

### Comparative Queries

| Prompt                                                                                       | Phi4 14B | Llama 3.3 70B |
|---------------------------------------------------------------------------------------------|------|----------------|
| Compare prices of flights from New Delhi to all Vietnamese cities                          |      |                |
| Show me the cheapest routes from Mumbai to Vietnam                                         | ✅     |     ✅           |
| List all flight options from Hanoi to Indian cities                                        |      |                |
| Compare fares from Ho Chi Minh City to Indian destinations                                 |      |                |

### Round Trip Queries

| Prompt                                                                                       | Phi4 14B | Llama 3.3 70B |
|---------------------------------------------------------------------------------------------|------|----------------|
| Find the cheapest round trip from New Delhi to Hanoi                                       | ✅   |                |
| Show me round trip options between Mumbai and Ho Chi Minh City                             |      |                |
| What are the most affordable round trip flights from New Delhi to Da Nang?                | ✅   |                |
| List round trip flights between Mumbai and Phu Quoc                                        | ✅   |                |
| List cheapest round trip flights between Mumbai and Phu Quoc                               |      |                |
| Find the cheapest return flight between New Delhi and Hanoi with at least 7 days gap       | ✅   |                |
| Show exactly one cheapest flight from New Delhi to Hanoi and exactly one from Hanoi to New Delhi, which should be at least 7 days later | ✅ |                |

### Statistical Analysis

| Prompt                                                                                       | Phi4 14B | Llama 3.3 70B |
|---------------------------------------------------------------------------------------------|------|----------------|
| What's the average price of flights from New Delhi to Vietnamese cities?                   |  ✅    |                |
| Compare fares between all India-Vietnam routes                                             |      |                |
| Show me the price distribution of flights from Vietnamese cities to Mumbai                 |      |                |
| Which Vietnam-India route has the most varying fares?                                      |      |                |

### Combination Queries

| Prompt                                                                                       | Phi4 14B | Llama 3.3 70B |
|---------------------------------------------------------------------------------------------|------|---------------|
| Find the cheapest direct flight from New Delhi to any Vietnamese city                      |  ✅    |   ✅         |
| List the most affordable flights from Vietnamese cities to Mumbai                          |  ✅     |   ✅         |
| Show me the top 5 best-value routes between India and Vietnam                              |  ✅    |   ✅          |
| What are the most economical flights from Hanoi to Indian cities?                          | ✅     |    ❌            |
