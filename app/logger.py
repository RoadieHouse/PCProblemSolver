import logging
import os
import tempfile

# Set up the log file path in the temp directory
log_file = os.path.join(tempfile.gettempdir(), "PC_Assistent.log")

# Configure the logger
logging.basicConfig(
    filename=log_file,
    filemode="w",  # Append to the file on each run
    level=logging.DEBUG,  # Set the logging level
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def reset_logging():
    """Reset the logging configuration to overwrite the log file."""
    log_file = os.path.join(tempfile.gettempdir(), "PC_Assistent.log")
    
    # Remove existing handlers to avoid duplicate logs
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Reconfigure logging to overwrite the log file
    logging.basicConfig(
        filename=log_file,
        filemode="w",  # Overwrite the log file
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
