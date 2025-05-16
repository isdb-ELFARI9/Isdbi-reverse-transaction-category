"""
FAS Applicability Agent
Purpose: Determines the applicability of AAOIFI FAS standards to a given financial transaction.
"""

from typing import Dict, List
from pydantic import BaseModel
from openai import OpenAI
from ..core.config import settings

class FASApplicability(BaseModel):
    """Model for FAS applicability assessment."""
    fas_id: str
    fas_name: str
    probability: float
    reasoning: str

class FASApplicabilityAgent:
    def __init__(self):
        """Initialize the FAS Applicability agent."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Core FAS standards to evaluate
        self.core_fas = {
            "FAS 4": "Musharaka Financing",
            "FAS 28": "Murabaha and Other Deferred Payment Sales",
            "FAS 7": "Salam and Parallel Salam",
            "FAS 10": "Istisna'a and Parallel Istisna'a",
            "FAS 32": "Ijarah"
        }

    def _format_fas_excerpts(self, fas_excerpts: Dict[str, List[str]]) -> str:
        """
        Format FAS excerpts into a structured string for the prompt.
        
        Args:
            fas_excerpts: Dictionary mapping FAS IDs to lists of excerpts
            
        Returns:
            Formatted string of FAS excerpts
        """
        formatted_excerpts = []
        for fas_id, excerpts in fas_excerpts.items():
            formatted_excerpts.append(f"\n=== {fas_id} ===")
            for i, excerpt in enumerate(excerpts, 1):
                formatted_excerpts.append(f"\nExcerpt {i}:\n{excerpt}")
        
        return "\n".join(formatted_excerpts)

    def analyze_applicability(
        self,
        original_transaction: str,
        fas_excerpts: Dict[str, List[str]]
    ) -> List[FASApplicability]:
        """
        Analyze the applicability of FAS standards to a transaction.
        
        Args:
            original_transaction: The original transaction text
            fas_excerpts: Dictionary mapping FAS IDs to lists of excerpts
            
        Returns:
            List of FASApplicability objects
        """
        # Format FAS excerpts
        formatted_excerpts = self._format_fas_excerpts(fas_excerpts)
        
        # Create the prompt
        prompt = f"""You are an expert AAOIFI (Accounting and Auditing Organization for Islamic Financial Institutions) Standards Analyst. Your task is to determine the applicability of specific AAOIFI Financial Accounting Standards (FAS) to a given financial transaction.

Here are relevant FAS findings that may be relevant to the situation ,found from RAG system:

{formatted_excerpts}

Original Transaction:
{original_transaction}

Please analyze the provided information and generate a JSON object containing a list of applicable standards. Each item in the list should be an object with the following keys:
* fas_id: (String) The FAS number (e.g., "FAS 4", "FAS 28")
* fas_name: (String) The full name of the FAS
* probability: (Float) The assigned probability between 0.0 and 1.0
* reasoning: (String) Detailed reasoning for the applicability assessment

For each FAS, consider:
1. Direct relevance to the transaction
2. Specific conditions and criteria mentioned
3. Exceptions or special cases
4. Supporting evidence from the excerpts

Probability ranges:
- 0.9-1.0: Very high probability
- 0.7-0.89: High probability
- 0.5-0.69: Medium probability
- 0.3-0.49: Low probability
- 0.0-0.29: Very low to no probability

Please provide your analysis in the following JSON format:
{{
  "applicable_standards": [
    {{
      "fas_id": "",
      "fas_name": "",
      "probability": ,
      "reasoning": "Detailed reasoning here..."
    }},
    // ... other standards
  ]
}}"""

        try:
            # Get analysis from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are a financial accounting expert specializing in Islamic finance and AAOIFI standards."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more focused and consistent outputs
                max_tokens=2000
            )
            
            # Parse the response
            analysis_text = response.choices[0].message.content.strip()
            
            # Extract the JSON part from the response
            import json
            import re
            
            # Find JSON in the response
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                analysis_json = json.loads(json_match.group())
                return [FASApplicability(**standard) for standard in analysis_json["applicable_standards"]]
            else:
                raise ValueError("Could not find valid JSON in the response")
            
        except Exception as e:
            print(f"Error analyzing FAS applicability: {e}")
            return []

    def print_applicability(self, applicability_list: List[FASApplicability]) -> None:
        """
        Print the applicability analysis in a formatted way.
        
        Args:
            applicability_list: List of FASApplicability objects
        """
        if not applicability_list:
            print("No applicability analysis available.")
            return

        print("\n=== FAS Applicability Analysis ===\n")
        
        # Sort by probability in descending order
        sorted_list = sorted(applicability_list, key=lambda x: x.probability, reverse=True)
        
        for fas in sorted_list:
            print(f"📊 {fas.fas_id} - {fas.fas_name}")
            print(f"Probability: {fas.probability:.2f}")
            print("=" * 50)
            print(f"Reasoning:\n{fas.reasoning}")
            print("\n" + "-" * 50 + "\n") 