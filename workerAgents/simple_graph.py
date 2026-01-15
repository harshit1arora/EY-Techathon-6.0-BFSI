# orchestrator/simple_graph.py - ULTRA SIMPLE WORKING VERSION
import os
import json
import re
from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

from sharedState.state import OrchestratorState
from workerAgents.sales import build_sales_graph
from workerAgents.verification import build_verification_graph
from workerAgents.underwriting import build_underwriting_graph
from workerAgents.sanction import build_sanction_graph

async def build_orchestrator(session):
    print("🧠 Building SIMPLE Orchestrator...")
    
    # 1. Initialize Worker Graphs
    sales_node = await build_sales_graph(session)
    verification_node = await build_verification_graph(session)
    underwriting_node = await build_underwriting_graph(session)
    sanction_node = await build_sanction_graph(session)

    # 2. SIMPLE Master Node that NEVER crashes
    async def master_node(state: OrchestratorState):
        print(f"\n[MASTER] Processing...")
        
        # Get last user message
        last_user_msg = ""
        if state.get("messages"):
            for msg in reversed(state["messages"]):
                if isinstance(msg, HumanMessage):
                    last_user_msg = msg.content
                    break
        
        print(f"[MASTER] User: '{last_user_msg}'")
        
        updates = {"last_active_worker": "master"}
        response_msg = ""
        
        try:
            if last_user_msg:
                msg_lower = last_user_msg.lower()
                
                # 1. Extract Customer ID
                if "cust" in msg_lower:
                    match = re.search(r'cust\s*(\d+)', msg_lower)
                    if match:
                        cid = f"CUST{match.group(1).zfill(3)}"
                        updates["customer_id"] = cid
                        updates["flow_stage"] = "verification"
                        response_msg = f"✅ Got your Customer ID: {cid}. Starting verification."
                        print(f"[MASTER] ✓ Extracted CID: {cid}")
                    else:
                        response_msg = "Please provide a valid Customer ID like CUST001."
                
                # 2. Extract Loan Amount
                elif any(word in msg_lower for word in ["loan", "amount", "need", "want", "rupees", "₹"]):
                    match = re.search(r'(\d+)', last_user_msg)
                    if match:
                        amount = int(match.group(1))
                        updates["requested_amount"] = amount
                        response_msg = f"✅ Got it! You need ₹{amount}. For how many months?"
                        print(f"[MASTER] ✓ Extracted amount: ₹{amount}")
                    else:
                        response_msg = "How much loan do you need? (e.g., 150000)"
                
                # 3. Extract Tenure
                elif any(word in msg_lower for word in ["month", "year", "for"]):
                    match = re.search(r'(\d+)\s*(?:months?|years?)', msg_lower)
                    if match:
                        tenure = int(match.group(1))
                        if "year" in msg_lower:
                            tenure *= 12
                        updates["preferred_tenure_months"] = tenure
                        response_msg = f"✅ {tenure} months. Let me check your eligibility."
                        print(f"[MASTER] ✓ Extracted tenure: {tenure} months")
                    else:
                        response_msg = "For how many months? (e.g., 12 months)"
                
                # 4. Default response
                else:
                    if not state.get("customer_id"):
                        response_msg = "👋 Hello! Please provide your Customer ID to get started."
                    else:
                        response_msg = "How can I help you further?"
            
            else:
                # First message
                response_msg = "👋 Hello! Welcome to Tata Capital. Please provide your Customer ID (e.g., CUST001)."
                updates["flow_stage"] = "start"
                
        except Exception as e:
            print(f"[MASTER] ERROR: {e}")
            response_msg = "I encountered an issue. Let's start fresh. Please provide your Customer ID."
            updates["flow_stage"] = "start"
        
        updates["messages"] = [AIMessage(content=response_msg)]
        return updates

    # 3. SIMPLE Router
    def deterministic_router(state: OrchestratorState) -> str:
        print(f"\n[ROUTER] Checking state...")
        
        # Get state with defaults
        customer_id = state.get("customer_id")
        kyc_status = state.get("kyc_status", "pending")
        negotiated_offer = state.get("negotiated_offer", {})
        offer_generated = negotiated_offer.get("offer_generated", False)
        offer_accepted = negotiated_offer.get("offer_accepted", False)
        uw_status = state.get("underwriting_status", "pending")
        sanction_status = state.get("sanction_letter_status", "pending")
        
        print(f"  CID: {customer_id}, KYC: {kyc_status}")
        
        # Simple decision tree
        if not customer_id:
            print("  -> master (need CID)")
            return "master"
        
        if customer_id and kyc_status == "pending":
            print("  -> verification")
            return "verification"
        
        if kyc_status == "verified" and not offer_generated:
            if state.get("requested_amount") and state.get("preferred_tenure_months"):
                print("  -> sales")
                return "sales"
            else:
                print("  -> master (need details)")
                return "master"
        
        if offer_generated and offer_accepted and uw_status == "pending":
            print("  -> underwriting")
            return "underwriting"
        
        if uw_status == "approved" and sanction_status != "generated":
            print("  -> sanction")
            return "sanction"
        
        print("  -> master (default)")
        return "master"

    # 4. Build Graph
    workflow = StateGraph(OrchestratorState)
    
    workflow.add_node("master", master_node)
    workflow.add_node("sales", sales_node)
    workflow.add_node("verification", verification_node)
    workflow.add_node("underwriting", underwriting_node)
    workflow.add_node("sanction", sanction_node)
    
    workflow.add_edge(START, "master")
    
    workflow.add_conditional_edges(
        "master",
        deterministic_router,
        {
            "master": "master",
            "sales": "sales",
            "verification": "verification",
            "underwriting": "underwriting",
            "sanction": "sanction",
            END: END
        }
    )
    
    workflow.add_edge("sales", "master")
    workflow.add_edge("verification", "master")
    workflow.add_edge("underwriting", "master")
    workflow.add_edge("sanction", "master")
    
    print("✅ SIMPLE Orchestrator built successfully!")
    return workflow.compile()