from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt5.QtGui import QPainter, QColor, QLinearGradient, QRadialGradient, QPainterPath, QPen, QBrush
from PyQt5.QtMultimedia import QAudioProbe
import random
import math

class MusicVisualizer(QWidget):
    def __init__(self, media_player, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 36)
        self.media_player = media_player
        self.bars = [5, 8, 12, 8, 5]
        self.color_phase = 0
        self.wave_offset = 0
        self.pulse = 0
        self.glow = 0
        self.opacity = 0.0 if self.media_player.isMuted() else 1.0
        self.audio_probe = QAudioProbe()
        self.audio_probe.setSource(self.media_player)
        self.audio_probe.audioBufferProbed.connect(self.process_audio)
        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self.animate_bars)
        self.timer.start()
        self.setAttribute(Qt.WA_TranslucentBackground)
    
    def process_audio(self, buffer):
        if self.media_player.isMuted():
            return
        data = buffer.data()
        if data and buffer.sampleCount() > 0:
            for i in range(len(self.bars)):
                energy = random.randint(8, 30)
                position_factor = 1.0 + 0.2 * math.sin(i * math.pi / (len(self.bars) - 1))
                target_height = energy * position_factor
                self.bars[i] = min(35, max(5, self.bars[i] * 0.7 + target_height * 0.3))
            if random.random() < 0.15:
                self.pulse = random.uniform(0.6, 1.0)
            self.glow = min(1.0, self.glow * 0.95 + 0.05 * (sum(self.bars) / len(self.bars)) / 15)
    
    def animate_bars(self):
        self.wave_offset = (self.wave_offset + 0.1) % (2 * math.pi)
        self.pulse *= 0.92
        self.color_phase = (self.color_phase + 0.3) % 360
        
        if self.media_player.isMuted():
            self.opacity = max(0.0, self.opacity - 0.04)
            for i in range(len(self.bars)):
                self.bars[i] = max(0, self.bars[i] - 0.8)
            self.glow *= 0.9
            if self.opacity <= 0.01 and all(bar <= 0.1 for bar in self.bars):
                self.timer.setInterval(100)
        else:
            self.timer.setInterval(16)
            self.opacity = min(1.0, self.opacity + 0.06)
            for i in range(len(self.bars)):
                wave = 5 + 3 * math.sin(self.wave_offset + i * math.pi / 2)
                target = 8 + wave
                self.bars[i] = self.bars[i] * 0.9 + target * 0.1
        
        self.update()
    
    def paintEvent(self, event):
        if self.opacity <= 0.01:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setOpacity(self.opacity)
        
        if self.glow > 0.1:
            glow_gradient = QRadialGradient(QPointF(self.width()/2, self.height()/2), self.width()/1.5)
            glow_color = QColor.fromHsv(int((self.color_phase + 180) % 360), 200, 255, int(60 * self.glow * self.opacity))
            glow_gradient.setColorAt(0, glow_color)
            glow_gradient.setColorAt(1, QColor(0, 0, 0, 0))
            painter.fillRect(self.rect(), glow_gradient)
        
        bar_width = 12
        gap = 8
        x = (self.width() - (len(self.bars) * bar_width + (len(self.bars) - 1) * gap)) // 2
        
        for i, height in enumerate(self.bars):
            if height < 1:
                continue
            bar_x = x + i * (bar_width + gap)
            bar_height = int(height)
            bar_y = self.height() - bar_height
            
            hue = int((self.color_phase + i * 30) % 360)
            color = QColor.fromHsv(hue, 220, 240)
            
            gradient = QLinearGradient(0, bar_y, 0, bar_y + bar_height)
            gradient.setColorAt(0, color.lighter(150))
            gradient.setColorAt(1, color.darker(110))
            
            if height > 10 and self.glow > 0.2:
                glow_path = QPainterPath()
                glow_path.addRoundedRect(bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4, 4, 4)
                glow_pen = QPen(QColor(color.red(), color.green(), color.blue(), int(80 * self.glow * self.opacity)))
                glow_pen.setWidth(3)
                painter.setPen(glow_pen)
                painter.drawPath(glow_path)
            
            bar_path = QPainterPath()
            bar_path.addRoundedRect(bar_x, bar_y, bar_width, bar_height, 3, 3)
            painter.fillPath(bar_path, QBrush(gradient))
            
            if self.pulse > 0.1:
                pulse_color = QColor(color.red(), color.green(), color.blue(), int(100 * self.pulse * self.opacity))
                pulse_gradient = QRadialGradient(QPointF(bar_x + bar_width/2, bar_y + bar_height/2), bar_width * 2)
                pulse_gradient.setColorAt(0, pulse_color)
                pulse_gradient.setColorAt(1, QColor(0, 0, 0, 0))
                pulse_rect = QRectF(bar_x - bar_width, bar_y - bar_height/2, bar_width * 3, bar_height * 2)
                painter.fillRect(pulse_rect, pulse_gradient)