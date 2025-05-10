import os
from pathlib import Path
from chunking import process_pdf_to_chunks, CHUNK_SIZE, CHUNK_OVERLAP
from embedding import get_openai_embedding, prepare_and_upsert_to_pinecone
import json

def print_chunk_details(chunk, chunk_num):
    """Print details of a single chunk."""
    print(f"\n=== Chunk {chunk_num} ===")
    print(f"Metadata:")
    for key, value in chunk['metadata'].items():
        print(f"  {key}: {value}")
    print(f"\nContent (first 200 chars):")
    print(f"{chunk['content'][:200]}...")
    print("-" * 80)

def test_single_document():
    """Test chunking and embedding for a single document."""
    # Get the first FAS document for testing
    script_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
    test_pdf = script_dir / "data" / "FAS" / "FAS_32.pdf"
    
    if not test_pdf.is_file():
        print(f"Error: Test PDF not found at {test_pdf}")
        return
    
    print(f"\nTesting with document: {test_pdf.name}")
    print(f"Chunk size: {CHUNK_SIZE} characters")
    print(f"Chunk overlap: {CHUNK_OVERLAP} characters")
    
    # Step 1: Create chunks
    print("\nStep 1: Creating chunks...")
    chunks = process_pdf_to_chunks(test_pdf)
    
    if not chunks:
        print("No chunks were created.")
        return
    
    # Step 2: Print first few chunks
    print(f"\nStep 2: Showing first 3 chunks (total chunks: {len(chunks)})")
    for i, chunk in enumerate(chunks[:3]):
        print_chunk_details(chunk, i + 1)
    
    # Step 3: Get embeddings for first chunk
    print("\nStep 3: Getting embedding for first chunk...")
    first_chunk = chunks[0]
    embedding = get_openai_embedding(first_chunk['content'])
    
    if embedding:
        print(f"Successfully generated embedding of length: {len(embedding)}")
        print(f"First 5 values of embedding: {embedding[:5]}")
    
    # Step 4: Save chunks to JSON for inspection
    output_dir = script_dir / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "test_chunks.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved all chunks to {output_file}")
    print(f"Total chunks created: {len(chunks)}")

def main():
    """Run the test."""
    print("=== Testing Chunking and Embedding Process ===")
    test_single_document()

if __name__ == "__main__":
    main() 