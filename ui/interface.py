"""
Chat Interface Module

Implements the main chat window interface for the PC Assistant application.
Handles user interactions, message display, screenshots, and API communication.
"""

import markdown2
import logging
import os
from PIL import Image
from PyQt5.QtCore import QTimer, Qt, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QMainWindow, QLineEdit,
                             QPushButton, QVBoxLayout, QWidget,
                             QScrollArea, QApplication, QHBoxLayout)

from app.mistral import encode_image
from app.resource_path import get_resource_path
from app.screenshot import take_screenshot
from app.handlers import handle_send_message
from ui.chat_bubble import ChatBubble
from ui.info_box import InfoBox

class ChatbotApp(QMainWindow):
    """
    Main chat interface window for the PC Assistant application.
    
    Manages the chat UI, message handling, and screenshot functionality.
    Provides methods for sending messages, displaying responses, and
    resetting the chat state.
    """
    
    def __init__(self, mistral_client) -> None:
        """
        Initialize the chat interface.
        
        Args:
            mistral_client: Instance of Mistral AI client for API communication
        """
        super().__init__()
        
        # Initialize state flags and components
        self.api_call_in_progress = False
        self.thread = None
        self.worker = None
        
        # Configure window properties
        self.setWindowIcon(QIcon(get_resource_path('ui/resources/icon.png')))
        self.mistral_client = mistral_client
        self.setWindowTitle("PC Assistent")
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(100, 100, 
                        int(screen_geometry.width() * 0.8), 
                        int(screen_geometry.height() * 0.8))
        
        # Set up main window layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        
        # Add information box
        self.info_box = InfoBox(self)
        layout.addWidget(self.info_box, alignment=Qt.AlignTop | Qt.AlignLeft)

        # Set up chat display area
        self.setup_chat_area(layout)
        
        # Set up input area
        self.setup_input_area(layout)

        # Finalize layout
        central_widget.setLayout(layout)
        
        # Initialize chat with screenshot
        self.show_screenshot()
        self.load_stylesheet()

    def setup_chat_area(self, layout: QVBoxLayout) -> None:
        """
        Set up the chat display area with scroll functionality.
        
        Args:
            layout: Main window layout to add chat area to
        """
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.chat_widget)

        layout.addWidget(self.scroll_area)

    def setup_input_area(self, layout: QVBoxLayout) -> None:
        """
        Set up the message input area with text field and send button.
        
        Args:
            layout: Main window layout to add input area to
        """
        input_layout = QHBoxLayout()
        
        # Text input field
        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText("Beschreibe das Problem")
        self.text_input.setFixedHeight(int(self.text_input.sizeHint().height() * 2))
        self.text_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.text_input, 85)
        
        # Send button
        send_button = QPushButton("SENDEN", self)
        send_button.setFixedHeight(self.text_input.height())
        send_button.clicked.connect(self.send_message)
        input_layout.addWidget(send_button, 15)
        
        layout.addLayout(input_layout)

    def show_screenshot(self) -> None:
        """
        Take and display a screenshot in the chat interface.
        
        Captures screen, saves as PNG, converts to base64 for API,
        and displays in chat window.
        """
        logging.info("show_screenshot called")
        
        # Take and save screenshot
        self.screenshot_path = take_screenshot()
        logging.info(f"Screenshot taken: {self.screenshot_path}")

        # Process screenshot
        screenshot_image = Image.open(self.screenshot_path)
        screenshot_image.save(self.screenshot_path, format="PNG", optimize=False)

        # Initialize chat history with empty message
        self.chat_history = [
            {
                "role": "user",
                "content": None,
            }
        ]

        # Convert screenshot to base64 for API
        self.base64_screenshot = encode_image(self.screenshot_path)
        
        # Verify screenshot file exists
        if not os.path.exists(self.screenshot_path):
            logging.error(f"Error: Screenshot file not found at {self.screenshot_path}")
            
        # Create URL for display
        screenshot_url = f"file:///{self.screenshot_path.replace('\\', '/')}"
        logging.info(f"Screenshot URL: {screenshot_url}")

        # Create and add screenshot bubble to chat
        screenshot_bubble = ChatBubble(
            f"""
            <div border-radius: 5px; class='screenshot'>
            <img src='{screenshot_url}' width='960' height='540'></div>""",
            True,
            "Screenshot",
        )
        self.chat_layout.addWidget(screenshot_bubble, alignment=Qt.AlignRight | Qt.AlignTop)
        
        # Log screenshot bubble status
        logging.info("Screenshot bubble added to chat layout")
        logging.info(f"Chat layout count after adding bubble: {self.chat_layout.count()}")
        logging.info(f"Bubble visible: {screenshot_bubble.isVisible()}, Parent: {screenshot_bubble.parent()}")
        
        # Update UI state
        self.screenshot_sent = False
        self.chat_widget.layout().invalidate()
        self.chat_widget.update()
        self.scroll_area.update()
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )
        QApplication.processEvents()

    def load_stylesheet(self) -> None:
        """Load application styling from QSS file."""
        styles_path = get_resource_path("ui/resources/styles.qss")
        with open(styles_path, 'r') as f:
            self.setStyleSheet(f.read())
    
    def send_message(self) -> None:
        """
        Process and send user message to Mistral AI service.
        
        Handles:
        - Getting user input
        - Message processing via handler
        - UI updates
        - Error handling
        - Auto-scrolling
        """
        try:
            user_input = self.text_input.text().strip()
            if not user_input:
                return

            logging.info("Starting message handling...")
            try:
                handle_send_message(self, user_input, self.mistral_client)
            except Exception as e:
                logging.error(f"Error in handle_send_message: {str(e)}")
                error_bubble = ChatBubble(
                    f"Error sending message: {str(e)}",
                    True,
                    "Error"
                )
                self.chat_layout.addWidget(error_bubble)
                return

            self.text_input.clear()
            
            # Scroll to latest message
            try:
                v_scroll = self.scroll_area.verticalScrollBar()
                if v_scroll:
                    QTimer.singleShot(100, lambda: v_scroll.setValue(v_scroll.maximum()))
            except Exception as e:
                logging.error(f"Error scrolling chat: {str(e)}")

            logging.info("Message handling completed successfully")
            
        except Exception as e:
            logging.error(f"Unexpected error in send_message: {str(e)}")
            error_bubble = ChatBubble(
                f"Unexpected error: {str(e)}",
                True,
                "Error"
            )
            self.chat_layout.addWidget(error_bubble)
            
    def convert_markdown_to_html(self, text: str) -> str:
        """
        Convert markdown formatted text to HTML.
        
        Args:
            text: Markdown formatted string
            
        Returns:
            str: HTML formatted string
        """
        markdowner = markdown2.Markdown()
        return markdowner.convert(text)
        
    def reset_chat(self) -> None:
        """
        Reset the chat interface to initial state.
        
        Clears chat history, updates UI, and takes new screenshot.
        """
        logging.info("Resetting application...")
        
        # Clear chat history
        self.chat_history = []
        logging.info("Chat history cleared")
        
        # Remove chat bubbles
        while self.chat_layout.count():
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        logging.info("Chat interface cleared")
        
        # Force UI updates
        QApplication.processEvents()
        QThread.msleep(100)
        
        # Take new screenshot
        self.show_screenshot()
        logging.info("New screenshot taken and displayed")
        
        # Clear input
        self.text_input.clear()
        
        # Force complete UI refresh
        self.chat_widget.update()
        self.chat_layout.update()
        self.chat_widget.adjustSize()
        self.scroll_area.update()
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )
        QApplication.processEvents()
        
        logging.info("Application reset complete")
