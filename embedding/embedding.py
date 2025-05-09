import os
import uuid
from dotenv import load_dotenv
import openai
import pinecone
import fitz  # PyMuPDF for reading PDFs
from typing import List

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX")

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Initialize Pinecone
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
index = pinecone.Index(PINECONE_INDEX_NAME)

# 1️⃣ Extract text from PDF
def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# 2️⃣ Split text into chunks
def split_text(text: str, max_tokens: int = 500) -> List[str]:
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_tokens:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

# 3️⃣ Embed a chunk
def embed_text(text: str, model="text-embedding-ada-002"):
    response = openai.Embedding.create(input=text, model=model)
    embedding = response['data'][0]['embedding']
    return embedding

# 4️⃣ Process and upload PDF to Pinecone
def process_pdf(pdf_path: str):
    print(f"Processing: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    chunks = split_text(text)
    print(f"Extracted {len(chunks)} chunks from {pdf_path}")
    
    upserts = []
    for idx, chunk in enumerate(chunks):
        embedding = embed_text(chunk)
        unique_id = str(uuid.uuid4())
        metadata = {
            "source": os.path.basename(pdf_path),
            "text": chunk
        }
        upserts.append((unique_id, embedding, metadata))
    
    # Batch upsert
    index.upsert(vectors=upserts)
    print(f"Uploaded {len(upserts)} vectors to Pinecone from {pdf_path}")

# 5️⃣ Main function
def main():
    pdf_folder = "./pdfs"  # Folder containing PDFs
    pdf_files = [os.path.join(pdf_folder, f) for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
    
    for pdf_file in pdf_files:
        process_pdf(pdf_file)

if __name__ == "__main__":
    main()
