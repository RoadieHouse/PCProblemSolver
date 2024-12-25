# pc_problem_helper/ui.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QApplication, QLabel, QMessageBox
from PIL import Image
from app.screenshot import take_screenshot
from app.handlers import handle_send_message

class ChatWindow(QWidget):
    def __init__(self, mistral_client):
        super().__init__()
        self.mistral_client = mistral_client

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Arial', sans-serif;
                font-size: 14px;
            }
            QTextEdit, QLineEdit {
                border: 3px solid #111;
                border-radius: 40px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        self.activateWindow()
        self.raise_()

        self.setWindowTitle('PC Problem Helper')
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(100, 100, int(screen_geometry.width() * 0.8), int(screen_geometry.height() * 0.8))

        self.layout = QVBoxLayout()

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("""
            QTextEdit {
                background-color: #2c2c2c;
                color: #ffffff;
                border: none;
                padding: 10px;
                border-radius: 20px;
            }
            """)
        self.layout.addWidget(self.chat_history)

        self.input_layout = QHBoxLayout()

        self.message_input = QLineEdit()
        self.message_input.setStyleSheet("""
            QLineEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
            """)
        self.message_input.returnPressed.connect(self.send_message)
        self.input_layout.addWidget(self.message_input)

        self.send_button = QPushButton('Senden')
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            """)
        self.send_button.clicked.connect(self.send_message)
        self.input_layout.addWidget(self.send_button)

        self.layout.addLayout(self.input_layout)

        self.setLayout(self.layout)

        self.screenshot_path = take_screenshot()

        screenshot_image = Image.open(self.screenshot_path)
        #screenshot_image = screenshot_image.resize((320, 240))
        screenshot_image.save(self.screenshot_path)

        self.chat_history.append(f'<div style="text-align: left; margin: 10px; border-radius: 10px; padding: 5px; background-color: #444; display: inline-block;"><img src="{self.screenshot_path}" width="640" height="480"></div>')

    def send_message(self):
        user_input = self.message_input.text()
        handle_send_message(self, self.screenshot_path, user_input, self.mistral_client)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Quit', 'Are you sure you want to quit?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            QApplication.quit()
        else:
            event.ignore()

    def display_user_message(self, message):
        self.chat_history.append(
            f'<div style="text-align: left; margin: 20px; border-radius: 20px; '
            f'padding: 5px; background-color: #4CAF50; display: inline-block;">You: {message}</div>'
        )

    def display_bot_message(self, message):
        formatted_message = message.replace("\n", "<br>").replace("**", "<b>").replace("**", "</b>")
        self.chat_history.append(
            f'<div style="text-align: right; margin: 30px; border-radius: 30px; '
            f'padding: 30px; background-color: #2196F3; display: inline-block;">Mistral: {formatted_message}</div>'
        )
