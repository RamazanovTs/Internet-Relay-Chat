import socket
import threading


clients=[]
users={}

def run_server():
    ip=''
    port='your port'#without quotation marks
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((ip,port))
    server.listen(0)
    print(f'Listening to {ip}:{port}')

    while True:
        client_socket,addr=server.accept()
        print(f"Accepted connection from {addr[0]}:{addr[1]}")

        thread=threading.Thread(target=handle_client,args=(client_socket,addr))
        thread.start()


def handle_client(client_socket,addr):
    username=client_socket.recv(1024).decode('utf-8')
    clients.append(client_socket)
    users[client_socket]=username
    broadcast(f'{username} joined chat',client_socket)
    try:
        while True:
            request=client_socket.recv(1024).decode('utf-8')

            if request.lower()=='close':
                client_socket.send('closed'.encode('utf-8'))
                break
            print(f'{username}: {request}')
            broadcast(f'{username}: {request}',client_socket)




    except Exception as e:
        print(f'Error {e}')
    finally:
        clients.remove(client_socket)
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
run_server()