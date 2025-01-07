"""
Typing Indicator Module

Implements a custom QLabel widget that displays an animated typing indicator.
Manages the loading and display of a GIF animation with proper cleanup handling.
"""

import logging
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QMovie
from pathlib import Path

class TypingIndicator(QLabel):
    """
    Custom QLabel widget that displays an animated typing indicator.
    
    Features:
    - Animated GIF display
    - Proper resource cleanup
    - Thread-safe deletion handling
    
    Signals:
        destroyed: Emitted when the widget is being destroyed
    """
    
    # Signal emitted when widget is about to be destroyed
    destroyed = pyqtSignal()
    
    def __init__(self):
        """
        Initialize the typing indicator widget.
        
        Sets up:
        - Widget alignment and styling
        - GIF animation loading
        - Size constraints
        """
        super().__init__()
        
        # Flag to prevent multiple deletion attempts
        self._is_deleting = False
        
        # Configure widget alignment
        self.setAlignment(Qt.AlignLeft)
        
        # Load and set up animation
        self.movie = QMovie(str(Path(__file__).parent.parent / "ui" / "resources" / "typing_text.gif"))
        if not self.movie.isValid():
            logging.error("Error: Invalid movie file")
            return
        self.setMovie(self.movie)
        
        # Apply styling
        self.setStyleSheet("""
            QLabel {
                background: transparent;
                padding: 10px;
                margin: 5px;
                border-radius: 10px;
            }
        """)
        
        # Configure size constraints
        self.setScaledContents(True)
        self.setMaximumSize(500, 280)  # Adjust size based on GIF dimensions

    def start(self):
        """
        Start the typing animation.
        
        Only starts if widget is not being deleted and movie exists.
        """
        if self._is_deleting or not self.movie:
            return
        self.movie.start()

    def stop(self):
        """
        Stop the typing animation.
        
        Only stops if widget is not being deleted and movie exists.
        """
        if self._is_deleting or not self.movie:
            return
        self.movie.stop()

    def delete(self):
        """
        Clean up resources and delete the widget.
        
        Handles:
        - Prevention of multiple deletion attempts
        - Proper stopping of animation
        - Resource cleanup
        - Signal emission
        """
        if self._is_deleting:
            return
            
        self._is_deleting = True
        self.stop()
        
        # Clean up movie object
        if self.movie:
            self.movie.deleteLater()
            self.movie = None
            
        # Signal destruction and schedule deletion
        self.destroyed.emit()
        self.deleteLater()
