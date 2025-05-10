"""
Orchestrator Agent
Purpose: Coordinates the workflow between Transaction Deconstructor, FAS Retriever, and FAS Applicability agents.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel
from .transaction_deconstructor import TransactionDeconstructor
from .fas_retriever import FASRetriever
from .retrieval_summarizer import RetrievalSummarizer
from .fas_applicability import FASApplicabilityAgent, FASApplicability

class OrchestratorResult(BaseModel):
    """Model for the complete analysis result."""
    transaction_analysis: Dict
    fas_summaries: Dict[str, str]
    fas_applicability: List[FASApplicability]

class Orchestrator:
    def __init__(self):
        """Initialize the Orchestrator with all required agents."""
        self.transaction_deconstructor = TransactionDeconstructor()
        self.fas_retriever = FASRetriever()
        self.retrieval_summarizer = RetrievalSummarizer()
        self.fas_applicability = FASApplicabilityAgent()

    def analyze_transaction(self, transaction_text: str) -> OrchestratorResult:
        """
        Analyze a transaction through the complete agent chain.
        
        Args:
            transaction_text: The original transaction text to analyze
            
        Returns:
            OrchestratorResult containing the complete analysis
        """
        print("\n=== Starting Transaction Analysis ===")
        
        # Step 1: Transaction Deconstruction
        print("\n1. Deconstructing Transaction...")
        transaction_analysis = self.transaction_deconstructor.deconstruct(transaction_text)
        
        # Step 2: FAS Retrieval
        print("\n2. Retrieving Relevant FAS Documents...")
        search_query = self._formulate_search_query(transaction_analysis)
        fas_results = self.fas_retriever.retrieve_across_namespaces(search_query)
        
        # Step 3: FAS Summarization
        print("\n3. Summarizing FAS Findings...")
        fas_summaries = self.retrieval_summarizer.summarize_findings(fas_results)
        
        # Step 4: FAS Applicability Analysis
        print("\n4. Analyzing FAS Applicability...")
        fas_excerpts = self._prepare_fas_excerpts(fas_results)
        applicability_list = self.fas_applicability.analyze_applicability(
            transaction_text,
            fas_excerpts
        )
        
        return OrchestratorResult(
            transaction_analysis=transaction_analysis,
            fas_summaries=fas_summaries,
            fas_applicability=applicability_list
        )

    def _formulate_search_query(self, transaction_analysis: Dict) -> str:
        """
        Formulate a search query from the transaction analysis.
        
        Args:
            transaction_analysis: The analysis from the Transaction Deconstructor
            
        Returns:
            Formulated search query string
        """
        # Extract key components from the analysis
        components = []
        
        # Add primary financial event
        if "primary_financial_event" in transaction_analysis:
            components.append(transaction_analysis["primary_financial_event"])
        
        # Add key financial items
        if "key_financial_items" in transaction_analysis:
            components.extend(transaction_analysis["key_financial_items"])
        
        # Add accounting treatments
        if "accounting_treatments" in transaction_analysis:
            components.extend(transaction_analysis["accounting_treatments"])
        
        # Add transaction nature
        if "transaction_nature" in transaction_analysis:
            components.append(transaction_analysis["transaction_nature"])
        
        # Combine components into a search query
        return " ".join(filter(None, components))

    def _prepare_fas_excerpts(self, fas_results: Dict[str, List]) -> Dict[str, List[str]]:
        """
        Prepare FAS excerpts from retrieval results for applicability analysis.
        
        Args:
            fas_results: Results from FAS Retriever
            
        Returns:
            Dictionary mapping FAS IDs to lists of excerpts
        """
        excerpts = {}
        for namespace, documents in fas_results.items():
            fas_id = namespace.replace("fas_", "FAS ")
            excerpts[fas_id] = [doc.text for doc in documents]
        return excerpts

    def print_analysis(self, result: OrchestratorResult) -> None:
        """
        Print the complete analysis in a formatted way.
        
        Args:
            result: The complete analysis result
        """
        print("\n=== Complete Transaction Analysis ===")
        
        # Print Transaction Analysis
        print("\n📝 Transaction Analysis:")
        print("=" * 50)
        for key, value in result.transaction_analysis.items():
            print(f"\n{key.replace('_', ' ').title()}:")
            if isinstance(value, list):
                for item in value:
                    print(f"- {item}")
            else:
                print(value)
        
        # Print FAS Summaries
        print("\n📚 FAS Document Summaries:")
        print("=" * 50)
        for fas, summary in result.fas_summaries.items():
            print(f"\n📄 {fas}")
            print("-" * 30)
            print(summary)
        
        # Print FAS Applicability
        print("\n📊 FAS Applicability Analysis:")
        print("=" * 50)
        # Sort by probability in descending order
        sorted_applicability = sorted(
            result.fas_applicability,
            key=lambda x: x.probability,
            reverse=True
        )
        for fas in sorted_applicability:
            print(f"\n📈 {fas.fas_id} - {fas.fas_name}")
            print(f"Probability: {fas.probability:.2f}")
            print("-" * 30)
            print(f"Reasoning:\n{fas.reasoning}") 