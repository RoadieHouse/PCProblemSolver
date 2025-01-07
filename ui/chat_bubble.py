"""
Chat Bubble Widget Module

Implements a custom widget for displaying chat messages in a bubble style format.
Supports different styles for user and bot messages with configurable appearance.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QVBoxLayout, QWidget, QLabel, QSizePolicy, QHBoxLayout)

class ChatBubble(QWidget):
    """
    A custom widget for displaying chat messages in a bubble format.
    
    Provides different styles for user and bot messages, with customizable
    appearance and layout. Supports text selection and proper sizing behavior.
    """
    
    def __init__(self, text: str, is_user: bool, title: str) -> None:
        """
        Initialize a chat bubble widget.

        Args:
            text (str): The text content of the chat bubble.
            is_user (bool): Flag indicating if the bubble is for user (True) or bot (False).
            title (str): The title text to display above the bubble.
        """
        super().__init__()
        
        # Configure size policy for proper layout behavior
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)

        # Create main layout with no margins
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # Create and style title label
        title_label = QLabel(title)
        title_label.setObjectName("title")
        title_label.setStyleSheet("""
            QLabel#title {
                font-weight: bold;
                font-family: "Times", sans-serif;
                font-size: 24px;
                margin-bottom: 3px;
                color: white;
            }
        """)

        # Create bubble layout for message content
        bubble_layout = QHBoxLayout()
        bubble_layout.setContentsMargins(0, 0, 0, 0)

        # Create and configure message label
        label = QLabel()
        label.setText(text)
        label.setWordWrap(True)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label.setTextFormat(Qt.RichText)
        # Enable text selection capabilities
        label.setTextInteractionFlags(
            Qt.TextSelectableByMouse | 
            Qt.TextSelectableByKeyboard | 
            Qt.LinksAccessibleByMouse
        )

        # Apply appropriate styles based on message type (user/bot)
        if is_user:
            label.setObjectName("user-bubble")
            # Set user bubble styles
            label.setStyleSheet("""
                QLabel#user-bubble {
                    background-color: #184458; 
                    color: #FFFFFF; 
                    border: 0px solid #184458;
                    border-radius: 10px; 
                    padding: 10px;
                    font-size: 22px;
                    font-family: "Arial", sans-serif;
                }
            """)
        else:
            label.setObjectName("bot-bubble")
            # Set bot bubble styles
            label.setStyleSheet("""
                QLabel#bot-bubble {
                    background-color: #64c6a0;
                    color: #000000; 
                    border: 1px solid #64c6a0; 
                    border-radius: 10px; 
                    padding: 10px;
                    font-size: 20px;
                }
            """)

        # Position elements based on message type
        if is_user:
            # Right-align user messages
            title_label.setAlignment(Qt.AlignRight)
            outer_layout.addWidget(title_label)
            bubble_layout.addStretch()
            bubble_layout.addWidget(label)
        else:
            # Left-align bot messages
            outer_layout.addWidget(title_label)
            bubble_layout.addWidget(label)
            bubble_layout.addStretch()

        # Combine layouts
        outer_layout.addLayout(bubble_layout)
        self.setLayout(outer_layout)