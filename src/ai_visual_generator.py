import os
import requests
import urllib.parse
from dotenv import load_dotenv

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH, override=True)

RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

def generate_ai_visual(visual_prompt: str, filename: str = "background.jpg") -> str:
    """
    Takes the exact visual prompt from Gemma and generates an AI image.
    """
    print(f"Generating AI visual for prompt: {visual_prompt}...")
    
    # URL encode the prompt so it can be passed in a web request
    safe_prompt = urllib.parse.quote(visual_prompt)
    
    # Pollinations AI endpoint (free, no API key). We request 1080x1920 resolution.
    url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1080&height=1920&nologo=true"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        output_path = os.path.join(RAW_DATA_DIR, filename)
        with open(output_path, 'wb') as f:
            f.write(response.content)
            
        print(f"Exact AI visual saved successfully to {output_path}")
        return output_path

    except requests.exceptions.RequestException as e:
        print(f"Error fetching AI visual: {e}")
        return ""
