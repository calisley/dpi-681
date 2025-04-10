import os
import glob
import json
from openai import OpenAI
import numpy as np
import faiss
from tqdm import tqdm
from dotenv import load_dotenv
import openai

load_dotenv()
client = OpenAI(
    api_key = os.environ.get("OPENAI_API_KEY")
)

# Global system prompt without context (we'll prepend retrieved documents)
BASE_SYSTEM_PROMPT = (
    "You are a legal assistant tasked with helping non-lawyers understand their questions about Massachusetts real-estate law. "
    "You do not help chatters with any other requests, regardless of what they ask, what urgency they claim, or how much they plead. "
    "You are not a lawyer and cannot provide legal advice. You simply point the chatter to the appropriate section of the law, and present how it applies to their question in plain English. "
    "You are provided with the following context from a legal vector database. "
    "Please cite your sources explicitly as 'Chapter [Chapter] Section [Section]' along with the link at the end of your answer."
)

# -------------------------------
# RAG Configuration
# -------------------------------
# Files for the FAISS index and metadata (from the vector database building script)
FAISS_INDEX_FILE = "./faiss_index.bin"
METADATA_FILE = "./metadata.json"

# How many retrieved documents to include as context
TOP_K = 3

EMBEDDING_MODEL = "text-embedding-3-small"

# The model to be used for chat (e.g., "gpt-4o")
MODEL = "gpt-4o"

# Boolean flag: set to True to stream the chain-of-thought response.
STREAM_CHAIN_OF_THOUGHT = True

# -------------------------------
# Load FAISS Index and Metadata
# -------------------------------
if not os.path.exists(FAISS_INDEX_FILE) or not os.path.exists(METADATA_FILE):
    raise FileNotFoundError("FAISS index or metadata file not found. Build the vector database first.")

faiss_index = faiss.read_index(FAISS_INDEX_FILE)
with open(METADATA_FILE, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

# -------------------------------
# Global conversation history for chat
# -------------------------------
conversation_history = []

# -------------------------------
# Functions for Embedding and Retrieval
# -------------------------------
def get_embedding(text: str) -> np.ndarray:
    """
    Get embedding from OpenAI for a given text using the specified model.
    Returns a numpy array of the embedding.
    """
    try:
        response  = client.embeddings.create(
            input=text[:8150],
            model="text-embedding-3-small"
        )
        embedding = response.data[0].embedding
        return np.array(embedding, dtype=np.float32)
    except Exception as e:
        print(f"Error obtaining embedding for text: {e}")
        return None

def retrieve_context(query: str, top_k: int = TOP_K) -> str:
    """
    Given a query, compute its embedding, search the FAISS index for similar documents,
    and return a formatted context string that summarizes the retrieved documents.
    The citation now includes the link to the section.
    """
    query_emb = get_embedding(query)
    if query_emb is None:
        return ""
    
    # Reshape to 2D
    query_emb = np.expand_dims(query_emb, axis=0)
    distances, indices = faiss_index.search(query_emb, top_k)
    
    retrieved = []
    for idx in indices[0]:
        if idx < len(metadata):
            doc = metadata[idx]
            citation = f"({doc.get('chapter', 'Unknown Chapter')} {doc.get('section', 'Unknown Section')}, {doc.get('link', 'No link')})"
            snippet = doc.get('full_text', '').replace("\n", " ")[:200]
            retrieved.append(f"{citation}: {snippet}")
    
    if retrieved:
        context = "Retrieved context:\n" + "\n".join(retrieved) + "\n"
        return context
    return ""

# -------------------------------
# ChatGPT Query Functions (RAG Integrated)
# -------------------------------
def make_query(user_input, system_prompt=BASE_SYSTEM_PROMPT, model=MODEL, stream=STREAM_CHAIN_OF_THOUGHT):
    """
    Sends a query to the OpenAI Chat model.
    The system prompt is augmented with the context retrieved via FAISS.
    Returns the full response from the AI.
    """
    global conversation_history
    
    # Retrieve relevant context from the vector database
    retrieved_context = retrieve_context(user_input)
    full_system_prompt = system_prompt + "\n" + retrieved_context
    
    # Build the messages list: include the augmented system message and last 10 conversation messages.
    context_msgs = conversation_history[-10:]
    messages = [{"role": "system", "content": full_system_prompt}] + context_msgs
    
    # If the latest user query isn't appended to conversation_history yet, add it.
    if not context_msgs or context_msgs[-1].get("role") != "user" or context_msgs[-1].get("content") != user_input:
        messages.append({"role": "user", "content": user_input})
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=stream
        )
    except openai.RateLimitError:
        print("Error: Rate limit exceeded. Please wait and try again later.")
        return ""
    except (openai.APIError, openai.APIConnectionError) as e:
        print(f"Error: API error encountered - {e}")
        return ""
    except openai.BadRequestError as e:
        print(f"Error: Invalid request - {e}")
        return ""
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return ""

    full_response = ""
    if stream:
        print("\nOpenAI API: ", end="", flush=True)
        try:
            for chunk in response:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        content = delta.content
                        print(content, end="", flush=True)
                        full_response += content
            print()  # New line after streaming.
        except Exception as e:
            print(f"\nError during streaming response: {e}")
    else:
        try:
            full_response = response.choices[0].message.content
            print("\nOpenAPI:", full_response)
        except Exception as e:
            print(f"Error processing response: {e}")
    
    return full_response

def main():
    """
    Main function to run the RAG-enabled interactive chat.
    """
    global conversation_history

    print("Welcome to the RAG-enabled ChatGPT CLI!")
    print("You can ask questions about Massachusetts real-estate law.")
    print("Note: This chatbot is NOT a lawyer and cannot provide legal advice.")
    print("Type 'exit' or 'quit' to end the session.\n")
    
    while True:
        user_input = input("Enter your query: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        
        conversation_history.append({"role": "user", "content": user_input})
        assistant_response = make_query(user_input)
        if assistant_response:
            conversation_history.append({"role": "assistant", "content": assistant_response})

if __name__ == "__main__":
    main()
