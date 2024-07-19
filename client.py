import socket
import threading
import os 


def run_client():
    ip = 'your_ip'
    port = 'your_port'  # without quotation marks
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((ip, port))
    except Exception as e:
        print(f"Unable to connect to the server: {e}")
        return

    global username
    username = input('Enter Username: ')
    client.send(username.encode('utf-8'))

    receive_thread = threading.Thread(target=receive_message)
    receive_thread.start()
    send_thread = threading.Thread(target=send_message)
    send_thread.start()

def send_message():
    while True:
        try:
            message = input()
            client.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")
            break

def receive_message():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message:
                print(message)
            else:
                break
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

run_client()