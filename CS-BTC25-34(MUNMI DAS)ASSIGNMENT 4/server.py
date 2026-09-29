import socket
import threading
from datetime import datetime

HOST = '0.0.0.0'
PORT = 5000

clients = {}
clients_lock = threading.Lock()
chat_log_lock = threading.Lock()

def log_server_event(event, username, client_ip):
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"{timestamp},{event},{username},{client_ip}\n"
    print(log_entry.strip())

def log_chat_message(username, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    with chat_log_lock:
        with open("chat_log.txt", "a") as f:
            f.write(f"{timestamp},{username},{message}\n")

def broadcast(message, sender_socket=None):
    with clients_lock:
        for client_sock in clients:
            if client_sock != sender_socket:
                try:
                    client_sock.sendall(message.encode('utf-8'))
                except:
                    pass

def handle_client(client_socket, address):
    client_ip = address[0]
    username = "UNKNOWN"
    try:
        username = client_socket.recv(1024).decode('utf-8').strip()
        with clients_lock:
            clients[client_socket] = username
        
        log_server_event("CONNECTED", username, client_ip)
        join_msg = f"[Server] {username} has joined the chat."
        broadcast(join_msg, client_socket)

        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            log_chat_message(username, message)
            formatted_msg = f"[{username}] {message}"
            broadcast(formatted_msg, client_socket)
    except:
        pass
    finally:
        with clients_lock:
            if client_socket in clients:
                del clients[client_socket]
        client_socket.close()
        log_server_event("DISCONNECTED", username, client_ip)
        leave_msg = f"[Server] {username} has left the chat."
        broadcast(leave_msg)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[*] Chat Server started on port {PORT}")

    while True:
        client_sock, address = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_sock, address))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    start_server()

