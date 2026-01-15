# quick_test.py - UPDATED FOR AUTO-AGENT TESTING
import requests
import json
import time

BASE_URL = "http://localhost:8083"

def test_auto_agent():
    print("🚀 AUTO AGENT SWITCHING TEST")
    print("="*50)
    
    # Create new session
    session_id = f"auto_test_{int(time.time())}"
    print(f"Session: {session_id}")
    
    test_steps = [
        ("CUST001", "Step 1: Customer ID"),
        ("₹150,000", "Step 2: Loan amount"),
        ("36 months", "Step 3: Tenure (SHOULD TRIGGER AGENTS)"),
    ]
    
    for user_input, description in test_steps:
        print(f"\n📝 {description}")
        print(f"👤 You: {user_input}")
        
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"session_id": session_id, "message": user_input}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"🤖 {data['last_active_worker'].upper()}: {data['response'][:70]}...")
            print(f"   Step: {data['flow_step']}, Agent: {data['last_active_worker']}")
            
            # Wait to see agent switching
            if description == "Step 3: Tenure (SHOULD TRIGGER AGENTS)":
                print("   ⏳ Waiting for agent chain...")
                time.sleep(2)
        else:
            print(f"❌ Error: {response.status_code}")
            break
    
    # Check what agents ran
    print("\n🔍 Checking final state...")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"session_id": session_id, "message": "status"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Final Agent: {data['last_active_worker']}")
        print(f"Final Step: {data['flow_step']}")
        print(f"Stage: {data.get('debug_stage')}")
    
    print("="*50)
    print("✅ Test completed!")

if __name__ == "__main__":
    test_auto_agent()