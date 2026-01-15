# EY Techathon 6.0 – NBFC Loan Assistant (BFSI)

End‑to‑end NBFC loan assistant for Tata Capital built for EY Techathon 6.0 (BFSI track).
The system combines:

- A **FastAPI backend** exposing a unified `/chat` endpoint
- A **tool-based MCP Server** that simulates Tata Capital backend services
- A **multi‑agent orchestration layer** (master + worker agents)
- A **frontend chat UI** (Vite + React, in the `frontend/` repo)

The assistant guides a user from first contact all the way to **loan disbursement**, using specialized worker agents for each stage of the journey.

---

## High‑Level Flow

1. **Master Agent** starts the conversation, collects `customer_id` and user intent.
2. **Sales Agent** fetches customer info from the MCP server and negotiates offer terms
   (amount, tenure, interest rate) within business constraints.
3. **Verification Agent** performs KYC checks using MCP tools and later verifies uploaded documents.
4. **Underwriting Agent** calls MCP underwriting tools using credit score and salary slip data.
5. **Sanction Agent** generates a **PDF sanction letter** via MCP, exposes a download URL served by FastAPI.
6. **Disbursement Agent** finalizes the loan and returns a disbursement confirmation.

All agents read and write to a shared **orchestration state**, so the full customer context is available at every step.

---

## Project Structure

```text
MCP_client_server-master/
├── MCPServer/              # MCP backend (customer data, KYC, underwriting, sanction tools)
│   └── server.py
├── api.py                  # FastAPI app + 7‑agent orchestration & /chat endpoint
├── orchestrator/
│   └── graph.py            # (legacy) graph‑based orchestrator reference
├── sharedState/
│   ├── __init__.py
│   └── state.py            # Typed orchestration state definition (OrchestrationState)
├── workerAgents/
│   ├── sales.py            # Sales Agent (offer generation & negotiation)
│   ├── verification.py     # Verification Agent (KYC + document verification)
│   ├── underwriting.py     # Underwriting Agent
│   ├── sanction.py         # Sanction Letter Generator Agent
│   ├── simple_graph.py     # simple example orchestration
│   └── __init__.py
├── storage/
│   ├── sanction_letters/   # Generated sanction PDFs (served statically by FastAPI)
│   └── mcp_audit.log       # MCP audit / debug log
├── start_all.bat           # Helper script to start MCP + API and run tests
├── test_client.py          # Manual console client for /chat
├── verify_flow.py          # Automated end‑to‑end flow test
├── test_sanction_flow.py   # Focused test for sanction letter generation & link
└── README.md
```

> The **frontend React UI** lives in a sibling `frontend/` directory and talks to the API on port `8083`.

---

## Multi‑Agent Architecture

### Orchestration State

Agents communicate through a shared `OrchestrationState` (see `sharedState/state.py`) that is stored per session in the API layer.
Key fields include:

- `customer_id`, `user_query`, `status`
- `customer_info`, `requested_amount`, `preferred_tenure_months`, `max_interest_rate`
- `kyc_result`, `kyc_status`
- `credit_score`, `salary_slip_resource`, `underwriting_result`, `underwriting_status`
- `sanction_letter_resource`, `sanction_letter_path`, `sanction_letter_url`
- `flow_stage` / `flow_step`, `messages`, `log_events`

This aligns with the original typed `OrchestrationState` and ensures every agent can read/write a consistent view of the user journey.

### Agents

- **Master Agent (in `api.py`)**
  - Owns the conversation and `flow_step`
  - Collects core inputs (customer id, amount, tenure, confirmations)
  - Routes to worker agents via `determine_next_agent(state)`

- **Sales Agent (`workerAgents/sales.py` and `api.py`)**
  - Uses `get_customer_info` MCP tool
  - Enforces business rules (e.g. limits vs pre‑approved amount)
  - Proposes offers and handles negotiation rounds

- **Verification Agent (`workerAgents/verification.py`, `api.py`)**
  - Uses `verify_kyc` and `get_credit_score` MCP tools
  - Step 3: KYC check
  - Step 4: Document verification after upload

- **Underwriting Agent (`workerAgents/underwriting.py`, `api.py`)**
  - Calls `underwrite_loan` MCP tool
  - Writes `underwriting_status` and decision metadata into state

- **Sanction Agent (`workerAgents/sanction.py`, `api.py`)**
  - Calls `generate_sanction_letter` MCP tool
  - Stores the returned resource and builds a public URL
    (`http://localhost:8083/sanction_letters/<file>.pdf`)
  - Updates response so the frontend can show a **download button**

- **Disbursement Agent (`api.py`)**
  - Simulates loan disbursement and returns a final confirmation

---

## Backend Setup (MCP + API)

> Requires **Python 3.10+** and `pip`.

1. Create and activate a virtual environment (optional but recommended):

   ```powershell
   cd "c:\Users\harsh\Downloads\MCP_client_server-master(1)\MCP_client_server-master"
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Install Python dependencies (FastAPI, `requests`, etc.). If a `requirements.txt` is available, run:

   ```powershell
   pip install -r requirements.txt
   ```

3. Start the MCP Server (backend tools):

   ```powershell
   python MCPServer\server.py
   ```

4. In a new terminal, start the API (multi‑agent orchestrator):

   ```powershell
   python api.py
   ```

   The API listens on `http://127.0.0.1:8083` and exposes:

   - `POST /chat` – main chat endpoint
   - `GET /health` – health check
   - `GET /reset/{session_id}` – clear session state
   - Static `GET /sanction_letters/<file>.pdf` – sanction PDFs

---

## Frontend Setup (Chat UI)

> The frontend lives in `frontend/` and uses Vite + React.

1. Install dependencies:

   ```powershell
   cd ..\frontend
   npm install
   ```

2. Run the dev server on port `5173`:

   ```powershell
   npm run dev
   ```

3. Open the UI in a browser:

   - `http://localhost:5173/`

Ensure the MCP Server and API (`api.py`) are running before using the chat UI.

---

## Testing the Agentic Flow

There are several Python helpers to test the multi‑agent flow without the frontend.

### 1. Automated Flow Test

```powershell
cd "c:\Users\harsh\Downloads\MCP_client_server-master(1)\MCP_client_server-master"
python verify_flow.py
```

This script:

- Hits `POST /chat` with realistic user messages
- Verifies progression through stages: master → sales → verification → underwriting → sanction
- Prints state snapshots (KYC status, underwriting result, etc.)

### 2. Sanction Letter Focused Test

```powershell
python test_sanction_flow.py
```

This script walks through a **happy path**:

1. Provide `customer_id` (`CUST001`)
2. Enter loan amount and tenure
3. Accept the offer
4. Upload documents
5. Proceed to sanction

It verifies that:

- The flow reaches the sanction stage
- A sanction PDF is generated under `storage/sanction_letters/`
- A valid download URL is present in the final response

### 3. Manual Console Test

```powershell
python test_client.py
```

This opens a simple console chat client connected to `POST /chat` for manual experimentation.

---

## Key Design Choices

- **Single shared state** per session stored in the API layer for predictable agent behavior
- **Deterministic routing** via `determine_next_agent(state)` to avoid uncontrolled agent loops
- **MCP tooling** for all backend‑like actions (KYC, underwriting, document handling, sanction letter generation)
- **Static serving** of generated sanction letters from `storage/sanction_letters` to keep things simple and debuggable

---

## Repository

This project is maintained in:

- `https://github.com/harshit1arora/EY-Techathon-6.0-BFSI` (branch: `main`)

Feel free to fork, experiment with new agent strategies, or plug in real backend services instead of the MCP simulator.
