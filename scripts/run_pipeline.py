import os
import sys
import random
from dotenv import load_dotenv

# Load environment variables from .env file FIRST
load_dotenv(override=True)

# Ensure Python can find the src modules
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, 'src'))

from gemma_client import generate_short_script
from gemma_client import generate_short_script, generate_visual_prompt
from tts_generator import generate_voiceover
from visual_fetcher import fetch_background_video
from video_editor import stitch_video
from telegram_reviewer import review_gate

def main():
    # Define a list of diverse, visual-friendly topics
    potential_topics = [
        "fascinating animals",
        "ancient trees",
        "exotic flowers",
        "the human body",
        "deep ocean life",
        "outer space",
        "extreme weather",
        "bizarre insects",
        "volcanoes",
        "ancient history"
    ]
    
    # Pick a random topic for this run
    topic = random.choice(potential_topics)
    
    print(f"--- Starting YouTube Shorts Pipeline for topic: {topic} ---")

        # 1. Generate Script
    script = generate_short_script(topic)
    if not script:
        print("Pipeline failed at script generation.")
        return

    # 2. Extract Exact Visual Prompt 
    visual_prompt = generate_visual_prompt(script)
    if not visual_prompt:
        print("Pipeline failed at visual prompt generation.")
        return

    # 3. Generate Audio and Subtitles
    audio_path, sub_path = generate_voiceover(script)
    if not audio_path:
        print("Pipeline failed at audio generation.")
        return

    # 4. Generate Exact AI Visuals
    from ai_visual_generator import generate_ai_visual
    image_path = generate_ai_visual(visual_prompt)
    if not image_path:
        print("Pipeline failed at AI visual generation.")
        return

        # 5. Stitch Video 
    draft_path = stitch_video(
        image_filename=os.path.basename(image_path),
        audio_filename=os.path.basename(audio_path),
        sub_filename=os.path.basename(sub_path)
    )
    if not draft_path:
        print("Pipeline failed at video stitching.")
        return

    # 6. Review Gate
    approved_video_path = review_gate(
        video_filename=os.path.basename(draft_path),
        topic=topic
    )

    # 7. Upload (Mocked)
    if approved_video_path:
        print(f"\nSUCCESS: Video approved and located at {approved_video_path}")
        print("TODO: Pass this path to youtube_uploader.py")
    else:
        print("\nPipeline terminated: Video was rejected or not found.")


if __name__ == "__main__":
    main()
