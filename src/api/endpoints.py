"""
FastAPI endpoints for the FAS analysis system.
"""

import time
from typing import Dict, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.api.models import (
    TransactionInput,
    OrchestratorResponse,
    TransactionAnalysis,
    FASDocument,
    FASSummary,
    FASApplicability,
    StepResult
)
from src.agents.orchestrator import Orchestrator

# Define models
class FASDocument(BaseModel):
    """Model for FAS document chunks."""
    fas_id: str
    text: str
    relevance_score: float
    metadata: Dict = {}

class FASSummary(BaseModel):
    """Model for FAS summaries."""
    fas_id: str
    summary: str

class FASApplicability(BaseModel):
    """Model for FAS applicability analysis."""
    fas_id: str
    fas_name: str
    probability: float
    reasoning: str

class TransactionAnalysis(BaseModel):
    """Model for transaction analysis results."""
    primary_financial_event: str
    key_financial_items: List[str]
    accounting_treatments: List[str]
    transaction_nature: str

class StepResult(BaseModel):
    """Model for step execution results."""
    step_name: str
    status: str
    data: Dict = {}
    message: str = ""

class TransactionInput(BaseModel):
    """Input model for transaction analysis."""
    transaction_text: str

class OrchestratorResponse(BaseModel):
    """Response model for the complete analysis."""
    transaction_analysis: TransactionAnalysis
    fas_documents: Dict[str, List[FASDocument]]
    fas_summaries: List[FASSummary]
    fas_applicability: List[FASApplicability]
    steps: List[StepResult]
    processing_time: float

router = APIRouter()
orchestrator = Orchestrator()

@router.post("/analyze-transaction", response_model=OrchestratorResponse)
async def analyze_transaction(input_data: TransactionInput) -> OrchestratorResponse:
    """
    Analyze a financial transaction using the complete agent chain.
    
    Args:
        input_data: Transaction text to analyze
        
    Returns:
        Complete analysis results including all intermediate steps
    """
    start_time = time.time()
    steps = []
    
    try:
        # Step 1: Transaction Deconstruction
        try:
            transaction_analysis = orchestrator.transaction_deconstructor.deconstruct(
                input_data.transaction_text
            )
            steps.append(StepResult(
                step_name="Transaction Deconstruction",
                status="success",
                data=transaction_analysis
            ))
        except Exception as e:
            steps.append(StepResult(
                step_name="Transaction Deconstruction",
                status="error",
                message=str(e)
            ))
            raise HTTPException(status_code=500, detail=f"Transaction deconstruction failed: {str(e)}")
        
        # Step 2: FAS Retrieval
        try:
            search_query = orchestrator._formulate_search_query(transaction_analysis)
            fas_results = orchestrator.fas_retriever.retrieve_across_namespaces(search_query)
            steps.append(StepResult(
                step_name="FAS Retrieval",
                status="success",
                data={"query": search_query, "results_count": len(fas_results)}
            ))
        except Exception as e:
            steps.append(StepResult(
                step_name="FAS Retrieval",
                status="error",
                message=str(e)
            ))
            raise HTTPException(status_code=500, detail=f"FAS retrieval failed: {str(e)}")
        
        # Step 3: FAS Summarization
        try:
            fas_summaries = orchestrator.retrieval_summarizer.summarize_findings(fas_results)
            steps.append(StepResult(
                step_name="FAS Summarization",
                status="success",
                data={"summaries_count": len(fas_summaries)}
            ))
        except Exception as e:
            steps.append(StepResult(
                step_name="FAS Summarization",
                status="error",
                message=str(e)
            ))
            raise HTTPException(status_code=500, detail=f"FAS summarization failed: {str(e)}")
        
        # Step 4: FAS Applicability Analysis
        try:
            fas_excerpts = orchestrator._prepare_fas_excerpts(fas_results)
            applicability_list = orchestrator.fas_applicability.analyze_applicability(
                input_data.transaction_text,
                fas_excerpts
            )
            steps.append(StepResult(
                step_name="FAS Applicability Analysis",
                status="success",
                data={"applicability_count": len(applicability_list)}
            ))
        except Exception as e:
            steps.append(StepResult(
                step_name="FAS Applicability Analysis",
                status="error",
                message=str(e)
            ))
            raise HTTPException(status_code=500, detail=f"FAS applicability analysis failed: {str(e)}")
        
        # Convert FASApplicability objects to dictionaries
        applicability_dicts = [
            {
                "fas_id": item.fas_id,
                "fas_name": item.fas_name,
                "probability": item.probability,
                "reasoning": item.reasoning
            }
            for item in applicability_list
        ]
        
        # Prepare the response
        return OrchestratorResponse(
            transaction_analysis=TransactionAnalysis(**transaction_analysis),
            fas_documents={
                namespace: [
                    FASDocument(
                        fas_id=doc.fas_id,
                        text=doc.text,
                        relevance_score=doc.relevance_score,
                        metadata=doc.metadata or {}
                    ) for doc in docs
                ] for namespace, docs in fas_results.items()
            },
            fas_summaries=[
                FASSummary(
                    fas_id=fas_id,
                    summary=summary
                ) for fas_id, summary in fas_summaries.items()
            ],
            fas_applicability=[FASApplicability(**item) for item in applicability_dicts],
            steps=steps,
            processing_time=time.time() - start_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}") 