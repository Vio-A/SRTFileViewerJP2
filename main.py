import sys
from PyQt5.QtWidgets import QApplication
from subtitle_viewer import SubtitleViewer
from theme import get_black_white_theme

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(get_black_white_theme())
    viewer = SubtitleViewer()
    viewer.show()
    sys.exit(app.exec_())
    