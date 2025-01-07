"""
PC Assistant Application - Main Entry Point

This module implements a Windows desktop application that provides an AI-powered
chat interface with screen capture capabilities. The application runs in the 
system tray and can be activated via a global hotkey.

Key components:
- CustomWindow: Handles window management and close events
- AssistantApplication: Main application logic and system tray integration
- Global hotkey support for quick access
- Admin privileges handling for system integration
"""

import sys
import logging
import ctypes
import os
from typing import NoReturn, Optional
from pathlib import Path

from PyQt5.QtCore import Qt, QSharedMemory, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon, QCloseEvent
import keyboard
from ui.interface import ChatbotApp
from app.mistral import create_mistral_client
from app.logger import reset_logging

# Windows API function imports for window management
SetForegroundWindow = ctypes.windll.user32.SetForegroundWindow
GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
GetCurrentThreadId = ctypes.windll.kernel32.GetCurrentThreadId
AttachThreadInput = ctypes.windll.user32.AttachThreadInput

class CustomWindow(ChatbotApp):
    """
    Extended ChatbotApp with custom close event handling.
    Manages window state and minimization behavior.
    """
    def __init__(self, mistral_client, minimize_callback):
        super().__init__(mistral_client=mistral_client)
        self._minimize_callback = minimize_callback
        self._hidden = False # Track whether window is hidden (not visible but running)


    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Override close event to minimize to system tray instead of closing.
        Args:
            event: Close event to be handled
        """
        event.ignore()  # Prevent default close behavior
        self._hidden = True  # Mark window as hidden
        self.hide()  # Hide the window
        self._minimize_callback()  # Execute minimize callback

    def showEvent(self, event):
        """
        Override show event to properly restore window state.
        Args:
            event: Show event to be handled
        """
        super().showEvent(event)
        if self._hidden:
            self._hidden = False
            self.setWindowState(Qt.WindowNoState) # Restore window to normal state (not minimized)
            self.raise_()  # Bring window to front
            self.activateWindow()  # Give window focus

class AssistantApplication(QObject):
    """
    Main application class handling core functionality.
    Manages application lifecycle, hotkeys, and system tray integration.
    """
    # Signal emitted when hotkey is triggered
    hotkey_triggered = pyqtSignal()
    
    def __init__(self):
        super(AssistantApplication, self).__init__()
        
        # Initialize main application components
        self.app: Optional[QApplication] = None
        self.window: Optional[CustomWindow] = None
        self.tray_icon: Optional[QSystemTrayIcon] = None
        self.hotkey = "ctrl+shift+space"
        
        # Connect hotkey signal to reset handler
        self.hotkey_triggered.connect(self.reset_application)
        
        # Check if application should start minimized
        self.start_minimized = "--start-minimized" in sys.argv

    def setup_single_instance(self) -> None:
        """
        Ensure only one instance of the application runs using shared memory.
        Exits if another instance is already running.
        """
        self.shared_memory = QSharedMemory('PCAssistantKey')
        
        if self.shared_memory.attach():
            # Another instance exists
            self.shared_memory.detach()
            logging.info("Another instance is already running")
            sys.exit(0)
            
        if not self.shared_memory.create(1):
            logging.error("Failed to create shared memory")
            sys.exit(1)

    def get_executable_path(self) -> str:
        """Get the absolute path to the executable."""
        if getattr(sys, 'frozen', False):
            # Running as a bundled executable
            return os.path.abspath(sys.executable)
        else:
            # Running as a script
            return os.path.abspath(sys.argv[0])
            
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
    
    def bring_app_to_foreground(self):
        """
        Forcefully bring the window to the foreground using Windows API.
        Uses Windows-specific API calls to ensure window activation.
        """
        try:
            logging.info("Bringing window to foreground: START")
            # Get the window handle for the application window
            hwnd = int(self.window.winId())

            # Get thread IDs for proper window focus handling
            foreground_hwnd = ctypes.windll.user32.GetForegroundWindow()
            foreground_thread_id = GetWindowThreadProcessId(foreground_hwnd, None)
            current_thread_id = GetCurrentThreadId()

            # Attach to foreground window's thread if different
            if foreground_thread_id != current_thread_id:
                AttachThreadInput(foreground_thread_id, current_thread_id, True)

            # Force window to foreground
            SetForegroundWindow(hwnd)

            # Detach from foreground window's thread if was attached
            if foreground_thread_id != current_thread_id:
                AttachThreadInput(foreground_thread_id, current_thread_id, False)

            # Additional Qt-specific window activation
            self.window.raise_()
            self.window.activateWindow()
            self.window.setFocus()
            logging.info("Bringing window to foreground: SUCCESS")

        except Exception as e:
            logging.error(f"Failed to bring window to foreground: {e}")

    def setup_tray_icon(self) -> None:
        """
        Set up the system tray icon and its context menu.
        Creates tray icon with quit action.
        """
        self.tray_icon = QSystemTrayIcon(self.app)
        icon_path = str(Path(__file__).parent / "ui" / "resources" / "icon.png")
        self.tray_icon.setIcon(QIcon(icon_path))

        # Create tray menu with quit and open actions
        tray_menu = QMenu()
        open_action = tray_menu.addAction("Open")
        open_action.triggered.connect(self.reset_application)
        tray_menu.addSeparator()
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_application)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def setup_hotkey(self) -> None:
        """
        Set up the global hotkey using keyboard module.
        Handles registration failures with user notification.
        """
        try:
            keyboard.add_hotkey(self.hotkey, self.handle_hotkey)
            logging.info(f"Successfully registered hotkey: {self.hotkey}")
            
        except Exception as e:
            logging.error(f"Failed to register hotkey: {e}")
            self.tray_icon.showMessage(
                "Hotkey Error",
                f"Failed to register hotkey {self.hotkey}. Please restart the application.",
                QSystemTrayIcon.Critical,
                5000
            )

    def handle_hotkey(self) -> None:
        """
        Handle hotkey press by emitting signal.
        Triggers application reset via signal emission.
        """
        logging.info("Hotkey pressed - emitting signal...")
        self.hotkey_triggered.emit()

    def reset_application(self) -> None:
        """
        Reset the application state without restarting.
        Handles window visibility and chat reset while preventing
        reset during active API calls.
        """
        logging.info("Resetting application state...")
        
        reset_logging()
        
        # Prevent reset if API call is in progress
        if self.window.api_call_in_progress:
            logging.info("API call in progress. Reset is disabled.")
            return
        
        try:
            if self.window:
                # Reset chat while window is hidden
                self.window.reset_chat()
                
                # Restore window visibility
                if self.window._hidden or self.window.isHidden():
                    self.window.show()
                if self.window.isMinimized():
                    self.window.showNormal()
                
                # Ensure window is in foreground
                self.bring_app_to_foreground()

        except Exception as e:
            logging.error(f"Failed to reset application: {e}")
            
    def quit_application(self) -> None:
        """
        Clean up and quit the application.
        Handles proper cleanup of resources before exit.
        """
        logging.info("Quitting application...")
        keyboard.remove_hotkey(self.hotkey)
        
        # Clean up window and thread if they exist
        if self.window:
            if hasattr(self.window, 'thread') and self.window.thread is not None:
                self.window.thread.terminate()
                self.window.thread.wait(100)
        
        # Hide tray icon before quitting
        if self.tray_icon:
            self.tray_icon.hide()
        
        self.app.quit()

    def start(self) -> NoReturn:
        """
        Start the main application with admin privileges.
        Initializes all application components and enters main event loop.
        """
        # Set up high DPI support
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        self.app = QApplication(sys.argv)
        
        # Initialize core components
        self.setup_single_instance()
        
        # Set up Mistral client
        mistral_client = create_mistral_client()
        if isinstance(mistral_client, str):
            logging.error(mistral_client)
            sys.exit(1)
        
        # Create main window
        self.window = CustomWindow(
            mistral_client=mistral_client,
            minimize_callback=self.minimize_to_tray
        )
        
        # Set up system integration
        self.setup_tray_icon()
        self.setup_hotkey()
        
        # Handle initial window state
        if self.start_minimized:
            self.minimize_to_tray()
        else:
            self.window.show()
            self.window.raise_()
            self.window.activateWindow()
        
        # Enter main event loop
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
