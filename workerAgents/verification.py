# verification.py - PRODUCTION READY
import asyncio
import json
import os
import logging
from datetime import datetime
from typing import TypedDict, Dict, Any, Annotated, List, Literal
from pydantic import Field, create_model
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, SystemMessage
from langgraph.graph.message import add_messages
from langchain_core.tools import StructuredTool
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from mcp.client.session import ClientSession
from sharedState.state import OrchestratorState
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

# Configure logging for production audit trail
os.makedirs("storage", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='storage/mcp_audit.log'
)
logger = logging.getLogger("VerificationAgent")

load_dotenv()

def mcp_to_langchain_tool(mcp_tool, session):
    # ... (existing tool conversion logic) ...
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
        logger.info(f"🛠️ Calling Tool: {mcp_tool.name} with args: {kwargs}")
        try:
            result = await session.call_tool(mcp_tool.name, arguments=kwargs)
            content = result.content[0].text if result.content else "No content"
            logger.info(f"✅ Tool {mcp_tool.name} result: {content[:100]}...")
            return content
        except Exception as e:
            logger.error(f"❌ Tool {mcp_tool.name} failed: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)})

    return StructuredTool.from_function(
        func=None,
        coroutine=wrapped_tool,
        name=mcp_tool.name,
        description=mcp_tool.description,
        args_schema= ToolInputSchema
    )


async def build_verification_graph(session: ClientSession):
    llm = ChatOllama(model="llama3.1", temperature=0)
    
    mcp_tools_list = await session.list_tools()
    tools = [mcp_to_langchain_tool(t, session) for t in mcp_tools_list.tools]

    # PRIORITY 2: VALIDATION NODE
    async def validate_inputs(state: OrchestratorState):
        logger.info(f"🔍 Validating inputs for session...")
        customer_id = state.get("customer_id")
        
        if not customer_id:
            logger.warning("⚠️ Missing customer_id in state")
            return {"kyc_status": "failed", "error_message": "Missing Customer ID"}
        
        return {"error_message": None}

    # NODE 0: Fetch Info if missing
    async def fetch_customer_info(state: OrchestratorState):
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
            logger.error(f"❌ Failed to fetch info for {cid}: {e}")
            return {"customer_info": {"error": str(e)}}
    
    # NODE 1 
    async def llm_node(state: OrchestratorState):
        llm_with_tools = llm.bind_tools(tools)
        
        customer_info = state.get("customer_info") or {}
        customer_id = state.get("customer_id", "")
        customer_name = customer_info.get("name", "Customer")
        customer_phone = customer_info.get("phone", "")
        customer_city = customer_info.get("city", "")

        # PRIORITY 3: USER-FRIENDLY SYSTEM PROMPT
        inputMessage = f'''
                            You are a helpful KYC Verification Agent for Tata Capital. 
                            Your goal is to verify {customer_name} ({customer_id}).
                            
                            CURRENT DATA:
                            - Phone: {customer_phone}
                            - City: {customer_city}

                            INSTRUCTIONS:
                            1. Call 'verify_kyc' once with these details.
                            2. If verified, say "I have successfully verified your details, {customer_name}!"
                            3. If it fails, explain why politely.
                            '''

        existing_history = state.get("verification_messages", [])
        has_tool_result = any(isinstance(m, ToolMessage) and m.name == "verify_kyc" for m in existing_history)

        try:
            if has_tool_result:
                response = AIMessage(content=f"✅ KYC verification for {customer_name} is complete.")
            else:
                response = await llm_with_tools.ainvoke([SystemMessage(content=inputMessage)] + existing_history)
        except Exception as e:
            logger.error(f"🤖 LLM Node Error: {e}")
            # Fallback to manual tool call if LLM fails
            import uuid
            tool_call_id = f"call_{uuid.uuid4().hex[:12]}"
            response = AIMessage(
                content="",
                tool_calls=[{
                    "name": "verify_kyc",
                    "args": {"customer_id": customer_id, "phone": customer_phone, "city": customer_city},
                    "id": tool_call_id
                }]
            )

        return {"verification_messages" : [response]}
    
    # NODE 2
    tool_node = ToolNode(tools, messages_key="verification_messages")

    # NODE 3: PRIORITY 3 & 4: FINAL STATUS & AUDIT
    async def final_status_node(state: OrchestratorState):
        messages = state.get("verification_messages", [])
        last_tool_msg = next((m for m in reversed(messages) if isinstance(m, ToolMessage)), None)
        
        status = "pending"
        kyc_result = {}
        customer_name = (state.get("customer_info") or {}).get("name", "Customer")
        
        if last_tool_msg is not None:
            try:
                kyc_result = json.loads(last_tool_msg.content)
            except:
                kyc_result = {"raw": last_tool_msg.content}
            
            result = kyc_result.get("result", {}) or {}
            p_verified = result.get("phone_verified", False)
            a_verified = result.get("address_verified", False)
            
            if p_verified and a_verified:
                status = "verified"
                msg_content = f"✅ **Verification Successful!**\n\nWelcome aboard, {customer_name}! Your identity has been verified via phone and address. We can now proceed with your loan offer."
            else:
                status = "failed"
                msg_content = f"❌ **Verification Failed**\n\nSorry {customer_name}, we couldn't verify your details. Please ensure your phone and city match our records."
        else:
            msg_content = "⚠️ Verification in progress..."

        # PRIORITY 4: AUDIT LOG ENTRY
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "customer_id": state.get("customer_id"),
            "action": "kyc_verification",
            "status": status,
            "result": kyc_result
        }
        logger.info(f"📝 AUDIT: {json.dumps(audit_entry)}")
        
        public_history = AIMessage(
            content=msg_content,
            name="VerificationAgent"
        )
        
        next_stage = "negotiation" if status == "verified" else "verification"
        
        # PRIORITY 1: WRITE BACK TO STATE (SESSION)
        return {
            "kyc_status": status, 
            "kyc_result": kyc_result, 
            "messages": [public_history], 
            "last_active_worker": "verification",
            "flow_stage": next_stage,
            "waiting_for_user": False
        }
        
    async def error_handler(state: OrchestratorState):
        error_msg = state.get("error_message", "Unknown error")
        logger.error(f"🛑 Error Handler Triggered: {error_msg}")
        return {
            "messages": [AIMessage(content=f"❌ **System Error:** {error_msg}. Please contact support.")],
            "waiting_for_user": True
        }

    def router_logic(state: OrchestratorState):
        if state.get("error_message"):
            return "error"
        
        messages = state.get("verification_messages", [])
        if messages and isinstance(messages[-1], AIMessage) and messages[-1].tool_calls:
            return "tools"
        
        # If we have a tool result, go to final logic
        if any(isinstance(m, ToolMessage) for m in messages):
            return "final"
            
        return "final"
    
    graph = StateGraph(OrchestratorState)
    graph.add_node("validate", validate_inputs)
    graph.add_node("fetch_info", fetch_customer_info)
    graph.add_node("llm_node", llm_node)
    graph.add_node("tool_node", tool_node)
    graph.add_node("final_logic", final_status_node)
    graph.add_node("error", error_handler)

    graph.add_edge(START, "validate")
    
    # Conditional edge from validate
    graph.add_conditional_edges(
        "validate",
        lambda s: "error" if s.get("error_message") else "fetch_info",
        {"error": "error", "fetch_info": "fetch_info"}
    )
    
    graph.add_edge("fetch_info", "llm_node")
    
    graph.add_conditional_edges(
        "llm_node", 
        router_logic, 
        {"tools": "tool_node", "final": "final_logic", "error": "error"}
    )
    
    graph.add_edge("tool_node", "llm_node")
    graph.add_edge("final_logic", END)
    graph.add_edge("error", END)
    
    return graph.compile()
