import pinecone
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX")

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

pinecone.create_index(PINECONE_INDEX_NAME, dimension=1536)  # if using OpenAI ada-002 (1536 dims)

index = pinecone.Index(PINECONE_INDEX_NAME)