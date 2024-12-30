import logging
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QMovie
from pathlib import Path

class TypingIndicator(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignLeft)
        self.movie = QMovie(str(Path(__file__).parent.parent / "ui" / "resources" / "typing_text.gif"))
        if not self.movie.isValid():
            logging.error("Error: Invalid movie file")
            return
        self.setMovie(self.movie)
        self.setStyleSheet("""
            QLabel {
                background: transparent;
                padding: 10px;
                margin: 5px;
                border-radius: 10px;
            }
        """)
        self.setScaledContents(True)
        self.setMaximumSize(350, 196)  # Adjust size based on your GIF

    def start(self):
        self.movie.start()

    def stop(self):
        self.movie.stop()

    def delete(self):
        self.stop()
        self.deleteLater()