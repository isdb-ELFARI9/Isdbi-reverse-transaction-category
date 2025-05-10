"""
Transaction Deconstructor Agent
Purpose: Breaks down input reverse transactions into core components and formulates queries.
"""

from typing import Dict, List, Tuple
from pydantic import BaseModel
import google.generativeai as genai
from ..core.config import settings
from ..core.prompts import TRANSACTION_DECONSTRUCTOR_PROMPT

class TransactionAnalysis(BaseModel):
    """Model for detailed transaction analysis."""
    primary_financial_event: str
    key_financial_items: List[str]
    accounting_treatments: List[str]
    transaction_nature: str
    search_keywords: List[str]

class TransactionDeconstructor:
    def __init__(self):
        """Initialize the Transaction Deconstructor agent."""
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=settings.MODEL_NAME,
            generation_config={"temperature": settings.TEMPERATURE}
        )
        
        # Initialize chat
        self.chat = self.model.start_chat(history=[])
        self.chat.send_message(TRANSACTION_DECONSTRUCTOR_PROMPT)

    def _parse_analysis_response(self, response: str) -> TransactionAnalysis:
        """
        Parse the model's response into structured format.
        
        Args:
            response: Raw response from the model
            
        Returns:
            Structured TransactionAnalysis object
        """
        # Split response into sections
        sections = response.split("**")
        
        # Extract primary event
        primary_event = sections[2].strip() if len(sections) > 2 else ""
        
        # Extract key items
        key_items = sections[4].strip().split("\n") if len(sections) > 4 else []
        key_items = [item.strip("- ").strip() for item in key_items if item.strip()]
        
        # Extract accounting treatments
        treatments = sections[6].strip().split("\n") if len(sections) > 6 else []
        treatments = [treat.strip("- ").strip() for treat in treatments if treat.strip()]
        
        # Extract transaction nature
        nature = sections[8].strip() if len(sections) > 8 else ""
        
        # Extract search keywords
        keywords = sections[10].strip().strip("[]").split(",") if len(sections) > 10 else []
        keywords = [kw.strip() for kw in keywords if kw.strip()]
        
        return TransactionAnalysis(
            primary_financial_event=primary_event,
            key_financial_items=key_items,
            accounting_treatments=treatments,
            transaction_nature=nature,
            search_keywords=keywords
        )

    def deconstruct(self, transaction_text: str) -> Dict:
        """
        Deconstruct a transaction into its core components.
        
        Args:
            transaction_text: Raw transaction text including context, adjustments, etc.
            
        Returns:
            Dictionary containing structured analysis
        """
        # Prepare the prompt
        prompt = f"""
        You are an expert financial analyst specializing in AAOIFI standards. Your primary task is to deconstruct financial transaction descriptions to extract key information. This information will be used to identify applicable AAOIFI Financial Accounting Standards (FAS).

        The primary AAOIFI FAS you should keep in mind for understanding the types of transactions common in Islamic finance are those covering:
        *   Partnership Financing (like Musharaka)
        *   Forward Purchase Agreements (like Salam)
        *   Manufacturing/Construction Contracts (like Istisna'a)
        *   Cost-Plus Sales and Deferred Payment Sales (like Murabaha)
        *   Leasing (like Ijarah)

        From the provided transaction text below, please:
        1.  **Identify the Primary Financial Event:** What is the main economic activity or change occurring?
        2.  **List Key Financial Items, Accounts, Contracts & Parties Involved:**
            *   Identify all significant financial elements, assets, liabilities, equity components, revenue, or expense categories.
            *   Note specific contract types if mentioned or inferable.
            *   Identify the roles of parties if discernible.
        3.  **Note Explicit Accounting Treatments:** List any specific accounting actions described.
        4.  **Infer the General Nature of the Transaction/Contract & Underlying Economic Substance:** Based on the event, items, and treatments, what is the fundamental economic activity or type of contractual arrangement involved?

        Transaction Text:
        ---
        {transaction_text}
        ---

        Output your analysis in the following format:

        **Analysis:**
        *   **Primary Financial Event:** [Your inference]
        *   **Key Financial Items, Accounts, Contracts & Parties:** [List]
        *   **Explicit Accounting Treatments:** [List]
        *   **Inferred General Nature of Transaction/Contract:** [Your description]

        **Search Keywords for FAS Lookup:**
        [keyword1, keyword2, keyword3, ...]
        """
        
        # Get response from Gemini
        response = self.chat.send_message(prompt)
        
        # Parse and structure the analysis
        analysis = self._parse_analysis_response(response.text)
        
        # Convert to dictionary for JSON serialization
        return analysis.model_dump() 