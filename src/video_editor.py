import os
import re
import PIL.Image

# Monkey-patch to fix moviepy compatibility with modern Pillow
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = getattr(PIL.Image, 'Resampling', PIL.Image).LANCZOS

from moviepy.editor import ImageClip, AudioFileClip, TextClip, CompositeVideoClip

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PENDING_DIR = os.path.join(BASE_DIR, "data", "pending_review")
os.makedirs(PENDING_DIR, exist_ok=True)

def parse_srt(srt_file):
    """Parses an SRT file and returns a list of ((start_sec, end_sec), word) tuples."""
    with open(srt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Matches SRT format: 00:00:00,000 --> 00:00:01,000
    pattern = re.compile(r"(\d{2}:\d{2}:\d{2}[,\.]\d{3}) --> (\d{2}:\d{2}:\d{2}[,\.]\d{3})\n(.*?)(?=\n\n|\Z)", re.DOTALL)
    
    def time_to_sec(t_str):
        # Replace comma with dot for math processing
        t_str = t_str.replace(',', '.')
        h, m, s = t_str.split(':')
        sec, ms = s.split('.')
        return int(h)*3600 + int(m)*60 + int(sec) + int(ms)/1000.0

    subs = []
    for match in pattern.finditer(content):
        start = time_to_sec(match.group(1))
        end = time_to_sec(match.group(2))
        text = match.group(3).strip()
        subs.append(((start, end), text))
    return subs

# Note the updated default sub_filename here
def stitch_video(image_filename="background.jpg", audio_filename="voiceover.mp3", sub_filename="subtitles.srt", output_filename="draft_short.mp4") -> str:
    print("Loading media and building captions...")
    image_path = os.path.join(RAW_DATA_DIR, image_filename)
    audio_path = os.path.join(RAW_DATA_DIR, audio_filename)
    sub_path = os.path.join(RAW_DATA_DIR, sub_filename)
    output_path = os.path.join(PENDING_DIR, output_filename)
    
    # 1. Load Audio & Image
    audio_clip = AudioFileClip(audio_path)
    video_clip = ImageClip(image_path).set_duration(audio_clip.duration)
    
    # 2. Build Subtitle Clips
    sub_data = parse_srt(sub_path)  # Call the new parser
    text_clips = []
    
    for (start, end), word in sub_data:
        txt_clip = TextClip(
            word, 
            fontsize=90, 
            color='white', 
            font='Arial-Bold', 
            stroke_color='black',
            stroke_width=4
        )
        txt_clip = txt_clip.set_position(('center', 1300)).set_start(start).set_end(end)
        text_clips.append(txt_clip)
    
    # 3. Compile everything together
    final_video = CompositeVideoClip([video_clip] + text_clips)
    final_video = final_video.set_audio(audio_clip)
    
    print(f"Rendering final short to {output_path}...")
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
    
    return output_path
