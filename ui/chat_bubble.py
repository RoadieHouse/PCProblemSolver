from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QVBoxLayout, QWidget, QLabel, QSizePolicy, QHBoxLayout)

class ChatBubble(QWidget):
    def __init__(self, text: str, is_user: bool, title: str) -> None:
        """
        Initialize a chat bubble widget.

        Args:
            text (str): The text content of the chat bubble.
            is_user (bool): Flag indicating if the bubble is for the user (True) or the bot (False).
            title (str): The title of the chat bubble.
        """
        super().__init__()
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(title)
        title_label.setObjectName("title")
        title_label.setStyleSheet("""
            QLabel#title {
                font-weight: bold;
                font-family: "Times", sans-serif;
                font-size: 16px;
                margin-bottom: 3px;
                color: white;
            }
        """)

        bubble_layout = QHBoxLayout()
        bubble_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel()
        label.setText(text)
        label.setWordWrap(True)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label.setTextFormat(Qt.RichText)  # Enable HTML formatting
        label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard | Qt.LinksAccessibleByMouse)  # Enable text selection and copying

        # Set the user or bot bubble colors
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
                    font-size: 18px;
                    font-family: "Times", sans-serif;  /* Ensure font family is set */
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
                    font-size: 18px;  /* Increase text size */
                }
            """)

        if is_user:
            title_label.setAlignment(Qt.AlignRight)
            outer_layout.addWidget(title_label)
            bubble_layout.addStretch()
            bubble_layout.addWidget(label)
        else:
            outer_layout.addWidget(title_label)
            bubble_layout.addWidget(label)
            bubble_layout.addStretch()

        outer_layout.addLayout(bubble_layout)
        self.setLayout(outer_layout)