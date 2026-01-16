# quick_test.py - UPDATED FOR AUTO-AGENT TESTING
import requests
import json
import time
import re

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
        ("upload documents", "Step 4: Upload documents for verification"),
        ("Pune", "Step 5: Provide city for verification"),
        ("proceed", "Step 6: Accept offer for final underwriting"),
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

def test_mismatch_verification():
    print("\n🚨 TESTING NAME-PHONE MISMATCH")
    print("="*50)
    
    session_id = f"mismatch_test_{int(time.time())}"
    print(f"Session: {session_id}")
    
    test_steps = [
        ("Asha Verma", "Step 0: Provide Name (Asha Verma)"),
        ("9810000005", "Step 1: Provide Phone of Nisha Patel (9810000005)"),
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
            print(f"🤖 BOT: {data['response']}")
        else:
            print(f"❌ Error: {response.status_code}")
            break
    print("="*50)

def test_match_verification():
    print("\n✅ TESTING NAME-PHONE MATCH")
    print("="*50)
    
    session_id = f"match_test_{int(time.time())}"
    print(f"Session: {session_id}")
    
    test_steps = [
        ("Asha Verma", "Step 0: Provide Name (Asha Verma)"),
        ("9810000001", "Step 1: Provide Phone of Asha Verma (9810000001)"),
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
            print(f"🤖 BOT: {data['response']}")
        else:
            print(f"❌ Error: {response.status_code}")
            break
    print("="*50)

def test_live_tracking():
    print("\n🛰️ TESTING LIVE TRACKING")
    print("="*50)
    
    session_id = f"tracking_test_{int(time.time())}"
    print(f"Session: {session_id}")
    
    # Complete the flow to get a Reference ID
    steps = [
        ("Asha Verma", "Provide Name"),
        ("9810000001", "Provide Phone"),
        ("150000", "Provide Amount"),
        ("36 months", "Provide Tenure"),
        ("upload documents", "Upload Docs"),
        ("Pune", "Provide City"),
        ("proceed", "Accept Offer"),
        ("generate sanction", "Generate Sanction")
    ]
    
    ref_id = None
    for user_input, desc in steps:
        print(f"👤 {desc}: {user_input}")
        resp = requests.post(f"{BASE_URL}/chat", json={"session_id": session_id, "message": user_input})
        if resp.status_code != 200:
            print(f"❌ Error in chat: {resp.status_code}")
            return
            
        data = resp.json()
        print(f"🤖 BOT: {data['response'][:100]}...")
        
        # Look for Reference ID in response
        match = re.search(r'Reference ID: (TATA-[A-Z0-9]+)', data['response'])
        if match:
            ref_id = match.group(1)
            print(f"✨ Found Reference ID: {ref_id}")

    if ref_id:
        print(f"\n🔍 Calling Tracking API for {ref_id}...")
        # Add a small delay for state propagation if needed (though it's in-memory)
        time.sleep(0.5)
        track_resp = requests.get(f"{BASE_URL}/track/{ref_id}")
        if track_resp.status_code == 200:
            track_data = track_resp.json()
            print(f"✅ Tracking Success!")
            print(f"   Customer: {track_data['customerName']}")
            print(f"   Amount: ₹{track_data['loanAmount']:,}")
            print(f"   Current Stage: {track_data['currentStage']}")
            for stage in track_data['stages']:
                print(f"   - {stage['name']}: {stage['status']}")
            
            # Now test in-chat tracking
            print(f"\n💬 Testing in-chat tracking for {ref_id}...")
            chat_resp = requests.post(f"{BASE_URL}/chat", json={"session_id": "new_user_123", "message": f"What is the status of {ref_id}?"})
            if chat_resp.status_code == 200:
                chat_data = chat_resp.json()
                print(f"🤖 BOT: {chat_data['response']}")
                if ref_id in chat_data['response'] and "Asha Verma" in chat_data['response']:
                    print("✅ In-chat tracking works!")
                else:
                    print("❌ In-chat tracking response incorrect")
            else:
                print(f"❌ In-chat tracking failed: {chat_resp.status_code}")
        else:
            print(f"❌ Tracking Failed: {track_resp.status_code}")
            print(f"   Response: {track_resp.text}")
    else:
        print("❌ Could not generate Reference ID")
    print("="*50)

if __name__ == "__main__":
    # test_auto_agent()
    # test_mismatch_verification()
    # test_match_verification()
    test_live_tracking()
