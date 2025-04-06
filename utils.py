import os
import re

def load_subtitle_files(folder_path):
    """Extract YouTube video IDs from SRT files in a folder"""
    video_data = []
    for file in os.listdir(folder_path):
        if file.endswith(".srt"):
            match = re.search(r"\[([a-zA-Z0-9_-]{11})\]\.srt$", file)
            if match:
                video_data.append({"title": "Loading...", "video_id": match.group(1)})
    return video_data