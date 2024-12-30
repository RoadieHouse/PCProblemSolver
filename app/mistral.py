import os
import sys
from pathlib import Path
import base64
import logging

from mistralai import Mistral
from dotenv import load_dotenv
from typing import Optional, Union

def get_env_path():
    """Get the path to the .env file in both dev and bundled environments."""
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

    Returns:
        Mistral: An instance of the Mistral client if the API key is set.
        str: An error message if the API key is not set.
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
    Encodes an image to a base64 string.

    Args:
        image_path (str): The path to the image file.

    Returns:
        Optional[str]: The base64 encoded string of the image, or None if an error occurs.
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def send_to_mistral(client: Mistral, chat_history: list) -> Optional[dict]:
    """
    Sends chat history to the Mistral client and retrieves a response.

    Args:
        client (Mistral): The Mistral client instance.
        chat_history (list): The chat history to send.

    Returns:
        Optional[dict]: The response from the Mistral client, or None if an error occurs.
    """
    try:
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