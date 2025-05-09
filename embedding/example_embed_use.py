import os
from dotenv import load_dotenv
import openai
import pinecone

# Load environment variables from .env file
load_dotenv()

# Get API keys and config from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX")

# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY

# Initialize Pinecone
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
index = pinecone.Index(PINECONE_INDEX_NAME)

# Function to embed text query
def embed_text(text, model="text-embedding-ada-002"):
    response = openai.Embedding.create(
        input=text,
        model=model
    )
    embedding = response['data'][0]['embedding']
    return embedding

# ---- QUERY PIPELINE ----
def query_pipeline(query_text, top_k=5):
    # Step 1: Embed the query
    print(f"Embedding query: {query_text}")
    query_embedding = embed_text(query_text)

    # Step 2: Query Pinecone
    print(f"Querying Pinecone index: {PINECONE_INDEX_NAME}")
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    # Step 3: Build context from retrieved docs
    print(f"Retrieved {len(results['matches'])} results.")
    context = "\n".join([match['metadata']['text'] for match in results['matches']])

    return context, results

# ---- MAIN EXECUTION ----
if __name__ == "__main__":
    query = input("Enter your query: ")
    context, results = query_pipeline(query)

    print("\n=== Retrieved Context ===")
    print(context)
