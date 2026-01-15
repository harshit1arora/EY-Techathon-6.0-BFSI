# test_client.py - UPDATED
import requests
import sys

# Configuration
API_URL = "http://127.0.0.1:8083/chat"
SESSION_ID = "terminal_test_user_01"

def main():
    print(f"--- 🤖 NBFC AI Agent CLI (Session: {SESSION_ID}) ---")
    print("Type 'exit' or 'quit' to stop. Type '/reset' to start fresh.\n")
    
    # Start fresh session
    try:
        requests.get(f"http://127.0.0.1:8083/reset/{SESSION_ID}")
    except:
        pass

    while True:
        try:
            # 1. Get User Input
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting...")
                break
            elif user_input.lower() == "/reset":
                try:
                    requests.get(f"http://127.0.0.1:8080/reset/{SESSION_ID}")
                    print("✅ Session reset. Starting fresh...\n")
                    continue
                except:
                    print("❌ Could not reset session\n")
                    continue
            
            # 2. Send to API
            payload = {
                "session_id": SESSION_ID,
                "message": user_input
            }
            
            print("🤖 Processing...", end="\r")
            
            response = requests.post(API_URL, json=payload, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ API Error {response.status_code}: {response.text[:100]}")
                continue
            
            # 3. Parse Response
            data = response.json()
            bot_text = data.get("response", "")
            stage = data.get("debug_stage", "UNKNOWN")
            flow_stage = data.get("flow_stage", "")
            
            # 4. Print Output with context
            print(f"🤖 Bot ({stage}): {bot_text}")
            
            # Show additional context if available
            if flow_stage:
                print(f"   📍 Flow stage: {flow_stage}")
            if data.get("customer_id"):
                print(f"   👤 Customer: {data.get('customer_id')}")
            if data.get("kyc_status") and data["kyc_status"] != "pending":
                print(f"   ✅ KYC: {data.get('kyc_status')}")
            if data.get("underwriting_status") and data["underwriting_status"] != "pending":
                print(f"   📄 Underwriting: {data.get('underwriting_status')}")
            if data.get("sanction_status") and data["sanction_status"] != "pending":
                print(f"   📑 Sanction: {data.get('sanction_status')}")
            
            print()  # Empty line for readability

        except requests.exceptions.ConnectionError:
            print("\n❌ Error: Could not connect to API. Is 'api.py' running?")
            print("   Make sure you run: python api.py")
            break
        except requests.exceptions.Timeout:
            print("\n❌ Error: Request timed out. Server might be busy.")
            continue
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue

if __name__ == "__main__":
    main()