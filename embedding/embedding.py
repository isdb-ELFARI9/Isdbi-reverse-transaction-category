# embedding.py
import os
import uuid
from dotenv import load_dotenv
import openai
from typing import List, Dict, Any
from pathlib import Path
import time # For batching and rate limits
import re # For cleaning names for namespace
from chunking import process_pdf_to_chunks
from pinecone import Pinecone, ServerlessSpec
# FAS_NAME_MAPPING will be defined in this script based on the one from chunking.py's context
# but for iteration, we'll redefine it or import it if chunking.py exposes it cleanly.

# --- Configuration for PDF processing ---
# This SCRIPT_DIR should point to the directory containing the 'embedding.py' script.
# The paths in FAS_NAME_MAPPING will be relative to the project root.
SCRIPT_DIR_EMBEDDING = Path(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = SCRIPT_DIR_EMBEDDING.parent # Assuming 'embedding.py' is in a subdirectory like 'embedding_scripts'
                                        # If 'embedding.py' is at the project root, then PROJECT_ROOT = SCRIPT_DIR_EMBEDDING


# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY_SS_FULL")
PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT") 
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_FAS_FULL") 

SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
FAS_FILES_TO_PROCESS_MAP = {
    SCRIPT_DIR / "data" / "FAS" / "FAS_32.pdf": "FAS_32_Ijarah",
    SCRIPT_DIR / "data" / "FAS" / "FAS_28_Murabaha_Deferred_Payment_Sales.pdf": "FAS_28_Murabaha_Deferred_Payment_Sales",
    SCRIPT_DIR / "data" / "FAS" / "FAS_10_Istisna.pdf": "FAS_10_Istisna",
    SCRIPT_DIR / "data" / "FAS" / "FAS_7_Salam_Parallel_Salam.pdf": "FAS_7_Salam_Parallel_Salam",
    SCRIPT_DIR / "data" / "FAS" / "FAS_4_Musharaka.pdf": "FAS_4_Musharaka",
}

SS_FILES_TO_PROCESS_MAP = {
    SCRIPT_DIR / "data" / "SS" / "SS_8_Murabahah.pdf": "SS_8_Murabahah",
    SCRIPT_DIR / "data" / "SS" / "SS_9_Ijarah_Ijarah_Muntahia_Bittamleek.pdf": "SS_9_Ijarah_Ijarah_Muntahia_Bittamleek",
    SCRIPT_DIR / "data" / "SS" / "SS_10_Salam_Parallel_Salam.pdf": "SS_10_Salam_Parallel_Salam",
    SCRIPT_DIR / "data" / "SS" / "SS_12_Musharakah.pdf": "SS_12_Musharakah",
}

# Initialize OpenAI client
if OPENAI_API_KEY:
    # For openai >= 1.0.0
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    # If you are using openai < 1.0.0, use: openai.api_key = OPENAI_API_KEY
else:
    print("Error: OPENAI_API_KEY not found in .env file")
    exit()

# Initialize Pinecone connection
if PINECONE_API_KEY and PINECONE_ENV and PINECONE_INDEX_NAME:
    pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        print(f"Error: Pinecone index '{PINECONE_INDEX_NAME}' not found in environment '{PINECONE_ENV}'. Please create it first.")
        exit()
    index = pc.Index(PINECONE_INDEX_NAME)
    print(f"Successfully connected to Pinecone index: {PINECONE_INDEX_NAME}")
else:
    print("Error: Pinecone API key, environment, or index name not found in .env file.")
    exit()

EMBEDDING_MODEL = "text-embedding-3-small"
TARGET_EMBEDDING_DIMENSION = 1536 # Default for text-embedding-3-small. Ensure Pinecone index matches.

def get_openai_embedding(text: str, model: str = EMBEDDING_MODEL, target_dimensions: int = None) -> List[float]:
    """Generates an embedding for the given text using OpenAI."""
    try:
        text_to_embed = text.replace("\n", " ") 
        params = {"input": [text_to_embed], "model": model}
        if target_dimensions and model in ["text-embedding-3-small", "text-embedding-3-large"]:
            params["dimensions"] = target_dimensions
        
        # Using the initialized client for openai >= 1.0.0
        response = client.embeddings.create(**params)
        # For openai < 1.0.0
        # response = openai.Embedding.create(input=[text_to_embed], model=model)
        embedding = response.data[0].embedding
        return embedding
    except Exception as e:
        print(f"Error getting embedding for text: '{text_to_embed[:100]}...': {e}")
        return None

def clean_for_namespace(name: str) -> str:
    """Cleans a string to be suitable for a Pinecone namespace."""
    name = name.lower()
    name = re.sub(r'\s+', '_', name)  # Replace spaces with underscores
    name = re.sub(r'[^a-z0-9_-]', '', name)  # Remove invalid characters
    return name[:512] # Pinecone namespace max length is 512

# --- Pinecone Upsert Function (MODIFIED to accept namespace) ---
def prepare_and_upsert_to_pinecone(chunks_data: List[Dict[str, Any]], pinecone_namespace: str, batch_size: int = 100):
    if not chunks_data:
        print(f"No chunks to process for namespace '{pinecone_namespace}'.")
        return

    vectors_to_upsert = []
    total_chunks = len(chunks_data)
    print(f"\n--- Preparing to upsert {total_chunks} chunks to namespace: {pinecone_namespace} ---")

    for i, chunk_item in enumerate(chunks_data):
        content = chunk_item.get("content")
        metadata = chunk_item.get("metadata", {})

        if not content:
            print(f"Skipping chunk {i+1}/{total_chunks} in namespace '{pinecone_namespace}' due to empty content.")
            continue

        # print(f"  Processing chunk {i+1}/{total_chunks} for '{pinecone_namespace}': Getting embedding...") # Less verbose
        embedding = get_openai_embedding(content, target_dimensions=TARGET_EMBEDDING_DIMENSION if EMBEDDING_MODEL.startswith("text-embedding-3") else None)

        if embedding:
            chunk_id = str(uuid.uuid4()) 
            pinecone_metadata = {
                "source_file": metadata.get("source_file", "N/A"),
                "standard_no": str(metadata.get("standard_no", "N/A")),
                "standard_name": metadata.get("standard_name", "N/A"),
                "page_start": str(metadata.get("page_start", "N/A")),
                "page_end": str(metadata.get("page_end", "N/A")),
                "main_section": metadata.get("main_section", "N/A"),
                "text_snippet": content[:500] # Store a snippet 
            }
            if "heading_path" in metadata and metadata["heading_path"]:
                pinecone_metadata["heading_path"] = [f"{hp[0]}: {hp[1]}" for hp in metadata["heading_path"] if isinstance(hp, tuple) and len(hp) == 2]
            
            vectors_to_upsert.append({
                "id": chunk_id,
                "values": embedding,
                "metadata": pinecone_metadata
            })

        if len(vectors_to_upsert) >= batch_size or (i == total_chunks - 1 and vectors_to_upsert):
            print(f"  Upserting batch of {len(vectors_to_upsert)} vectors to namespace '{pinecone_namespace}'...")
            try:
                # --- MODIFIED: Added namespace to upsert call ---
                index.upsert(vectors=vectors_to_upsert, namespace=pinecone_namespace)
                print(f"  Successfully upserted batch to namespace '{pinecone_namespace}'.")
                vectors_to_upsert = [] 
            except Exception as e:
                print(f"  Error upserting batch to Pinecone namespace '{pinecone_namespace}': {e}")
            if i < total_chunks - 1 : # Avoid sleep after the very last batch
                time.sleep(0.5) 

    print(f"--- Finished processing and upserting for namespace: {pinecone_namespace} ---")


# --- Main Workflow (MODIFIED to loop through PDF files) ---
if __name__ == "__main__":
    if not FAS_FILES_TO_PROCESS_MAP:
        print("No PDF files defined in FAS_FILES_TO_PROCESS_MAP. Exiting.")
        exit()

    for pdf_path, standard_name_from_map in SS_FILES_TO_PROCESS_MAP.items():
        print(f"\n======================================================================")
        print(f"Processing Document: {pdf_path.name}")
        print(f"======================================================================")

        if not pdf_path.is_file():
            print(f"ERROR: PDF file not found: {pdf_path}. Skipping.")
            continue
        
        # --- Determine Namespace ---
        pinecone_namespace = clean_for_namespace(standard_name_from_map)
        fn_match_num = re.search(r"FAS(?:_|\s|-)?(\d+)", pdf_path.name, re.IGNORECASE)
        if fn_match_num:
            standard_no_for_ns = fn_match_num.group(1)
            pinecone_namespace = f"SS{standard_no_for_ns}"
        else:
            pinecone_namespace = clean_for_namespace(standard_name_from_map if standard_name_from_map else pdf_path.stem)
            print(f"Warning: Could not extract SS number from filename '{pdf_path.name}'. Using namespace: '{pinecone_namespace}'")
            pinecone_namespace = "FAS_FULL"

        pinecone_namespace = "FAS_FULL"
        
        print(f"Target Pinecone Namespace: {pinecone_namespace}")

        print(f"Step 1: Chunking PDF document: {pdf_path.name}...")
      
        all_chunks = process_pdf_to_chunks(pdf_path) # This function is from chunking.py

        if all_chunks:
            print(f"Step 1: Successfully chunked PDF. Found {len(all_chunks)} chunks.")
            print(f"Step 2: Preparing chunks and upserting to Pinecone index '{PINECONE_INDEX_NAME}' (Namespace: '{pinecone_namespace}')...")
            prepare_and_upsert_to_pinecone(all_chunks, pinecone_namespace=pinecone_namespace)
        else:
            print(f"No chunks were generated from {pdf_path.name}. Nothing to embed for this file.")
        
        print(f"--- Completed processing for {pdf_path.name} ---")

    print("\n======================================================================")
    print("All specified PDF files have been processed.")
    print("======================================================================")