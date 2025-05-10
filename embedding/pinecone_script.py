import pinecone
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX_FAS = os.getenv("PINECONE_INDEX_FAS")
PINECONE_INDEX_SS = os.getenv("PINECONE_INDEX_SS")

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

pinecone.create_index(PINECONE_INDEX_FAS, dimension=1536)  # text-embedding-3-small	
pinecone.create_index(PINECONE_INDEX_FAS, dimension=1536)  # text-embedding-3-small	


index_fas = pinecone.Index(PINECONE_INDEX_FAS)
index_ss = pinecone.Index(PINECONE_INDEX_SS)