import socket
import threading
import csv
import os
from datetime import datetime

# Server configuration
HOST = '0.0.0.0'
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()

clients = {}  # Format: {username: {'socket': client_socket, 'addr': client_addr, 'login_time': time}}
chat_history_file = 'chat_history.csv'

# Initialize CSV file if not exists
if not os.path.exists(chat_history_file):
    with open(chat_history_file, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'sender', 'receiver', 'message_type', 'message'])

def log_message(sender, receiver, msg_type, message):
    with open(chat_history_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), sender, receiver, msg_type, message])

def get_last_five_messages(username):
    if not os.path.exists(chat_history_file):
        return []
    messages = []
    with open(chat_history_file, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['sender'] == username or row['receiver'] == username or row['receiver'] == 'ALL':
                messages.append(f"[{row['timestamp']}] {row['sender']}: {row['message']}")
    return messages[-5:]

def broadcast(message, sender_username):
    for user, info in clients.items():
        if user != sender_username:
            try:
                info['socket'].send(message.encode('utf-8'))
            except:
                info['socket'].close()

def handle_client(client_socket, client_addr):
    username = None
    try:
        # Receive username
        username = client_socket.recv(1024).decode('utf-8').strip()
        login_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        clients[username] = {
            'socket': client_socket,
            'addr': client_addr,
            'login_time': login_time
        }
        
        print(f"[NEW CONNECTION] {username} connected from {client_addr}")
        
        # Send last 5 messages for persistent chat history
        last_msgs = get_last_five_messages(username)
        if last_msgs:
            client_socket.send("\n--- Last 5 Messages ---\n".encode('utf-8'))
            for m in last_msgs:
                client_socket.send((m + "\n").encode('utf-8'))
            client_socket.send("-----------------------\n".encode('utf-8'))

        broadcast(f"\n[SERVER] {username} has joined the chat.\n", username)

        while True:
            msg = client_socket.recv(1024).decode('utf-8')
            if not msg:
                break
            
            msg = msg.strip()

            # Task 3: Online User List Command (/list)
            if msg == '/list':
                user_list = ", ".join(clients.keys())
                client_socket.send(f"[SERVER] Online Users: {user_list}\n".encode('utf-8'))

            # Task 2: Private Messaging Command (/msg <username> <message>)
            elif msg.startswith('/msg '):
                parts = msg.split(' ', 2)
                if len(parts) >= 3:
                    target_user = parts[1]
                    private_msg = parts[2]
                    if target_user in clients:
                        clients[target_user]['socket'].send(f"[PRIVATE from {username}]: {private_msg}\n".encode('utf-8'))
                        log_message(username, target_user, 'PRIVATE', private_msg)
                    else:
                        client_socket.send(f"[SERVER error] User '{target_user}' does not exist.\n".encode('utf-8'))
                else:
                    client_socket.send(f"[SERVER error] Invalid format. Use /msg <username> <message>\n".encode('utf-8'))

            # Broadcast Message
            else:
                broadcast(f"{username}: {msg}\n", username)
                log_message(username, 'ALL', 'BROADCAST', msg)

    except Exception as e:
        print(f"[ERROR] {e}")
    
    finally:
        if username and username in clients:
            del clients[username]
            print(f"[DISCONNECT] {username} disconnected.")
            broadcast(f"\n[SERVER] {username} has left the chat.\n", username)
        client_socket.close()

def receive():
    print(f"[SERVER STARTED] Server is listening on port {PORT}")
    while True:
        client_socket, client_addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, client_addr))
        thread.start()

if __name__ == "__main__":
    receive()
