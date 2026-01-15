# orchestrator/graph.py - FIXED VERSION WITH AUTO-KYC
import os
import json
import re
from typing import Literal, Optional, List, Dict, Any
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

from sharedState.state import OrchestratorState
from workerAgents.sales import build_sales_graph
from workerAgents.verification import build_verification_graph
from workerAgents.underwriting import build_underwriting_graph
from workerAgents.sanction import build_sanction_graph

async def build_orchestrator(session):
    print("🧠 Building Orchestrator Graph...")
    
    # 1. Initialize Worker Graphs
    sales_node = await build_sales_graph(session)
    verification_node = await build_verification_graph(session)
    underwriting_node = await build_underwriting_graph(session)
    sanction_node = await build_sanction_graph(session)

    # 2. MASTER NODE - WITH AUTO-KYC FIX
    async def master_node(state: OrchestratorState):
        print(f"\n[MASTER] Processing...")
        
        # CRITICAL: If a worker already set waiting_for_user, don't re-process
        if state.get("waiting_for_user") and state.get("last_active_worker") != "master":
            print(f"[MASTER] Worker {state.get('last_active_worker')} already set waiting_for_user. Passing through.")
            return state

        # CRITICAL: Start with existing state to preserve data
        updates = state.copy()
        
        # Get the LAST message in conversation
        messages = state.get("messages", [])
        last_user_msg = ""
        
        if messages:
            # Find the most recent human message
            for msg in reversed(messages):
                if isinstance(msg, HumanMessage):
                    last_user_msg = msg.content
                    break
        
        print(f"[MASTER] Last user message: '{last_user_msg}'")
        print(f"[MASTER] Current state - CID: {state.get('customer_id')}, KYC: {state.get('kyc_status')}, Amount: {state.get('requested_amount')}")
        
        # If there's no user message, just greet
        if not last_user_msg:
            updates["flow_stage"] = "start"
            updates["last_active_worker"] = "master"
            updates["messages"] = [AIMessage(content="👋 Hello! Welcome to Tata Capital. Please provide your Customer ID (e.g., CUST001).")]
            updates["waiting_for_user"] = True
            return updates
        
        # Process the user message
        extracted_something = False
        response_msg_parts = []
        
        try:
            msg_lower = last_user_msg.lower()
            
            # 1. Extract Customer ID
            if "cust" in msg_lower and not state.get("customer_id"):
                match = re.search(r'cust\s*(\d+)', msg_lower)
                if match:
                    cid = f"CUST{match.group(1).zfill(3)}"
                    updates["customer_id"] = cid
                    updates["kyc_status"] = "pending" # Set to pending to trigger Verification Agent
                    response_msg_parts.append(f"✅ Customer ID {cid} identified.")
                    extracted_something = True

            # 2. Extract Loan Amount
            if any(word in msg_lower for word in ["loan", "amount", "need", "want", "rupees", "₹", "lakh", "thousand"]) or re.search(r'\d+', msg_lower):
                if not updates.get("requested_amount") and state.get("customer_id") or updates.get("customer_id"):
                    numbers = re.findall(r'(\d+(?:,\d+)*(?:\.\d+)?)', last_user_msg)
                    if numbers:
                        # Filter out numbers that look like Customer IDs (e.g. 001)
                        # We'll take the largest number that isn't the CID
                        amount_str = max(numbers, key=lambda x: float(x.replace(',', '')))
                        amount = float(amount_str.replace(',', ''))
                        
                        if "lakh" in msg_lower:
                            amount *= 100000
                        
                        if amount > 1000: # Simple heuristic to avoid small numbers
                            updates["requested_amount"] = int(amount)
                            response_msg_parts.append(f"✅ Loan amount ₹{int(amount):,} noted.")
                            extracted_something = True

            # 3. Extract Tenure
            if any(word in msg_lower for word in ["month", "year"]):
                match = re.search(r'(\d+)\s*(?:months?|years?)', msg_lower)
                if match:
                    tenure = int(match.group(1))
                    if "year" in msg_lower:
                        tenure *= 12
                    updates["preferred_tenure_months"] = tenure
                    response_msg_parts.append(f"✅ Tenure {tenure} months noted.")
                    extracted_something = True

            # 4. Check for offer acceptance
            if any(word in msg_lower for word in ["yes", "ok", "accept", "proceed", "i accept", "agree"]):
                if state.get("negotiated_offer", {}).get("offer_generated"):
                    updates["offer_accepted"] = True
                    updates["flow_stage"] = "underwriting"
                    response_msg_parts.append("✅ Offer accepted! Processing underwriting...")
                    extracted_something = True

            # Construct final response
            if extracted_something:
                response_msg = " ".join(response_msg_parts)
                # Check what's missing
                if not updates.get("customer_id") and not state.get("customer_id"):
                    response_msg += " Please provide your Customer ID."
                elif not updates.get("requested_amount") and not state.get("requested_amount"):
                    response_msg += " How much loan do you need?"
                elif not updates.get("preferred_tenure_months") and not state.get("preferred_tenure_months"):
                    response_msg += " For how many months?"
                elif updates.get("preferred_tenure_months") and not state.get("offer_accepted"):
                    response_msg += " Let me generate an offer for you."
            else:
                # Default logic if nothing extracted
                if not state.get("customer_id"):
                    response_msg = "👋 Welcome! Please provide your Customer ID (e.g., CUST001)."
                elif not state.get("requested_amount"):
                    response_msg = "How much loan do you need? (e.g., 500000)"
                elif not state.get("preferred_tenure_months"):
                    response_msg = "For how many months would you like the loan?"
                else:
                    response_msg = "How can I help you today?"

                
        except Exception as e:
            print(f"[MASTER] ERROR: {e}")
            response_msg = "I encountered an issue. Let's start fresh. Please provide your Customer ID."
            updates["flow_stage"] = "start"
            updates["debug_stage"] = "error"
        
        # Update state
        updates["last_active_worker"] = "master"
        
        # Decide if we need to wait for user
        # If we have everything needed for sales but haven't run sales yet, don't wait
        if state.get("sanction_letter_status") == "generated":
            updates["waiting_for_user"] = True
            print("[MASTER] Loan process completed. Waiting for user.")
            # Don't add a new message if sanction just finished
            if state.get("last_active_worker") == "sanction":
                 return {"waiting_for_user": True}
        
        elif (updates.get("customer_id") or state.get("customer_id")) and \
           (updates.get("kyc_status") == "verified" or state.get("kyc_status") == "verified") and \
           (updates.get("requested_amount") or state.get("requested_amount")) and \
           (updates.get("preferred_tenure_months") or state.get("preferred_tenure_months")) and \
           not state.get("negotiated_offer", {}).get("offer_generated"):
            updates["waiting_for_user"] = False
            print("[MASTER] All data present, proceeding to Sales...")
        # If we just got CID and need verification, don't wait
        elif (updates.get("customer_id") or state.get("customer_id")) and \
             (updates.get("kyc_status") == "pending" or state.get("kyc_status") == "pending"):
            # Only auto-proceed to verification if we just got the CID
            if updates.get("customer_id"):
                updates["waiting_for_user"] = False
                print("[MASTER] CID present, proceeding to Verification...")
            else:
                updates["waiting_for_user"] = True
        # If offer just accepted, proceed to underwriting
        elif (updates.get("offer_accepted") or state.get("offer_accepted")) and \
             state.get("underwriting_status", "pending") == "pending":
            updates["waiting_for_user"] = False
            print("[MASTER] Offer accepted, proceeding to Underwriting...")
        # If underwriting approved, proceed to sanction
        elif (updates.get("underwriting_status") == "approved" or state.get("underwriting_status") == "approved") and \
             state.get("sanction_letter_status", "pending") == "pending":
            updates["waiting_for_user"] = False
            print("[MASTER] Underwriting approved, proceeding to Sanction...")
        else:
            updates["waiting_for_user"] = True
            
        # Append AI response to messages (preserve conversation history)
        if "messages" not in updates:
            updates["messages"] = [AIMessage(content=response_msg)]
        else:
            updates["messages"] = updates["messages"] + [AIMessage(content=response_msg)]
        
        print(f"[MASTER] Updated state - CID: {updates.get('customer_id')}, KYC: {updates.get('kyc_status')}, Amount: {updates.get('requested_amount')}")
        
        return updates

    # 3. ROUTER - FIXED VERSION
    def deterministic_router(state: OrchestratorState) -> str:
        print(f"\n[ROUTER] Checking state...")
        
        customer_id = state.get("customer_id")
        kyc_status = state.get("kyc_status", "pending")
        requested_amount = state.get("requested_amount")
        preferred_tenure = state.get("preferred_tenure_months")
        waiting_for_user = state.get("waiting_for_user", False)
        offer_accepted = state.get("offer_accepted", False)
        negotiated_offer = state.get("negotiated_offer", {})
        offer_generated = negotiated_offer.get("offer_generated", False)
        underwriting_status = state.get("underwriting_status", "pending")
        sanction_letter_status = state.get("sanction_letter_status", "pending")
        
        print(f"  CID: {customer_id}, KYC: {kyc_status}")
        print(f"  Amount: {requested_amount}, Tenure: {preferred_tenure}")
        print(f"  Offer Generated: {offer_generated}, Accepted: {offer_accepted}")
        print(f"  Underwriting: {underwriting_status}, Sanction: {sanction_letter_status}")
        print(f"  Waiting for User: {waiting_for_user}")
        
        # Stop graph when response is ready for user
        if waiting_for_user:
            print("  -> END (Response sent to user)")
            return END
        
        # Decision tree
        if not customer_id:
            print("  -> master (need CID)")
            return "master"
        
        if customer_id and kyc_status == "pending":
            print("  -> verification")
            return "verification"
        
        # Sanction Stage
        if underwriting_status == "approved" and sanction_letter_status == "pending":
            print("  -> sanction")
            return "sanction"
            
        # Underwriting Stage
        if offer_accepted and underwriting_status == "pending":
            print("  -> underwriting")
            return "underwriting"
            
        # Sales Stage
        if kyc_status == "verified" and requested_amount and preferred_tenure and not offer_generated:
            print("  -> sales (ready for offer)")
            return "sales"
        
        if kyc_status == "verified" and requested_amount and not preferred_tenure:
            print("  -> master (need tenure)")
            return "master"
        
        if kyc_status == "verified" and not requested_amount:
            print("  -> master (need amount)")
            return "master"
        
        # Default fallback
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
    
    print("✅ Orchestrator graph built successfully!")
    return workflow.compile()