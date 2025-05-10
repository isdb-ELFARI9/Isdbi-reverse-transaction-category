"""
Test script for the Retrieval Summarizer agent.
"""

import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.agents.fas_retriever import FASRetriever
from src.agents.retrieval_summarizer import RetrievalSummarizer

def test_retrieval_summarizer():
    """Test the Retrieval Summarizer agent with a sample query."""
    # Initialize agents
    retriever = FASRetriever()
    summarizer = RetrievalSummarizer()
    
    # Sample query
    query = "a lessee shall account for non-Ijarah"
    
    print("\n=== Testing Retrieval Summarizer ===")
    print(f"Query: {query}")
    
    # Step 1: Retrieve relevant documents
    print("\n1. Retrieving relevant documents...")
    results = retriever.retrieve_across_namespaces(query)
    
    # Step 2: Generate summaries
    print("\n2. Generating summaries...")
    summaries = summarizer.summarize_findings(results)
    
    # Step 3: Print summaries
    print("\n3. Printing summaries...")
    summarizer.print_summaries(summaries)

if __name__ == "__main__":
    test_retrieval_summarizer() 