import json
import httpx
import time

def run_demo():
    print("Starting Comprehensive Demo Ingestion...")
    try:
        with open("demo_data_comprehensive.json", "r") as f:
            data = json.load(f)
            
        with httpx.Client() as client:
            print("Resetting database to ensure a clean demo run...")
            reset_resp = client.post("http://localhost:8000/api/v1/reset")
            if reset_resp.status_code == 200:
                print("Database reset successfully.")
            else:
                print(f"Warning: Failed to reset database: {reset_resp.text}")
                
            for claim in data:
                print(f"Submitting Claim: {claim['id']} - '{claim['claim']}' (Source: {claim['source_id']}, Rel: {claim['source_reliability']})")
                response = client.post("http://localhost:8000/api/v1/claims", json=claim, timeout=60.0)
                if response.status_code == 200:
                    res_json = response.json()
                    action = res_json.get("action")
                    reason = res_json.get("reason")
                    delta = res_json.get("confidence_delta", 0.0)
                    print(f"  Result: Action={action} (Delta={delta})")
                    print(f"  Reason: {reason}")
                else:
                    print(f"  Error {response.status_code}: {response.text}")
                print("-" * 60)
                # Small delay to allow processing
                time.sleep(1.5)
                
        print("Comprehensive Demo Completed. Please check the Streamlit dashboard Change Log, Memory Store, and Evolution Timeline pages!")
    except Exception as e:
        print(f"Failed to run comprehensive demo: {e}")

if __name__ == "__main__":
    run_demo()
