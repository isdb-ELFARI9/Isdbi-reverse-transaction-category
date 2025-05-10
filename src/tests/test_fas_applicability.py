"""
Test script for the FAS Applicability Agent.
"""

import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.agents.fas_applicability import FASApplicabilityAgent

def test_fas_applicability():
    """Test the FAS Applicability agent with a sample transaction and FAS excerpts."""
    # Initialize agent
    agent = FASApplicabilityAgent()
    
    # Sample transaction
    transaction = """
    Al Baraka Bank acquires 100% ownership of GreenTech's equity stake for $1,750,000.
    The transaction involves:
    - Buyout of GreenTech's equity stake
    - Payment of $1,750,000 in cash
    - Recognition of acquisition expense
    - Derecognition of GreenTech's equity
    """
    
    # Sample FAS excerpts
    fas_excerpts = {
        "FAS 4": [
            "Musharaka is a partnership where profit is shared in a pre-agreed ratio, while loss is shared in proportion to each partner's share in capital.",
            "The Islamic bank's share in Musharaka capital should be recognized at the time of contracting."
        ],
        "FAS 28": [
            "Murabaha is a sale of goods with a deferred payment, where the seller discloses the cost and markup.",
            "The seller should recognize the sale when the goods are delivered to the buyer."
        ],
        "FAS 32": [
            "Ijarah is a contract of usufruct of assets or services for a consideration.",
            "The lessor should recognize the Ijarah asset at cost and depreciate it over its useful life."
        ]
    }
    
    print("\n=== Testing FAS Applicability Agent ===")
    print("\nTransaction:")
    print(transaction)
    
    # Analyze applicability
    print("\nAnalyzing FAS applicability...")
    applicability_list = agent.analyze_applicability(transaction, fas_excerpts)
    
    # Print results
    print("\nApplicability Analysis Results:")
    agent.print_applicability(applicability_list)

if __name__ == "__main__":
    test_fas_applicability() 