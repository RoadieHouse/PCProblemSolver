# PC Assistant (personal project for my father)

PC Assistant is a small desktop application designed to assist users with PC-related issues by interacting with the Mistral AI service (Using a customized Pixtral Large Agent, see system_prompt.md). The application provides a chat interface where users can send messages and screenshots to receive assistance. The main focus was to make the application as easy and barrier-free to use as possible.

## Features

- **Chat Interface**: A user-friendly chat interface for interacting with the Mistral AI.
- **Screenshot Capture**: A new chat always starts with automatically capturing and displaying a screenshot in the chat that is part of the first prompt.
- **Single Mistral Client Instance**: Efficiently uses a single instance of the Mistral client to handle API interactions.
- **Simplicity**: The program is always available in the background. One single hotkey brings the application to the foreground, takes a new screenshot and resets any previous chat.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/RoadieHouse/PCProblemSolver.git
   cd PCProblemSolver
   ```

2. **Install Dependencies**:
   Ensure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment**
- Create a .env file in the root directory
- Add your Mistral API key:

'''bash
MISTRAL_API_KEY=your_api_key_here
'''

## Usage

1. **Run the Application**:
   ```bash
   python main.py
   ```
   
   OR for development mode with hot reload:
   ```bash
   python -m main
   ```

2. **Build with PyInstaller**:
   To create a standalone executable:
   ```bash
   pip install pyinstaller
   pyinstaller --onedir --windowed --icon=app.ico main.py
   ```
   
   The executable will be created in the `dist` directory. You can customize the build using the `main.spec` file.

3. **Interact with the Chat**:
   - If the program is not the active window, press the hotkey to bring it to the foreground.
   - The application will capture a screenshot and send it along with your message to the Mistral AI.
   - Type your message in the input field and press Enter or click the "Senden" button.

4. **Add autostart**
   - The logic for enabling autostart is not part of the code.
   - For a manual setup, create a task in Windows Task Scheduler with admin privileges, trigger on startup or logon and "start an application" with the path to the executable.

## Requirements

- PyQt5
- Pillow
- mistralai
- markdown2
- keyboard
- python-dotenv

- Mistral AI API Key (and client id)

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.
