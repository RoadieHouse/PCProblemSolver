import sys
import logging
import winreg
import os
from typing import NoReturn, Optional
from pathlib import Path

from PyQt5.QtCore import Qt, QTimer, QSharedMemory
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QWidget
from PyQt5.QtGui import QIcon, QCloseEvent
from keyboard import add_hotkey, remove_hotkey
from ui.interface import ChatbotApp
from app.mistral import create_mistral_client

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        
class CustomWindow(ChatbotApp):
    """Extended ChatbotApp with custom close event handling"""
    def __init__(self, mistral_client, minimize_callback):
        super().__init__(mistral_client=mistral_client)
        self._minimize_callback = minimize_callback

    def closeEvent(self, event: QCloseEvent) -> None:
        """Override close event to minimize instead of closing"""
        event.ignore()
        self.hide()
        self._minimize_callback()

class AssistantApplication:
    def __init__(self):
        self.app: Optional[QApplication] = None
        self.window: Optional[CustomWindow] = None
        self.tray_icon: Optional[QSystemTrayIcon] = None
        self.hotkey = "ctrl+shift+b"
        self.start_minimized = "--start-minimized" in sys.argv

    def setup_single_instance(self) -> None:
        """Ensure only one instance of the application runs"""
        self.shared_memory = QSharedMemory('PCAssistantKey')
        
        if self.shared_memory.attach():
            self.shared_memory.detach()
            logging.info("Another instance is already running")
            sys.exit(0)
            
        if not self.shared_memory.create(1):
            logging.error("Failed to create shared memory")
            sys.exit(1)

    def get_executable_path(self) -> str:
        """Get the path to the executable or script."""
        if getattr(sys, 'frozen', False):
            return sys.executable
        return str(Path(sys.argv[0]).resolve())

    def setup_autostart(self) -> None:
        """Set up the application to run on Windows startup."""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_path = self.get_executable_path()
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, 
                            winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE) as key:
                if getattr(sys, 'frozen', False):
                    new_value = f'"{app_path}" --start-minimized'
                else:
                    new_value = f'"{sys.executable}" "{app_path}" --start-minimized'
                
                winreg.SetValueEx(key, "PCAssistant", 0, winreg.REG_SZ, new_value)
                logging.info("Successfully added application to autostart")
                
        except Exception as e:
            logging.error(f"Failed to set up autostart: {e}")
            
    def minimize_to_tray(self) -> None:
        """Handle minimizing to tray with notification"""
        if not hasattr(self, '_first_minimize'):
            self._first_minimize = True
            self.tray_icon.showMessage(
                "PCAssistant",
                f"Application is running in background. Press {self.hotkey} to open.",
                QSystemTrayIcon.Information,
                3000
            )

    def setup_tray_icon(self) -> None:
        """Set up the system tray icon and its context menu."""
        self.tray_icon = QSystemTrayIcon(self.app)
        icon_path = str(Path(__file__).parent / "ui" / "resources" / "icon.png")
        self.tray_icon.setIcon(QIcon(icon_path))

        tray_menu = QMenu()
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_application)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def setup_hotkey(self) -> None:
        """Set up the global hotkey."""
        try:
            add_hotkey(self.hotkey, self.handle_hotkey)
            logging.info(f"Successfully registered hotkey: {self.hotkey}")
        except Exception as e:
            logging.error(f"Failed to register hotkey: {e}")

    def handle_hotkey(self) -> None:
        """Handle hotkey press by resetting the application state"""
        self.reset_application()

    def reset_application(self) -> None:
        """Reset the application state without restarting"""
        logging.info("Resetting application state...")
        
        try:
            # Clear the chat window
            if self.window:
                self.window.reset_chat()
                
            # Show window if minimized
            if self.window and self.window.isHidden():
                self.window.show()
                self.window.raise_()
                self.window.activateWindow()
                
        except Exception as e:
            logging.error(f"Failed to reset application: {e}")

    def quit_application(self) -> None:
        """Clean up and quit the application."""
        logging.info("Quitting application...")
        remove_hotkey(self.hotkey)
        
        if self.window:
            if hasattr(self.window, 'thread') and self.window.thread is not None:
                self.window.thread.terminate()
                self.window.thread.wait(100)
        
        if self.tray_icon:
            self.tray_icon.hide()
        
        self.app.quit()

    def start(self) -> NoReturn:
        """Start the main application."""
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        self.app = QApplication(sys.argv)
        
        self.setup_single_instance()
        self.setup_autostart()

        mistral_client = create_mistral_client()
        if isinstance(mistral_client, str):
            logging.error(mistral_client)
            sys.exit(1)
        
        self.window = CustomWindow(
            mistral_client=mistral_client,
            minimize_callback=self.minimize_to_tray
        )
        
        self.setup_tray_icon()
        self.setup_hotkey()
        
        if self.start_minimized:
            # When started minimized, show tray notification
            self.minimize_to_tray()
        else:
            self.window.show()
            self.window.raise_()
            self.window.activateWindow()
        
        sys.exit(self.app.exec_())

def main() -> NoReturn:
    """Main entry point of the application."""
    try:
        assistant = AssistantApplication()
        assistant.setup_single_instance()
        assistant.start()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
