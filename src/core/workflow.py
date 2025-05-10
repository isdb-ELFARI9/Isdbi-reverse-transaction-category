"""
LangGraph workflow for FAS analysis system.
"""

from typing import Dict, List, TypedDict, Annotated
from langgraph.graph import Graph, StateGraph
from langgraph.prebuilt import ToolNode
import operator

from ..agents.transaction_deconstructor import TransactionDeconstructor
from ..agents.fas_retriever import FASRetriever
from ..agents.fas_applicability import FASApplicability

class AgentState(TypedDict):
    """State for the agent workflow."""
    transaction_text: str
    components: Dict
    fas_documents: List[Dict]
    results: List[Dict]

def create_workflow(
    transaction_deconstructor: TransactionDeconstructor,
    fas_retriever: FASRetriever,
    fas_applicability: FASApplicability
) -> Graph:
    """
    Create the LangGraph workflow for FAS analysis.
    
    Args:
        transaction_deconstructor: Transaction deconstructor agent
        fas_retriever: FAS retriever agent
        fas_applicability: FAS applicability agent
        
    Returns:
        Configured LangGraph workflow
    """
    # Initialize workflow
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("deconstruct", transaction_deconstructor.deconstruct)
    workflow.add_node("retrieve", fas_retriever.retrieve)
    workflow.add_node("determine", fas_applicability.determine_applicability)
    
    # Define edges
    workflow.add_edge("deconstruct", "retrieve")
    workflow.add_edge("retrieve", "determine")
    
    # Set entry point
    workflow.set_entry_point("deconstruct")
    
    # Compile workflow
    return workflow.compile() 