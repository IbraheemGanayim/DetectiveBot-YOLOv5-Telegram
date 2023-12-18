# DetectiveBot - YOLOv5 Telegram Bot

![DetectiveBot Logo](path/to/your/logo.png)

DetectiveBot is a Telegram bot powered by YOLOv5, a state-of-the-art object detection AI model. It provides users with the ability to detect objects in images and respond with the detected objects.

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
- [Contributing](#contributing)
- [License](#license)

## Introduction

DetectiveBot is a Telegram bot designed for image object detection using YOLOv5. It is integrated with a YOLOv5 microservice that performs real-time object detection on images sent by users.

## Features

- Real-time object detection in images.
- Integration with Telegram Bot API for seamless user interaction.
- YOLOv5 microservice for accurate object detection.

## Implementation Guidelines

### 1. Running the Telegram Bot Locally

- Clone this repository to your local machine.
- Install the required dependencies by running:

  ```bash
  pip install -r requirements.txt
Set up your Telegram Bot API token and Ngrok URL by creating a .env_poly file. Example:

env
Copy code
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_APP_URL=your_ngrok_url
Run the Telegram bot:

bash
Copy code
python polybot/app.py
2. Running the YOLOv5 Microservice
Clone the YOLOv5 repository to your local machine.

Build the YOLOv5 Docker image:

bash
Copy code
docker build -t yolo5-app -f docker_project/yolo5/Dockerfile .
Run the YOLOv5 Docker container:

bash
Copy code
docker run -d -p 8081:8081 yolo5-app
For more detailed instructions, refer to the Implementation Guidelines section in the project overview.

Getting Started
Prerequisites
Python 3.x
Docker
Ngrok
Telegram Bot API Token
Installation
Clone the DetectiveBot repository:

bash
Copy code
git clone https://github.com/IbraheemGanayim/DetectiveBot-YOLOv5-Telegram.git
Install the required Python dependencies:

bash
Copy code
pip install -r requirements.txt
Set up the .env_poly file with your Telegram Bot API token and Ngrok URL:

env
Copy code
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_APP_URL=your_ngrok_url
Build and run the YOLOv5 Docker container:

bash
Copy code
cd docker_project/yolo5
docker build -t yolo5-app -f Dockerfile .
docker run -d -p 8081:8081 yolo5-app
Run the DetectiveBot Telegram bot:

bash
Copy code
cd ../..
python polybot/app.py
Running the Bot Locally
Make sure the YOLOv5 microservice is running.

Run the DetectiveBot Telegram bot:

bash
Copy code
python polybot/app.py
Setting Up Ngrok for Webhook
Download and install Ngrok.

Authenticate your Ngrok agent:

bash
Copy code
ngrok auth your-ngrok-authtoken
Start Ngrok to expose your local server:

bash
Copy code
ngrok http 8443
Set the TELEGRAM_APP_URL in the .env_poly file to the Ngrok forwarding URL.

Telegram Bot Usage
Start a chat with the Telegram bot.

Send an image to the bot.

Receive real-time object detection results.

Running YOLOv5 Microservice
Ensure the YOLOv5 microservice is running:

bash
Copy code
docker run -d -p 8081:8081 yolo5-app
Contributing
We welcome contributions! If you find any issues or have improvements to suggest, please open an issue or create a pull request.