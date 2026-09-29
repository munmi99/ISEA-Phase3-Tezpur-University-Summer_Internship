import socket
import threading
import sys

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(message, end="")
        except:
            print("\n[DISCONNECTED] Connection lost from server.")
            client_socket.close()
            sys.exit()

def start_client():
    # Server IP for Mininet (h1 ka IP usually 10.0.0.1 hota hai topology single,5 me)
    SERVER_IP = '10.0.0.1' 
    PORT = 5000

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_IP, PORT))
    except Exception as e:
        print(f"Could not connect to server: {e}")
        return

    username = input("Enter your username: ")
    client.send(username.encode('utf-8'))

    # Start thread to receive messages from server
    thread = threading.Thread(target=receive_messages, args=(client,))
    thread.daemon = True
    thread.start()

    print("\n--- Connected to Chat Room ---")
    print("Commands:")
    print("  /list                    -> View online users")
    print("  /msg <username> <msg>    -> Send private message")
    print("  Type normally            -> Broadcast message to everyone\n")

    while True:
        try:
            message = input()
            if message.lower() == 'exit':
                break
            client.send(message.encode('utf-8'))
        except:
            break

    client.close()

if __name__ == "__main__":
    start_client()
