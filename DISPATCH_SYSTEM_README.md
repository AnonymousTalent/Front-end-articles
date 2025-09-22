# AI Dispatch System

This project is a private, AI-powered dispatch system designed for a "Commander" to manage a fleet of riders.

## Core Features

*   **AI-Powered Dispatch**: Automatically assigns orders to the most suitable rider based on location and other factors.
*   **Manual Payment Control**: All financial transactions are handled manually through Bank of Taiwan transfers, ensuring complete control. The system tracks the status of these transfers asynchronously.
*   **Google Sheets Reporting**: All operational data, including orders, dispatches, and financial transactions, is logged to a private Google Sheet for analysis.
*   **Private & Secure**: The entire system is designed to be deployed in a private, VPN-protected environment.

## Tech Stack

*   **Backend**: Python with FastAPI
*   **Frontend**: Vue.js
*   **Deployment**: Docker

This project is built to the specifications of the "Commander".

## Usage (Backend Service)

To run the backend service, you need to have Docker installed.

### 1. Build the Docker Image

Navigate to the `backend/` directory and run the following command to build the Docker image:

```bash
docker build -t dispatch-system-backend .
```

### 2. Run the Docker Container

Once the image is built, you can run it as a container with this command:

```bash
docker run -d -p 8000:8000 --name dispatch-backend dispatch-system-backend
```

*   `-d` runs the container in detached mode.
*   `-p 8000:8000` maps port 8000 on your host machine to port 8000 in the container.
*   `--name dispatch-backend` gives the container a memorable name.

The API will then be accessible at `http://localhost:8000`. You can view the auto-generated documentation at `http://localhost:8000/docs`.
---
*This file was created to avoid conflict with the repository's original README.md file.*
