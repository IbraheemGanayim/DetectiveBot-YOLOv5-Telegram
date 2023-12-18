# DetectiveBot-YOLOv5-Telegram

Leveraging YOLOv5, Flask, Telegram API, and Ngrok, this project delivers a Dockerized solution for image object detection via a user-friendly chat-based interface. The Object Detection Telegram Bot utilizes the Telegram Bot API to seamlessly receive user images and provide swift responses with detected objects.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Implementation Guidelines](#implementation-guidelines)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Running the Bot Locally](#running-the-bot-locally)
- [Setting Up Ngrok for Webhook](#setting-up-ngrok-for-webhook)
- [Telegram Bot Usage](#telegram-bot-usage)
- [Running YOLOv5 Microservice](#running-yolov5-microservice)



## Implementation Guidelines - `polybot` Microservice

### Running the Telegram Bot Locally

The Telegram app, implemented in Flask, serves as a chat-based interface for users to interact with image object detection functionality.

#### Prerequisites
- Python environment
- Docker

#### Steps

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/ibraheemGanayim/DetectiveBot-YOLOv5-Telegram.git
   cd DetectiveBot-YOLOv5-Telegram
   ```

2. **Build and Run the Docker Containers:**
   ```bash
   docker-compose up --build
   ```

3. **Set Up Ngrok for Secure Tunneling:**
   - Sign up for Ngrok and install the Ngrok agent.
   - Authenticate Ngrok with your authtoken:
     ```bash
     ngrok config add-authtoken <your-authtoken>
     ```
   - Start Ngrok to expose the local server:
     ```bash
     ngrok http 8443
     ```
   - Obtain the Ngrok public URL (e.g., https://16ae-2a06-c701-4501-3a00-ecce-30e9-3e61-3069.ngrok-free.app).
   - Set the `TELEGRAM_APP_URL` environment variable to your Ngrok URL.

4. **Test the Echo Bot:**
   - The default behavior echoes incoming messages. Try it out!

5. **Extend with QuoteBot:**
   - Change the instantiated instance in `app.py`:
     ```diff
     - Bot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)
     + QuoteBot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)
     ```

### Extending with ObjectDetectionBot

The `ObjectDetectionBot` class in `bot.py` handles incoming messages for image object detection.

- Change the instantiated instance in `app.py`:
     ```diff
     - Bot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)
     + ObjectDetectionBot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)
     ```

- **Run the Object Detection Bot:**
  - Start Ngrok to expose the local server:
     ```bash
     ngrok http 8443
     ```
   - Start the other services:
     ```bash
     docker-compose up --build
     ```
   - Send an image to the bot and observe the results.

Feel free to customize and enhance the project based on your needs. Contributions are welcome!
