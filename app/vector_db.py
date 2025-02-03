import json
import os
from pathlib import Path
from typing import List, Dict
import openai
import tiktoken
from config import llm
from strip_think_tags import strip_think_tags
from luggage_prompt import luggage_prompt

client = openai.AsyncOpenAI()

# Usage example:
documents = [
    {"name": "IndiGo", "policy_file": "../data/indigo_policy.txt"},
    {"name": "VietJet Air", "policy_file": "../data/vietjet_policy.txt"}
]

def read_file(file_path: str) -> str:
    # Get the directory containing the script
    script_dir = Path(__file__).parent.absolute()

    # Construct absolute path to the file
    absolute_path = os.path.join(script_dir, file_path)

    try:
        with open(absolute_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Current working directory: {os.getcwd()}")
        print(f"Trying to read file at: {absolute_path}")
        raise

def split_document(text: str, max_tokens: int = 500) -> List[str]:
    # Initialize tokenizer for ada-002
    enc = tiktoken.encoding_for_model("text-embedding-ada-002")

    chunks = []
    current_chunk = []
    current_size = 0

    # Split into sentences (basic implementation)
    sentences = text.replace('\n', ' ').split('. ')

    for sentence in sentences:
        sentence = sentence.strip() + '. '
        sentence_tokens = len(enc.encode(sentence))

        if current_size + sentence_tokens > max_tokens:
            # Join the current chunk and add to chunks
            chunks.append(''.join(current_chunk))
            current_chunk = [sentence]
            current_size = sentence_tokens
        else:
            current_chunk.append(sentence)
            current_size += sentence_tokens

    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(''.join(current_chunk))

    return chunks

async def get_embedding(text: str) -> List[float]:
    response = await client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

async def process_documents(documents: List[Dict], embedding_cache_dir: str = "./embeddings_cache"):
    # Create cache directory if it doesn't exist
    Path(embedding_cache_dir).mkdir(parents=True, exist_ok=True)

    document_chunks = []
    chunk_embeddings = []
    chunk_metadata = []

    for doc in documents:
        # Create a unique cache filename for this document
        cache_filename = f"{doc['name'].lower().replace(' ', '_')}_embeddings.json"
        cache_path = os.path.join(embedding_cache_dir, cache_filename)

        # Check if we have cached embeddings
        if os.path.exists(cache_path):
            print(f"Loading cached embeddings for {doc['name']}")
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)
                document_chunks.extend(cached_data['chunks'])
                chunk_embeddings.extend(cached_data['embeddings'])
                chunk_metadata.extend(cached_data['metadata'])
        else:
            print(f"Creating new embeddings for {doc['name']}")
            # Read and process the document
            text = read_file(doc['policy_file'])
            doc_chunks = split_document(text)

            # Store new chunks and their metadata
            doc_embeddings = []
            doc_metadata = []

            for i, chunk in enumerate(doc_chunks):
                embedding = await get_embedding(chunk)
                doc_embeddings.append(embedding)
                doc_metadata.append({
                    "airline": doc["name"],
                    "chunk_index": i,
                    "total_chunks": len(doc_chunks)
                })

            # Save to cache
            cache_data = {
                'chunks': doc_chunks,
                'embeddings': doc_embeddings,
                'metadata': doc_metadata
            }
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)

            # Add to our current results
            document_chunks.extend(doc_chunks)
            chunk_embeddings.extend(doc_embeddings)
            chunk_metadata.extend(doc_metadata)

    return {
        'chunks': document_chunks,
        'embeddings': chunk_embeddings,
        'metadata': chunk_metadata
    }

async def generate_llm_response(airline: str, query: str, relevant_text: str) -> str:
    prompt = luggage_prompt.format(airline=airline, query=query, relevant_text=relevant_text)

    try:
        response = await llm.ainvoke(prompt)
        return strip_think_tags(response).strip()
    except Exception:
        # Fallback to a basic response if LLM fails
        return f"According to {airline}'s policy: {relevant_text}"

def search_policy(airline: str, query: str) -> str:
    policy_file = next((doc["policy_file"] for doc in documents
                       if doc["name"].lower() == airline.lower()), None)

    script_dir = Path(__file__).parent.absolute()
    absolute_path = os.path.join(script_dir, policy_file)

    if not policy_file:
        return f"I apologize, but I don't have any policy information available for {airline}."

    try:
        with open(absolute_path, 'r', encoding='utf-8') as file:
            policy_text = file.read()
    except FileNotFoundError:
        return f"I apologize, but I couldn't find the policy document for {airline}."

    query_keywords = query.lower().split()

    # Searching for the most relevant section
    sections = policy_text.split("\n\n")
    relevant_sections = []

    for section in sections:
        if any(keyword in section.lower() for keyword in query_keywords):
            relevant_sections.append(section)

    if relevant_sections:
        relevant_text = "\n\n".join(relevant_sections[:3])
        return generate_llm_response(airline, query, relevant_text)
    else:
        return generate_llm_response(
            airline,
            query,
            "No specific information found in the policy document."
        )
