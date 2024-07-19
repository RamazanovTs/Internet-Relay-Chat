import socket
import threading
import time

clients=[]
users={}

def run_server():
    ip='ip'
    port='port' #without quotation marks
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((ip,port))
    server.listen(0)
    print(f'Listening to {ip}:{port}')

    while True:
        client_socket,addr=server.accept()
        print(f"Accepted connection from {addr[0]}:{addr[1]}")

        thread=threading.Thread(target=handle_client,args=(client_socket,addr))
        thread.start()

        users_thread=threading.Thread(target=send_users,args=(client_socket,users))
        users_thread.start()


def handle_client(client_socket, addr):

    try:
        # Attempt to receive the username
        username = client_socket.recv(1024).decode('utf-8')
        
        if not username:  # Check if the username is empty
            raise ValueError("No username received")

        # Add the client to the lists and broadcast their arrival
        clients.append(client_socket)
        users[client_socket] = username
        broadcast(f'{username} joined the chat', client_socket)

        # Start receiving messages
        while True:
            request = client_socket.recv(1024).decode('utf-8')
            if not request:  # Check if the request is empty (disconnection)
                break
            if request.lower() == 'close':
                client_socket.send('closed'.encode('utf-8'))
                broadcast(f'{username} has disconnected',client_socket)
                break
            if request=='usercheck':
                pass
            else:
                print(f'{username}: {request}')
                broadcast(f'{username}: {request}', client_socket)

    except (ValueError, Exception) as e:
        # If an exception occurs, remove the client and close the connection
        print(f'Error: {e}')
        if client_socket in clients:
            clients.remove(client_socket)
        if client_socket in users:
            del users[client_socket]
        client_socket.close()
    finally:
        if client_socket in clients:
            clients.remove(client_socket)
        if client_socket in users:
            del users[client_socket]
        client_socket.close()


def broadcast(message,client_socket):
    for client in clients:
        if client!=client_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                broadcast(f'{users[client]} left',client)
                clients.remove(client)
                del users[client]

def send_users(client_socket,users):
        try:
            while True:
                userlist=[user for user in users.values()]
                client_socket.send(f'ul {userlist}'.encode('utf-8'))
                time.sleep(5)
        except Exception as e:
            print(e)


run_server()