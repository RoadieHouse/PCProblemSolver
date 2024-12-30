import logging
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QMovie
from pathlib import Path
from mistralai import Mistral
from app.worker import MistralWorker
from ui.chat_bubble import ChatBubble
from ui.typing_indicator import TypingIndicator

MAX_CHAT_HISTORY_LENGTH = 10

def cleanup_thread(window):
    """Safe cleanup of thread and worker with proper synchronization."""
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
            
            # Disconnect signals
            try:
                window.worker.finished.disconnect()
                window.worker.error.disconnect()
            except Exception as e:
                logging.warning(f"Error disconnecting worker signals: {e}")
            
            # Clean up worker
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
    logging.info("handle_send_message called")
    logging.debug(f"Window object: {window}")
    logging.debug(f"User input: {user_input}")
    logging.debug(f"Mistral client: {mistral_client}")
    logging.debug(f"Window has thread: {hasattr(window, 'thread')}")
    logging.debug(f"Window has worker: {hasattr(window, 'worker')}")
    
    # Safely cleanup previous thread if it exists
    cleanup_thread(window)
    
    # Add user input to chat history
    window.chat_history.append({"role": "user", "content": user_input})

    # Display user message in the chat layout
    user_msg = ChatBubble(f"{user_input}", True, "Du")
    window.chat_layout.addWidget(user_msg)

    # Show typing indicator with animated GIF
    if hasattr(window, 'typing_indicator'):
        if window.typing_indicator is not None:
            if not window.typing_indicator.isWidgetType():
                window.typing_indicator.delete()
            else:
                window.typing_indicator = None
    window.typing_indicator = TypingIndicator()
    window.chat_layout.addWidget(window.typing_indicator)
    window.typing_indicator.start()

    #window.typing_indicator = typing_indicator
    # Prepare the chat history for Mistral API
    if not window.screenshot_sent:
        window.chat_history[0]["content"] = [
            {"type": "text", "text": user_input},
            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{window.base64_screenshot}"},
        ]
        window.screenshot_sent = True

    # Limit chat history length
    if len(window.chat_history) > MAX_CHAT_HISTORY_LENGTH:
        window.chat_history = window.chat_history[-MAX_CHAT_HISTORY_LENGTH:]

    try:
        # Create new thread and worker
        window.thread = QtCore.QThread()
        window.worker = MistralWorker(mistral_client, window.chat_history)
        logging.info("Worker and thread created")
        
        # Move worker to thread
        window.worker.moveToThread(window.thread)
        
        # Connect signals and slots
        window.thread.started.connect(window.worker.run)
        
        # Use lambda to ensure proper variable capture
        window.worker.finished.connect(
            lambda response, w=window, ti=window.typing_indicator: handle_receive_response(w, ti, response)
        )
        window.worker.error.connect(
            lambda error, w=window, ti=window.typing_indicator: handle_error(w, ti, error)
        )
        
        # Connect cleanup handlers with proper lifecycle management
        def safe_cleanup():
            try:
                if window.thread and window.thread.isRunning():
                    window.thread.quit()
                    window.thread.wait(2000)  # Wait up to 2 seconds
                cleanup_thread(window)
            except Exception as e:
                logging.error(f"Error during safe cleanup: {e}")

        window.worker.finished.connect(
            lambda: QtCore.QTimer.singleShot(0, safe_cleanup)
        )
        window.worker.error.connect(
            lambda: QtCore.QTimer.singleShot(0, safe_cleanup)
        )
        
        # Start the thread
        window.thread.start()
        logging.info("Thread started and worker moved to thread")
        
        # Ensure thread is properly initialized
        if not window.thread.isRunning():
            logging.error("Thread failed to start")
            safe_cleanup()
            handle_error(window, window.typing_indicator, "Thread failed to start")
        
    except Exception as e:
        logging.error(f"Error setting up thread: {e}")
        cleanup_thread(window)
        handle_error(window, window.typing_indicator, str(e))

def handle_error(window, typing_indicator: QLabel, error: str):
    """Handle errors from the worker thread."""
    logging.error(f"Error in worker thread: {error}")
    try:
        typing_indicator.setText("Error occurred while processing request.")
        typing_indicator.setStyleSheet("color: red; font-size: 14px;")
    except Exception as e:
        logging.error(f"Error updating typing indicator: {e}")

def handle_receive_response(window, typing_indicator: QLabel, response: dict) -> None:
    logging.info("handle_receive_response called")
    
    try:
        if hasattr(window, 'typing_indicator'):
            window.typing_indicator.stop()
            window.typing_indicator.deleteLater()
            window.typing_indicator = None

        # Add the response to chat history
        window.chat_history.append({"role": "assistant", "content": response["content"]})
        
        # Convert markdown to HTML
        formatted_response = window.convert_markdown_to_html(response["content"])
        
        # Create and display assistant message
        assistant_msg = ChatBubble(formatted_response, False, "PC Assistent")
        window.chat_layout.addWidget(assistant_msg)
        
        # Scroll to the position where the last user message is at the top
        user_msg_index = len(window.chat_history) - 2  # Index of the last user message
        user_msg_widget = window.chat_layout.itemAt(user_msg_index).widget()
        scroll_position = user_msg_widget.y()
        v_scroll = window.scroll_area.verticalScrollBar()
        QtCore.QTimer.singleShot(100, lambda: v_scroll.setValue(scroll_position))
        
    except Exception as e:
        logging.error(f"Error in handle_receive_response: {e}")
        handle_error(window, typing_indicator, str(e))
