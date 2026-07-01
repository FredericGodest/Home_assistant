import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("IP_URL")

while True:
    query = input("\nPosez une question (ou tapez 'exit' pour quitter) : ")
    print(f"Question: {str(query)}")
    if query.lower() == "exit":
        break
    r = requests.post(
            f"{BASE_URL}/ask",
            json={"question": query},
            headers={"X-API-Key": os.getenv("GATEWAY_API_KEY")},
            timeout=30,
        )
    if r.status_code == 200:
        print(r.text)
