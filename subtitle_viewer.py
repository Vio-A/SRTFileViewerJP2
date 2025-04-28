import os
import webbrowser
import re
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QScrollArea, QWidget, QHBoxLayout, QToolButton, QSlider, QStatusBar, 
    QLineEdit, QShortcut, QMenu, QAction)
from PyQt5.QtGui import QPixmap, QFontDatabase, QFont, QIcon, QKeySequence
from PyQt5.QtCore import Qt, QUrl, QPoint, QEvent
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from thumbnail_loader import ThumbnailLoader
from music_player import MusicVisualizer
from utils import load_subtitle_files

class SubtitleViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SRT Thumbnail + Title Viewer")
        self.setGeometry(100, 100, 800, 1000)
        self.setWindowIcon(QIcon("icon2.png"))
        self.video_widgets = {}
        self.thumbnail_size = (320, 180)
        self.base_font_size = 14
        self.current_font_size = self.base_font_size
        self.resizing = False
        self.setup_font()
        self.setup_ui()
        self.setup_music_player()
        self.setup_status_bar()

        self.search_shortcut = QShortcut(QKeySequence("⌘+F"), self)
        self.search_shortcut.activated.connect(self.focus_search)

        self.setFocus()

    def focus_search(self):
        self.search_input.setFocus()
        self.search_input.selectAll()

    def setup_font(self):
        from PyQt5.QtGui import QFontDatabase, QFont
        import os
        import platform

        self.base_font_size = 13
        self.title_font_size = 16 

        self.custom_font = QFont("Helvetica", self.base_font_size) #basic fallback

        if platform.system() == "Darwin":
            print("Running on macOS, attempting to load system Japanese fonts...")
            japanese_fonts = ["Hiragino Sans", "Hiragino Kaku Gothic Pro", "Apple SD Gothic Neo"]
            found_font = False
            font_db = QFontDatabase()
            available_families = font_db.families()

            for font_name in japanese_fonts:
                if font_name in available_families:
                    self.custom_font = QFont(font_name, self.base_font_size)
                    print(f"Using macOS system font: {font_name}")
                    found_font = True
                    break

            if not found_font:
                print("Warning: No suitable Japanese system font found on macOS. Using default.")

        else:
            print("Running on non-macOS system, attempting to load custom font...")
            current_dir = os.path.dirname(os.path.abspath(__file__))
            font_path = os.path.join(current_dir, "NotoSerifJP-VariableFont_wght.ttf")

            if os.path.exists(font_path):
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    font_families = QFontDatabase.applicationFontFamilies(font_id)
                    if font_families:
                        font_family = font_families[0]
                        self.custom_font = QFont(font_family, self.base_font_size)
                        print(f"Successfully loaded custom font: {font_family}")
                    else:
                        print(f"Warning: Custom font '{os.path.basename(font_path)}' loaded (id={font_id}) but reported no families. Using default.")
                else:
                    print(f"Warning: Failed to load custom font from {font_path} (id={font_id}). Using default.")
            else:
                print(f"Warning: Custom font file not found at {font_path}. Using default.")

        self.custom_font.setWeight(QFont.Medium)
                
    def setup_ui(self):
        self.main_layout = QVBoxLayout()
        top_row = QHBoxLayout()
        
        select_button = QPushButton("フォルダー選択")
        select_button.setFont(self.custom_font)
        select_button.clicked.connect(self.select_folder)
        top_row.addWidget(select_button)
        
        self.sort_button = QPushButton("並び替え ▼")
        self.sort_button.setFont(self.custom_font)
        sort_menu = QMenu(self)
        
        self.sort_actions = {}
        self.sort_actions["date_newest"] = QAction("アップロード日 (新しい順)", self)
        self.sort_actions["date_oldest"] = QAction("アップロード日 (古い順)", self)
        self.sort_actions["length"] = QAction("タイトルの長さ (短い順)", self)
        
        for key, action in self.sort_actions.items():
            sort_menu.addAction(action)
            action.triggered.connect(lambda checked=False, k=key: self.sort_videos(k))
        
        self.current_sort = "date_newest"
        self.sort_actions["date_newest"].setCheckable(True)
        self.sort_actions["date_newest"].setChecked(True)
        
        self.sort_button.setMenu(sort_menu)
        top_row.addWidget(self.sort_button)
        
        top_row.addStretch()
        
        self.search_input = QLineEdit()
        self.search_input.setFont(self.custom_font)
        self.search_input.setPlaceholderText("検索...　「⌘+F」")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setFixedWidth(220)
        self.search_input.textChanged.connect(self.filter_videos)
        top_row.addWidget(self.search_input)
        
        self.main_layout.addLayout(top_row)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

        self.slider_layout = QHBoxLayout()
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setMinimum(200)
        self.size_slider.setMaximum(400)
        self.size_slider.setValue(320)
        self.size_slider.setFixedWidth(200)
        self.size_slider.valueChanged.connect(self._update_sizes)
        self.slider_layout.addWidget(self.size_slider, alignment=Qt.AlignCenter)
        self.main_layout.addLayout(self.slider_layout)

        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

    def setup_music_player(self):
        self.media_player = QMediaPlayer()
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile("song.mp3")))
        self.media_player.setVolume(20)
        self.media_player.play()
        self.media_player.setMuted(True)

        music_container = QWidget()
        music_container.setObjectName("musicContainer")
        
        music_layout = QHBoxLayout(music_container)
        music_layout.setContentsMargins(8, 4, 8, 4)
        music_layout.setSpacing(8)
        music_layout.setAlignment(Qt.AlignCenter)
        
        self.mute_button = QToolButton()
        self.mute_button.setText("🔇") 
        self.mute_button.clicked.connect(self.toggle_music)
        music_layout.addWidget(self.mute_button)
        
        self.visualizer = MusicVisualizer(self.media_player)
        music_layout.addWidget(self.visualizer)
        
        container_layout = QHBoxLayout()
        container_layout.addStretch(1)
        container_layout.addWidget(music_container)
        container_layout.addStretch(1)
        
        self.main_layout.addLayout(container_layout)

    def setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.status_label = QLabel("")
        self.status_bar.addWidget(self.status_label)
        self.setStatusBar(self.status_bar)

    def toggle_music(self):
        is_muted = self.media_player.isMuted()
        self.media_player.setMuted(not is_muted)
        self.mute_button.setText("🔊" if is_muted else "🔇")
        self.visualizer.update()

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.video_widgets.clear()
            self.search_input.clear()
            video_data = load_subtitle_files(folder_path)
            if video_data:
                self.display_videos(video_data)
                self.load_thumbnails(video_data)

    def display_videos(self, video_data):
        for i in range(self.scroll_layout.count() - 1, -1, -1):
            self.scroll_layout.itemAt(i).widget().deleteLater()
        self.video_widgets.clear()

        title_width = int(self.thumbnail_size[0] * 1.1)
        
        for video in video_data:
            video_widget = QWidget()
            video_layout = QHBoxLayout(video_widget)

            title_label = QLabel(video["title"])
            title_label.setFont(self.custom_font)
            title_label.setWordWrap(True)
            title_label.setFixedWidth(title_width)
            video_layout.addWidget(title_label)

            thumbnail_container = QWidget()
            thumbnail_layout = QVBoxLayout(thumbnail_container)
            thumbnail_layout.setAlignment(Qt.AlignCenter)

            link_button = QToolButton()
            link_button.setObjectName("linkButton")
            link_button.setText("🔗")
            link_button.clicked.connect(lambda _, vid=video["video_id"]: 
                                     webbrowser.open(f"https://www.youtube.com/watch?v={vid}"))
            thumbnail_layout.addWidget(link_button, alignment=Qt.AlignCenter)

            thumbnail_label = QLabel()
            placeholder = QPixmap(*self.thumbnail_size)
            placeholder.fill(Qt.gray)
            thumbnail_label.setPixmap(placeholder)
            thumbnail_label.setFixedSize(*self.thumbnail_size)
            thumbnail_label.installEventFilter(self)
            thumbnail_layout.addWidget(thumbnail_label, alignment=Qt.AlignCenter)
            
            date_overlay = QLabel(self.scroll_area.viewport())
            date_overlay.setObjectName("dateOverlay")
            date_overlay.setAlignment(Qt.AlignCenter)
            date_overlay.setMinimumWidth(200)
            date_overlay.setText("アップロード日: 読み込み中...")
            date_overlay.setContentsMargins(8, 6, 8, 6)
            date_overlay.adjustSize()
            date_overlay.hide()
            date_overlay.setAttribute(Qt.WA_TransparentForMouseEvents)

            video_layout.addWidget(thumbnail_container)
            self.scroll_layout.addWidget(video_widget)
            self.video_widgets[video["video_id"]] = {
                "thumbnail_label": thumbnail_label,
                "title_label": title_label,
                "date_overlay": date_overlay,
                "original_pixmap": None,
                "scaled_pixmaps": {},
                "status": "loading"
            }
        self.update_status_label()

    def mark_thumbnail_failed(self, video_id):
        if video_id in self.video_widgets:
            self.video_widgets[video_id]["status"] = "failed"
            self.update_status_label()

    def load_thumbnails(self, video_data):
        self.thumbnail_loader = ThumbnailLoader(video_data)
        self.thumbnail_loader.thumbnail_loaded.connect(self.update_thumbnail)
        self.thumbnail_loader.thumbnail_failed.connect(self.mark_thumbnail_failed)
        self.thumbnail_loader.start()

    def update_thumbnail(self, video):
        widget = self.video_widgets[video["video_id"]]
        if video["thumbnail"] and not video["thumbnail"].isNull():
            widget["original_pixmap"] = video["thumbnail"]
            scaled_thumbnail = video["thumbnail"].scaled(
                self.thumbnail_size[0], self.thumbnail_size[1], 
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            widget["scaled_pixmaps"][self.thumbnail_size] = scaled_thumbnail
            widget["thumbnail_label"].setPixmap(scaled_thumbnail)
            widget["thumbnail_label"].setFixedSize(self.thumbnail_size[0], self.thumbnail_size[1])
            widget["title_label"].setText(video["title"])
            
            widget["date_overlay"].setText(f"アップロード日: {video['upload_date']}")
            widget["date_overlay"].adjustSize()
            
            widget["status"] = "loaded"
            
            if all(w["status"] != "loading" for w in self.video_widgets.values()):
                self.sort_videos(self.current_sort)
        else:
            widget["status"] = "failed"
        self.update_status_label()

    def update_status_label(self):
        loaded = sum(1 for w in self.video_widgets.values() if w["status"] == "loaded")
        loading = sum(1 for w in self.video_widgets.values() if w["status"] == "loading")
        failed = sum(1 for w in self.video_widgets.values() if w["status"] == "failed")
        self.status_label.setText(f"読み込みました: {loaded} | 読み込み中: {loading} | 失敗: {failed}")

    def _update_sizes(self, new_width=None):
        if new_width is None:
            new_width = self.size_slider.value()
        
        new_height = int(new_width * 9 / 16)
        self.thumbnail_size = (new_width, new_height)
        
        title_width = int(new_width * 1.1)
        
        font_scale = new_width / 320
        new_font_size = max(10, min(20, int(self.base_font_size * font_scale)))
        if new_font_size != self.current_font_size:
            self.current_font_size = new_font_size
            self.custom_font.setPointSize(new_font_size)
        
        for widget in self.video_widgets.values():
            if widget["original_pixmap"]:
                if self.thumbnail_size not in widget["scaled_pixmaps"]:
                    widget["scaled_pixmaps"][self.thumbnail_size] = widget["original_pixmap"].scaled(
                        new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                scaled_pixmap = widget["scaled_pixmaps"][self.thumbnail_size]
            else:
                scaled_pixmap = QPixmap(new_width, new_height)
                scaled_pixmap.fill(Qt.gray)
            
            widget["thumbnail_label"].setPixmap(scaled_pixmap)
            widget["thumbnail_label"].setFixedSize(new_width, new_height)
            widget["title_label"].setFont(self.custom_font)
            widget["title_label"].setFixedWidth(title_width)
            
            overlay = widget["date_overlay"]
            overlay.setFont(self.custom_font)
            
            margin_scale = font_scale * 1.2  
            overlay.setContentsMargins(
                int(8 * margin_scale),
                int(6 * margin_scale),
                int(8 * margin_scale),
                int(6 * margin_scale)
            )
            
            overlay.setMinimumWidth(max(200, int(new_width * 0.7)))
            overlay.setMaximumWidth(int(new_width * 1.2))
            overlay.adjustSize()

    def filter_videos(self, search_text):
        search_text = search_text.lower()
        
        if not search_text:
            for _, widget_data in self.video_widgets.items():
                widget_data["title_label"].parentWidget().setVisible(True)
            self.update_status_label()
            return
        
        showing = 0
        hidden = 0
        
        for _, widget_data in self.video_widgets.items():
            title = widget_data["title_label"].text().lower()
            if search_text in title:
                widget_data["title_label"].parentWidget().setVisible(True)
                showing += 1
            else:
                widget_data["title_label"].parentWidget().setVisible(False)
                hidden += 1
        
        self.status_label.setText(f"表示中: {showing} | 非表示: {hidden}")

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Enter:
            for video_id, data in self.video_widgets.items():
                if watched == data["thumbnail_label"]:
                    overlay = data["date_overlay"]
                    global_pos = watched.mapToGlobal(QPoint(0, 0))
                    viewport_pos = self.scroll_area.viewport().mapFromGlobal(global_pos)
                    overlay.adjustSize()  
                    overlay.move(
                        viewport_pos.x() + (watched.width() - overlay.width()) // 2,
                        viewport_pos.y() + watched.height() // 3
                    )
                    overlay.raise_()
                    overlay.show()
                    break
        
        elif event.type() == QEvent.Leave:
            for video_id, data in self.video_widgets.items():
                if watched == data["thumbnail_label"]:
                    data["date_overlay"].hide()
                    break
        
        return super().eventFilter(watched, event)

    def sort_videos(self, sort_key):
        if not self.video_widgets:
            return
        
        for key, action in self.sort_actions.items():
            action.setChecked(key == sort_key)
        
        self.current_sort = sort_key
        
        videos = []
        for video_id, widget_data in self.video_widgets.items():
            title = widget_data["title_label"].text()
            upload_date = widget_data["date_overlay"].text().replace("アップロード日: ", "")
            videos.append({
                "video_id": video_id,
                "title": title,
                "upload_date": upload_date,
                "widget": widget_data["title_label"].parentWidget()
            })
        
        if sort_key == "date_newest":
            videos.sort(key=lambda x: x["upload_date"], reverse=True)
        elif sort_key == "date_oldest":
            videos.sort(key=lambda x: x["upload_date"])
        elif sort_key == "length":
            videos.sort(key=lambda x: len(x["title"]))
        
        for i in reversed(range(self.scroll_layout.count())):
            self.scroll_layout.takeAt(i)
        
        for video in videos:
            self.scroll_layout.addWidget(video["widget"])

    def resizeEvent(self, event):
        if not self.resizing and self.video_widgets:
            self.resizing = True
            new_thumb_width = max(200, min(400, int(self.width() * 0.35)))
            self.size_slider.blockSignals(True)
            self.size_slider.setValue(new_thumb_width)
            self.size_slider.blockSignals(False)
            self._update_sizes(new_thumb_width)
            self.resizing = False
        super().resizeEvent(event)