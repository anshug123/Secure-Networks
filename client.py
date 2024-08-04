import socket
import pickle
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import threading
import json
import time
import base64
import cv2,struct


client_public_keys={}
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 12345)
client_socket.connect(server_address)

client_name = input("Enter your name: ")

key = RSA.generate(2048)
public_key=key.publickey()
private_key=key

client_socket.send(client_name.encode())

isConnedted = True

receive1=client_socket.recv(4096).decode() 
if receive1.startswith("ERROR:"):
    isConnedted =  False
    print(receive1)
    client_socket.close()
# else:
#     print("")
    
if isConnedted:                
    client_socket.send(public_key.exportKey().decode().encode())


k=[]

def encrypt(pkey,message):
        r=RSA.import_key(pkey)
        cipher=PKCS1_OAEP.new(r)
        en_m=cipher.encrypt(message.encode())
        return en_m
    
    
def receive_messages(client_socket,receive):
    data=json.loads(receive)
    encoded=data["en"]
    if (not encoded):
        if "type" in data and "info" in data:
            broadcast_info=data["type"]
            client=data["info"]
            if broadcast_info=="Bcast":
                clients_info=client
                
                for name, public_key in clients_info.items():
                    client_public_keys[name]=public_key.strip()
                r = set(client_public_keys) - set(clients_info)
                for n in r:
                    del client_public_keys[n] 

def h(client_socket,receive,private_key):
    j_data=json.loads(receive)
    en=j_data["en"]
    if (en):
        m=j_data["en_m"]
        decrypted_message=""
        try:
            cipher=PKCS1_OAEP.new(private_key)
            decrypted_message=cipher.decrypt(base64.b64decode(m))
        except Exception as e:
            pass
        if decrypted_message:
            print("Received Message:",decrypted_message.decode())
        else:
            print("")
        
def l(client_socket,receive):
    global k
    data=json.loads(receive)
    encoded=data["en"]
    if (not encoded):
        if "type" in data and "info" in data:
            broadcast_info=data["type"]
            client=data["info"]
            if broadcast_info=="vid":
                list=client
                k=list
                print("Available videos:")
                for video in list:
                    print(video)  
                    
def recv_data(socket, size):
    """Receive data from socket until the given size."""
    received_data = b""
    while len(received_data) < size:
        chunk = socket.recv(min(size - len(received_data), 1024))
        if not chunk:
            return None
        received_data += chunk
    return received_data

def playing_video(client_socket):
    payload_size = struct.calcsize("Q")
    received_data = b""
    
    try:
        while True:
            # Receiving the payload size
            received_data += recv_data(client_socket, payload_size)
            packed_msg_size = received_data[:payload_size]
            received_data = received_data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]
            
            # Receiving the frame data
            received_data += recv_data(client_socket, msg_size)
            frame_data = received_data[:msg_size]
            received_data = received_data[msg_size:]
            
            # Check for termination signal
            if frame_data == b'done':
                break
            
            # Display the frame
            frame = pickle.loads(frame_data)
            cv2.imshow('client', frame)
            key = cv2.waitKey(1)

    except Exception as e:
        pass
    finally:
        cv2.destroyAllWindows()

def play(client_socket,receive):
    data=json.loads(receive)
    encoded=data["en"]
    if (not encoded):
        if "type" in data and "info" in data:
            broadcast_info=data["type"]
            client=data["info"]
            if broadcast_info=="play":
                print(client)
                playing_video(client_socket)
    
def m(client_socket):    
    while True:
        try:
            receive=client_socket.recv(4096).decode() 
            if not receive:
                break           
            receive_messages(client_socket,receive)
            h(client_socket,receive,private_key)
            l(client_socket,receive)
            play(client_socket,receive)
            
        except Exception as e:
            print("Client is disconnected form server.")
            break
  
if isConnedted:  
        
    th=threading.Thread(target=m,args=(client_socket,)) 
    th.start()


    while True: 
        try:
                quit_response = input("Do you want to quit? (yes/no): ")
                client_socket.sendall(quit_response.encode())


                if quit_response.lower() == "yes":
                    break
                elif quit_response.lower() == "no":
                    i=input("Type 'List' to get list of available videos/ Type 'Chat' to start communication with other clients: ")
                    client_socket.sendall(i.encode())
                    
                    if i=="List":
                        time.sleep(2)
                        while True:
                            m=input("Enter name of video you want to play (eg. video1, video2): ")
                            if m+"_720p.mp4" not in k:
                                print("Video does not exists. or You gave a name in wrong format.") 
                            else:
                                client_socket.send(f"Play {m}".encode())
                                break 
                            
                        
                    elif i=="Chat":
                        name = input('Enter recipient\'s name: ')
                        try:
                            if name in client_public_keys:
                                message=input('Enter your message:')
                                pkey=client_public_keys[name]
                                i=encrypt(pkey,message)
                                e_m=base64.b64encode(i).decode()
                                json_data={
                                    "en":True,
                                    "en_m": e_m
                                }
                                j_s=json.dumps(json_data)
                                client_socket.sendall(j_s.encode())
                            else :
                                print("Recepient not in the list.")
                                json_data={
                                    "en":False,
                                    "en_m": ""
                                }
                                j_s=json.dumps(json_data)
                            client_socket.sendall(j_s.encode())
                        except:
                            print("ERROR. May the receipent left server.")
                    else:
                        print("Invalid response. Please enter 'List' or 'Chat'.")
                else:
                    print("Invalid response. Please enter 'yes' or 'no'.")

        except:
            break