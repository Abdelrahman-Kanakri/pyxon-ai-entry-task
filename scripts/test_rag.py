import requests
import json

API_URL = "http://localhost:8000/api/v1"

def test_rag():
    print("Testing RAG Query...")
    payload = {
        "query": "What is the summary of the document?",
        "top_k": 3
    }
    
    try:
        response = requests.post(f"{API_URL}/retrieval/query", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ Query Successful")
            print(f"Total Results: {data['total_results']}")
            
            answer = data.get("answer")
            if answer:
                print(f"✅ AI Answer Received:\n{answer}")
            else:
                print("❌ No AI Answer generated")
        else:
            print(f"❌ Query Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_rag()
