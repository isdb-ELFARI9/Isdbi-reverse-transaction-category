"""
Pydantic models for the FastAPI endpoints.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class TransactionInput(BaseModel):
    """Input model for transaction analysis request."""
    transaction_text: str = Field(
        ...,
        description="The transaction text to analyze",
        example="Al Baraka Bank acquires 100% ownership of GreenTech's equity stake for $1,750,000."
    )

class TransactionAnalysis(BaseModel):
    """Model for transaction deconstruction results."""
    primary_financial_event: str = Field(..., description="The main financial event in the transaction")
    key_financial_items: List[str] = Field(..., description="List of key financial items involved")
    accounting_treatments: List[str] = Field(..., description="List of accounting treatments")
    transaction_nature: str = Field(..., description="The nature of the transaction")
    search_keywords: List[str] = Field(..., description="Keywords for FAS search")

class FASDocument(BaseModel):
    """Model for FAS document chunks."""
    text: str = Field(..., description="The text content of the document chunk")
    metadata: Dict = Field(..., description="Metadata about the document chunk")
    score: float = Field(..., description="Relevance score of the chunk")

class FASSummary(BaseModel):
    """Model for FAS document summary."""
    fas_id: str = Field(..., description="The FAS identifier (e.g., 'FAS 32')")
    summary: str = Field(..., description="Summary of the FAS document")

class FASApplicability(BaseModel):
    """Model for FAS applicability analysis."""
    fas_id: str = Field(..., description="The FAS identifier (e.g., 'FAS 32')")
    fas_name: str = Field(..., description="The full name of the FAS")
    probability: float = Field(..., description="Probability of applicability (0.0 to 1.0)")
    reasoning: str = Field(..., description="Reasoning for the applicability assessment")

class StepResult(BaseModel):
    """Model for individual step results."""
    step_name: str = Field(..., description="Name of the processing step")
    status: str = Field(..., description="Status of the step (success/error)")
    message: Optional[str] = Field(None, description="Additional message or error details")
    data: Optional[Dict] = Field(None, description="Step-specific data")

class OrchestratorResponse(BaseModel):
    """Complete response model for the orchestrator endpoint."""
    transaction_analysis: TransactionAnalysis = Field(..., description="Results from transaction deconstruction")
    fas_documents: Dict[str, List[FASDocument]] = Field(..., description="Retrieved FAS documents by namespace")
    fas_summaries: List[FASSummary] = Field(..., description="Summaries of FAS documents")
    fas_applicability: List[FASApplicability] = Field(..., description="FAS applicability analysis")
    steps: List[StepResult] = Field(..., description="Results of each processing step")
    processing_time: float = Field(..., description="Total processing time in seconds") 