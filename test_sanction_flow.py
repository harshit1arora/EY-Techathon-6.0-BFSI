
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8083"
SESSION_ID = "sanction_test_user_final_v2"

def chat(message):
    print(f"\n👤 USER: {message}")
    payload = {"session_id": SESSION_ID, "message": message}
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    data = response.json()
    print(f"🤖 BOT: {data.get('response')}")
    return data

def run_sanction_test():
    print("🚀 Starting Precise Flow to Sanction...")
    chat("My customer ID is CUST001")
    chat("50000")
    chat("12 months")
    chat("Yes, proceed with this offer")
    chat("upload documents")
    chat("proceed")
    print("\n--- Final Step: Sanctioning ---")
    result = chat("generate sanction")
    
    response_text = result.get('response', '')
    print(f"\nFinal Response: {response_text}")
    
    if "sanction" in response_text.lower() or "download" in response_text.lower() or "congratulations" in response_text.lower():
        print("\n✅ SUCCESS: Sanction letter flow completed!")
        if "http://localhost:8083/sanction_letters/" in response_text:
            print("🔗 Valid download link found!")
        else:
            print("⚠️ Download link might be missing or in wrong format.")
    else:
        print("\n❌ FAILED: Sanction letter not found in response.")

if __name__ == "__main__":
    run_sanction_test()
