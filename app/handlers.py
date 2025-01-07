"""
Message handling module for PC Assistant application.

This module handles message processing, thread management, and UI updates
for the chat interface. It manages communication between the UI and the
Mistral AI service while ensuring proper cleanup of resources.
"""

import logging
from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel
from mistralai import Mistral
from app.worker import MistralWorker
from ui.chat_bubble import ChatBubble
from ui.typing_indicator import TypingIndicator

# Maximum number of messages to keep in chat history
MAX_CHAT_HISTORY_LENGTH = 10

def cleanup_thread(window):
    """
    Safely clean up thread and worker with proper synchronization.
    
    Ensures proper cleanup of worker and thread objects to prevent memory leaks
    and resource issues. Handles disconnection of signals and proper thread termination.
    
    Args:
        window: The main window instance containing thread and worker objects
    """
    logging.info("Starting thread cleanup")
    
    # Clean up worker first
    if hasattr(window, 'worker') and window.worker:
        try:
            logging.info("Stopping worker")
            window.worker.stop()  # Signal worker to stop
            
            # Wait for worker to finish if thread is running
            if hasattr(window, 'thread') and window.thread and window.thread.isRunning():
                logging.info("Waiting for worker to finish")
                if not window.thread.wait(2000):  # Wait up to 2 seconds
                    logging.warning("Worker did not finish in time")
            
            # Disconnect signals to prevent memory leaks
            try:
                window.worker.finished.disconnect()
                window.worker.error.disconnect()
            except Exception as e:
                logging.warning(f"Error disconnecting worker signals: {e}")
            
            # Clean up worker object
            window.worker.deleteLater()
            window.worker = None
            logging.info("Worker cleaned up")
            
        except Exception as e:
            logging.error(f"Error during worker cleanup: {e}")
            # Continue with thread cleanup even if worker cleanup failed

    # Clean up thread after worker
    if hasattr(window, 'thread') and window.thread:
        try:
            logging.info("Stopping thread")
            if window.thread.isRunning():
                window.thread.quit()
                if not window.thread.wait(1000):  # Wait up to 1 second
                    logging.warning("Thread did not finish in time")
                    window.thread.terminate()
            
            window.thread.deleteLater()
            window.thread = None
            logging.info("Thread cleaned up")
            
        except Exception as e:
            logging.error(f"Error during thread cleanup: {e}")
            # Continue with cleanup even if thread cleanup failed

    logging.info("Thread cleanup completed")

def handle_send_message(window, user_input: str, mistral_client: Mistral) -> None:
    """
    Process and send user message to Mistral AI service.
    
    Creates a new thread for API communication, updates UI with user message,
    and shows typing indicator while waiting for response.
    
    Args:
        window: Main window instance containing chat interface
        user_input: User's message text
        mistral_client: Instance of Mistral AI client
    """
    logging.info("handle_send_message called")

    # Ensure clean state before starting new operation
    cleanup_thread(window)

    # Update chat history with user message
    window.chat_history.append({"role": "user", "content": user_input})

    # Show user message in chat interface
    user_msg = ChatBubble(f"{user_input}", True, "Du")
    window.chat_layout.addWidget(user_msg)

    # Handle typing indicator cleanup and creation
    if hasattr(window, 'typing_indicator'):
        if window.typing_indicator is not None:
            if not window.typing_indicator.isWidgetType():
                window.typing_indicator.delete()
            else:
                window.typing_indicator = None

    # Create and show new typing indicator
    window.typing_indicator = TypingIndicator()
    window.chat_layout.addWidget(window.typing_indicator)
    window.typing_indicator.start()

    # Prepare first message with screenshot if not sent yet
    if not window.screenshot_sent:
        window.chat_history[0]["content"] = [
            {"type": "text", "text": user_input},
            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{window.base64_screenshot}"},
        ]
        window.screenshot_sent = True

    # Maintain chat history length limit
    if len(window.chat_history) > MAX_CHAT_HISTORY_LENGTH:
        window.chat_history = window.chat_history[-MAX_CHAT_HISTORY_LENGTH:]

    try:
        # Set up thread and worker for API communication
        window.thread = QtCore.QThread()
        window.worker = MistralWorker(mistral_client, window.chat_history)
        logging.info("Worker and thread created")

        # Configure worker thread
        window.worker.moveToThread(window.thread)
        window.thread.started.connect(window.worker.run)

        # Connect response handlers with proper context
        window.worker.finished.connect(
            lambda response, w=window, ti=window.typing_indicator: handle_receive_response(w, ti, response)
        )
        window.worker.error.connect(
            lambda error, w=window, ti=window.typing_indicator: handle_error(w, ti, error)
        )

        # Set up cleanup handlers
        def safe_cleanup():
            try:
                if window.thread and window.thread.isRunning():
                    window.thread.quit()
                    window.thread.wait(2000)  # Wait up to 2 seconds
                cleanup_thread(window)
            except Exception as e:
                logging.error(f"Error during safe cleanup: {e}")

        # Connect cleanup handlers to worker signals
        window.worker.finished.connect(
            lambda: QtCore.QTimer.singleShot(0, safe_cleanup)
        )
        window.worker.error.connect(
            lambda: QtCore.QTimer.singleShot(0, safe_cleanup)
        )

        # Track API call status
        window.api_call_in_progress = True

        # Start worker thread
        window.thread.start()
        logging.info("Thread started and worker moved to thread")

        # Verify thread started successfully
        if not window.thread.isRunning():
            logging.error("Thread failed to start")
            safe_cleanup()
            handle_error(window, window.typing_indicator, "Thread failed to start")

    except Exception as e:
        logging.error(f"Error setting up thread: {e}")
        cleanup_thread(window)
        handle_error(window, window.typing_indicator, str(e))

def handle_error(window, typing_indicator: QLabel, error: str):
    """
    Handle errors from the worker thread.
    
    Updates UI to show error message and ensures proper cleanup.
    
    Args:
        window: Main window instance
        typing_indicator: Current typing indicator widget
        error: Error message to display
    """
    logging.error(f"Error in worker thread: {error}")
    try:
        typing_indicator.setText("Error occurred while processing request.\nEntweder kein Internet oder Sohnemann fragen.")
        typing_indicator.setStyleSheet("color: red; font-size: 18px;")
    except Exception as e:
        logging.error(f"Error updating typing indicator: {e}")
    finally:
        # Reset API call status
        window.api_call_in_progress = False

def handle_receive_response(window, typing_indicator: QLabel, response: dict) -> None:
    """
    Process response from Mistral AI service.
    
    Updates chat interface with AI response and handles cleanup.
    
    Args:
        window: Main window instance
        typing_indicator: Current typing indicator widget
        response: Response data from Mistral AI
    """
    logging.info("handle_receive_response: called")

    try:
        # Clean up typing indicator
        if hasattr(window, 'typing_indicator'):
            window.typing_indicator.stop()
            window.typing_indicator.deleteLater()
            window.typing_indicator = None

        # Update chat history with response
        window.chat_history.append({"role": "assistant", "content": response["content"]})

        # Format and display response
        formatted_response = window.convert_markdown_to_html(response["content"])
        assistant_msg = ChatBubble(formatted_response, False, "PC Assistent")
        window.chat_layout.addWidget(assistant_msg)

        # Scroll to appropriate position
        user_msg_index = len(window.chat_history) - 2  # Index of the last user message
        user_msg_widget = window.chat_layout.itemAt(user_msg_index).widget()
        scroll_position = user_msg_widget.y()
        v_scroll = window.scroll_area.verticalScrollBar()
        QtCore.QTimer.singleShot(100, lambda: v_scroll.setValue(scroll_position))

        logging.info("handle_receive_response: completed")

    except Exception as e:
        logging.error(f"Error in handle_receive_response: {e}")
        handle_error(window, typing_indicator, str(e))
    finally:
        # Reset API call status
        window.api_call_in_progress = False
