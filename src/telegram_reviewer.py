import os
import time
import requests
import shutil
from dotenv import load_dotenv

# Define paths and explicitly load the .env file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

PENDING_DIR = os.path.join(BASE_DIR, "data", "pending_review")
APPROVED_DIR = os.path.join(BASE_DIR, "data", "approved")
os.makedirs(APPROVED_DIR, exist_ok=True)

# Load Telegram credentials
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "your_bot_token")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "your_chat_id")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def send_video_for_review(video_path: str, topic: str) -> int:
    """Sends the video to Telegram with Approve/Reject inline buttons."""
    print(f"Sending {os.path.basename(video_path)} to Telegram for review...")
    url = f"{BASE_URL}/sendVideo"
    
    keyboard = {
        "inline_keyboard": [[
            {"text": "✅ Approve", "callback_data": f"approve_{topic}"},
            {"text": "❌ Reject", "callback_data": f"reject_{topic}"}
        ]]
    }
    
    with open(video_path, 'rb') as video:
        files = {'video': video}
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'caption': f"🎥 *New Short Ready for Review*\nTopic: {topic}\n\nApprove for upload?",
            'parse_mode': 'Markdown',
            'reply_markup': str(keyboard).replace("'", '"') # Telegram requires strict JSON double quotes
        }
        
        response = requests.post(url, data=data, files=files)
        response.raise_for_status()
        
    message_id = response.json()['result']['message_id']
    return message_id

def wait_for_decision() -> bool:
    """Polls Telegram for the button click and returns True if approved."""
    print("Waiting for your decision on Telegram...")
    url = f"{BASE_URL}/getUpdates"
    offset = None
    
    while True:
        params = {'timeout': 100, 'offset': offset}
        try:
            response = requests.get(url, params=params).json()
            
            for update in response.get('result', []):
                offset = update['update_id'] + 1
                
                if 'callback_query' in update:
                    action = update['callback_query']['data']
                    
                    # Acknowledge the button press to remove the loading state on Telegram
                    callback_id = update['callback_query']['id']
                    requests.post(f"{BASE_URL}/answerCallbackQuery", data={'callback_query_id': callback_id})
                    
                    if action.startswith("approve"):
                        print("User approved the video!")
                        return True
                    elif action.startswith("reject"):
                        print("User rejected the video.")
                        return False
                        
        except requests.exceptions.RequestException as e:
            print(f"Connection error while polling Telegram: {e}")
            
        time.sleep(2) # Prevent hammering the API

def review_gate(video_filename="draft_short.mp4", topic="whale") -> str:
    """Main orchestrator for the review step."""
    video_path = os.path.join(PENDING_DIR, video_filename)
    
    if not os.path.exists(video_path):
        print("Error: No pending video found.")
        return ""
        
    send_video_for_review(video_path, topic)
    approved = wait_for_decision()
    
    if approved:
        approved_path = os.path.join(APPROVED_DIR, video_filename)
        shutil.move(video_path, approved_path)
        print(f"Video moved to: {approved_path}")
        return approved_path
    else:
        print("Video rejected. Discarding...")
        os.remove(video_path)
        return ""

if __name__ == "__main__":
    # Test the review gate
    # Ensure you place a dummy 'draft_short.mp4' in data/pending_review/ first
    final_path = review_gate()
    if final_path:
        print("Ready to trigger YouTube upload!")
