import os
import glob
import json
import re
import openai
import numpy as np
import faiss
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv()

# Instantiate the client using the API key
from openai import OpenAI
client = OpenAI(
    api_key = os.environ.get("OPENAI_API_KEY")
)

# Directory containing the text files generated from the web scraper
TEXT_FILES_DIR = "./admin/sections_output"
# Output files for the FAISS index and metadata
FAISS_INDEX_FILE = "./faiss_index.bin"
METADATA_FILE = "./metadata.json"

# The embedding model to use (adjust as needed)
EMBEDDING_MODEL = "text-embedding-3-small"

# Base URL components used to reconstruct section links.
BASE_URL = "https://malegislature.gov"
START_PATH = "/Laws/GeneralLaws/PartII/TitleI/"

def get_embedding(text: str) -> np.ndarray:
    """
    Get embedding from OpenAI for a given text using the specified model.
    Returns a numpy array of the embedding.
    """
    try:
        response  = client.embeddings.create(
            input=text[:8150],
            model=EMBEDDING_MODEL
        )
        embedding = response.data[0].embedding
        return np.array(embedding, dtype=np.float32)
    except Exception as e:
        print(f"Error obtaining embedding for text: {e}")
        return None

def parse_filename(filename: str):
    """
    Given a filename (e.g., "Chapter184A_Section2.txt"),
    extract the chapter and section parts.
    Inserts a space between "Chapter" and the first digit and between "Section" and the first digit.
    Returns a tuple (chapter, section). If parsing fails, returns (None, None).
    """
    base, _ = os.path.splitext(filename)
    parts = base.split('_')
    if len(parts) == 2:
        chapter = parts[0].strip()
        section = parts[1].strip()
        # Insert a space between "Chapter" and the first digit
        chapter = re.sub(r'^(Chapter)(\d)', r'\1 \2', chapter)
        # Insert a space between "Section" and the first digit
        section = re.sub(r'^(Section)(\d)', r'\1 \2', section)
        return chapter, section
    return None, None

def reconstruct_section_link(chapter: str, section: str) -> str:
    """
    Reconstruct the full URL for a section from its chapter and section metadata.
    Removes spaces from the chapter and section before constructing the URL.
    For example, ("Chapter 184A", "Section 2") becomes:
      https://malegislature.gov/Laws/GeneralLaws/PartII/TitleI/Chapter184A/Section2
    """
    chapter_clean = chapter.replace(" ", "")
    section_clean = section.replace(" ", "")
    return f"{BASE_URL}{START_PATH}{chapter_clean}/{section_clean}"

def load_text_files(directory: str):
    """
    Load all text files from the specified directory.
    Returns a list of dictionaries with keys: 'filename', 'full_text', 'chapter', 'section', and 'link'.
    """
    files = glob.glob(os.path.join(directory, "*.txt"))
    documents = []
    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read().strip()
            filename = os.path.basename(filepath)
            chapter, section = parse_filename(filename)
            link = reconstruct_section_link(chapter, section) if chapter and section else None
            documents.append({
                'filename': filename,
                'full_text': text,
                'chapter': chapter,
                'section': section,
                'link': link
            })
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
    return documents

def build_vector_database(documents):
    """
    Given a list of documents, obtains their embeddings and builds a FAISS index.
    Each document entry is expected to have 'full_text'.
    Returns the FAISS index and a metadata list mapping FAISS vector id to document details.
    """
    embeddings = []
    metadata = []

    for doc in tqdm(documents, desc="Embedding documents"):
        print(f"Embedding document: {doc['filename']}")
        emb = get_embedding(doc['full_text'])
        if emb is not None:
            embeddings.append(emb)
            metadata.append({
                'filename': doc['filename'],
                'chapter': doc['chapter'],
                'section': doc['section'],
                'link': doc['link'],
                'full_text': doc['full_text']  # Store entire text for citation/reference
            })
        else:
            print(f"Skipping {doc['filename']} due to embedding error.")
    
    if not embeddings:
        raise ValueError("No embeddings were obtained from documents.")
    
    embeddings = np.stack(embeddings)
    dimension = embeddings.shape[1]
    print(f"Building FAISS index with dimension {dimension} and {len(embeddings)} vectors")
    
    # Using a simple index (IndexFlatL2). For larger collections consider more advanced indices.
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    return index, metadata

def save_vector_database(index, metadata, index_file, metadata_file):
    """
    Saves the FAISS index to disk and writes the metadata to a JSON file.
    """
    faiss.write_index(index, index_file)
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved FAISS index to {index_file} and metadata to {metadata_file}")

def main():
    # Load documents from the text files directory
    documents = load_text_files(TEXT_FILES_DIR)
    if not documents:
        print("No text files found. Exiting.")
        return

    # Build FAISS index and metadata from document embeddings
    index, metadata = build_vector_database(documents)
    
    # Save the vector database (FAISS index) and metadata
    save_vector_database(index, metadata, FAISS_INDEX_FILE, METADATA_FILE)
    
    print("Vector database construction complete.")

if __name__ == '__main__':
    main()
