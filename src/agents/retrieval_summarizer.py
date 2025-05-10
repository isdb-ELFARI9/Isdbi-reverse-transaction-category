"""
Retrieval Summarizer Agent
Purpose: Summarizes findings from FAS documents retrieved by FASRetriever.
"""

from typing import Dict, List
from openai import OpenAI
from ..core.config import settings
from .fas_retriever import FASDocument

class RetrievalSummarizer:
    def __init__(self):
        """Initialize the Retrieval Summarizer agent."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def _summarize_fas_findings(self, documents: List[FASDocument]) -> str:
        """
        Summarize findings from a list of FAS documents.
        
        Args:
            documents: List of FASDocument objects from a specific FAS
            
        Returns:
            Summary of the findings
        """
        if not documents:
            return "No relevant findings found."

        # Prepare context from documents
        context = "\n\n".join([
            f"Document {i+1} (Relevance: {doc.relevance_score:.2f}):\n{doc.text}"
            for i, doc in enumerate(documents)
        ])

        # Create prompt for summarization
        prompt = f"""Please analyze the following FAS document excerpts and provide a concise summary of the key findings. 
        Focus on the most relevant and important information that would be useful for understanding the accounting treatment.

        Document excerpts:
        {context}

        Please provide a clear and concise summary that:
        1. Highlights the key accounting principles or requirements
        2. Identifies any specific conditions or criteria mentioned
        3. Notes any important exceptions or special cases
        4. Maintains technical accuracy while being understandable

        Summary:"""

        try:
            # Get summary from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial accounting expert specializing in Islamic finance and FAS standards."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more focused and consistent outputs
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Error generating summary."

    def summarize_findings(self, results_by_namespace: Dict[str, List[FASDocument]]) -> Dict[str, str]:
        """
        Summarize findings from all FAS documents across namespaces.
        
        Args:
            results_by_namespace: Dictionary mapping FAS namespaces to their retrieved documents
            
        Returns:
            Dictionary mapping FAS namespaces to their summaries
        """
        summaries = {}
        
        for namespace, documents in results_by_namespace.items():
            # Get FAS number from namespace (e.g., "fas_32" -> "FAS 32")
            fas_number = namespace.replace("fas_", "FAS ")
            
            # Generate summary for this FAS
            summary = self._summarize_fas_findings(documents)
            summaries[fas_number] = summary
            
        return summaries

    def print_summaries(self, summaries: Dict[str, str]) -> None:
        """
        Print the summaries in a formatted way.
        
        Args:
            summaries: Dictionary of FAS summaries
        """
        if not summaries:
            print("No summaries available.")
            return

        print("\n=== FAS Document Summaries ===\n")
        
        for fas, summary in summaries.items():
            print(f"📄 {fas}")
            print("=" * 50)
            print(summary)
            print("\n" + "-" * 50 + "\n") 