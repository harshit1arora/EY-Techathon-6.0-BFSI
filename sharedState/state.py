# sharedState/state.py - COMPLETE
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class OrchestratorState(TypedDict, total=False):
    # Core Identification
    customer_id: Optional[str]
    
    # Workflow Control
    flow_stage: str  # 'start', 'verification', 'negotiation', 'underwriting', 'sanction', 'completed'
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Loan Details
    requested_amount: Optional[int]
    preferred_tenure_months: Optional[int]
    max_interest_rate: Optional[float]
    
    # Negotiated Offer
    negotiated_offer: Dict[str, Any]
    
    # Customer Data
    customer_info: Dict[str, Any]
    credit_score: Any
    
    # Worker Results
    kyc_status: str  # 'pending', 'verified', 'failed'
    underwriting_status: str  # 'pending', 'approved', 'rejected'
    sanction_letter_status: str  # 'pending', 'generated'
    sanction_letter_path: Optional[str]
    
    # Tracking
    last_active_worker: Optional[str]
    waiting_for_user: bool
    offer_accepted: Optional[bool]
    
    # Worker Histories
    sales_messages: Annotated[List[BaseMessage], add_messages]
    verification_messages: Annotated[List[BaseMessage], add_messages]
    underwriting_messages: Annotated[List[BaseMessage], add_messages]
    sanction_messages: Annotated[List[BaseMessage], add_messages]