"""
Nebius Token Factory & NVIDIA Nemotron Verification Script.
Run this script to verify that your Nebius API key and model endpoint are working live.

Usage:
  python test_nebius_connection.py
"""
import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

def verify_nebius():
    api_key = os.getenv("NEBIUS_API_KEY", "").strip()
    base_url = os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/")
    model = os.getenv("NEBIUS_MODEL", "nvidia/Llama-3_1-Nemotron-Ultra-253B-v1")

    print("=================================================================")
    print(" Nebius Token Factory & NVIDIA Nemotron Verification")
    print("=================================================================")
    print(f"Base URL : {base_url}")
    print(f"Model ID : {model}")
    print(f"API Key  : {api_key[:6]}...{api_key[-4:] if len(api_key) > 10 else '(empty or default)'}")
    print("-----------------------------------------------------------------")

    if not api_key or api_key == "your_key_here" or api_key == "your_actual_nebius_key":
        print("❌ ERROR: NEBIUS_API_KEY is not set in your .env file!")
        print("\nTo fix this:")
        print("1. Open https://tokenfactory.nebius.com (or https://console.nebius.com)")
        print("2. Navigate to 'API Keys' -> 'Create API Key'")
        print("3. Copy your key and paste it in d:\\paisapath-ai\\.env:")
        print("   NEBIUS_API_KEY=your_copied_key")
        return False

    try:
        from openai import OpenAI
    except ImportError:
        print("❌ ERROR: 'openai' Python package is not installed. Run: pip install openai")
        return False

    print("Initiating test inference call to Nebius Token Factory...")
    client = OpenAI(base_url=base_url, api_key=api_key)
    
    start_time = time.time()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are PaisaPath AI running on Nebius Token Factory with NVIDIA Nemotron."},
                {"role": "user", "content": "Confirm you are active by answering in one short sentence: What is an emergency fund?"}
            ],
            temperature=0.2,
            max_tokens=60
        )
        elapsed = time.time() - start_time
        reply = response.choices[0].message.content.strip()

        print("-----------------------------------------------------------------")
        print(f"✅ SUCCESS! Connected to Nebius Token Factory in {elapsed:.2f} seconds.")
        print(f"NVIDIA Nemotron Response: \"{reply}\"")
        print("-----------------------------------------------------------------")
        print("Your project is ready to submit with live Nebius Token Factory runtime calls!")
        return True

    except Exception as exc:
        print(f"❌ Connection Failed: {exc}")
        print("\nTroubleshooting:")
        print("1. Check if the model ID matches available models in your Nebius console.")
        print("   Common model IDs:")
        print("   - nvidia/Llama-3_1-Nemotron-Ultra-253B-v1")
        print("   - nvidia/Llama-3_1-Nemotron-70B-Instruct")
        print("2. Verify your API key has active credits from the Nebius Builder Program.")
        print("3. Ensure base_url is 'https://api.tokenfactory.nebius.com/v1/' or 'https://api.studio.nebius.ai/v1/'")
        return False

if __name__ == "__main__":
    success = verify_nebius()
    sys.exit(0 if success else 1)
