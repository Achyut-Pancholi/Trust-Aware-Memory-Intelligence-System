import json
import httpx
import time

def run_demo():
    print("Starting Demo Ingestion...")
    try:
        with open("demo_data.json", "r") as f:
            data = json.load(f)
            
        with httpx.Client() as client:
            for claim in data:
                print(f"Submitting Claim ID: {claim['id']} - '{claim['claim']}'")
                response = client.post("http://localhost:8000/api/v1/claims", json=claim, timeout=30.0)
                if response.status_code == 200:
                    print(f"Success! Action taken: {response.json().get('action')}")
                else:
                    print(f"Error {response.status_code}: {response.text}")
                
                # Small delay to observe the dashboard updates if needed
                time.sleep(2)
                
        print("Demo completed.")
    except Exception as e:
        print(f"Failed to run demo: {e}")

if __name__ == "__main__":
    run_demo()
