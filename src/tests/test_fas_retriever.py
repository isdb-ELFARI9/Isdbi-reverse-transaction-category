"""
Test script for FAS Retriever agent.
"""

import sys
import os
import json
from typing import List, Optional, Dict

# Add the src directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.agents.fas_retriever import FASRetriever
from src.agents.transaction_deconstructor import TransactionDeconstructor

def test_standalone_retriever():
    """Test FAS Retriever agent independently."""
    print("\n=== Testing FAS Retriever Standalone ===")
    
    # Initialize the agent
    retriever = FASRetriever()
    
    # Test Case 1: Direct query
    print("\nTest Case 1: Direct Query")
    print("=" * 50)
    query = "Scope of the Standard FAS 28"
    results = retriever.retrieve(query, namespace="fas_32", top_n=5)
    
    print_results(results)
    
    # Test Case 2: Keywords
    print("\nTest Case 2: Keywords")
    print("=" * 50)
    keywords = [
        "equity",
        "buyout",
        "acquisition",
        "derecognition",
        "ownership transfer"
    ]
    results = retriever.retrieve_by_keywords(keywords, top_n=3,namespace="fas_4")
    
    print_results(results)

def test_agent_chain():
    """Test the chain of Transaction Deconstructor → FAS Retriever."""
    print("\n=== Testing Agent 1 → Agent 2 Chain ===")
    
    # Initialize both agents
    deconstructor = TransactionDeconstructor()
    retriever = FASRetriever()
    
    # Example transaction
    transaction = """
    Context: GreenTech exits in Year 3, and Al Baraka Bank buys out its stake.
    Adjustments:
    Buyout Price: $1,750,000
    Bank Ownership: 100%
    Accounting Treatment:
    Derecognition of GreenTech's equity
    Recognition of acquisition expense
    Journal Entry for Buyout:
    Dr. GreenTech Equity
    Cr. Cash
    $1,750,000
    $1,750,000
    """
    
    # Step 1: Get analysis from Agent 1
    print("\nStep 1: Transaction Analysis from Agent 1")
    print("=" * 50)
    analysis = deconstructor.deconstruct(transaction)
    
    # Print Agent 1's analysis
    print("\nTransaction Analysis:")
    print(f"Primary Event: {analysis['primary_financial_event']}")
    print("\nKey Financial Items:")
    for item in analysis['key_financial_items']:
        print(f"- {item}")
    print("\nAccounting Treatments:")
    for treatment in analysis['accounting_treatments']:
        print(f"- {treatment}")
    print(f"\nTransaction Nature: {analysis['transaction_nature']}")
    
    # Step 2: Formulate search query from Agent 1's output
    print("\nStep 2: Formulating Search Query")
    print("=" * 50)
    
    # Extract key terms for search
    search_terms = []
    
    # Add primary event terms
    if analysis['primary_financial_event']:
        search_terms.append(analysis['primary_financial_event'])
    
    # Add key financial items
    search_terms.extend(analysis['key_financial_items'])
    
    # Add accounting treatments
    search_terms.extend(analysis['accounting_treatments'])
    
    # Add transaction nature
    if analysis['transaction_nature']:
        search_terms.append(analysis['transaction_nature'])
    
    # Clean and format search terms
    search_terms = [term.strip() for term in search_terms if term.strip()]
    search_terms = list(set(search_terms))  # Remove duplicates
    
    print("\nFormulated Search Terms:")
    for term in search_terms:
        print(f"- {term}")
    
    # Step 3: Use Agent 2 to retrieve relevant FAS documents
    print("\nStep 3: Retrieving Relevant FAS Documents")
    print("=" * 50)
    results = retriever.retrieve_by_keywords(search_terms, top_n=5)
    
    print_results(results)

def print_results(results):
    """Helper function to print search results."""
    for i, doc in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"FAS ID: {doc.fas_id}")
        print(f"Relevance Score: {doc.relevance_score:.4f}")
        print(f"Text: {doc.text[:200]}...")  # Print first 200 chars
        if doc.metadata:
            print("Metadata:", json.dumps(doc.metadata, indent=2))

if __name__ == "__main__":
    # Run standalone test
    test_standalone_retriever()
   