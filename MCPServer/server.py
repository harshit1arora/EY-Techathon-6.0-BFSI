# mcp_http_server.py - SIMPLE HTTP VERSION
import os
import json
import uuid
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from reportlab.pdfgen import canvas

app = FastAPI(title="NBFC MCP HTTP Server")

# CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Storage - Use absolute path or consistent relative path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_DIR = os.path.join(BASE_DIR, "storage", "sanction_letters")
os.makedirs(STORAGE_DIR, exist_ok=True)

# Customer data (same as before)
CUSTOMERS = {
    "CUST001": {"customer_id":"CUST001","name":"Asha Verma","age":32,"city":"Pune","phone":"9810000001","email":"asha@example.com","pre_approved_limit":300000,"salary_monthly":60000,"credit_score":745},
    "CUST002": {"customer_id":"CUST002","name":"Rahul Sharma","age":29,"city":"Delhi","phone":"9810000002","email":"rahul@example.com","pre_approved_limit":200000,"salary_monthly":45000,"credit_score":712},
    "CUST003": {"customer_id":"CUST003","name":"Sneha Iyer","age":35,"city":"Bengaluru","phone":"9810000003","email":"sneha@example.com","pre_approved_limit":400000,"salary_monthly":85000,"credit_score":780},
    "CUST004": {"customer_id":"CUST004","name":"Vikram Singh","age":40,"city":"Lucknow","phone":"9810000004","email":"vikram@example.com","pre_approved_limit":150000,"salary_monthly":30000,"credit_score":690},
    "CUST005": {"customer_id":"CUST005","name":"Nisha Patel","age":27,"city":"Ahmedabad","phone":"9810000005","email":"nisha@example.com","pre_approved_limit":250000,"salary_monthly":52000,"credit_score":710},
    "CUST006": {"customer_id":"CUST006","name":"Arjun Rao","age":31,"city":"Hyderabad","phone":"9810000006","email":"arjun@example.com","pre_approved_limit":350000,"salary_monthly":70000,"credit_score":760},
    "CUST007": {"customer_id":"CUST007","name":"Meera Desai","age":30,"city":"Surat","phone":"9810000007","email":"meera@example.com","pre_approved_limit":180000,"salary_monthly":40000,"credit_score":695},
    "CUST008": {"customer_id":"CUST008","name":"Karan Mehta","age":33,"city":"Mumbai","phone":"9810000008","email":"karan@example.com","pre_approved_limit":320000,"salary_monthly":65000,"credit_score":735},
    "CUST009": {"customer_id":"CUST009","name":"Priya Nair","age":28,"city":"Kochi","phone":"9810000009","email":"priya@example.com","pre_approved_limit":280000,"salary_monthly":48000,"credit_score":725},
    "CUST010": {"customer_id":"CUST010","name":"Sourav Ghosh","age":36,"city":"Kolkata","phone":"9810000010","email":"sourav@example.com","pre_approved_limit":500000,"salary_monthly":90000,"credit_score":790}
}

# EMI calculation
def compute_emi(P: float, annual_rate: float, n_months: int) -> float:
    r = annual_rate / 12.0 / 100.0
    if r == 0:
        return P / n_months
    num = P * r * (1 + r) ** n_months
    den = (1 + r) ** n_months - 1
    return num / den

# Models
class UnderwriteInput(BaseModel):
    customer_id: str
    requested_amount: int
    tenure_months: int = 36
    annual_rate: float = 12.0
    salary_provided: int = None
    salary_slip_resource: str = None

# Endpoints
@app.post("/call/get_customer_info")
def get_customer_info(payload: Dict[str, Any]):
    cid = payload.get("customer_id")
    if not cid:
        raise HTTPException(400, "customer_id required")
    
    cust = CUSTOMERS.get(cid)
    if not cust:
        raise HTTPException(404, "customer not found")
    
    return {"status": "ok", "result": cust}

@app.post("/call/get_customer_by_phone")
def get_customer_by_phone(payload: Dict[str, Any]):
    phone = payload.get("phone")
    if not phone:
        raise HTTPException(400, "phone required")
    for cid, cust in CUSTOMERS.items():
        if cust.get("phone") == phone:
            return {"status": "ok", "result": cust}
    raise HTTPException(404, "customer not found")

@app.post("/call/verify_kyc")
def verify_kyc(payload: Dict[str, Any]):
    cid = payload.get("customer_id")
    phone = payload.get("phone")
    
    if not cid or not phone:
        raise HTTPException(400, "customer_id and phone required")
    
    cust = CUSTOMERS.get(cid)
    if not cust:
        raise HTTPException(404, "customer not found")
    
    phone_verified = (cust.get("phone") == phone)
    return {"status": "ok", "result": {"phone_verified": phone_verified, "address_verified": True}}

@app.post("/call/get_credit_score")
def get_credit_score(payload: Dict[str, Any]):
    cid = payload.get("customer_id")
    if not cid:
        raise HTTPException(400, "customer_id required")
    
    cust = CUSTOMERS.get(cid)
    if not cust:
        raise HTTPException(404, "customer not found")
    
    return {"status": "ok", "result": {"credit_score": cust.get("credit_score")}}

@app.post("/call/underwrite_loan")
def underwrite_loan(payload: UnderwriteInput):
    data = payload.dict()
    cid = data["customer_id"]
    
    cust = CUSTOMERS.get(cid)
    if not cust:
        raise HTTPException(404, "customer not found")
    
    score = cust.get("credit_score", 0)
    pre_limit = cust.get("pre_approved_limit", 0)
    requested = data["requested_amount"]
    tenure = data["tenure_months"]
    annual_rate = data["annual_rate"]
    
    if score < 700:
        return {"status": "ok", "result": {
            "decision": "reject", 
            "reason": "credit_score_below_700",
            "credit_score": score
        }}
    
    if requested <= pre_limit:
        emi = compute_emi(requested, annual_rate, tenure)
        return {"status": "ok", "result": {
            "decision": "approve",
            "emi": emi,
            "reason": "within_pre_approved_limit"
        }}
    
    if requested <= 2 * pre_limit:
        if not data["salary_slip_resource"] and not data["salary_provided"]:
            return {"status": "ok", "result": {
                "decision": "require_salary_slip",
                "reason": "salary_slip_required"
            }}
        
        salary = data["salary_provided"] if data["salary_provided"] is not None else cust.get("salary_monthly", 0)
        emi = compute_emi(requested, annual_rate, tenure)
        
        if emi <= 0.5 * salary:
            return {"status": "ok", "result": {
                "decision": "approve",
                "emi": emi,
                "reason": "emi_within_50pct_salary"
            }}
        else:
            return {"status": "ok", "result": {
                "decision": "reject",
                "reason": "emi_exceeds_50pct_salary",
                "emi": emi,
                "salary_monthly": salary
            }}
    
    return {"status": "ok", "result": {
        "decision": "reject",
        "reason": "amount_exceeds_2x_pre_approved",
        "pre_limit": pre_limit,
        "requested": requested
    }}

@app.post("/call/generate_sanction_letter")
def generate_sanction_letter(payload: Dict[str, Any]):
    cid = payload.get("customer_id")
    amount = payload.get("amount")
    
    if not cid or not amount:
        raise HTTPException(400, "customer_id and amount required")
    
    cust = CUSTOMERS.get(cid)
    if not cust:
        raise HTTPException(404, "customer not found")
    
    filename = f"sanction_{cid}_{uuid.uuid4().hex}.pdf"
    path = os.path.join(STORAGE_DIR, filename)
    
    c = canvas.Canvas(path)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 800, "Sanction Letter")
    c.setFont("Helvetica", 11)
    c.drawString(50, 770, f"Date: {datetime.utcnow().strftime('%Y-%m-%d')}")
    c.drawString(50, 750, f"Customer: {cust.get('name')} (ID: {cid})")
    c.drawString(50, 730, f"Approved Amount: INR {amount}")
    c.drawString(50, 710, f"Tenure: {payload.get('tenure_months', 36)} months")
    c.drawString(50, 690, f"Interest Rate (annual): {payload.get('interest_rate', 12.0)}%")
    c.drawString(50, 660, "This is a demo sanction letter generated by MCP server.")
    c.save()
    
    resource_url = f"resource://{filename}"
    return {"status": "ok", "result": {"resource": resource_url, "path": path}}

@app.get("/health")
def health():
    return {"status": "ok", "service": "mcp-http-server", "time": datetime.utcnow().isoformat()}

@app.get("/")
def root():
    return {
        "service": "NBFC MCP HTTP Server",
        "status": "running",
        "endpoints": {
            "POST /call/get_customer_info": "Get customer info",
            "POST /call/verify_kyc": "Verify KYC",
            "POST /call/get_credit_score": "Get credit score",
            "POST /call/underwrite_loan": "Underwrite loan",
            "POST /call/generate_sanction_letter": "Generate sanction letter",
            "GET /health": "Health check"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting NBFC MCP HTTP Server...")
    print("✅ Port: 8000")
    print("✅ Customers: 10 mock customers")
    print("✅ Endpoints: /call/* for tools")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
