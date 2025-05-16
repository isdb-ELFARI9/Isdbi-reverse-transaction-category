"""
Test script for the Orchestrator agent.
"""

import sys
from pathlib import Path
import unittest
from typing import Dict, List

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.agents.orchestrator import Orchestrator, OrchestratorResult

class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        print("\n=== Setting up test environment ===")
        self.orchestrator = Orchestrator()
        print("Orchestrator initialized successfully")

    def test_default_transaction(self):
        """Test the Orchestrator with a default transaction scenario."""
        print("\n=== Testing Default Transaction Scenario ===")
        
        # Sample transaction
        transaction = """
        Context: The client pays all outstanding amounts on time, reducing expected losses. 
Adjustments:  
Loss provision reversed. 
Recognized revenue adjusted. 
Accounting Treatment:  
Reduction in impairment expense. 
Recognition of full contract revenue. 
Journal Entry for Loss Provision Reversal: 
Dr. Allowance for Impairment    $500,000   
Cr. Provision for Losses    $500,000   
This restores revenue after full payment. 
        """
        print(f"\nTransaction Text:\n{transaction}")
        
        # Run the complete analysis
        print("\nStarting transaction analysis...")
        result = self.orchestrator.analyze_transaction(transaction)
        
        # Verify results
        print("\nVerifying results...")
        self.assertIsInstance(result, OrchestratorResult)
        self.assertIn("transaction_analysis", result.__dict__)
        self.assertIn("fas_documents", result.__dict__)
        self.assertIn("fas_summaries", result.__dict__)
        self.assertIn("fas_applicability", result.__dict__)
        
        # Print detailed results
        print("\n=== Detailed Analysis Results ===")
        self.orchestrator.print_analysis(result)
        
        print("\nDefault transaction test completed successfully")



def main():
    """Run the test suite."""
    print("\n=== Starting Orchestrator Test Suite ===")
    unittest.main(verbosity=2)

if __name__ == "__main__":
    main() 