import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Load environment variables from .env file
load_dotenv()


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_PINE_ENV = os.getenv("PINECONE_ENVIRONMENT")

PINECONE_INDEX_FAS_NAME = os.getenv("PINECONE_INDEX_FAS")
PINECONE_INDEX_SS_NAME = os.getenv("PINECONE_INDEX_SS")

DIMENSION = 1536  # For text-embedding-3-small
METRIC = "cosine" 

# --- Initialization ---
if not PINECONE_API_KEY or not PINECONE_PINE_ENV:
    raise ValueError("PINECONE_API_KEY and (PINECONE_ENVIRONMENT or PINECONE_ENV) must be set in your environment variables.")

pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_PINE_ENV)

print(f"Pinecone client initialized for environment: {PINECONE_PINE_ENV}")

def create_index_if_not_exists(index_name, dimension, metric, environment_for_spec):
    if not index_name:
        print("Index name not provided. Skipping creation.")
        return

    
    print(f"Creating index '{index_name}' with dimension {dimension} and metric '{metric}'...")
    try:
    # If using Serverless (ensure your environment supports it):
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(
                cloud="aws",  
                region="us-east-1", 
            )
        )
        print(f"Index '{index_name}' created successfully or creation initiated.")

    except Exception as e: # Catching general exception, could be more specific e.g. ApiException
        print(f"Error creating index '{index_name}': {e}")


# Create indexes if they don't exist
create_index_if_not_exists(PINECONE_INDEX_FAS_NAME, DIMENSION, METRIC, PINECONE_PINE_ENV)
create_index_if_not_exists(PINECONE_INDEX_SS_NAME, DIMENSION, METRIC, PINECONE_PINE_ENV)


# --- Get Index Objects ---
index_fas = None
if PINECONE_INDEX_FAS_NAME:
    try:
        index_fas = pc.Index(PINECONE_INDEX_FAS_NAME)
        # You can verify connection by describing stats (optional)
        stats = index_fas.describe_index_stats()
        print(f"\nSuccessfully connected to index '{PINECONE_INDEX_FAS_NAME}'. Stats: {stats}")
    except Exception as e:
        print(f"\nCould not connect to index '{PINECONE_INDEX_FAS_NAME}'. Error: {e}")
        print(f"Please ensure index '{PINECONE_INDEX_FAS_NAME}' exists and is ready in environment '{PINECONE_PINE_ENV}'.")


index_ss = None
if PINECONE_INDEX_SS_NAME:
    try:
        index_ss = pc.Index(PINECONE_INDEX_SS_NAME)
        stats = index_ss.describe_index_stats()
        print(f"Successfully connected to index '{PINECONE_INDEX_SS_NAME}'. Stats: {stats}")
    except Exception as e:
        print(f"\nCould not connect to index '{PINECONE_INDEX_SS_NAME}'. Error: {e}")
        print(f"Please ensure index '{PINECONE_INDEX_SS_NAME}' exists and is ready in environment '{PINECONE_PINE_ENV}'.")