import requests
from bs4 import BeautifulSoup
import re
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from datetime import datetime

class ThumbnailLoader(QThread):
    thumbnail_loaded = pyqtSignal(dict)
    thumbnail_failed = pyqtSignal(str)

    def __init__(self, video_data):
        super().__init__()
        self.video_data = video_data

    def run(self):
        for video in self.video_data:
            video_id = video["video_id"]
            try:
                title, upload_date = self.fetch_video_info(video_id)
                thumbnail = self.fetch_thumbnail(video_id)
                self.thumbnail_loaded.emit({
                    "title": title, 
                    "video_id": video_id, 
                    "thumbnail": thumbnail,
                    "upload_date": upload_date
                })
            except Exception:
                self.thumbnail_failed.emit(video_id)
    
    def fetch_video_info(self, video_id):
        response = requests.get(f"https://www.youtube.com/watch?v={video_id}", timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        
        title_tag = soup.find("title")
        title = title_tag.text.replace(" - YouTube", "").strip() if title_tag else "Unknown Title"
        
        upload_date = "Unknown Date"
        scripts = soup.find_all("script")
        for script in scripts:
            if script.string and '"uploadDate":' in script.string:
                date_match = re.search(r'"uploadDate":"([^"]+)"', script.string)
                if date_match:
                    upload_date = date_match.group(1)
                    try:
                        dt = datetime.fromisoformat(upload_date)
                        upload_date = dt.strftime('%Y-%m-%d')
                    except ValueError:
                        pass
                    break
        
        return title, upload_date

    def fetch_thumbnail(self, video_id):
        response = requests.get(f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg", timeout=5)
        image = QImage()
        image.loadFromData(response.content)
        return QPixmap.fromImage(image)