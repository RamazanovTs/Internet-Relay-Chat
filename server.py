import socket
import threading
import time

clients = []
users = {}
sockets = {}
lock = threading.Lock() 

def run_server():
    ip = 'ip'
    port = 'port'
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen(5) 
    print(f'Listening to {ip}:{port}')

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr[0]}:{addr[1]}")

        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

def handle_client(client_socket, addr):
    try:
        username = client_socket.recv(1024).decode('utf-8')
        if not username:
            raise ValueError("No username received")


        with lock:
            clients.append(client_socket)
            users[client_socket] = username
            sockets[username] = client_socket

        broadcast(f'{username} joined the chat', client_socket)

        user_thread = threading.Thread(target=send_users, args=(client_socket,))
        user_thread.start()


        while True:
            request = client_socket.recv(1024).decode('utf-8')
            if not request:
                break
            elif request.lower() == 'close':
                client_socket.send('closed'.encode('utf-8'))
                broadcast(f'{username} has disconnected', client_socket)
                break
            elif request.startswith('$Priv'):
                parts = request.split(' ', 2)
                if len(parts) < 3:
                    continue
                target_user = parts[1].strip()
                message = parts[2].strip()
                send_private_message(f'[PRIV]{username}: {message}', target_user)
            elif request == 'usercheck':
                pass
            else:
                print(f'{username}: {request}')
                broadcast(f'{username}: {request}', client_socket)

    except ValueError as e:
        print(f'Error: {e}')
    except socket.error as e:
        print(f'Socket error: {e}')
    finally:
        with lock:
            if client_socket in clients:
                clients.remove(client_socket)
            if client_socket in users:
                del users[client_socket]
            username = users.get(client_socket)
            if username in sockets:
                del sockets[username]
        client_socket.close()

def broadcast(message, client_socket):
    with lock:
        for client in clients:
            if client != client_socket:
                try:
                    client.send(message.encode('utf-8'))
                except socket.error:
                    # Handle broken connection
                    with lock:
                        broadcast(f'{users[client]} left', client)
                        clients.remove(client)
                        del users[client]
                        del sockets[users[client]]

def send_private_message(message, target_user):
    if target_user in sockets:
        try:
            sockets[target_user].send(message.encode('utf-8'))
        except socket.error:

            client_socket = sockets.pop(target_user, None)
            if client_socket:
                with lock:
                    clients.remove(client_socket)
                    del users[client_socket]
                client_socket.close()

def send_users(client_socket):
    try:
        while True:
            with lock:
                userlist = [user for user in users.values()]
            client_socket.send(f'ul {userlist}'.encode('utf-8'))
            time.sleep(5)
    except socket.error:
        print("Error sending user list")
    finally:
        with lock:
            if client_socket in clients:
                clients.remove(client_socket)
            if client_socket in users:
                del users[client_socket]
        client_socket.close()

if __name__ == "__main__":
    run_server()
