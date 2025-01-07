"""
Mistral Worker Module

Handles asynchronous API communication with Mistral AI service in a separate thread.
Provides thread-safe operations and proper signal handling for UI updates.
"""

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QMutex
from mistralai import Mistral
from app.mistral import send_to_mistral
import logging

class MistralWorker(QObject):
    """
    Worker class for handling Mistral AI API calls in a separate thread.
    
    Signals:
        finished (dict): Emitted when API call completes successfully
        error (str): Emitted when an error occurs during API call
    """
    
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, mistral_client: Mistral, chat_history: list):
        """
        Initialize the worker with required components.
        
        Args:
            mistral_client (Mistral): Instance of Mistral API client
            chat_history (list): List of previous chat messages
        """
        super().__init__()
        self.mistral_client = mistral_client
        self.chat_history = chat_history.copy()  # Create a copy to prevent modifications
        self._running = False  # Thread execution control flag
        self._mutex = QMutex()  # Mutex for thread-safe operations
        logging.info("MistralWorker initialized with chat history length: %d", len(self.chat_history))

    def stop(self):
        """
        Safely stop the worker thread.
        Uses mutex to ensure thread-safe operation.
        """
        self._mutex.lock()
        try:
            if self._running:
                logging.info("Stopping MistralWorker")
                self._running = False
        finally:
            self._mutex.unlock()

    @pyqtSlot()
    def run(self):
        """
        Execute the Mistral API call in the worker thread.
        
        Handles:
        - Thread safety with mutex
        - API communication
        - Signal emission for success/failure
        - Proper cleanup
        """
        # Set initial running state
        self._mutex.lock()
        self._running = True
        self._mutex.unlock()

        logging.info("MistralWorker run method started")
        try:
            # Check if we should proceed
            self._mutex.lock()
            if not self._running:
                logging.info("Worker stopped before execution")
                return
            self._mutex.unlock()

            # Make API call
            logging.info("Sending request to Mistral...")
            response = send_to_mistral(self.mistral_client, self.chat_history)
            
            # Check if we should continue after API call
            self._mutex.lock()
            if not self._running:
                logging.info("Worker stopped after API call")
                return
            self._mutex.unlock()

            # Handle empty response
            if response is None:
                error_msg = "No response received from Mistral"
                logging.error(error_msg)
                self.error.emit(error_msg)
                return

            logging.info("Response received from Mistral successfully")
            logging.debug("Response content: %s", str(response))
            
            # Format and emit response
            if isinstance(response, dict) and "content" in response:
                self.finished.emit(response)
            else:
                # Ensure response is in expected format
                formatted_response = {"content": str(response)}
                self.finished.emit(formatted_response)
                
        except Exception as e:
            # Handle any exceptions during execution
            error_msg = f"Exception in MistralWorker: {str(e)}"
            logging.error(error_msg)
            self.error.emit(error_msg)
            
        finally:
            # Ensure running flag is reset
            self._mutex.lock()
            self._running = False
            self._mutex.unlock()
