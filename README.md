# MyChatBot

Welcome to MyChatBot. A PySide6-based application that uses Mistal AI API for users to send messages, attach files and images, and view responses from the Mistrl AI. This project was not hand written by me. This project serves as my first attempt at AI prompting. I elected to do something small with interacting with the AI and creating a raw, unsanitized dataset from those interactions. Each dataset is saved to a relational database on your system as I support user privacy. You may do with these datasets as you please.

## Features

- **User Interface**: A clean and intuitive chat interface built with PySide6.
- **Message Logging**: Messages are logged into an SQLite database.
- **File and Image Attachments**: Users can attach and send files and images.
- **Markdown Support**: Messages can be formatted using Markdown.
- **Concurrency**: Uses QThread for background tasks to keep the UI responsive.

## Project Structure

```
.
├── .env
├── .gitignore
├── chat_dataset.db
├── chat_widget.py
├── dataset_agent.py
├── main.py
├── mistral_agent.py
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.x

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/mek0124/MyChatBot
    cd MyChatBot
    ```

2. Create a virtual environment and activate it:

    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3. Install the required dependencies:

    ```sh
    pip install -r requirements.txt
    ```

4. Set up the environment variables by creating a `.env` file in the project root:

    ```ini
    MISTRAL_API_KEY=your_mistral_api_key_here # do not encase in double quotes!
    ```

## Running the Application

To run the application, execute the following command:

```sh
python main.py

# python3 main.py if on linux/mac
```

## Codebase Overview

### `.gitignore`

Specifies files and directories to be ignored by Git.

### `chat_dataset.db`

> .gitignored by default

A binary file containing the SQLite database used to store chat profiles and messages.

### `chat_widget.py`

Contains the custom PySide6 widgets used in the chat interface:

- **LoadingWidget**: Displays a loading animation.
- **ChatMessageWidget**: Displays chat messages with Markdown support and options to copy or save messages.

### `dataset_agent.py`

Handles interactions with the SQLite database:

- **DatasetAgent**: Manages database operations for profiles and messages.
- **DatasetAgentWorker**: A QThread for performing database operations in the background.

### `main.py`

The main entry point of the application:

- **MainWindow**: The main window class that sets up the UI and handles user interactions.
- Initializes profiles for the user and AI.
- Manages sending messages and handling responses.

### `mistral_agent.py`

Handles interactions with the Mistral AI API:

- **MistralWorker**: A QThread for sending messages to the Mistral AI API and receiving responses.

### `requirements.txt`

Lists the Python dependencies required to run the application.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to the Mistral AI team for providing the API.
- Thanks to the PySide6 community for their excellent UI framework.
