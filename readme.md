# RAG on Flight Data

![demo](https://github.com/user-attachments/assets/9a2a8256-adf2-4841-96e6-3c37981b70ab)

## Frontend Repo

[https://github.com/harsh-vardhhan/ai-agent-flight-scanner-frontend](https://github.com/harsh-vardhhan/ai-agent-flight-scanner-frontend)

## Technical spec

| Spec                            |           |
|----------------------------------------- |-----------|
| Platform to run LLM                      | Groq    |
| LLM                                      | deepseek-r1-distill-llama-70b |
| AI agent framework                       | LangChain |
| Database                                 | SQLite    |
| REST framework                           | FastAPI   |

## Application architecture

<img width="640" alt="AI agent" src="https://github.com/user-attachments/assets/ad49ef60-c012-4f62-8d9a-d408a24c17ce" />

##  Create `.env` and set environment variables file

```python
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

## Running models in Ollama

### Change in `app/config.py`

```python
PLATFORM_NAME='OLLAMA'
MODEL_NAME='deepseek-r1:14b'
```

## Running DeepSeek R1 on Groq

### Change in `app/config.py`

```python
PLATFORM_NAME = 'GROQ'
MODEL_NAME = 'deepseek-r1-distill-llama-70b'
```

## Running application

```
python3 app/main.py
```

## Prompt testing

### Basic Price Queries (India to Vietnam)

| Prompt                                                                                       |
|---------------------------------------------------------------------------------------------|
| What is the cheapest flight from New Delhi to Hanoi?                                        |
| Find the lowest price flight from Mumbai to Ho Chi Minh City                                |
| Show me the cheapest flight from New Delhi to Da Nang                                       |
| What is the lowest fare from Mumbai to Phu Quoc?                                            |

### Basic Price Queries (Vietnam to India)

| Prompt                                                                                       |
|---------------------------------------------------------------------------------------------|
| What is the cheapest flight from Hanoi to New Delhi?                                        |
| Find the lowest price flight from Ho Chi Minh City to Mumbai                                |
| Show me the cheapest flight from Da Nang to New Delhi                                       |
| What is the lowest fare from Phu Quoc to Mumbai?                                            |

### Price Range Queries (Generic)

| Prompt                                                                                       |
|---------------------------------------------------------------------------------------------|
| Show me flights from New Delhi to Hanoi ordered by price                                    |
| List all flights from Ho Chi Minh City to Mumbai from lowest to highest price              |
| What are the available flights from Mumbai to Da Nang sorted by fare?                      |
| Find flights from Phu Quoc to New Delhi ordered by cost                                    |

### Flight Type Specific

| Prompt                                                                                       |
|---------------------------------------------------------------------------------------------|
| Show me all direct flights from New Delhi to Ho Chi Minh City                              |
| List connecting flights from Hanoi to Mumbai                                               |
| What types of flights are available from New Delhi to Da Nang?                             |
| Find direct flights from Phu Quoc to Mumbai                                               |

### Comparative Queries

| Prompt                                                                                       |
|---------------------------------------------------------------------------------------------|
| Compare prices of flights from New Delhi to all Vietnamese cities                          |
| Show me the cheapest routes from Mumbai to Vietnam                                         |
| List all flight options from Hanoi to Indian cities                                        |
| Compare fares from Ho Chi Minh City to Indian destinations                                 |

### Round Trip Queries

| Prompt                                                                                       |
|---------------------------------------------------------------------------------------------|
| Find the cheapest round trip from New Delhi to Hanoi                                       |
| Show me round trip options between Mumbai and Ho Chi Minh City                             |
| What are the most affordable round trip flights from New Delhi to Da Nang?                |
| List round trip flights between Mumbai and Phu Quoc                                        |
| List cheapest round trip flights between Mumbai and Phu Quoc                               |
| Find the cheapest return flight between New Delhi and Hanoi with at least 7 days gap       |
| Show exactly one cheapest flight from New Delhi to Hanoi and exactly one from Hanoi to New Delhi, which should be at least 7 days later |

### Statistical Analysis

| Prompt                                                                                       |
|---------------------------------------------------------------------------------------------|
| What's the average price of flights from New Delhi to Vietnamese cities?                   |
| Compare fares between all India-Vietnam routes                                             |
| Show me the price distribution of flights from Vietnamese cities to Mumbai                 |
| Which Vietnam-India route has the most varying fares?                                      |

### Combination Queries

| Prompt                                                                                       |
|---------------------------------------------------------------------------------------------|
| Find the cheapest direct flight from New Delhi to any Vietnamese city                      |
| List the most affordable flights from Vietnamese cities to Mumbai                          |
| Show me the top 5 best-value routes between India and Vietnam                              |
| What are the most economical flights from Hanoi to Indian cities?                          |
