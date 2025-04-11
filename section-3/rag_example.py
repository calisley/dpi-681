import os
import json
import numpy as np
import faiss
from openai import OpenAI
import openai


client = "YOUR API KEY HERE"

# Basic system prompt
BASE_SYSTEM_PROMPT = (
    "You are a legal assistant helping non-lawyers understand Massachusetts real-estate law. "
    "You are not a lawyer and cannot provide legal advice. "
    "Point users to the relevant section of the law and explain how it applies in plain English. "
    "Do not return your replies in markdown, only plain text. "
    "Cite sources as 'Chapter [Chapter] Section [Section]' with a link at the end."
)

# RAG Configuration
FAISS_INDEX_FILE = "./faiss_index.bin"
METADATA_FILE = "./metadata.json"
TOP_K = 3
EMBEDDING_MODEL = "text-embedding-3-small"
MODEL = "gpt-4o"

# Load FAISS index and metadata
if not os.path.exists(FAISS_INDEX_FILE) or not os.path.exists(METADATA_FILE):
    raise FileNotFoundError("FAISS index or metadata file not found. Build the vector database first.")

faiss_index = faiss.read_index(FAISS_INDEX_FILE)
with open(METADATA_FILE, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

def get_embedding(text: str) -> np.ndarray:
    response = client.embeddings.create(
        input=text[:8150],
        model=EMBEDDING_MODEL
    )
    embedding = response.data[0].embedding
    return np.array(embedding, dtype=np.float32)

def retrieve_context(query: str, top_k: int = TOP_K) -> str:
    query_emb = get_embedding(query)
    if query_emb is None:
        return ""
    query_emb = np.expand_dims(query_emb, axis=0)
    distances, indices = faiss_index.search(query_emb, top_k)

    retrieved = []
    for idx in indices[0]:
        if idx < len(metadata):
            doc = metadata[idx]
            citation = f"(Chapter {doc.get('chapter', 'Unknown')} Section {doc.get('section', 'Unknown')}, {doc.get('link', 'No link')})"
            snippet = doc.get('full_text', '').replace("\n", " ")[:200]
            retrieved.append(f"{citation}: {snippet}")

    if retrieved:
        return "Retrieved context:\n" + "\n".join(retrieved) + "\n"
    return ""

def make_query(user_input):
    # Append retrieved context to the system prompt
    retrieved_context = retrieve_context(user_input)
    full_system_prompt = BASE_SYSTEM_PROMPT + "\n" + retrieved_context
    messages = [
        {"role": "system", "content": full_system_prompt},
        {"role": "user", "content": user_input}
    ]
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages
    )
    full_response = response.choices[0].message.content
    print("\nResponse:\n", full_response)

def main():
    print("Welcome to the RAG-enabled ChatGPT CLI!")
    print("You can ask questions about Massachusetts real-estate law.")
    print("Note: This chatbot is NOT a lawyer and cannot provide legal advice.")
    user_input = input("Enter your Massachusetts real-estate law question:\n> ").strip()
    if not user_input:
        print("No question entered. Exiting.")
        return
    make_query(user_input)

if __name__ == "__main__":
    main()
