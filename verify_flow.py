# verify_flow.py - UPDATED FOR NEW API
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8083"
SESSION_ID = "automated_test_user"

def chat(message, wait_time=1):
    print(f"\n👤 USER: {message}")
    payload = {"session_id": SESSION_ID, "message": message}
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
            return None
        
        data = response.json()
        
        # Format response
        stage = data.get("debug_stage", "unknown")
        response_text = data.get("response", "No response")
        
        print(f"🤖 BOT ({stage}): {response_text}")
        
        # Show state progression
        print("   📊 STATE:")
        if data.get("flow_stage"):
            print(f"     • Flow: {data['flow_stage']}")
        if data.get("customer_id"):
            print(f"     • Customer ID: {data['customer_id']}")
        if data.get("kyc_status") and data['kyc_status'] != "pending":
            print(f"     • KYC: {data['kyc_status']}")
        if data.get("underwriting_status") and data['underwriting_status'] != "pending":
            print(f"     • Underwriting: {data['underwriting_status']}")
        if data.get("sanction_status") and data['sanction_status'] != "pending":
            print(f"     • Sanction: {data['sanction_status']}")
        
        time.sleep(wait_time)
        return data
        
    except requests.exceptions.Timeout:
        print("❌ Timeout: Server not responding")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def run_test():
    print("=" * 60)
    print("🧪 NBFC LOAN ASSISTANT - AUTOMATED TEST")
    print("=" * 60)
    
    # Check if API is running
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ API Status: {health.json().get('status', 'unknown')}")
    except:
        print("❌ API not reachable. Make sure api.py is running!")
        return
    
    # Reset session
    try:
        reset = requests.get(f"{BASE_URL}/reset/{SESSION_ID}")
        print(f"✅ Session reset: {reset.json().get('message', '')}")
    except:
        print("⚠ Could not reset session, continuing anyway...")
    
    time.sleep(1)
    
    # Test flow with natural language
    test_steps = [
        ("Hi, I need a personal loan", "Initial greeting"),
        ("My customer ID is CUST001", "Provide Customer ID"),
        ("I need 150000 rupees", "Specify loan amount"),
        ("For 12 months", "Specify tenure"),
        ("Yes, please proceed with this offer", "Accept offer"),
        ("What's the status?", "Check progress")
    ]
    
    successful_steps = 0
    
    for i, (message, description) in enumerate(test_steps, 1):
        print(f"\n{'='*40}")
        print(f"STEP {i}: {description}")
        print(f"{'='*40}")
        
        result = chat(message)
        if result:
            successful_steps += 1
            
            # Check if we're progressing
            if result.get("flow_stage"):
                stage = result["flow_stage"]
                print(f"   → Progress: {stage.upper()}")
                
                # If we reached completed state, we can stop early
                if stage == "completed":
                    print("🎉 Test completed successfully!")
                    break
        else:
            print(f"❌ Step {i} failed")
            break
        
        # Add extra wait before final step
        if i == len(test_steps) - 1:
            time.sleep(2)
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total steps: {len(test_steps)}")
    print(f"Successful: {successful_steps}")
    print(f"Success rate: {(successful_steps/len(test_steps))*100:.1f}%")
    
    if successful_steps == len(test_steps):
        print("✅ TEST PASSED: All steps completed successfully!")
    elif successful_steps >= 4:
        print("⚠ TEST PARTIALLY PASSED: Most steps completed")
    else:
        print("❌ TEST FAILED: Too many steps failed")
    
    # Show final session state
    try:
        print(f"\n📊 Final session state:")
        state_resp = requests.get(f"{BASE_URL}/session/{SESSION_ID}")
        if state_resp.status_code == 200:
            state = state_resp.json()
            print(f"   Flow stage: {state.get('flow_stage', 'unknown')}")
            print(f"   KYC status: {state.get('kyc_status', 'unknown')}")
            print(f"   UW status: {state.get('underwriting_status', 'unknown')}")
            print(f"   Sanction: {state.get('sanction_letter_status', 'unknown')}")
    except:
        print("   Could not retrieve final state")
    
    print(f"{'='*60}")

if __name__ == "__main__":
    run_test()