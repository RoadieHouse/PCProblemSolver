"""
Mistral AI Client Module

Handles the configuration and interaction with the Mistral AI API.
Provides functionality for client creation, image encoding, and API communication.
"""

import os
import sys
from pathlib import Path
import base64
import logging
from mistralai import Mistral
from dotenv import load_dotenv
from typing import Optional, Union

def get_env_path() -> Path:
    """
    Get the path to the .env file in both development and bundled environments.
    
    Returns:
        Path: Path to the .env file, handling both PyInstaller bundled and development environments
    """
    if getattr(sys, 'frozen', False):
        # If running as bundled executable
        base_path = Path(sys._MEIPASS)
    else:
        # If running as script
        base_path = Path(__file__).parent.parent
    return base_path / '.env'

def create_mistral_client() -> Union[Mistral, str]:
    """
    Creates and configures an instance of the Mistral client.
    
    Loads environment variables and initializes the Mistral client with the API key.
    
    Returns:
        Union[Mistral, str]: An instance of the Mistral client if successful,
                            or error message string if API key is not set
    """
    env_path = get_env_path()
    load_dotenv(env_path)
    
    API_KEY = os.getenv("MISTRAL_API_KEY")
    if not API_KEY:
        return "Fehler: MISTRAL_API_KEY ist nicht gesetzt."
    else:
        return Mistral(api_key=API_KEY)

def encode_image(image_path: str) -> Optional[str]:
    """
    Encode an image file to base64 format.
    
    Args:
        image_path (str): Path to the image file to encode
        
    Returns:
        Optional[str]: Base64 encoded string of the image if successful, None if failed
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logging.error(f"Error encoding image: {e}")
        return None

def send_to_mistral(client: Mistral, chat_history: list) -> Optional[dict]:
    """
    Sends chat history to the Mistral client and retrieves a response.
    
    Args:
        client (Mistral): The Mistral client instance
        chat_history (list): The chat history to send
        
    Returns:
        Optional[dict]: The response from the Mistral client, or None if an error occurs
        
    Note:
        The response is formatted as a dictionary with a 'content' key containing
        the AI's response text
    """
    try:
        # Send request to Mistral API
        response = client.agents.complete(
            agent_id=os.getenv("AGENT_ID"),
            messages=chat_history
        )
        logging.info(f"Response from Mistral: {response}")
        
        # Extract the content from the response
        content = response.choices[0].message.content
        return {"content": content}
        
    except Exception as e:
        logging.error(f"Error: {e}")
        return None