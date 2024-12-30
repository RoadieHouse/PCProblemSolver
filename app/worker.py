from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QMutex
from mistralai import Mistral
from app.mistral import send_to_mistral
import logging

class MistralWorker(QObject):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, mistral_client: Mistral, chat_history: list):
        super().__init__()
        self.mistral_client = mistral_client
        self.chat_history = chat_history.copy()
        self._running = False
        self._mutex = QMutex()
        logging.info("MistralWorker initialized with chat history length: %d", len(self.chat_history))

    def stop(self):
        """Safely stop the worker."""
        self._mutex.lock()
        try:
            if self._running:
                logging.info("Stopping MistralWorker")
                self._running = False
        finally:
            self._mutex.unlock()

    @pyqtSlot()
    def run(self):
        """Execute the Mistral API call in the worker thread."""
        self._mutex.lock()
        self._running = True
        self._mutex.unlock()

        logging.info("MistralWorker run method started")
        try:
            # Check if we should continue
            self._mutex.lock()
            if not self._running:
                logging.info("Worker stopped before execution")
                return
            self._mutex.unlock()

            logging.info("Sending request to Mistral...")
            response = send_to_mistral(self.mistral_client, self.chat_history)
            
            # Check if we should continue after API call
            self._mutex.lock()
            if not self._running:
                logging.info("Worker stopped after API call")
                return
            self._mutex.unlock()

            if response is None:
                error_msg = "No response received from Mistral"
                logging.error(error_msg)
                self.error.emit(error_msg)
                return

            logging.info("Response received from Mistral successfully")
            logging.debug("Response content: %s", str(response))
            
            if isinstance(response, dict) and "content" in response:
                self.finished.emit(response)
            else:
                formatted_response = {"content": str(response)}
                self.finished.emit(formatted_response)
                
        except Exception as e:
            error_msg = f"Exception in MistralWorker: {str(e)}"
            logging.error(error_msg)
            self.error.emit(error_msg)
        finally:
            self._mutex.lock()
            self._running = False
            self._mutex.unlock()
