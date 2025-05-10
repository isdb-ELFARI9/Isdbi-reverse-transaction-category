"""
Test script for the Orchestrator agent.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.agents.orchestrator import Orchestrator

def test_orchestrator():
    """Test the Orchestrator with a sample transaction."""
    # Initialize the Orchestrator
    orchestrator = Orchestrator()
    
    # Sample transaction
    transaction = """
    Al Baraka Bank acquires 100% ownership of GreenTech's equity stake for $1,750,000.
    The transaction involves:
    - Buyout of GreenTech's equity stake
    - Payment of $1,750,000 in cash
    - Recognition of acquisition expense
    - Derecognition of GreenTech's equity
    """
    
    # Run the complete analysis
    result = orchestrator.analyze_transaction(transaction)
    
    # Print the results
    orchestrator.print_analysis(result)

if __name__ == "__main__":
    test_orchestrator() 