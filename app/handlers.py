# pc_problem_helper/handlers.py
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QTimer
from app.mistral import send_to_mistral

def handle_send_message(window, screenshot_path, user_input, mistral_client):
    """
    Behandelt das Senden einer Nachricht und zeigt den 'typing'-Indikator an.
    """
    window.display_user_message(user_input)
    window.message_input.clear()

    # Show typing indicator
    typing_indicator = QLabel("Mistral is typing...")
    typing_indicator.setStyleSheet("color: #888;")
    window.layout.addWidget(typing_indicator)

    # Simulate response delay
    QTimer.singleShot(2000, lambda: handle_receive_response(window, typing_indicator, screenshot_path, user_input, mistral_client))

def handle_receive_response(window, typing_indicator, screenshot_path, user_input, mistral_client):
    """
    Behandelt die Antwort des Mistral-Clients und aktualisiert die Chat-History.
    """
    typing_indicator.deleteLater()

    response = send_to_mistral(mistral_client, screenshot_path, user_input)
    window.display_bot_message(response)