# pip install requests

import requests
import json

def generate_with_rest(model: str, prompt: str):
    url = "http://192.168.5.241:11434/api/chat"  # Default Ollama API endpoint
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False  # Set to True for streaming responses
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        print("Generated Text:\n", data.get("response", "No output"))
    except requests.exceptions.RequestException as e:
        print(f"HTTP Error: {e}")
    except json.JSONDecodeError:
        print("Error decoding JSON from Ollama API.")

if __name__ == "__main__":
    generate_with_rest("llama3", "Write a short poem about the ocean.")