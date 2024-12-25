# PC Problem Solver

PC Problem Solver is a desktop application designed to assist users with PC-related issues by interacting with the Mistral AI service. The application provides a chat interface where users can send messages and screenshots to receive assistance.

## Features

- **Chat Interface**: A user-friendly chat interface for interacting with the Mistral AI.
- **Screenshot Capture**: Automatically captures and displays screenshots in the chat.
- **Single Mistral Client Instance**: Efficiently uses a single instance of the Mistral client to handle API interactions.

<!--## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/pc_problem_helper.git
   cd pc_problem_helper
   ```

2. **Install Dependencies**:
   Ensure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```
   
   -->
## Usage

1. **Run the Application**:
   ```bash
   python -m app.main
   ```

2. **Interact with the Chat**:
   - Type your message in the input field and press Enter or click the "Senden" button.
   - The application will capture a screenshot and send it along with your message to the Mistral AI.

## Requirements

- Python 3.x
- PyQt5
- Pillow
- mistralai

- Mistral AI API Key (and client id)

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.
