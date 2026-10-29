"""
Nebius Token Factory & NVIDIA Nemotron Verification Script.
Run this script to verify that your API key and Nemotron endpoint are working live.

Usage:
  python test_nebius_connection.py
"""
import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

def safe_print(text: str):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", "replace").decode("ascii"))

def verify_nebius():
    api_key = os.getenv("NEBIUS_API_KEY", "").strip()
    base_url = os.getenv("NEBIUS_BASE_URL", "https://integrate.api.nvidia.com/v1/").rstrip("/") + "/"
    model = os.getenv("NEBIUS_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")

    safe_print("=================================================================")
    safe_print(" NVIDIA Nemotron / Nebius Token Factory Verification")
    safe_print("=================================================================")
    safe_print(f"Base URL : {base_url}")
    safe_print(f"Model ID : {model}")
    safe_print(f"API Key  : {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '(empty or default)'}")
    safe_print("-----------------------------------------------------------------")

    if not api_key or api_key == "your_key_here":
        safe_print("[ERROR] NEBIUS_API_KEY is not set in your .env file!")
        return False

    try:
        from openai import OpenAI
    except ImportError:
        safe_print("[ERROR] 'openai' Python package is not installed. Run: pip install openai")
        return False

    safe_print("Initiating test inference call to NVIDIA Nemotron...")
    client = OpenAI(base_url=base_url, api_key=api_key)
    
    start_time = time.time()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are PaisaPath AI, an expert financial education companion."},
                {"role": "user", "content": "Confirm you are active by answering in one short sentence: What is an emergency fund?"}
            ],
            temperature=0.2,
            max_tokens=60
        )
        elapsed = time.time() - start_time
        reply = response.choices[0].message.content.strip()

        safe_print("-----------------------------------------------------------------")
        safe_print(f"[SUCCESS] Connected to NVIDIA Nemotron in {elapsed:.2f} seconds!")
        safe_print(f"Nemotron Response: \"{reply}\"")
        safe_print("-----------------------------------------------------------------")
        safe_print("Your application is officially making live NVIDIA Nemotron runtime calls!")
        return True

    except Exception as exc:
        safe_print(f"[FAILED] Connection error: {exc}")
        return False

if __name__ == "__main__":
    success = verify_nebius()
    sys.exit(0 if success else 1)
