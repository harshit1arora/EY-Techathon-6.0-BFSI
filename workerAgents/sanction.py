# sanction.py
import json
import os
import logging
from datetime import datetime
from pydantic import Field, create_model
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage, SystemMessage
from langchain_ollama import ChatOllama
from mcp.client.session import ClientSession
from sharedState.state import OrchestratorState
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import StructuredTool

# Configure logging for production audit trail
os.makedirs("storage", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='storage/mcp_audit.log'
)
logger = logging.getLogger("SanctionAgent")

load_dotenv()

DOWNLOAD_DIR = os.environ.get("SANCTION_DOWNLOAD_DIR", "./downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


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


async def build_sanction_graph(session: ClientSession):
    llm = ChatOllama(model="llama3.1", temperature=0)
    mcp_tools_list = await session.list_tools()
    tools = [mcp_to_langchain_tool(t, session) for t in mcp_tools_list.tools]

    # PRIORITY 2: VALIDATION NODE
    async def validate_inputs(state: OrchestratorState):
        logger.info("🔍 Validating inputs for Sanction Agent...")
        customer_id = state.get("customer_id")
        underwriting_status = state.get("underwriting_status")
        negotiated_offer = state.get("negotiated_offer") or {}

        if not customer_id:
            logger.warning("⚠️ Missing customer_id in state")
            return {"sanction_letter_status": "failed", "error_message": "Missing Customer ID"}
        
        if underwriting_status != "approved":
            logger.warning(f"⚠️ Underwriting not approved for {customer_id}. Status: {underwriting_status}")
            return {"sanction_letter_status": "failed", "error_message": "Underwriting must be approved before sanctioning."}

        if not negotiated_offer.get("approved_amount"):
            logger.warning(f"⚠️ Missing loan amount in negotiated offer for {customer_id}")
            return {"sanction_letter_status": "failed", "error_message": "Loan amount not specified in offer."}

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
            logger.error(f"❌ Failed to fetch info for {cid}: {str(e)}")
            return {"customer_info": {"error": str(e)}}

    # NODE 1 -> LLM Node
    async def llm_node(state: OrchestratorState):
        if state.get("error_message"):
            return {}

        logger.info(f"--- Sanction Worker: LLM Node for {state.get('customer_id')} ---")
        llm_with_tools = llm.bind_tools(tools)
        
        negotiated_offer = state.get("negotiated_offer") or {}
        customer_id = state.get("customer_id", "")
        approved_amount = negotiated_offer.get("approved_amount", 0)
        tenure_months = negotiated_offer.get("tenure_months", 0)
        interest_rate = negotiated_offer.get("interest_rate", 0.0)
        underwriting_status = state.get("underwriting_status", "pending")

        existing_history = state.get("sanction_messages", [])
        has_tool_result = any(isinstance(m, ToolMessage) and m.name == "generate_sanction_letter" for m in existing_history)

        if has_tool_result:
            logger.info("Sanction Worker: Tool result found, generating final response.")
            try:
                response = await llm.ainvoke([
                    SystemMessage(content="You are a Sanction Agent. The sanction letter has been generated. Confirm this clearly to the user."),
                ] + existing_history)
            except Exception as e:
                logger.error(f"LLM final confirmation failed: {e}")
                response = AIMessage(content="Sanction Agent: Your sanction letter has been generated successfully.")
        else:
            logger.info(f"Sanction Worker: Calling generate_sanction_letter for {customer_id}")
            inputMessage = f'''
                You are a Sanction Agent. 
                Your task is to call the 'generate_sanction_letter' tool for an approved loan.

                LOAN DETAILS:
                - Customer ID: {customer_id}
                - Amount: {approved_amount}
                - Tenure: {tenure_months} months
                - Interest Rate: {interest_rate}%
                - Underwriting: {underwriting_status}

                INSTRUCTIONS:
                1. Call 'generate_sanction_letter' with these details.
                2. If already called, do not call again.
                '''
            try:
                response = await llm_with_tools.ainvoke([SystemMessage(content=inputMessage)] + existing_history)
            except Exception as e:
                logger.error(f"LLM tool call failed ({e}), using fallback tool call...")
                import uuid
                tool_call_id = f"call_{uuid.uuid4().hex[:12]}"
                response = AIMessage(
                    content="",
                    tool_calls=[{
                        "name": "generate_sanction_letter",
                        "args": {
                            "customer_id": customer_id,
                            "amount": approved_amount,
                            "tenure_months": tenure_months,
                            "interest_rate": interest_rate
                        },
                        "id": tool_call_id
                    }]
                )

        return {"sanction_messages" : [response]}
    
    # NODE 2 -> TOOL NODE
    tool_node = ToolNode(tools, messages_key="sanction_messages")

    # NODE 3 -> FINAL STATUS NODE
    async def final_status_node(state: OrchestratorState):
        if state.get("error_message"):
            err = state.get("error_message")
            return {
                "messages": [AIMessage(content=f"⚠️ **Sanction Error**: {err}", name="SanctionAgent")],
                "flow_stage": "underwriting", # Go back or stay
                "waiting_for_user": True
            }

        messages = state.get("sanction_messages", [])
        last_tool_msg = next((m for m in reversed(messages) if isinstance(m, ToolMessage)), None)
        
        status = "failed"
        resource = None
        path = None
        msg_content = ""
        customer_name = (state.get("customer_info") or {}).get("name", "Customer")

        if last_tool_msg is not None:
            try:
                sanction_result = json.loads(last_tool_msg.content)
                result = sanction_result.get("result", {}) if isinstance(sanction_result, dict) else {}
                
                resource = result.get("sanction_letter_resource")
                path = result.get("sanction_letter_path")

                if resource and path:
                    status = "generated"
                    # Generate a proper URL exposed via the main API (port 8083)
                    filename = os.path.basename(path)
                    download_url = f"http://localhost:8083/sanction_letters/{filename}"
                    msg_content = (
                        f"🎊 **Congratulations, {customer_name}!** 🎊\n\n"
                        f"Your loan has been officially sanctioned. We have generated your formal Sanction Letter.\n\n"
                        f"📄 **Download Here**: [{filename}]({download_url})\n\n"
                        f"Please review the document. Our disbursement team will contact you shortly for the next steps."
                    )
                    logger.info(f"✅ Sanction letter generated for {customer_name}: {path}")
                else:
                    msg_content = f"❌ **Sanction Failed**: We encountered an issue generating your letter. Please contact support."
                    logger.warning(f"⚠️ Sanction tool returned success but missing paths for {customer_name}")
            except Exception as e:
                logger.error(f"Error parsing sanction tool result: {e}")
                msg_content = f"❌ **Error**: Failed to process sanction result."
        else:
            msg_content = f"⏳ **Sanction Pending**: We are still processing your request."

        public_history = AIMessage(content=msg_content, name="SanctionAgent")       
        
        return {
            "sanction_letter_resource": resource,
            "sanction_letter_path": path,
            "sanction_letter_status": status,
            "messages": [public_history],
            "last_active_worker": "sanction",
            "flow_stage": "completed" if status == "generated" else "sanction",
            "waiting_for_user": False
        }

    # Build the graph
    graph = StateGraph(OrchestratorState)

    graph.add_node("validate", validate_inputs)
    graph.add_node("fetch_info", fetch_customer_info)
    graph.add_node("llm_node", llm_node)
    graph.add_node("tool_node", tool_node)
    graph.add_node("final_logic", final_status_node)

    # Define flow
    graph.add_edge(START, "validate")
    
    def after_validate(state: OrchestratorState):
        if state.get("error_message"):
            return "final_logic"
        return "fetch_info"

    graph.add_conditional_edges("validate", after_validate, {
        "final_logic": "final_logic",
        "fetch_info": "fetch_info"
    })
    
    graph.add_edge("fetch_info", "llm_node")

    def custom_tools_condition(state: OrchestratorState):
        messages = state.get("sanction_messages", [])
        if messages and isinstance(messages[-1], AIMessage) and messages[-1].tool_calls:
            return "tools"
        return "final_logic"

    graph.add_conditional_edges("llm_node", custom_tools_condition, {
        "tools": "tool_node", 
        "final_logic" : "final_logic" 
    })
    
    graph.add_edge("tool_node", "llm_node")
    graph.add_edge("final_logic", END)

    return graph.compile()
