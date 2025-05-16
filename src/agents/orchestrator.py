"""
Orchestrator Agent
Purpose: Coordinates the workflow between Transaction Deconstructor, FAS Retriever, Retrieval Summarizer, and FAS Applicability agents.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel
from .transaction_deconstructor import TransactionDeconstructor
from .fas_retriever import FASRetriever, FASDocument
from .retrieval_summarizer import RetrievalSummarizer
from .fas_applicability import FASApplicabilityAgent, FASApplicability

class OrchestratorResult(BaseModel):
    """Model for the complete analysis result."""
    transaction_analysis: Dict
    fas_documents: List[FASDocument]
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
        print(f"Transaction Analysis: {transaction_analysis}")
        
        # Step 2: FAS Retrieval
        print("\n2. Retrieving Relevant FAS Documents...")
        # Use search keywords from transaction analysis for better retrieval
        search_query = " ".join(transaction_analysis.get("search_keywords", []))
        fas_documents = self.fas_retriever.retrieve(
            query=search_query,
            top_n=5  # Get top 5 most relevant documents
        )
        print(f"Retrieved {len(fas_documents)} relevant documents")
        
        # Step 3: FAS Summarization
        print("\n3. Summarizing FAS Findings...")
        # Group documents by their document type for better summarization
        documents_by_type = {}
        for doc in fas_documents:
            if doc.document_type not in documents_by_type:
                documents_by_type[doc.document_type] = []
            documents_by_type[doc.document_type].append(doc)
        
        # Generate summaries for each document type
        fas_summaries = self.retrieval_summarizer.summarize_findings(documents_by_type)
        print(f"Generated summaries for {len(fas_summaries)} document types")
        
        # Step 4: FAS Applicability Analysis
        print("\n4. Analyzing FAS Applicability...")
        # Prepare excerpts for applicability analysis
        fas_excerpts = {}
        for doc in fas_documents:
            # Extract FAS ID from document type (e.g., "FAS_32" -> "FAS 32")
            fas_id = doc.document_type.replace("_", " ")
            if fas_id not in fas_excerpts:
                fas_excerpts[fas_id] = []
            fas_excerpts[fas_id].append(doc.text)
        
        # Analyze applicability using both original transaction and summarized findings
        applicability_list = self.fas_applicability.analyze_applicability(
            original_transaction=transaction_text,
            fas_excerpts=fas_excerpts
        )
        print(f"Analyzed applicability for {len(applicability_list)} FAS standards")
        
        return OrchestratorResult(
            transaction_analysis=transaction_analysis,
            fas_documents=fas_documents,
            fas_summaries=fas_summaries,
            fas_applicability=applicability_list
        )

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
        
        # Print FAS Documents
        print("\n📚 Retrieved FAS Documents:")
        print("=" * 50)
        for doc in result.fas_documents:
            print(f"\n📄 {doc.document_type} - {doc.section_heading}")
            print(f"Relevance Score: {doc.relevance_score:.2f}")
            print("-" * 30)
            print(f"Content:\n{doc.text[:200]}...")  # Print first 200 chars
        
        # Print FAS Summaries
        print("\n📝 FAS Document Summaries:")
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