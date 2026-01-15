# underwriting.py
import asyncio
import json
import os
import logging
from datetime import datetime
from langchain_ollama import ChatOllama
import base64
from mcp.client.session import ClientSession
from sharedState.state import OrchestratorState
from langchain_core.tools import StructuredTool

from typing import TypedDict, Dict, Any, Optional, Annotated, List
from pydantic import Field, create_model

from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, ToolMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
import httpx

# Configure logging for production audit trail
os.makedirs("storage", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='storage/mcp_audit.log'
)
logger = logging.getLogger("UnderwritingAgent")

# Business Rules Constants
MIN_CREDIT_SCORE = 700
MAX_EMI_RATIO = 0.45 # Max 45% of salary can go to EMI

load_dotenv()


def mcp_to_langchain_tool(mcp_tool, session):
    
    fields = {}
    mcp_schema = mcp_tool.inputSchema or {}
    properties = mcp_schema.get("properties", {})
    required_fields = mcp_schema.get("required", [])

    for prop_name, prop_def in properties.items():
        py_type = str
        if prop_def.get("type") == "integer": py_type = int
        elif prop_def.get("type") == "boolean": py_type = bool
        elif prop_def.get("type") == "number": py_type = float
        elif prop_def.get("type") == "object": py_type = dict
        
        if prop_name in required_fields:
            fields[prop_name] = (py_type, Field(description=prop_def.get("description", "")))
        else:
            fields[prop_name] = (py_type, Field(default=None, description=prop_def.get("description", "")))

    ToolInputSchema = create_model(f"{mcp_tool.name}Input", **fields)

    async def wrapped_tool(**kwargs):
        result = await session.call_tool(mcp_tool.name, arguments=kwargs)
        return result.content[0].text if result.content else "No content"

    return StructuredTool.from_function(
        func=None,
        coroutine=wrapped_tool,
        name=mcp_tool.name,
        description=mcp_tool.description,
        args_schema= ToolInputSchema
    )

async def build_underwriting_graph(session: ClientSession):
    llm = ChatOllama(model="llama3.1", temperature=0)
    
    mcp_tools_list = await session.list_tools()
    tools = [mcp_to_langchain_tool(t, session) for t in mcp_tools_list.tools]

    # PRIORITY 1: INPUT VALIDATION
    async def validate_inputs(state: OrchestratorState):
        logger.info(f"🔍 [UNDERWRITING] Validating inputs...")
        customer_id = state.get("customer_id")
        offer = state.get("negotiated_offer", {})
        
        if not customer_id:
            logger.warning("⚠️ Missing customer_id")
            return {"underwriting_status": "failed", "error_message": "Missing Customer ID"}
        
        if not offer or not offer.get("approved_amount"):
            logger.warning("⚠️ Missing negotiated offer details")
            return {"underwriting_status": "failed", "error_message": "No negotiated offer found. Please complete Sales first."}
            
        return {"error_message": None}

    # NODE 0 -> FETCH CUSTOMER INFO
    async def fetch_customer_info(state: OrchestratorState):
        if state.get("customer_info"):
            return {}
        
        cid = str(state.get("customer_id", ""))
        logger.info(f"📡 [UNDERWRITING] Fetching info for {cid}")
            
        try:
            result = await session.call_tool("get_customer_info", arguments={"customer_id": cid})
            data = json.loads(result.content[0].text)
            cust_info = data.get("result", data)
            logger.info(f"✅ [UNDERWRITING] Got info for {cust_info.get('name', cid)}")
            return {"customer_info": cust_info}
        except Exception as e:
            logger.error(f"❌ [UNDERWRITING] Failed to fetch info: {e}")
            return {"customer_info": {"error": str(e)}}

    # NODE 1 -> FETCH CREDIT SCORE
    async def fetch_credit_score(state: OrchestratorState):
        if state.get("credit_score"):
            return {}
            
        cid = str(state.get("customer_id", ""))
        logger.info(f"📊 [UNDERWRITING] Fetching credit score for {cid}")
        try:
            result = await session.call_tool("get_credit_score", arguments={"customer_id": cid})
            data = json.loads(result.content[0].text)
            score_data = data.get("result", data)
            score = score_data.get("credit_score", 0) if isinstance(score_data, dict) else score_data
            logger.info(f"✅ [UNDERWRITING] Credit Score: {score}")
            return {"credit_score": score}
        except Exception as e:
            logger.error(f"❌ [UNDERWRITING] Failed to fetch credit score: {e}")
            return {"credit_score": {"error": str(e)}}

    # PRIORITY 2: BUSINESS RULE VALIDATION
    async def validate_business_rules(state: OrchestratorState):
        logger.info(f"🛡️ [UNDERWRITING] Checking business rules...")
        
        credit_score = state.get("credit_score", 0)
        offer = state.get("negotiated_offer", {})
        customer = state.get("customer_info", {})
        
        salary = customer.get("salary_monthly", 0)
        requested_amount = offer.get("approved_amount", 0)
        tenure = offer.get("tenure_months", 12)
        
        # 1. Credit Score Check
        if isinstance(credit_score, int) and credit_score < MIN_CREDIT_SCORE:
            logger.warning(f"🚫 [UNDERWRITING] Credit score {credit_score} below minimum {MIN_CREDIT_SCORE}")
            return {
                "underwriting_status": "rejected", 
                "underwriting_reason": f"Credit score ({credit_score}) is below our minimum requirement of {MIN_CREDIT_SCORE}."
            }
            
        # 2. EMI Ratio Check (Approximate EMI: P * r * (1+r)^n / ((1+r)^n - 1))
        # For simplicity: (Amount / Tenure) * 1.1 (adding 10% for interest)
        if salary > 0:
            estimated_emi = (requested_amount / tenure) * 1.1
            emi_ratio = estimated_emi / salary
            logger.info(f"📈 [UNDERWRITING] Estimated EMI: {estimated_emi:.2f}, Ratio: {emi_ratio:.2%}")
            
            if emi_ratio > MAX_EMI_RATIO:
                logger.warning(f"🚫 [UNDERWRITING] EMI Ratio {emi_ratio:.2%} exceeds max {MAX_EMI_RATIO:.2%}")
                return {
                    "underwriting_status": "require_salary_slip",
                    "underwriting_reason": f"Your estimated EMI exceeds {MAX_EMI_RATIO*100}% of your monthly income. We need to verify your salary slip."
                }
        
        return {"underwriting_status": "pending"}

    # NODE 2 -> LLM NODE (Calling underwrite_loan tool)
    async def llm_node(state: OrchestratorState):
        if state.get("underwriting_status") in ["rejected", "require_salary_slip"]:
            return {}
            
        llm_with_tools = llm.bind_tools(tools)
        
        customer_id = state.get("customer_id", "")
        offer = state.get("negotiated_offer", {})
        requested_amount = offer.get("approved_amount", 0)
        tenure_months = offer.get("tenure_months", 0)
        annual_rate = offer.get("interest_rate", 0.0)
        salary_provided = state.get("customer_info", {}).get("salary_monthly", 0)

        inputMessage = f"""
        You are an Underwriting Agent. 
        Your task is to call the 'underwrite_loan' tool to get a final system decision.

        CUSTOMER DETAILS:
        - ID: {customer_id}
        - Requested Amount: ₹{requested_amount}
        - Tenure: {tenure_months} months
        - Interest Rate: {annual_rate}%
        - Monthly Salary: ₹{salary_provided}
        - Credit Score: {state.get('credit_score')}

        INSTRUCTIONS:
        1. Call 'underwrite_loan' with these parameters.
        2. If you see a ToolMessage with the result in history, respond with "System underwriting complete."
        3. Do not explain your reasoning yet.
        """

        existing_history = state.get("underwriting_messages", [])
        has_tool_result = any(isinstance(m, ToolMessage) and m.name == "underwrite_loan" for m in existing_history)

        try:
            if has_tool_result:
                response = AIMessage(content="System underwriting complete.")
            else:
                response = await llm_with_tools.ainvoke([SystemMessage(content=inputMessage)] + existing_history)
        except Exception as e:
            logger.error(f"❌ [UNDERWRITING] LLM Invoke failed: {e}")
            # Fallback tool call
            import uuid
            tool_call_id = f"call_{uuid.uuid4().hex[:12]}"
            response = AIMessage(
                content="",
                tool_calls=[{
                    "name": "underwrite_loan",
                    "args": {
                        "customer_id": customer_id,
                        "requested_amount": requested_amount,
                        "tenure_months": tenure_months,
                        "annual_rate": annual_rate,
                        "salary_provided": str(salary_provided) if salary_provided else None
                    },
                    "id": tool_call_id
                }]
            )

        return {"underwriting_messages": [response]}

    # NODE 3 -> TOOL NODE
    tool_node = ToolNode(tools, messages_key="underwriting_messages")

    # NODE 4 -> FINAL STATUS NODE (Enhanced UX & Audit)
    async def final_status_node(state: OrchestratorState):
        status = state.get("underwriting_status", "pending")
        reason = state.get("underwriting_reason", "")
        customer_name = state.get("customer_info", {}).get("name", "Customer")
        
        # If status is still pending, check tool results
        if status == "pending":
            messages = state.get("underwriting_messages", [])
            last_tool_msg = next((m for m in reversed(messages) if isinstance(m, ToolMessage)), None)
            
            if last_tool_msg:
                try:
                    tool_data = json.loads(last_tool_msg.content)
                    result = tool_data.get("result", tool_data)
                    status = "approved" if result.get("decision") == "approve" else result.get("decision", "pending")
                    reason = result.get("reason", "").replace("_", " ").capitalize()
                except:
                    status = "error"
                    reason = "System error during final assessment"

        # PRIORITY 3: ENHANCED UX MESSAGES
        if status == "approved":
            msg_content = f"🎊 **Great news, {customer_name}!** Your loan application has been **Approved** by our underwriting team.\n\n" \
                          f"✅ **Next Step:** We are now generating your formal Sanction Letter. One moment please..."
            next_stage = "sanction"
        elif status == "require_salary_slip":
            msg_content = f"📄 **Additional Information Needed, {customer_name}.**\n\n" \
                          f"To proceed with your application, our underwriters require a copy of your **latest salary slip**.\n\n" \
                          f"💡 **Why?** {reason}\n" \
                          f"👉 Please upload the document to continue."
            next_stage = "underwriting"
        elif status == "rejected":
            msg_content = f"🙏 **Application Update for {customer_name}**\n\n" \
                          f"Unfortunately, we cannot proceed with your loan application at this time.\n\n" \
                          f"🚫 **Reason:** {reason}\n" \
                          f"We appreciate your interest in Tata Capital."
            next_stage = "start"
        else:
            msg_content = f"⏳ **Underwriting Update**\n\nYour application is currently being reviewed. Status: **{status.upper()}**."
            next_stage = "underwriting"

        # PRIORITY 4: AUDIT LOGGING
        logger.info(f"📝 [AUDIT] Underwriting Decision: {status.upper()} | CID: {state.get('customer_id')} | Reason: {reason}")
        
        public_history = AIMessage(content=msg_content, name="UnderwritingAgent")
        
        return {
            "underwriting_status": "approved" if status == "approved" else status,
            "underwriting_reason": reason,
            "messages": [public_history],
            "last_active_worker": "underwriting",
            "flow_stage": next_stage,
            "waiting_for_user": True if status in ["require_salary_slip", "rejected"] else False
        }

    # NODE 5 -> ERROR HANDLER
    async def error_handler(state: OrchestratorState):
        error_msg = state.get("error_message", "Unknown underwriting error")
        logger.error(f"🛑 [UNDERWRITING] Error: {error_msg}")
        return {
            "messages": [AIMessage(content=f"⚠️ **Underwriting Issue:** {error_msg}. Please try again or contact support.")],
            "waiting_for_user": True,
            "last_active_worker": "underwriting"
        }

    # REBUILD GRAPH
    workflow = StateGraph(OrchestratorState)

    workflow.add_node("validate", validate_inputs)
    workflow.add_node("fetch_info", fetch_customer_info)
    workflow.add_node("fetch_credit_score", fetch_credit_score)
    workflow.add_node("validate_rules", validate_business_rules)
    workflow.add_node("llm_node", llm_node)
    workflow.add_node("tool_node", tool_node)
    workflow.add_node("final_logic", final_status_node)
    workflow.add_node("error", error_handler)

    workflow.add_edge(START, "validate")
    
    workflow.add_conditional_edges(
        "validate",
        lambda s: "error" if s.get("error_message") else "fetch_info",
        {"error": "error", "fetch_info": "fetch_info"}
    )
    
    workflow.add_edge("fetch_info", "fetch_credit_score")
    workflow.add_edge("fetch_credit_score", "validate_rules")
    
    workflow.add_conditional_edges(
        "validate_rules",
        lambda s: "final_logic" if s.get("underwriting_status") in ["rejected", "require_salary_slip"] else "llm_node",
        {"final_logic": "final_logic", "llm_node": "llm_node"}
    )
    
    workflow.add_conditional_edges(
        "llm_node", 
        lambda s: "tool_node" if s.get("underwriting_messages") and isinstance(s["underwriting_messages"][-1], AIMessage) and s["underwriting_messages"][-1].tool_calls else "final_logic",
        {"tool_node": "tool_node", "final_logic": "final_logic"}
    )
    
    workflow.add_edge("tool_node", "llm_node")
    workflow.add_edge("final_logic", END)
    workflow.add_edge("error", END)

    return workflow.compile()