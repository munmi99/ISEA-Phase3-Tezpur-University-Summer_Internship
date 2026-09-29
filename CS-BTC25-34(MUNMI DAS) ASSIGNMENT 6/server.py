import socket
import threading

HOST = '0.0.0.0'
PORT = 5000

clients = {}  # {client_socket: username}
client_addresses = {}

def broadcast(message, sender_socket=None):
    """Broadcast a message to all connected clients except the sender."""
    for client_socket in list(clients.keys()):
        if client_socket != sender_socket:
            try:
                client_socket.send(message.encode('utf-8'))
            except:
                remove_client(client_socket)

def send_user_list():
    """Send the updated list of online usernames to all clients."""
    user_list = ",".join(clients.values())
    message = f"USERLIST:{user_list}"
    for client_socket in list(clients.keys()):
        try:
            client_socket.send(message.encode('utf-8'))
        except:
            remove_client(client_socket)

def handle_client(client_socket, address):
    """Handle individual client connection, authentication, and messaging."""
    try:
        username = client_socket.recv(1024).decode('utf-8').strip()
        if not username or username in clients.values():
            client_socket.send("REJECT:Username taken or invalid".encode('utf-8'))
            client_socket.close()
            return
        
        client_socket.send("ACCEPT:Connected".encode('utf-8'))
        clients[client_socket] = username
        client_addresses[client_socket] = address
        print(f"[+] {username} connected from {address}")
        
        broadcast(f"[SERVER]: {username} has joined the chat.")
        send_user_list()

        while True:
            try:
                message = client_socket.recv(4096).decode('utf-8')
                if not message:
                    break
                
                # Check for private message format: @username message
                if message.startswith('@'):
                    parts = message.split(' ', 1)
                    if len(parts) == 2:
                        target_user = parts[0][1:]
                        pm_content = parts[1]
                        sent_flag = False
                        for sock, user in clients.items():
                            if user == target_user:
                                sock.send(f"[PM from {username}]: {pm_content}".encode('utf-8'))
                                client_socket.send(f"[PM to {target_user}]: {pm_content}".encode('utf-8'))
                                sent_flag = True
                                break
                        if not sent_flag:
                            client_socket.send(f"[SERVER]: User {target_user} not found.".encode('utf-8'))
                    else:
                        client_socket.send("[SERVER]: Invalid private message format. Use @username message".encode('utf-8'))
                else:
                    broadcast(f"{username}: {message}", client_socket)
            except ConnectionResetError:
                break
    except Exception as e:
        print(f"Error handling client {address}: {e}")
    finally:
        remove_client(client_socket)

def remove_client(client_socket):
    """Remove disconnected client and cleanup resources."""
    if client_socket in clients:
        username = clients[client_socket]
        print(f"[-] {username} disconnected.")
        del clients[client_socket]
        if client_socket in client_addresses:
            del client_addresses[client_socket]
        try:
            client_socket.close()
        except:
            pass
        broadcast(f"[SERVER]: {username} has left the chat.")
        send_user_list()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[*] Chat Server started on port {PORT}...")

    while True:
        client_socket, address = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, address))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    start_server()
