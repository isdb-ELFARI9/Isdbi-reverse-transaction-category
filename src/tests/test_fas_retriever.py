"""
Test script for FAS Retriever agent.
"""

import sys
import os
import json
from typing import List, Optional, Dict

# Add the src directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.agents.fas_retriever import FASDocument, FASRetriever
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
    results = retriever.retrieve_across_namespaces(query)
    
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

def print_results(results: Dict[str, List[FASDocument]]):
    """
    Print results from retrieve_across_namespaces in an organized way.
    
    Args:
        results: Dictionary of results organized by namespace
    """
    if not results:
        print("No results found.")
        return

    print("\n=== Search Results by Standard ===")
    print("=" * 80)

    for namespace, documents in results.items():
        print(f"\n📚 Standard: {namespace}")
        print("-" * 80)
        
        for i, doc in enumerate(documents, 1):
            print(f"\nResult {i}:")
            print(f"Relevance Score: {doc.relevance_score:.4f}")
            print(f"Document ID: {doc.fas_id}")
            
            # Print metadata if available
            if doc.metadata:
                print("\nMetadata:")
                for key, value in doc.metadata.items():
                    if key != "text_snippet":  # Skip text_snippet as we'll print the full text
                        print(f"  {key}: {value}")
            
            # Print the text content
            print("\nContent:")
            print(f"{doc.text[:500]}...")  # Print first 500 chars
            print("-" * 40)

    print("\n=== End of Results ===")
    print("=" * 80)

if __name__ == "__main__":
    # Run standalone test
    test_standalone_retriever()
   