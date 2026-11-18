import os
import asyncio
import edge_tts

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

async def _generate_audio_and_subs(text, audio_path, sub_path):
    communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural")
    submaker = edge_tts.SubMaker()
    
    with open(audio_path, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)
                
    with open(sub_path, "w", encoding="utf-8") as file:
        # Changed to SRT
        file.write(submaker.get_srt())

# Changed default extension to .srt
def generate_voiceover(script: str, audio_filename="voiceover.mp3", sub_filename="subtitles.srt") -> tuple:
    print("Generating voiceover and subtitles...")
    audio_path = os.path.join(RAW_DATA_DIR, audio_filename)
    sub_path = os.path.join(RAW_DATA_DIR, sub_filename)
    
    asyncio.run(_generate_audio_and_subs(script, audio_path, sub_path))
    
    print(f"Voiceover and subtitles saved to {RAW_DATA_DIR}")
    return audio_path, sub_path
