import socket
import json
import signal
import sys
from concurrent.futures import ThreadPoolExecutor

# Task 4: Load Configuration
with open("config.json", "r") as f:
    config = json.load(f)

HOST = config["HOST"]
PORT = config["PORT"]
BUFFER_SIZE = config["BUFFER_SIZE"]
MAX_WORKERS = config["MAX_WORKERS"]
TIMEOUT = config["TIMEOUT"]

clients = {}
running = True

def broadcast(message, sender_socket=None):
    """Sends messages to all active clients except the sender."""
    for client_sock in list(clients.keys()):
        if client_sock != sender_socket:
            try:
                client_sock.sendall(message.encode('utf-8'))
            except Exception:
                remove_client(client_sock)

def remove_client(client_socket):
    """Task 1: Detects & removes inactive clients and releases resources."""
    if client_socket in clients:
        username = clients.pop(client_socket)
        client_socket.close()
        print(f"[DISCONNECT] {username} disconnected.")
        broadcast(f"System: {username} left the chat.")

def handle_client(client_socket, address):
    """Task 1 & 2: Handles communication, timeouts, and exceptions."""
    client_socket.settimeout(TIMEOUT)
    try:
        username = client_socket.recv(BUFFER_SIZE).decode('utf-8').strip()
        if not username:
            remove_client(client_socket)
            return
        clients[client_socket] = username
        print(f"[CONNECTED] {username} from {address}")
        broadcast(f"System: {username} joined the chat!", client_socket)

        while running:
            try:
                msg = client_socket.recv(BUFFER_SIZE).decode('utf-8')
                if not msg:
                    break
                broadcast(f"{username}: {msg}", client_socket)
            except socket.timeout:
                continue  # Keep connection alive during idle periods
            except (ConnectionResetError, BrokenPipeError):
                break
    except Exception as e:
        print(f"[ERROR] Error with client {address}: {e}")
    finally:
        remove_client(client_socket)

def graceful_shutdown(sig, frame):
    """Task 2: Graceful server shutdown."""
    global running
    print("\n[SHUTDOWN] Server shutting down gracefully...")
    running = False
    for client_sock in list(clients.keys()):
        try:
            client_sock.sendall("System: Server shutting down.".encode('utf-8'))
            client_sock.close()
        except Exception:
            pass
    sys.exit(0)

def start_server():
    signal.signal(signal.SIGINT, graceful_shutdown)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[STARTED] Server running on {HOST}:{PORT}")

    # Task 3: ThreadPoolExecutor for scalable concurrency
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        while running:
            try:
                server.settimeout(1.0)
                client_socket, address = server.accept()
                executor.submit(handle_client, client_socket, address)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[ERROR] Accept error: {e}")
                break

if __name__ == "__main__":
    start_server()
