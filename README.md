# Video Streaming and Chat Application

## Video Demo:
[Watch Video Demo](https://drive.google.com/file/d/1LJyAnAMeViFKOv6X28HwfbGm1GV8eLmq/view?usp=sharing)

## Overview:

This repository contains code for a video streaming and chat application implemented using Python sockets. The application allows clients to connect to a server, stream videos, and communicate with each other via encrypted messages.

## Dependencies:

- Python 3.x
- OpenCV (`pip install opencv-python`)
- imutils (`pip install imutils`)
- Crypto (`pip install pycryptodome`)

## Instructions:

### Server Setup:
1. Run the `server.py` file.
2. The server will start listening for incoming connections on port 12345.

### Client Setup:
1. Run the `client.py` file.
2. Enter your name when prompted.
3. If the entered name already exists on the server, you'll need to choose a different name.
4. The client will connect to the server and start the interaction loop.

### Client Operations:
- **Quit:** To quit the application, type 'yes' when prompted. To continue interacting, type 'no' and choose between listing videos or initiating a chat.
- **List Videos:** Type 'List' to get a list of available videos stored in the server's video directory.
- **Play Video:** After listing the available videos, type the name of the video you want to play (e.g., `video` or `v2`).
- **Chat:** Type 'Chat' to initiate communication with other connected clients. Enter the recipient's name and your message.

## Notes:
- Videos to be streamed should be stored in the `video/` directory on the server.
- For eg : video/
-               -video1_240p.mp4
-               -video1_720p.mp4
-               -video1_1440p.mp4
- The chat messages are encrypted using RSA encryption for secure communication.
- The video streaming utilizes OpenCV to read and stream video frames efficiently.

