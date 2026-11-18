import os
import requests

# Load configuration from environment variables with fallbacks
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "gemma4:26b"

def generate_short_script(topic: str) -> str:
    """
    Calls a local Gemma model via Ollama to generate a YouTube Short script.
    """
    url = f"{OLLAMA_URL}/api/generate"
    
    # Strict prompt to ensure glitch-free text-to-speech later
    prompt = (
        f"Generate a 50-word 'Did you know?' fascinating fact about {topic}. "
        "Keep the tone engaging and fast-paced for a YouTube Short. "
        "Do not include any formatting, markdown, or emojis, just the raw spoken text."
    )
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "").strip()
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to local Gemma server at {OLLAMA_URL}: {e}")
        return ""



def generate_visual_prompt(script: str) -> str:
    """
    Reads the generated script and creates a highly detailed visual prompt for an AI generator.
    """
    url = f"{OLLAMA_URL}/api/generate"
    
    prompt = (
        f"Read this short script: '{script}'\n\n"
        "Describe exactly what should be shown on screen to match this text. "
        "Describe the subject, the action, and the environment. "
        "Keep it under 30 words. Do not include text, words, or formatting. "
        "Make it highly cinematic and photorealistic."
    )
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.RequestException as e:
        print(f"Error generating visual prompt: {e}")
        return ""


if __name__ == "__main__":
    # Test the endpoint
    topic = "a whale"
    script = generate_short_script(topic)
    
    print(f"Topic: {topic}\n")
    print("Generated Script:")
    print(script)
