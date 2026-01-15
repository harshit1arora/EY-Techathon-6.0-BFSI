# workerAgents/sales.py - HYBRID CONVERSATIONAL SALES AGENT
import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from mcp.client.session import ClientSession
from sharedState.state import OrchestratorState

# Configure logging for production audit trail
os.makedirs("storage", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='storage/mcp_audit.log'
)
logger = logging.getLogger("SalesAgent")

load_dotenv()

class NegotiatedOffer(BaseModel):
    customer_id: str = Field(description="Unique identifier for the customer")
    approved_amount: int = Field(description="Amount upto which NBFC is allowed to give up personal loan")
    tenure_months: int = Field(description="Period in months for which loan is to be taken")
    interest_rate: float = Field(description="Interest rate upto which loan can be approved")
    justification: str = Field(description="Justification for the approval or rejection of deal")
    persuasive_message: str = Field(description="A friendly and persuasive message for the customer")


async def build_sales_graph(session: ClientSession):
    logger.info("🛒 Building Hybrid Sales Graph...")
    
    llm = ChatOllama(model="llama3.1", temperature=0.2)
    structured_llm = llm.with_structured_output(NegotiatedOffer)

    # PRIORITY 2: VALIDATION NODE
    async def validate_inputs(state: OrchestratorState):
        logger.info("🔍 Validating inputs for Sales Agent...")
        customer_id = state.get("customer_id")
        requested_amount = state.get("requested_amount")
        
        if not customer_id:
            logger.warning("⚠️ Missing customer_id in state")
            return {"error_message": "Missing Customer ID"}
        
        if not requested_amount:
            logger.warning(f"⚠️ Missing requested_amount for {customer_id}")
            return {"error_message": "Loan amount not specified. Please tell me how much you need."}

        return {"error_message": None}

    # NODE 1 → FETCH CUSTOMER INFO
    async def fetch_customer_info(state: OrchestratorState) -> OrchestratorState:
        if state.get("customer_info"):
            return {}
            
        cid = str(state.get("customer_id", ""))
        logger.info(f"📡 Fetching info for {cid}")
        
        try:
            result = await session.call_tool("get_customer_info", arguments={"customer_id": cid})
            data = json.loads(result.content[0].text)
            cust_info = data.get("result", data)
            logger.info(f"✅ Retrieved info for {cust_info.get('name', cid)}")
            return {"customer_info": cust_info}
        except Exception as e:
            logger.error(f"❌ Failed to fetch info for {cid}: {str(e)}")
            return {"customer_info": {"error": str(e)}}

    # NODE 2 → HYBRID CONVERSATION & NEGOTIATION
    async def hybrid_sales_node(state: OrchestratorState):
        if state.get("error_message"):
            return {}

        customer = state.get("customer_info", {})
        requested = state.get("requested_amount", 0)
        tenure = state.get("preferred_tenure_months", 36)
        customer_name = customer.get("name", "Valued Customer")
        
        logger.info(f"🤝 Negotiating offer for {customer_name} ({state.get('customer_id')})")

        # Business Rules Logic (Pre-calculation for LLM guidance)
        pre_approved = customer.get('pre_approved_limit', 100000)
        credit_score = customer.get('credit_score', 700)
        
        # Rule: Max 2x pre-approved
        max_limit = pre_approved * 2
        safe_amount = min(requested, max_limit)
        
        # Rule: Interest rate based on credit score
        if credit_score >= 750: base_rate = 10.99
        elif credit_score >= 700: base_rate = 12.50
        else: base_rate = 14.99

        prompt = f"""
        You are a persuasive Sales Agent for Tata Capital. 
        Your goal is to negotiate a loan deal and answer customer questions professionally.

        CUSTOMER PROFILE:
        - Name: {customer_name}
        - Salary: ₹{customer.get('salary_monthly', 'N/A')}/month
        - Pre-approved Limit: ₹{pre_approved:,}
        - Credit Score: {credit_score}

        BUSINESS RULES (STRICT):
        1. Max Loan Amount: ₹{max_limit:,} (2x pre-approved limit)
        2. Interest Rate: {base_rate}% p.a.
        3. Benefits to Highlight: Instant approval, No hidden charges, Quick disbursal.

        CURRENT REQUEST:
        - Amount: ₹{requested:,}
        - Tenure: {tenure} months

        TASK:
        1. If the user has questions or objections in history, address them professionally.
        2. Provide a structured loan offer.
        3. Generate a friendly, persuasive message (max 3 sentences).

        CONVERSATION HISTORY:
        {state.get("messages", [])}
        """

        # Session Integration: We use both shared 'messages' for context and 'sales_messages' for internal state
        existing_history = state.get("sales_messages", [])
        
        try:
            # Use structured output for the negotiation data
            # Combine system prompt with internal history and general messages for full context
            context_messages = [SystemMessage(content=prompt)] + existing_history
            result = await structured_llm.ainvoke(context_messages)
            negotiated_offer = result.model_dump()
            
            # Ensure rules are enforced (LLM might hallucinate)
            negotiated_offer["approved_amount"] = min(negotiated_offer["approved_amount"], max_limit)
            negotiated_offer["interest_rate"] = max(negotiated_offer["interest_rate"], base_rate)
            
        except Exception as e:
            logger.error(f"❌ Sales LLM failed: {e}")
            # Fallback
            negotiated_offer = {
                "customer_id": state.get("customer_id"),
                "approved_amount": int(safe_amount),
                "tenure_months": int(tenure),
                "interest_rate": float(base_rate),
                "justification": "Calculated based on pre-approved limits and credit score (fallback).",
                "persuasive_message": f"Hi {customer_name}, I've got a great deal for you! Based on your profile, we can offer ₹{safe_amount:,} at {base_rate}% interest."
            }

        negotiated_offer["offer_generated"] = True
        negotiated_offer["offer_accepted"] = False
        
        msg_content = (
            f"🤝 **Personalized Loan Offer**\n\n"
            f"{negotiated_offer['persuasive_message']}\n\n"
            f"💰 **Amount**: ₹{negotiated_offer['approved_amount']:,}\n"
            f"📈 **Rate**: {negotiated_offer['interest_rate']}% p.a.\n"
            f"📅 **Tenure**: {negotiated_offer['tenure_months']} months\n\n"
            f"Would you like to proceed with this offer? Type 'proceed' to start verification."
        )
        
        public_msg = AIMessage(content=msg_content, name="SalesAgent")
        
        logger.info(f"✅ Sales offer generated for {customer_name}: ₹{negotiated_offer['approved_amount']} @ {negotiated_offer['interest_rate']}%")

        # Update both shared and internal history
        new_sales_history = existing_history + [AIMessage(content=json.dumps(negotiated_offer))]
        
        return {
            "negotiated_offer": negotiated_offer,
            "messages": [public_msg],
            "sales_messages": new_sales_history,
            "last_active_worker": "sales",
            "flow_stage": "negotiation",
            "waiting_for_user": True
        }

    # NODE 3 → FINAL STATUS NODE
    async def final_status_node(state: OrchestratorState):
        if state.get("error_message"):
            err = state.get("error_message")
            return {
                "messages": [AIMessage(content=f"👋 **Sales**: {err}", name="SalesAgent")],
                "flow_stage": "start",
                "waiting_for_user": True
            }
        
        return {
            "last_active_worker": "sales",
            "flow_stage": "negotiation",
            "waiting_for_user": True
        }

    # BUILD GRAPH
    graph = StateGraph(OrchestratorState)
    
    graph.add_node("validate", validate_inputs)
    graph.add_node("fetch_info", fetch_customer_info)
    graph.add_node("sales_logic", hybrid_sales_node)
    graph.add_node("final", final_status_node)

    graph.add_edge(START, "validate")
    
    def after_validate(state: OrchestratorState):
        if state.get("error_message"):
            return "final"
        return "fetch_info"

    graph.add_conditional_edges("validate", after_validate, {
        "final": "final",
        "fetch_info": "fetch_info"
    })
    
    graph.add_edge("fetch_info", "sales_logic")
    graph.add_edge("sales_logic", "final")
    graph.add_edge("final", END)

    logger.info("🛒 Sales Graph built successfully!")
    return graph.compile()
