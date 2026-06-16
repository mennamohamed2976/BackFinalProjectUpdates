import requests
import json

AI_URL = "http://localhost:8001/api/matching/"

with open("matching_request_1000_recipients.json", "r", encoding="utf-8") as f:
    payload = json.load(f)

payload["top_k"] = 1

print("🔄 Sending data to the AI...")
response = requests.post(AI_URL, json=payload, timeout=120)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Done! Number of matches: {len(result['top_matches'])}")
    print("\n🏆 Top Results:")
    for i, match in enumerate(result['top_matches'], 1):
        print(f"  {i}. recipient_id: {match['recipient_id']} | score: {match['score']}%")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)