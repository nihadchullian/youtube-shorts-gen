import os
import requests
import random
from dotenv import load_dotenv

# Define paths and explicitly load the .env file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# Load API key from environment
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "your_pixabay_api_key")


def fetch_background_video(query: str, filename: str = "background.mp4") -> str:
    """
    Searches Pixabay for a stock video matching the query and downloads it.
    """
    if PIXABAY_API_KEY == "your_pixabay_api_key":
        print("Error: Please set your PIXABAY_API_KEY environment variable.")
        return ""

    # Search Pixabay for videos
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={requests.utils.quote(query)}&video_type=film"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if int(data.get("totalHits", 0)) == 0:
            print(f"No videos found for query: {query}")
            return ""
            
        # Select a random video from the top results
        video = random.choice(data["hits"])
        
        # Pixabay offers multiple sizes; grab the "large" or "medium" mp4
        video_urls = video.get("videos", {})
        download_url = video_urls.get("large", {}).get("url") or video_urls.get("medium", {}).get("url")
        
        if not download_url:
            print("Could not find a suitable video file format.")
            return ""
        
        print(f"Downloading video from Pixabay (Query: {query})...")
        vid_response = requests.get(download_url)
        vid_response.raise_for_status()
        
        output_path = os.path.join(RAW_DATA_DIR, filename)
        with open(output_path, 'wb') as f:
            f.write(vid_response.content)
            
        print(f"Background video saved successfully to {output_path}")
        return output_path

    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Pixabay API: {e}")
        return ""

if __name__ == "__main__":
    # Test the visual fetcher
    topic = "ocean whale"
    saved_path = fetch_background_video(topic)
    print(f"Test video available at: {saved_path}")
