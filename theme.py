def get_black_white_theme():
    return """
        QWidget {
            background-color: rgba(245, 245, 245, 0.85);
            color: #202020;
            
        }
        QPushButton, QToolButton {
            background-color: rgba(240, 240, 240, 0.8);
            border: 1px solid rgba(180, 180, 180, 0.6);
            border-radius: 8px;
            padding: 6px 14px;
            color: #202020;
        }
        QPushButton:hover, QToolButton:hover {
            background-color: rgba(225, 225, 225, 0.9);
            border: 1px solid rgba(150, 150, 150, 0.8);
        }

        QToolButton#linkButton {
            padding: 6px;
            min-width: 30px;
            max-width: 30px;
            min-height: 30px;
            max-height: 30px;
        }
        /* Add this style for the date overlay */
        QLabel#dateOverlay {
            background-color: rgba(240, 240, 240, 0.9);
            border: 1px solid rgba(180, 180, 180, 0.7);
            border-radius: 8px;
            padding: 6px 10px;
            min-width: 180px;  /* Add minimum width */
        }
        QLineEdit {
            background-color: rgba(255, 255, 255, 0.7);
            border: 1px solid rgba(180, 180, 180, 0.6);
            border-radius: 6px;
            padding: 4px;
        }
        QScrollArea {
            background-color: transparent;
            border: none;
        }
        QScrollBar {
            background-color: rgba(240, 240, 240, 0.4);
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle {
            background-color: rgba(180, 180, 180, 0.7);
            border-radius: 5px;
            margin: 2px;
        }
        QScrollBar::add-line, QScrollBar::sub-line {
            background: none;
            border: none;
            height: 0px;
        }
        QScrollBar::add-page, QScrollBar::sub-page {
            background: none;
        }
        QSlider::groove:horizontal {
            height: 4px;
            background-color: rgba(200, 200, 200, 0.7);
            border-radius: 2px;
        }
        QSlider::handle:horizontal {
            background-color: rgba(150, 150, 150, 0.9);
            border: 1px solid rgba(120, 120, 120, 0.7);
            width: 14px;
            margin: -5px 0;
            border-radius: 7px;
        }
        QLabel {
            background-color: transparent;
            color: #202020;
        }
        QStatusBar {
            background-color: rgba(240, 240, 240, 0.8);
            color: #202020;
            border-top: 1px solid rgba(200, 200, 200, 0.5);
        }
        QMenu::item:selected {
            background-color: rgba(220, 220, 220, 0.7);
            border-radius: 4px;
        }
    """