# api_complete.py - COMPLETE 7-AGENT SYSTEM WITH FIXED ROUTER
import re
import asyncio
import time
import json
import uuid
import requests
import os
from typing import Dict, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# ========== MODELS ==========
class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    flow_step: int = 1
    customer_id: Optional[str] = None
    kyc_status: str = "pending"
    last_active_worker: str = "master"
    debug_stage: Optional[str] = None
    underwriting_status: Optional[str] = None
    sanctioned_amount: Optional[int] = None
    sanction_letter_url: Optional[str] = None

# ========== MCP CONFIG ==========
MCP_BACKEND_URL = "http://localhost:8000"

# ========== GLOBALS ==========
sessions: Dict[str, dict] = {}
# Global mapping of TATA-REF-ID to session_id for live tracking
reference_id_map: Dict[str, str] = {}

# Create storage directory for sanction letters
os.makedirs("storage/sanction_letters", exist_ok=True)

# ========== MCP TOOL CALLS ==========
def call_mcp_tool(tool_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Call MCP backend tool with robust error handling"""
    try:
        url = f"{MCP_BACKEND_URL}/call/{tool_name}"
        print(f"📡 Calling MCP tool: {tool_name}")
        response = requests.post(url, json=payload, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print(f"📡 MCP Result: {result.get('status')}")
            return result
        elif response.status_code == 404:
            print(f"❌ MCP Error: Tool '{tool_name}' not found (404)")
            return {"status": "error", "message": f"Tool {tool_name} not found"}
        else:
            print(f"❌ MCP Error: HTTP {response.status_code}")
            return {"status": "error", "message": f"HTTP {response.status_code}"}
    except requests.exceptions.ConnectionError:
        print("❌ MCP Connection Error: Backend not running")
        return {"status": "error", "message": "MCP backend not reachable"}
    except Exception as e:
        print(f"❌ MCP Exception: {str(e)}")
        return {"status": "error", "message": str(e)}

def get_customer_info(customer_id: str) -> Dict[str, Any]:
    """Get customer info from MCP"""
    if not customer_id: return {}
    result = call_mcp_tool("get_customer_info", {"customer_id": customer_id})
    return result.get("result", {}) if result.get("status") == "ok" else {}

def get_customer_by_phone(phone: str) -> Dict[str, Any]:
    if not phone: return {}
    result = call_mcp_tool("get_customer_by_phone", {"phone": phone})
    return result.get("result", {}) if result.get("status") == "ok" else {}

def verify_kyc(customer_id: str, phone: str) -> Dict[str, Any]:
    """Verify KYC through MCP"""
    if not customer_id or not phone: return {"phone_verified": False, "address_verified": False}
    result = call_mcp_tool("verify_kyc", {"customer_id": customer_id, "phone": phone})
    return result.get("result", {}) if result.get("status") == "ok" else {"phone_verified": False, "address_verified": False}

def get_credit_score(customer_id: str) -> Dict[str, Any]:
    """Get credit score from MCP"""
    if not customer_id: return {"credit_score": 0}
    result = call_mcp_tool("get_credit_score", {"customer_id": customer_id})
    return result.get("result", {}) if result.get("status") == "ok" else {"credit_score": 0}

def underwrite_loan(customer_id: str, amount: int, tenure: int = 36) -> Dict[str, Any]:
    """Underwrite loan using MCP"""
    if not customer_id or not amount: return {"decision": "reject", "reason": "missing_data"}
    payload = {"customer_id": customer_id, "requested_amount": amount, "tenure_months": tenure, "annual_rate": 12.0}
    result = call_mcp_tool("underwrite_loan", payload)
    return result.get("result", {}) if result.get("status") == "ok" else {"decision": "reject", "reason": "underwriting_failed"}

def generate_sanction_letter_mcp(customer_id: str, amount: int, tenure: int = 36) -> Dict[str, Any]:
    """Generate sanction letter via MCP"""
    if not customer_id or not amount: return {"status": "error", "message": "Missing data"}
    payload = {"customer_id": customer_id, "amount": amount, "tenure_months": tenure, "interest_rate": 12.0}
    return call_mcp_tool("generate_sanction_letter", payload)

# ========== WORKER AGENTS ==========

async def verification_agent(state: dict) -> dict:
    """Agent 2: Verification Agent (KYC & Document Verification)"""
    print("👮 [VERIFICATION AGENT] Running...")
    customer_id = state.get("customer_id")
    
    # CASE 1: KYC Verification (Step 3)
    if state.get("flow_step") == 3 and not state.get("verification_complete"):
        if customer_id:
            customer_info = get_customer_info(customer_id)
            if customer_info:
                state.update({
                    "customer_name": customer_info.get("name"),
                    "phone": customer_info.get("phone"),
                    "pre_approved_limit": customer_info.get("pre_approved_limit", 0),
                    "credit_score": customer_info.get("credit_score", 0),
                    "salary_monthly": customer_info.get("salary_monthly", 0)
                })
            
            if state.get("phone"):
                verification = verify_kyc(customer_id, state["phone"])
                state["kyc_status"] = "verified" if verification.get("phone_verified") else "pending"
                print(f"✅ [VERIFICATION] KYC Status: {state['kyc_status']}")
        
        state["verification_complete"] = True

    # CASE 2: Document Verification (Step 4)
    elif state.get("flow_step") == 4 and state.get("doc_received_by_agent"):
        print("👮 [VERIFICATION AGENT] Verifying uploaded documents...")
        if customer_id and not state.get("document_checks_done"):
            credit_result = get_credit_score(customer_id)
            state["credit_score"] = credit_result.get("credit_score", 0)
            state["document_checks_done"] = True
        
        if state.get("city_needs_verification") and state.get("user_city"):
            cust_info = get_customer_info(customer_id) if customer_id else {}
            db_city = (cust_info or {}).get("city", "")
            user_city = state.get("user_city", "")
            if user_city and db_city and user_city.strip().lower() == db_city.strip().lower():
                state["city_verified"] = True
                state["document_verification_complete"] = True
                state["flow_step"] = 5
                state["city_needs_verification"] = False
                state["awaiting_city_input"] = False
                state["response"] = f"📄Documents and City Verified Successfully!\n\n" \
                                   f"✅ KYC Status: {state.get('kyc_status', 'pending').upper()}\n" \
                                   f"✅ Credit Score: {state.get('credit_score', 0)}/900\n\n" \
                                   f"Your application is ready for final underwriting.\n" \
                                   f"Type 'proceed' to continue."
            else:
                state["city_verified"] = False
                state["city_needs_verification"] = False
                state["awaiting_city_input"] = True
                state["response"] = "⚠️ City verification failed. Please re-enter your registered city (e.g., Pune):"
        elif not state.get("awaiting_city_input"):
            state["awaiting_city_input"] = True
            state["response"] = f"📄Documents Verified Successfully!\n\n" \
                               f"✅ KYC Status: {state.get('kyc_status', 'pending').upper()}\n" \
                               f"✅ Credit Score: {state.get('credit_score', 0)}/900\n\n" \
                               f"Please provide your city for verification (e.g., Pune):"
    
    state["last_active_worker"] = "verification"
    return state

async def sales_agent(state: dict) -> dict:
    """Agent 3: Sales Agent (Offer Generation)"""
    print("💰 [SALES AGENT] Running...")
    amount = state.get("requested_amount", 0)
    tenure = state.get("preferred_tenure_months", 36)
    customer_id = state.get("customer_id")
    
    if state.get("kyc_status") == "verified" and amount and tenure:
        underwriting_result = underwrite_loan(customer_id, amount, tenure)
        state["underwriting_result"] = underwriting_result
        state["offer_generated"] = True
        state["flow_step"] = 4
        
        decision = underwriting_result.get("decision", "pending")
        if decision == "approve":
            emi = underwriting_result.get("emi", 0)
            state["response"] = f"💰 Personalized Offer Approved!\n\n" \
                               f"✅ Approved Amount: ₹{amount:,}\n" \
                               f"✅ Tenure: {tenure} months\n" \
                               f"✅ EMI: ₹{emi:,.2f}/month\n" \
                               f"✅ Interest Rate: 12.0%\n\n" \
                               f"Please upload required documents (Aadhaar, PAN, Bank Statements).\n" \
                               f"Type 'upload documents' when ready."
        elif decision == "require_salary_slip":
            state["response"] = f"📄Additional Verification Required\n\n" \
                               f"We need your salary slip to proceed with ₹{amount:,}.\n" \
                               f"Please upload your latest salary slip or type 'upload documents'."
        else:
            state["flow_step"] = 99
            state["response"] = f"Loan Application Review\n\n" \
                               f"Status: Not approved\n" \
                               f"Reason: {underwriting_result.get('reason', 'Underwriting failed').replace('_', ' ').title()}"
    
    state["last_active_worker"] = "sales"
    return state

async def document_agent(state: dict) -> dict:
    """Agent 4: Document Agent (Document Collection)"""
    print("📎 [DOCUMENT AGENT] Running...")
    state["doc_received_by_agent"] = True
    state["last_active_worker"] = "document"
    # Document agent just acknowledges and hands over to verification
    state["response"] = "📎Documents received. Passing to Verification Agent for validation..."
    return state

async def underwriting_agent(state: dict) -> dict:
    """Agent 5: Underwriting Agent (Credit Assessment)"""
    print("📊 [UNDERWRITING AGENT] Running...")
    amount = state.get("requested_amount", 0)
    tenure = state.get("preferred_tenure_months", 36)
    result = underwrite_loan(state.get("customer_id"), amount, tenure)
    
    state["underwriting_status"] = result.get("decision", "pending")
    state["flow_step"] = 6
    
    if state["underwriting_status"] == "approve":
        state["response"] = f"Final Underwriting Approved!\n\n" \
                           f"Loan Amount: ₹{amount:,}\n" \
                           f"Tenure:{tenure} months\n" \
                           f"EMI: ₹{result.get('emi', 0):,.2f}/month\n\n" \
                           f"Generating your sanction letter...\n" \
                           f"Type 'generate sanction' to proceed."
    else:
        state["response"] = f"❌ Final Underwriting Result\n\nStatus: Not approved\n" \
                           f"Reason: {result.get('reason', 'Failed').replace('_', ' ').title()}"
    
    state["last_active_worker"] = "underwriting"
    return state

async def sanction_agent(state: dict) -> dict:
    """Agent 6: Sanction Agent (Sanction Letter)"""
    print("📄 [SANCTION AGENT] Running...")
    amount = state.get("requested_amount", 0)
    tenure = state.get("preferred_tenure_months", 36)
    result = generate_sanction_letter_mcp(state.get("customer_id"), amount, tenure)
    
    # Final state update for Sanction
    # Use the filename returned by MCP if available
    # The MCP server returns a response like {"status": "ok", "result": {"resource": "sanction_CUST001_xxx.pdf", "path": "..."}}
    filename = result.get("result", {}).get("resource", "").replace("resource://", "")
    if not filename:
        # Fallback if MCP response structure is different
        filename = f"sanction_{state.get('customer_id')}.pdf"
    
    # Correct downloadable URL exposed via FastAPI StaticFiles
    # The backend (api_complete.py) runs on 8083 and mounts "storage/sanction_letters" at "/sanction_letters"
    state["sanction_letter_url"] = f"http://localhost:8083/sanction_letters/{filename}"
    state["sanctioned_amount"] = amount
    state["sanction_letter_generated"] = True
    
    # Generate and store Reference ID for live tracking
    if not state.get("reference_id"):
        # Remove hyphens from UUID to ensure it's alphanumeric
        ref_uuid = str(uuid.uuid4()).replace("-", "").upper()[:8]
        ref_id = f"TATA-{ref_uuid}"
        state["reference_id"] = ref_id
        # Also store session_id in the state for easier lookup
        # (It's already in sessions dict, but having it here helps)
        # We need the key used in 'sessions' dict.
        # Since we don't have session_id directly in the agent state, 
        # we'll rely on the chat loop to populate the map.
    
    ref_id = state.get("reference_id")
    state["flow_step"] = 7
    state["response"] = f"🎉Congratulations! Your Loan is Sanctioned.\n\n" \
                       f"Sanctioned Amount: ₹{amount:,}\n" \
                       f"Reference ID: {ref_id}\n\n" \
                       f"You can now download your official Sanction Letter below.\n" \
                       f"Click the button to view and save your PDF."
    
    state["last_active_worker"] = "sanction"
    return state

async def disbursement_agent(state: dict) -> dict:
    """Agent 7: Disbursement Agent (Loan Disbursement)"""
    print("💸 [DISBURSEMENT AGENT] Running...")
    state["disbursement_status"] = "completed"
    state["flow_step"] = 8
    transaction_id = f"TATA{int(time.time())}"
    
    state["response"] = f"🎉 LOAN DISBURSED SUCCESSFULLY!\n\n" \
                       f"Amount: ₹{state.get('requested_amount', 0):,}\n" \
                       f"Account: XXXX-XXXX-8765\n" \
                       f"Transaction ID: {transaction_id}\n\n" \
                       f"Thank you for choosing Tata Capital! 🎊"
    state["last_active_worker"] = "disbursement"
    return state

# ========== MASTER AGENT (Orchestrator) ==========

async def handle_master_agent(state: dict, user_message: str) -> dict:
    """Master Agent - Step-by-step data collection and orchestration"""
    flow_step = state.get("flow_step", 1)
    print(f"🤖 [MASTER] Step {flow_step} processing...")
    
    # Check for Reference ID lookup first (Live Tracking)
    # Be more flexible with regex to catch variations (allow hyphens in case they exist)
    ref_match = re.search(r'(TATA-[A-Z0-9-]+)', user_message.upper())
    if ref_match:
        ref_id = ref_match.group(1).strip().rstrip('.') # Remove trailing dots if any
        session_id = reference_id_map.get(ref_id)
        if session_id and session_id in sessions:
            target_state = sessions[session_id]
            cust_name = target_state.get("customer_name") or target_state.get("user_provided_name") or "Customer"
            amount = target_state.get("requested_amount", 0)
            
            # Determine status string
            status = "Processing"
            if target_state.get("disbursement_status") == "completed": status = "Disbursed ✅"
            elif target_state.get("sanction_letter_generated"): status = "Sanctioned 📄"
            elif target_state.get("underwriting_status") == "approve": status = "Approved (Awaiting Sanction)"
            elif target_state.get("document_verification_complete"): status = "Verified (Awaiting Underwriting)"
            elif target_state.get("doc_received_by_agent"): status = "Documents Under Review"
            
            state["response"] = f"🔍 **Application Status for {ref_id}**\n\n" \
                               f"👤 Customer: {cust_name}\n" \
                               f"💰 Loan Amount: ₹{amount:,}\n" \
                               f"📊 Current Status: {status}\n\n" \
                               f"Is there anything else I can help you with?"
            return state
        else:
            state["response"] = f"❌ I couldn't find any application with Reference ID {ref_id}. Please check the ID and try again."
            return state

    try:
        if flow_step == 1:
            phone_match = re.search(r'\b(\d{10})\b', user_message)
            cust_match = re.search(r'CUST\d+', user_message.upper())
            
            # Capture Name First if not present
            if not state.get("user_provided_name") and not phone_match and not cust_match:
                state["user_provided_name"] = user_message.strip()
                state["response"] = f"🙏 Welcome {state['user_provided_name']}!\n\nPlease provide your registered mobile number (e.g., 9810000001):"
                return state

            if phone_match:
                phone = phone_match.group(1)
                cust_info = get_customer_by_phone(phone)
                if cust_info:
                    customer_id = cust_info.get("customer_id")
                    db_name = cust_info.get("name", "there")
                    
                    # Validate Name if provided
                    provided_name = state.get("user_provided_name", "").lower()
                    if provided_name:
                        db_name_lower = db_name.lower()
                        # Check if any part of the provided name is in the database name
                        name_parts = [p for p in provided_name.split() if len(p) > 2]
                        if not any(part in db_name_lower for part in name_parts) and provided_name not in db_name_lower:
                            state["response"] = f"❌ Verification failed. The name '{state.get('user_provided_name')}' does not match our records for this mobile number. Please provide the registered mobile number for '{state.get('user_provided_name')}' or re-enter your details."
                            return state

                    state["customer_id"] = customer_id
                    state["customer_name"] = db_name
                    state["phone"] = phone
                    kyc_result = verify_kyc(customer_id, phone)
                    phone_verified = kyc_result.get("phone_verified", False)
                    address_verified = kyc_result.get("address_verified", False)
                    state["kyc_status"] = "verified" if phone_verified and address_verified else "failed"
                    state["flow_step"] = 2
                    if phone_verified and address_verified:
                        state["response"] = f"✅ Verification successful for {db_name} (ID: {customer_id}).\n\nHow much loan do you need? (e.g., ₹150,000)"
                    elif phone_verified:
                        state["response"] = f"✅ Phone verified for {db_name} (ID: {customer_id}). Address verification pending.\n\nHow much loan do you need? (e.g., ₹150,000)"
                    else:
                        state["response"] = "❌ Phone verification failed. Please re-enter your registered mobile number (e.g., 9810000001)."
                        state["flow_step"] = 1
                else:
                    state["response"] = "I could not find a customer with that mobile number. Please enter your registered mobile number (e.g., 9810000001)."
            elif cust_match:
                customer_id = cust_match.group()
                cust_info = get_customer_info(customer_id)
                if cust_info:
                    db_name = cust_info.get("name", "there")
                    
                    # Validate Name if provided
                    provided_name = state.get("user_provided_name", "").lower()
                    if provided_name:
                        db_name_lower = db_name.lower()
                        name_parts = [p for p in provided_name.split() if len(p) > 2]
                        if not any(part in db_name_lower for part in name_parts) and provided_name not in db_name_lower:
                            state["response"] = f"❌ Verification failed. The name '{state.get('user_provided_name')}' does not match our records for ID {customer_id}."
                            return state

                    state["customer_id"] = customer_id
                    state["flow_step"] = 2
                    state["phone"] = cust_info.get("phone")
                    if state["phone"]:
                        kyc_result = verify_kyc(customer_id, state["phone"])
                        phone_verified = kyc_result.get("phone_verified", False)
                        address_verified = kyc_result.get("address_verified", False)
                        state["kyc_status"] = "verified" if phone_verified and address_verified else "failed"
                    state["response"] = f"✅ Customer ID: {customer_id}\n\nHi {db_name}! How much loan do you need? (e.g., ₹150,000)"
                else:
                    state["response"] = f"I could not find customer ID {customer_id}. Please check the ID and try again."
            else:
                state["response"] = "🙏 Welcome to Tata Capital!\n\nMay I know your name?"
                return state

        # STEP 2: Get Loan Amount
        elif flow_step == 2:
            clean_msg = user_message.lower().replace(',', '').replace('₹', '').replace('rs', '')
            amount = None
            lakh_match = re.search(r'(\d+\.?\d*)\s*lakh', clean_msg)
            if lakh_match:
                amount = int(float(lakh_match.group(1)) * 100000)
            else:
                num_match = re.search(r'(\d+)', clean_msg)
                if num_match: amount = int(num_match.group(1))
            
            if amount:
                state["requested_amount"] = amount
                state["flow_step"] = 3
                state["response"] = f"✅ Loan Amount: ₹{amount:,}\n\n" \
                                   f"Step 3: For how many months? (e.g., 36 months)"
            else:
                state["response"] = "Step 2: Please specify loan amount (e.g., ₹150,000):"

        # STEP 3: Get Tenure
        elif flow_step == 3:
            num_match = re.search(r'(\d+)', user_message)
            if num_match:
                tenure = int(num_match.group(1))
                if "year" in user_message.lower(): tenure *= 12
                if 6 <= tenure <= 84:
                    state["preferred_tenure_months"] = tenure
                    state["needs_verification"] = True # Flag for router
                    state["response"] = "✅ Tenure set. Verifying your profile..."
                else:
                    state["response"] = "⚠️ Invalid Tenure: Must be between 6 and 84 months. Please re-enter:"
            else:
                state["response"] = "Please specify tenure (e.g., 36 months):"

        # STEP 4: Document Upload and City Capture
        elif flow_step == 4:
            if state.get("awaiting_city_input"):
                city = user_message.strip()
                if city:
                    state["user_city"] = city
                    state["city_needs_verification"] = True
                    state["awaiting_city_input"] = False
                    state["response"] = "Thank you. Verifying your city details..."
                else:
                    state["response"] = "Please provide your city name for verification (e.g., Pune):"
            else:
                if any(word in user_message.lower() for word in ['upload', 'doc', 'yes', 'ready']):
                    state["documents_uploaded"] = True
                else:
                    state["response"] = "Type 'upload documents' when you are ready to proceed."

        # STEP 5: Accept Offer
        elif flow_step == 5:
            if any(word in user_message.lower() for word in ['proceed', 'yes', 'accept']):
                state["offer_accepted"] = True # Flag for router
                state["underwriting_status"] = "pending"
            else:
                state["response"] = "Type 'proceed' to accept the offer and start final underwriting."

        # STEP 6: Generate Sanction
        elif flow_step == 6:
            if any(word in user_message.lower() for word in ['generate', 'sanction', 'letter', 'yes']):
                state["needs_sanction"] = True # Flag for router
            else:
                state["response"] = "Step 6: Type 'generate sanction' to create your letter."

        # STEP 7: Disbursement
        elif flow_step == 7:
            if any(word in user_message.lower() for word in ['disburse', 'transfer', 'yes']):
                state["needs_disbursement"] = True # Flag for router
            else:
                state["response"] = "Step 7: Type 'disburse' to transfer funds."

        state["last_active_worker"] = "master"
        return state
    except Exception as e:
        print(f"❌ [MASTER] Error: {e}")
        state["response"] = "Encountered an error. Please try again."
        return state

# ========== ROUTER ==========

def determine_next_agent(state: dict) -> str:
    """Router logic that decides which worker agent should run next"""
    flow_step = state.get("flow_step", 1)
    
    # Step 3 Chain: Tenure -> Verification -> Sales
    if flow_step == 3 and state.get("preferred_tenure_months") and not state.get("verification_complete"):
        return "verification"
    if flow_step == 3 and state.get("verification_complete") and not state.get("offer_generated"):
        return "sales"
    
    # Step 4 Chain: Documents Uploaded -> Document Agent (Collection) -> Verification Agent (Verification)
    if flow_step == 4 and state.get("documents_uploaded") and not state.get("doc_received_by_agent"):
        return "document"
    if flow_step == 4 and state.get("doc_received_by_agent") and not state.get("document_verification_complete") and not state.get("awaiting_city_input") and not state.get("city_needs_verification"):
        return "verification"
    if flow_step == 4 and state.get("doc_received_by_agent") and state.get("city_needs_verification") and not state.get("document_verification_complete"):
        return "verification"
    
    # Step 5: Underwriting
    if flow_step == 5 and state.get("offer_accepted") and state.get("underwriting_status") == "pending":
        return "underwriting"
    
    # Step 6: Sanction
    if flow_step == 6 and state.get("needs_sanction") and not state.get("sanction_letter_generated"):
        return "sanction"
    
    # Step 7: Disbursement
    if flow_step == 7 and state.get("needs_disbursement") and not state.get("disbursement_status"):
        return "disbursement"
    
    return "master"

# ========== FASTAPI APP ==========

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Serve static files (Sanction Letters)
# Files are stored in storage/sanction_letters
STATIC_DIR = os.path.join(os.getcwd(), "storage", "sanction_letters")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/sanction_letters", StaticFiles(directory=STATIC_DIR), name="sanction_letters")

async def call_worker_agent(agent_name: str, state: dict) -> dict:
    """Call the specified worker agent function"""
    if agent_name == "verification": return await verification_agent(state)
    if agent_name == "sales": return await sales_agent(state)
    if agent_name == "document": return await document_agent(state)
    if agent_name == "underwriting": return await underwriting_agent(state)
    if agent_name == "sanction": return await sanction_agent(state)
    if agent_name == "disbursement": return await disbursement_agent(state)
    return state

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    print(f"\n💬 {request.session_id}: {request.message}")
    
    if request.session_id not in sessions:
        sessions[request.session_id] = {
            "flow_step": 1, "customer_id": None, "requested_amount": None, "preferred_tenure_months": None,
            "kyc_status": "pending", "documents_uploaded": False, "last_active_worker": "master",
            "offer_generated": False, "offer_accepted": False, "underwriting_status": None,
            "sanction_letter_status": None, "sanction_letter_generated": False,
            "verification_complete": False, "document_verification_complete": False,
            "doc_received_by_agent": False, "awaiting_city_input": False,
            "city_needs_verification": False, "city_verified": False, "user_city": None,
            "needs_sanction": False, "needs_disbursement": False,
            "user_provided_name": None
        }
    
    state = sessions[request.session_id]
    
    # 1. Run Master Agent to process input
    state = await handle_master_agent(state, request.message)
    
    # 2. Loop Router to trigger worker agent chains (like Verification -> Sales)
    max_loops = 5
    while max_loops > 0:
        next_agent = determine_next_agent(state)
        if next_agent == "master":
            break
        
        print(f"🎯 Router triggering: {next_agent}")
        state = await call_worker_agent(next_agent, state)
        max_loops -= 1
    
    # Update Reference ID mapping if it exists
    if state.get("reference_id"):
        reference_id_map[state["reference_id"]] = request.session_id
        print(f"🔗 Linked Ref ID {state['reference_id']} to Session {request.session_id}")
    
    sessions[request.session_id] = state
    
    return ChatResponse(
        response=state.get("response", "Please continue..."),
        flow_step=state.get("flow_step", 1),
        customer_id=state.get("customer_id"),
        kyc_status=state.get("kyc_status", "pending"),
        last_active_worker=state.get("last_active_worker", "master"),
        debug_stage=state.get("last_active_worker"),
        underwriting_status=state.get("underwriting_status"),
        sanctioned_amount=state.get("sanctioned_amount"),
        sanction_letter_url=state.get("sanction_letter_url")
    )

@app.get("/track/{reference_id}")
async def track_application(reference_id: str):
    """Live tracking endpoint for loan applications"""
    ref_id = reference_id.strip().upper().rstrip('.')
    print(f"🔍 Tracking request for: '{ref_id}'")
    
    session_id = reference_id_map.get(ref_id)
    print(f"📍 Session ID found: {session_id}")
    
    if not session_id or session_id not in sessions:
        print(f"❌ 404: Application not found for {ref_id}")
        # Log all current mapping keys for debugging
        print(f"📋 Current Map Keys: {list(reference_id_map.keys())}")
        raise HTTPException(status_code=404, detail="Application not found")
    
    state = sessions[session_id]
    
    # Map internal flow steps to frontend tracking stages
    # Frontend stages: 
    # 0: Application Submitted
    # 1: Document Verification
    # 2: Credit Assessment
    # 3: Loan Sanctioned
    # 4: Disbursement
    
    current_stage = 0
    flow_step = state.get("flow_step", 1)
    
    if state.get("disbursement_status") == "completed":
        current_stage = 4
    elif state.get("sanction_letter_generated"):
        current_stage = 3
    elif state.get("underwriting_status") == "approve":
        current_stage = 3
    elif state.get("document_verification_complete"):
        current_stage = 2
    elif state.get("doc_received_by_agent"):
        current_stage = 1
    elif flow_step >= 2:
        current_stage = 0
        
    stages = [
        {"name": "Application Submitted", "status": "completed" if current_stage >= 0 else "pending", "description": "Your loan application has been received"},
        {"name": "Document Verification", "status": "completed" if current_stage > 1 else ("current" if current_stage == 1 else "pending"), "description": "KYC and Income documents verification"},
        {"name": "Credit Assessment", "status": "completed" if current_stage > 2 else ("current" if current_stage == 2 else "pending"), "description": "Credit score and eligibility evaluation"},
        {"name": "Loan Sanctioned", "status": "completed" if current_stage > 3 else ("current" if current_stage == 3 else "pending"), "description": "Final approval and sanction letter generation"},
        {"name": "Disbursement", "status": "completed" if current_stage == 4 else "pending", "description": "Loan amount credit to account"},
    ]
    
    # Update stage statuses based on current_stage
    for i, stage in enumerate(stages):
        if i < current_stage:
            stage["status"] = "completed"
            stage["date"] = datetime.now().strftime("%Y-%m-%d")
        elif i == current_stage:
            stage["status"] = "current"
        else:
            stage["status"] = "pending"

    return {
        "referenceNumber": ref_id,
        "customerName": state.get("customer_name") or state.get("user_provided_name") or "Customer",
        "loanAmount": state.get("requested_amount", 0),
        "appliedDate": datetime.now().strftime("%Y-%m-%d"),
        "currentStage": current_stage + 1,
        "stages": stages
    }

@app.get("/health")
async def health():
    return {"status": "ok", "agents": 7, "mcp_url": MCP_BACKEND_URL}

@app.get("/reset/{session_id}")
async def reset(session_id: str):
    if session_id in sessions: 
        # Also remove from reference_id_map
        ref_id = sessions[session_id].get("reference_id")
        if ref_id and ref_id in reference_id_map:
            del reference_id_map[ref_id]
        del sessions[session_id]
    return {"status": "reset"}

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting Fixed 7-Agent Loan API on Port 8083...")
    uvicorn.run(app, host="127.0.0.1", port=8083)
