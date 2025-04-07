from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen
import random

class MusicVisualizer(QWidget):
    def __init__(self, media_player, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 36)
        self.media_player = media_player
        self.bars = [5, 8, 12, 8, 5]
        self.opacity = 0.0 if self.media_player.isMuted() else 1.0
        
        self.timer = QTimer(self)
        self.timer.setInterval(50)  
        self.timer.timeout.connect(self.animate_bars)
        self.timer.start()
        self.setAttribute(Qt.WA_TranslucentBackground)
    
    def animate_bars(self):
        if self.media_player.isMuted():
            self.opacity = max(0.0, self.opacity - 0.02) 
            for i in range(len(self.bars)):
                self.bars[i] = max(0, self.bars[i] - 0.5)
            if self.opacity <= 0.01:
                self.timer.setInterval(200)  
        else:
            self.timer.setInterval(50)
            self.opacity = min(1.0, self.opacity + 0.03)  
            for i in range(len(self.bars)):
                target = random.randint(5, 15)
                self.bars[i] = self.bars[i] * 0.85 + target * 0.15  
        self.update()
    
    def paintEvent(self, event):
        if self.opacity <= 0.01: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setOpacity(self.opacity)
        
        bar_width = 8
        gap = 6
        x = (self.width() - (len(self.bars) * bar_width + (len(self.bars) - 1) * gap)) // 2
        
        for i, height in enumerate(self.bars):
            if height < 1: continue
            bar_x = x + i * (bar_width + gap)
            bar_height = int(height)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(40, 40, 40))
            painter.drawRoundedRect(bar_x, self.height() - bar_height, bar_width, bar_height, 2, 2)