"""
Test script for Transaction Deconstructor agent.
"""

import sys
import os
import json

# Add the src directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.agents.transaction_deconstructor import TransactionDeconstructor

def test_transaction_deconstructor():
    # Initialize the agent
    deconstructor = TransactionDeconstructor()
    
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
    
    # Deconstruct the transaction
    analysis = deconstructor.deconstruct(transaction)
    
    # Print the analysis in a formatted way
    print("\nTransaction Analysis:")
    print("=" * 50)
    print(f"Primary Financial Event: {analysis['primary_financial_event']}")
    print("\nKey Financial Items:")
    for item in analysis['key_financial_items']:
        print(f"- {item}")
    print("\nAccounting Treatments:")
    for treatment in analysis['accounting_treatments']:
        print(f"- {treatment}")
    print(f"\nTransaction Nature: {analysis['transaction_nature']}")
    print("\nSearch Keywords:")
    print(", ".join(analysis['search_keywords']))
    
    # Print raw JSON for verification
    print("\nRaw JSON Output:")
    print(json.dumps(analysis, indent=2))

if __name__ == "__main__":
    test_transaction_deconstructor() 