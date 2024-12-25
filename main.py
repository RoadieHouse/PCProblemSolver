import sys
from PyQt5.QtWidgets import QApplication
from app.ui import ChatWindow
from app.mistral import create_mistral_client

def start_app():
    """Startet die Hauptanwendung."""
    app = QApplication(sys.argv)
    
    # Create the Mistral client
    mistral_client = create_mistral_client()
    
    # Pass the client to the UI
    window = ChatWindow(mistral_client=mistral_client)
    window.show()
    app.exec_()

def main():
    start_app()

if __name__ == "__main__":
    main()