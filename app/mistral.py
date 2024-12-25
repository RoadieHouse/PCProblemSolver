import base64
from mistralai import Mistral
import os
from dotenv import load_dotenv

load_dotenv()

def create_mistral_client():
    """Erstellt und konfiguriert eine Instanz des Mistral-Clients."""
    API_KEY = os.getenv("MISTRAL_API_KEY")
    if not API_KEY:
        return "Fehler: MISTRAL_API_KEY ist nicht gesetzt."
    else:
        return Mistral(api_key=API_KEY)

def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def send_to_mistral(client, screenshot_path, user_input):
    base64_image = encode_image(screenshot_path)
    if not base64_image:
        return "Fehler: Screenshot konnte nicht geladen oder encodiert werden."

    try:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_input},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"}
                ]
            }
        ]

        response = client.agents.complete(
            agent_id=os.getenv("AGENT_ID"),
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Fehler bei der Verarbeitung: {e}"