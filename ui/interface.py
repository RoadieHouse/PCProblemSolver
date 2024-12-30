import markdown2
import logging
import os
from PIL import Image
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QMainWindow, QLineEdit,
                             QPushButton, QVBoxLayout, QWidget,
                             QScrollArea, QApplication, QHBoxLayout)
from app.mistral import encode_image
from app.resource_path import get_resource_path  # Import the function from the appropriate module
from app.screenshot import take_screenshot
from app.handlers import handle_send_message
from ui.chat_bubble import ChatBubble

class ChatbotApp(QMainWindow):
    def __init__(self, mistral_client) -> None:
        self.thread = None
        self.worker = None
        """
        Initialize the Chatbot application.

        Args:
            mistral_client: The Mistral client instance.
        """
        super().__init__()
        self.setWindowIcon(QIcon('ui/resources/icon.png'))
        
        self.mistral_client = mistral_client
        
        self.setWindowTitle("PC Assistent")
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(100, 100, int(screen_geometry.width() * 0.8), int(screen_geometry.height() * 0.8))
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Chat display box with scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setAlignment(Qt.AlignTop)  # Align the layout to the top
        self.scroll_area.setWidget(self.chat_widget)

        layout.addWidget(self.scroll_area)

        # Create a horizontal layout for input and button
        input_layout = QHBoxLayout()
        
        # Create and configure text input
        self.text_input = QLineEdit(self)
        self.text_input.setFixedHeight(int(self.text_input.sizeHint().height() * 2))  # Increase height by 15%
        self.text_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.text_input, 85)  # Set to take 85% of width
        
        # Create and configure send button
        send_button = QPushButton("SENDEN", self)
        send_button.setFixedHeight(self.text_input.height())  # Match input height
        send_button.clicked.connect(self.send_message)
        input_layout.addWidget(send_button, 15)  # Set to take 15% of width
        
        # Add the input layout to the main layout
        layout.addLayout(input_layout)

        central_widget.setLayout(layout)
        
        self.show_screenshot()
        
        # Load stylesheet
        self.load_stylesheet()
        
    def show_screenshot(self) -> None:
        """Show the screenshot in the chat layout."""
        logging.info("show_screenshot called")  # Debug logging

        self.screenshot_path = take_screenshot()
        logging.info(f"Screenshot taken: {self.screenshot_path}")  # Debug logging

        screenshot_image = Image.open(self.screenshot_path)
        screenshot_image.save(self.screenshot_path, format="PNG", optimize=False)

        self.chat_history = [
            {
                "role": "user",
                "content": None,  # Will be set later to include the first prompt and image
            }
        ]

        # Convert the screenshot to base64 for the first prompt
        self.base64_screenshot = encode_image(self.screenshot_path)

        # Add the screenshot message to the chat layout
        logging.info(f"Displaying screenshot from: {self.screenshot_path}")  # Debug logging
        if not os.path.exists(self.screenshot_path):
            logging.error(f"Error: Screenshot file not found at {self.screenshot_path}")
            
        # Convert path to file:// URL format for proper display
        screenshot_url = f"file:///{self.screenshot_path.replace('\\', '/')}"
        logging.info(f"Screenshot URL: {screenshot_url}")  # Debug logging

        screenshot_bubble = ChatBubble(
            f"""
            <div border-radius: 5px; class='screenshot'>
            <img src='{screenshot_url}' width='960' height='540'></div>""",
            True,
            "Screenshot",
        )
        self.chat_layout.addWidget(screenshot_bubble, alignment=Qt.AlignRight | Qt.AlignTop)
        logging.info("Screenshot bubble added to chat layout")  # Debug logging
        logging.info(f"Chat layout count after adding bubble: {self.chat_layout.count()}")
        logging.info(f"Bubble visible: {screenshot_bubble.isVisible()}, Parent: {screenshot_bubble.parent()}")
        
        # Initialize screenshot_sent flag
        self.screenshot_sent = False

        self.chat_widget.layout().invalidate()
        # Force UI updates
        self.chat_widget.update()
        self.scroll_area.update()
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
        QApplication.processEvents()

    def load_stylesheet(self) -> None:
        """
        Load and apply the stylesheet from a QSS file.

        This function reads the QSS file and sets the application's stylesheet.

        Returns:
            None
        """
        # Open the QSS file and read its contents
        styles_path = get_resource_path("ui/resources/styles.qss")
        with open(styles_path, 'r') as f:
            self.setStyleSheet(f.read())
    
    def send_message(self) -> None:
        """
        Send the user's message with proper error handling and UI updates.
        """
        try:
            user_input = self.text_input.text().strip()
            
            if not user_input:
                return

            # Log message sending start
            logging.info("Starting message handling...")
            
            # Delegate API call to handler with error handling
            try:
                handle_send_message(self, user_input, self.mistral_client)
            except Exception as e:
                logging.error(f"Error in handle_send_message: {str(e)}")
                # Show error message in UI
                error_bubble = ChatBubble(
                    f"Error sending message: {str(e)}",
                    True,
                    "Error"
                )
                self.chat_layout.addWidget(error_bubble)
                return

            # Clear the input field after successful message handling
            self.text_input.clear()

            # Scroll to the bottom of the chat layout
            try:
                v_scroll = self.scroll_area.verticalScrollBar()
                if v_scroll:
                    QTimer.singleShot(100, lambda: v_scroll.setValue(v_scroll.maximum()))
            except Exception as e:
                logging.error(f"Error scrolling chat: {str(e)}")

            logging.info("Message handling completed successfully")
            
        except Exception as e:
            print(f"Unexpected error in send_message: {str(e)}")
            # Show error message in UI
            error_bubble = ChatBubble(
                f"Unexpected error: {str(e)}",
                True,
                "Error"
            )
            self.chat_layout.addWidget(error_bubble)
            
    def convert_markdown_to_html(self, text: str) -> str:
        """
        Convert a markdown text to HTML.

        Args:
            text (str): The markdown text to convert.

        Returns:
            str: The converted HTML text.
        """
        # Create a Markdown converter instance
        markdowner = markdown2.Markdown()
        # Convert the markdown text to HTML
        return markdowner.convert(text)
        
    def reset_chat(self) -> None:
        """Clear the chat window and reset state"""
        logging.info("reset_chat called")

        # Clear chat layout properly
        while self.chat_layout.count():
            item = self.chat_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()  # This is safer than setParent(None)

        # Force immediate layout update
        self.chat_widget.layout().update()
        self.chat_widget.updateGeometry()

        # Ensure the chat_widget is properly set as the parent for new widgets
        self.chat_layout.setParent(self.chat_widget)
        
        try:
            self.show_screenshot()
            logging.info("Chat window reset successfully")
        except Exception as e:
            logging.error(f"Failed to show screenshot: {e}")
        
        # Force UI updates
        self.chat_widget.update()
        self.scroll_area.update()
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
        QApplication.processEvents()
        
        # Ensure proper widget visibility
        self.chat_widget.show()
        self.scroll_area.show()
        
        # Ensure window is visible and focused
        self.show()
        self.raise_()
