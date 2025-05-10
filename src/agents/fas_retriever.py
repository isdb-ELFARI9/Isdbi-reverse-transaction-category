"""
FAS Document Retriever Agent
Purpose: Retrieves relevant sections from FAS documents based on queries.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel
from pinecone import Pinecone
from ..core.config import settings
import openai
from openai import OpenAI

class FASDocument(BaseModel):
    """Model for FAS document chunks."""
    fas_id: str
    text: str
    relevance_score: float
    metadata: Optional[Dict] = None

class FASRetriever:
    def __init__(self):
        """Initialize the FAS Retriever agent."""
        # Initialize Pinecone client
        self.pc = Pinecone(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT
        )
        
        # Get the FAS index
        self.index = self.pc.Index("fas-embeddings-index")
        
        # Verify index connection
        try:
            stats = self.index.describe_index_stats()
            print(f"Connected to Pinecone index. Stats: {stats}")
        except Exception as e:
            print(f"Error connecting to Pinecone index: {e}")
            raise

    def embed_query(self, query: str) -> list:
        """
        Embed a query string into a vector using OpenAI's text-embedding-3-small model.
        """
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.embeddings.create(input=query, model="text-embedding-3-small")
        return response.data[0].embedding

    def _format_search_results(self, results: List[Dict]) -> List[FASDocument]:
        """
        Format Pinecone search results into FASDocument objects.
        
        Args:
            results: Raw search results from Pinecone
            
        Returns:
            List of formatted FASDocument objects
        """
        formatted_results = []
        for match in results:
            # Extract metadata
            metadata = match.get('metadata', {})
            fas_id = metadata.get('fas_id', 'Unknown')
            
            # Create FASDocument object
            doc = FASDocument(
                fas_id=fas_id,
                text=match.get('text', ''),
                relevance_score=match.get('score', 0.0),
                metadata=metadata
            )
            formatted_results.append(doc)
        
        return formatted_results

    def retrieve(
        self,
        query: str,
        top_n: int = 5,
        filter_criteria: Optional[Dict] = None,
        namespace: str = ""
    ) -> List[FASDocument]:
        """
        Retrieve relevant FAS document chunks based on the query.
        
        Args:
            query: Search query from Transaction Deconstructor
            top_n: Number of top results to return
            filter_criteria: Optional filter criteria for the search
            
        Returns:
            List of FASDocument objects containing relevant chunks
        """
        try:
            query_vector = self.embed_query(query)
            search_results = self.index.query(
                vector=query_vector,
                top_k=top_n,
                include_metadata=True,
                filter=filter_criteria,
                namespace=namespace
            )
            print(f"Raw search results: {search_results.matches}")  # Log raw results
            return self._format_search_results(search_results.matches)
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []

    def retrieve_by_keywords(
        self,
        keywords: List[str],
        top_n: int = 5,
        filter_criteria: Optional[Dict] = None,
        namespace: str = ""
    ) -> List[FASDocument]:
        """
        Retrieve documents using a list of keywords.
        
        Args:
            keywords: List of search keywords
            top_n: Number of top results to return
            filter_criteria: Optional filter criteria for the search
            
        Returns:
            List of FASDocument objects containing relevant chunks
        """
        query = " ".join(keywords)
        return self.retrieve(query, top_n, filter_criteria,namespace=namespace) 
    

def get_embedding(text: str) -> list:
    response = openai.embeddings.create(
        input=[text],
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding

def retrieve_knowledge_from_pinecone_ss(query: str, ss_namespace: str) -> str:
    embedding = get_embedding(query)
    # Query Pinecone for the top 2 matches in the correct namespace
    result = index_ss.query(vector=embedding, top_k=2, namespace=ss_namespace, include_metadata=True)
    if result and result.matches:
        # Concatenate the text of the top matches
        return '\n'.join([m.metadata.get('text', '') for m in result.matches])
    return '[No relevant Shariah document found]'