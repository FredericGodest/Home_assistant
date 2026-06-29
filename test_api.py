#!/usr/bin/env python3
"""Test script for FastAPI API"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("IP_URL")

def test_health():
    """GET /health — vérifie status 200 et "status": "ok" """
    print("\n── GET /health ──")
    try:
        print(f"{BASE_URL}/health")
        r = requests.get(f"{BASE_URL}/health", timeout=10)
        ok = r.status_code == 200 and "status" in r.json() and r.json()["status"] == "ok"
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        print("PASS ✅" if ok else f"FAIL ❌")
        return ok
    except Exception as e:
        print(f"FAIL ❌ — exception: {e}")
        return False


def test_ask_success():
    """POST /ask avec question — vérifie 200 et clé "answer" """
    print("\n── POST /ask (avec clé API) ──")
    api_key = os.getenv("GATEWAY_API_KEY")
    if not api_key:
        print("FAIL ❌ — GATEWAY_API_KEY non définie")
        return False
    try:
        r = requests.post(
            f"{BASE_URL}/ask",
            json={"question": "Que vois tu à la caméra ?"},
            headers = {"X-API-Key": os.getenv("GATEWAY_API_KEY")},
            timeout=30,
        )
        ok = r.status_code == 200 and "answer" in r.json()
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:500]}")
        print("PASS ✅" if ok else f"FAIL ❌")
        return ok
    except Exception as e:
        print(f"FAIL ❌ — exception: {e}")
        return False

def main():
    print("=" * 50)
    print("TEST API")
    print("=" * 50)

    results = [
        ("GET /health", test_health),
        ("POST /ask (success)", test_ask_success),
    ]

    passed = sum(1 for _, test in results if test())
    total = len(results)

    print("\n" + "=" * 50)
    print(f"RÉSULTAT : {passed}/{total} test(s) passé(s)")
    print("=" * 50)


if __name__ == "__main__":
    main()