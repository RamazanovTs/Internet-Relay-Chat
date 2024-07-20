import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
import time
import customtkinter


def run_client():
    global client, username, userlist, Color, Connection_info
    try:
        ip = ip_entry.get()  # Use the IP address from the entry
        port = int(port_entry.get())
        if not ip or not port:
            raise ValueError("IP and Port number cannot be empty")

        username = name_entry.get()
        if not username:
            raise ValueError("Username cannot be empty")

        if check_connection():
            show_alert('You are already connected to the server', 'red')
        else:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((ip, port))
            show_alert(f'Successfully Connected to {ip}:{port}', 'green')
            client.send(username.encode('utf-8'))
            update_connection_info('Online', 'green')
            threading.Thread(target=receive_message, daemon=True).start()
            threading.Thread(target=update_users, daemon=True).start()

    except ValueError as ve:
        messagebox.showwarning("Input Error", str(ve))
    except socket.error as se:
        messagebox.showerror("Connection Error", f"Socket error: {se}")
    except Exception as e:
        messagebox.showerror("Connection Error", f"Unable to connect to the server: {e}")


def send_message():
    if check_connection():
        message = message_entry.get()
        message_entry.delete(0, tk.END)
        if message:
            try:
                if message.lower().startswith('/msg'):
                    parts = message.split(' ', 2)
                    if len(parts) >= 3:
                        target_user = parts[1]
                        private_message = parts[2]
                        client.send(f'$Priv {target_user} {private_message}'.encode('utf-8'))
                        update_chat_display(f'[PRIV]{username} --> {target_user}: {private_message}\n')
                    else:
                        show_alert('Incorrect private message format. Use /msg [user] [message]', 'red')
                else:
                    client.send(message.encode('utf-8'))
                    if message.lower() == 'exit':
                        client.close()
                        root.quit()
                    update_chat_display(f'{username}: {message}\n')
            except Exception as e:
                update_chat_display(f"Error sending message: {e}\n")
    else:
        show_alert('You are not connected to the server', 'red')


def receive_message():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message:
                if message.startswith('ul'):
                    global userlist
                    userlist = eval(message[2:])
                    root.after(0, update_online_users)
                    root.after(0, update_users_online_number)
                else:
                    root.after(0, lambda: update_chat_display(f"{message}\n"))
            else:
                break
        except Exception as e:
            print(f"Error receiving message: {e}")
            break


def update_users():
    while True:
        if check_connection():
            root.after(0, update_online_users)
        time.sleep(5)


def update_chat_display(message):
    chat_display.config(state='normal')
    chat_display.insert(tk.END, message)
    chat_display.config(state='disabled')
    chat_display.yview(tk.END)


def update_online_users():
    online_users.config(state='normal')
    online_users.delete('1.0', tk.END)
    if check_connection() and userlist:
        for user in userlist:
            online_users.insert(tk.END, f"{user}\n")
    online_users.config(state='disabled')
    online_users.yview(tk.END)


def show_alert(message, color):
    alert_label = tk.Label(root, text=message, fg=color, font=('Helvetica', 12, 'bold'))
    alert_label.grid(row=2, column=0, columnspan=2)
    root.after(3000, alert_label.destroy)


def check_connection():
    try:
        client.send('usercheck'.encode('utf-8'))
        return True
    except:
        return False


def disconnect():
    if check_connection():
        client.send('close'.encode('utf-8'))
        client.close()
        show_alert('Successfully Disconnected', 'red')
        update_connection_info('Offline', 'red')
        update_online_users()
        chat_display.config(state='normal')
        chat_display.delete('1.0', tk.END)
        chat_display.config(state='disabled')
        chat_display.yview(tk.END)
        Users_Online.configure(text=f'Users: {0}')
    else:
        show_alert('You are not connected to the server', 'red')


def update_connection_info(status, color):
    Color.set(color)
    Connection_info.configure(text=status, text_color=Color.get())


def update_users_online_number():
    if userlist:
        Users_Online.configure(text=f'Users: {len(userlist)}')
    else:
        Users_Online.configure(text=f'Users: {0}')


root = customtkinter.CTk()
root.title('IRC Client')
root.geometry('1100x550')
root.minsize(height=550, width=1100)
root.maxsize(height=550, width=1100)

chat_display = scrolledtext.ScrolledText(root, state='disabled', wrap='word')
chat_display.grid(row=0, column=1, columnspan=2, padx=10, pady=10)

online_users = scrolledtext.ScrolledText(root, state='disabled', wrap='word', width=20)
online_users.grid(row=0, column=3, columnspan=1, padx=2, pady=2)

message_entry = customtkinter.CTkEntry(root, width=500)
message_entry.grid(row=1, column=1, padx=10, pady=10)

send_button = customtkinter.CTkButton(root, text="Send", command=send_message)
send_button.grid(row=1, column=2, padx=10, pady=10)

frame_join = customtkinter.CTkFrame(root)
frame_join.grid(row=0, column=0, padx=10, pady=2)

frame_info = customtkinter.CTkFrame(root)
frame_info.grid(row=1, column=3, padx=10, pady=10)

Color = customtkinter.StringVar()
Color.set('red')

Connection_info = customtkinter.CTkLabel(frame_info, text='Offline', text_color=Color.get(), font=('Helvetica', 18, 'bold'))
Connection_info.pack(pady=5)

Users_Online = customtkinter.CTkLabel(frame_info, text=f'Users: {0}', font=('Helvetica', 18, 'bold'))
Users_Online.pack(pady=5, padx=75)

name_label = customtkinter.CTkLabel(frame_join, text='Username')
name_label.grid(row=0, column=0, padx=5, pady=5)

name_entry = customtkinter.CTkEntry(frame_join, width=150)
name_entry.grid(row=1, column=0, padx=5, pady=5)

ip_label = customtkinter.CTkLabel(frame_join, text='IP')
ip_label.grid(row=2, column=0, padx=5, pady=5)

ip_entry = customtkinter.CTkEntry(frame_join, width=150)
ip_entry.grid(row=3, column=0, padx=5, pady=5)

port_label = customtkinter.CTkLabel(frame_join, text='Port')
port_label.grid(row=4, column=0, padx=5, pady=5)

port_entry = customtkinter.CTkEntry(frame_join, width=150)
port_entry.grid(row=5, column=0, padx=5, pady=5)

connect_button = customtkinter.CTkButton(frame_join, text='Connect', command=run_client)
connect_button.grid(row=6, column=0, padx=5, pady=5)

disconnect_button = customtkinter.CTkButton(frame_join, text='Disconnect', command=disconnect)
disconnect_button.grid(row=7, column=0, padx=5, pady=5)

root.mainloop()
