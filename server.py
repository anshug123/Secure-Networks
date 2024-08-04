import socket
import pickle
from Crypto.PublicKey import RSA
import sys
import threading
import json
import os
import cv2
import imutils 
import socket,cv2, pickle,struct

client_sockets=[]
client_public_keys = {}

VIDEO_DIRECTORY = "video/"

import os
from pathlib import Path

def list_videos_in_folder(folder_path):
    video=[]
    videos=os.listdir(VIDEO_DIRECTORY)
    for f in videos:
        if f.endswith(".mp4"):
            video.append(f)
    return video
        


def broadcast():
    c=client_public_keys
    final_info={
        "en":False,
        "type":"Bcast",
        "info": c
    }
    for client_socket in client_sockets:
        client_socket.sendall(json.dumps(final_info).encode())
        

def send_vid(conn, video_name):
    resolutions = ["240p", "720p", "1440p"]
    video_names = [f'{video_name}_{res}.mp4' for res in resolutions]
    video_paths = [os.path.join(VIDEO_DIRECTORY, name) for name in video_names]

    # Open video files and get total frame counts
    caps = [cv2.VideoCapture(path) for path in video_paths]

    total_frames = int(caps[0].get(cv2.CAP_PROP_FRAME_COUNT))
    frame_size = total_frames // len(resolutions)

    # Set starting frame positions for higher resolution videos
    for i in range(1, len(caps)):
        start_frame = frame_size * i
        caps[i].set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    # Send frames from each video
    for cap in caps:
        for _ in range(frame_size):
            ret, frame = cap.read()
            if not ret:
                break
            frame = imutils.resize(frame, width=720)
            frame_data = pickle.dumps(frame)
            message = struct.pack("Q", len(frame_data)) + frame_data
            conn.sendall(message)

    # Send a message to indicate end of video
    conn.sendall(struct.pack("Q", len(b'done')) + b'done')

    # Release video resources
    for cap in caps:
        cap.release()
        
def handle_client(client_socket,client_name):
    while True:
        quit_message = client_socket.recv(1024).decode()
        if quit_message.lower() == "yes":
            del client_public_keys[client_name]
            client_sockets.remove(client_socket)
            print(f"Client {client_name} disconnected.")
            broadcast()
            client_socket.close()
            break
        
        elif quit_message.lower() == "no":
            m=client_socket.recv(1024).decode()
            if m=="List":
                video_list=list_videos_in_folder(VIDEO_DIRECTORY)
                # print(video_list)
                final_info={
                    "en":False,
                    "type":"vid",
                    "info": video_list
                    }
                client_socket.sendall(json.dumps(final_info).encode())
                l=client_socket.recv(1024).decode()
                if l.startswith("Play "):
                    o = l[5:]  # Extract everything after "Play "
                    # print("Received message:", m)
                v_info={
                    "en":False,
                    "type":"play",
                    "info": f"Playing {o} video in different resolutions."
                    } 
                client_socket.sendall(json.dumps(v_info).encode())
                r=o
                # k=r.replace('.mp4', '')
                send_vid(client_socket,o)
                # print(l)
                
            elif m=="Chat":
                    d=client_socket.recv(1024)
                    data=d.decode()
                    json_data=json.loads(data)
                    encoded_message=json_data["en"]
                    if (encoded_message):
                        for  cl in client_sockets:
                            cl.sendall(d)
            else:
                continue
        else:
            continue
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 12345)
server_socket.bind(server_address)
server_socket.listen(5)
print("Server is listening for incoming connections...")

while True:
    try:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}.")
        client_sockets.append(client_socket)
        client_name = client_socket.recv(1024).decode()
        if client_name not in client_public_keys.keys():
            client_socket.send("Success".encode())
            print(f"Client {client_name} connected.")

            public_key = client_socket.recv(1024).decode()

            client_public_keys[client_name] = public_key
            broadcast()
            th=threading.Thread(target=handle_client,args=(client_socket,client_name,))
            th.start()
        else:
            # client_sockets.remove(client_socket)
            # c=client_public_keys
            # for client_socket in client_sockets:
            client_socket.sendall("ERROR: username already exists".encode())
            client_sockets.remove(client_socket)
            # client_socket.close()
            print(f"{client_address} disconnected. Client with this name already exists.")
            
            
    except Exception as e:
        print("No any client is connected to server.")