# MyChatBot

Welcome to MyChatBot. A PySide6-based application that uses Mistal AI API for users to send messages, attach files and images, and view responses from the Mistrl AI. This project was not hand written by me. This project serves as my first attempt at AI prompting. I elected to do something small with interacting with the AI and creating a raw, unsanitized dataset from those interactions. Each dataset is saved to a relational database on your system as I support user privacy. You may do with these datasets as you please. These prompts are done using DeekSeek and ChatGPT. It's for me to obtain an idea of how I'm going to build my model. This application took approximately 50 prompts to get finalized to this first working version.

## Docker Setup

The application is now Dockerized for easier deployment and cross-platform compatibility.

### Prerequisites
- Docker Engine
- Docker Compose
- X11 server (for GUI on Linux/macOS)

### Project Structure

```
MyChatBot/
├── backend/ # Database and AI backend
├── frontend/ # GUI components
├── .env # Environment variables
├── Dockerfile # Docker configuration
├── docker-compose.yml # Service definition
├── build.sh # Build script
├── run.sh # Run script
└── cleanup.sh # Cleanup script
```


## Quick Start

1. **Build the container**:
    ```bash
    chmod +x *.sh && ./build.sh
    ```
2. **Run the application**:
    ```bash
    ./run.sh
    ```
3. Clean up when done:
    ```bash
    ./cleanup.sh
    ```

## Script Details

- build.sh: Builds the Docker image with all dependencies

- run.sh: Starts the application with proper X11 forwarding

- cleanup.sh: Removes all project-specific Docker resources

## Features

- Chat Interface: Send messages and receive AI responses

- File Attachments: Analyze text files and images

- Data Collection: All interactions are stored in SQLite

- Markdown Support: View formatted responses

- Cross-Platform: Runs on Linux, macOS, and Windows (WSL)

## Development Notes

This project was developed through AI collaboration, with the Docker implementation being particularly challenging to configure correctly for cross-platform GUI support. The final solution includes:

- Multi-stage Docker builds

- Automatic X11 forwarding

- Isolated data storage

- Clean resource management

## License

MIT License - see [LICENSE.txt](https://github.com/mek0124/MyChatBot/LICENSE.txt) for details.
