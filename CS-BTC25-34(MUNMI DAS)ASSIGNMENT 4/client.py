import socket
import threading

SERVER_IP = '10.0.0.1'  # Mininet topology single,4 ka server IP[span_0](start_span)[span_0](end_span)
PORT = 5000

def receive_messages(sock):
    while True:
        try:
            message = sock.recv(1024).decode('utf-8')
            if not message:
                break
            print(message)
        except:
            print("[*] Disconnected from server.")
            sock.close()
            break

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_IP, PORT))
    except Exception as e:
        print(f"[-] Connection Error: {e}")
        return

    username = input("Enter Username: ")
    client.sendall(username.encode('utf-8'))

    recv_thread = threading.Thread(target=receive_messages, args=(client,))
    recv_thread.daemon = True
    recv_thread.start()

    print("[*] Connected! Type your messages below:")
    while True:
        try:
            msg = input()
            if msg.lower() == 'exit':
                break
            client.sendall(msg.encode('utf-8'))
        except KeyboardInterrupt:
            break

    client.close()

if __name__ == "__main__":
    start_client()
