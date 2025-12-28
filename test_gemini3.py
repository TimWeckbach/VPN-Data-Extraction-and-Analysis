import requests
import json
import time

API_KEY = "AIzaSyDnU_8SoiS_XSR7eIQSmYoEZhCVtKlAM1Y"
MODEL_NAME = "gemini-3-flash-preview"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

CATEGORIES = {
    "Technical Blocking": "Measures/Technologies used to detect or block the specific use of VPNs/Proxies.",
    "Legal Threat": "Explicit threats of account termination...",
    "Price Discrimination": "Differences in pricing...",
    "General Terms": "Standard legal text..."
}

SYSTEM_PROMPT = f"""You are a scientific classifier.
CATEGORIES:
1. Technical Blocking: {CATEGORIES['Technical Blocking']}
2. Legal Threat: {CATEGORIES['Legal Threat']}
3. Price Discrimination: {CATEGORIES['Price Discrimination']}
...
INSTRUCTIONS:
- Return a JSON array of objects for the sentences in EXACT order.
- Format: [ {{ "category": "Category Name", "confidence": 0.9 }}, ... ]
"""

sentences = [
    "We use IP blocking to stop VPNs.",
    "Subscription price varies by country.",
    "Hello world.",
    "Terms of service apply.",
    "Users caught using proxies will be banned."
]

formatted_input = "\n".join([f"{i+1}. {s}" for i, s in enumerate(sentences)])

payload = {
    "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\nSENTENCES:\n{formatted_input}\nJSON OUTPUT:"}]}],
    "generationConfig": {"responseMimeType": "application/json"}
}

print(f"Sending request to {MODEL_NAME}...")
start = time.time()
try:
    response = requests.post(API_URL, json=payload, timeout=60)
    print(f"Status: {response.status_code}")
    print(f"Time: {time.time() - start:.2f}s")
    if response.status_code != 200:
        print(f"Error Body: {response.text}")
    else:
        print("Response OK. Parsing...")
        print(response.json())
except Exception as e:
    print(f"Exception: {e}")
