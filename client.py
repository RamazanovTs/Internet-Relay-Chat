import socket
import threading
import os 


def run_client():
    ip='your ip'
    port='your port'#without quotation marks
    global client
    client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((ip,port))
    global username
    username=input('Enter Username: ')
    client.send(username.encode('utf-8'))


def send_message():
    while True:
        request=input()
        request=client.send(request.encode('utf-8'))

def recieve_message():
    while True:
        request=client.recv(1024).decode('utf-8')
        print(request)


run_client()

receive_thread = threading.Thread(target=recieve_message)
receive_thread.start()
write_thread = threading.Thread(target=send_message)
write_thread.start()