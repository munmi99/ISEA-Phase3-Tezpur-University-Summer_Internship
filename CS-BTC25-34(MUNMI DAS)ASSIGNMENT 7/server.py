import socket
import threading
import hashlib
import json
import time
import os

HOST = '0.0.0.0'
PORT = 5000
MAX_MSG_LEN = 512
SESSION_TIMEOUT = 60  # seconds

# Global Data Structures
active_sessions = {}      # username -> socket
failed_attempts = {}      # username -> {'count': int, 'lockout_until': float}
lock = threading.Lock()

def log_event(event_text):
    """Secure Logging: Never log passwords."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {event_text}\n"
    with open("security_log.txt", "a") as f:
        f.write(log_entry)
    print(log_entry.strip())

def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return {}

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def handle_client(conn, addr):
    log_event(f"Connection established with {addr}")
    authenticated_user = None
    last_activity = time.time()

    try:
        while True:
            conn.settimeout(10.0) # Periodically check session activity
            try:
                data = conn.recv(1024).decode('utf-8')
            except socket.timeout:
                if authenticated_user and (time.time() - last_activity > SESSION_TIMEOUT):
                    conn.sendall(b"ERROR: Inactivity timeout. Logged out.\n")
                    log_event(f"User {authenticated_user} timed out due to inactivity.")
                    break
                continue

            if not data:
                break

            last_activity = time.time()

            # Task 4: Input Validation (Oversized messages)
            if len(data) > MAX_MSG_LEN:
                conn.sendall(b"ERROR: Message exceeds maximum allowed size (512 bytes).\n")
                continue

            lines = data.strip().split('\n')
            for line in lines:
                parts = line.split(' ', 2)
                cmd = parts[0].upper()

                if cmd == "LOGIN":
                    if len(parts) < 3:
                        conn.sendall(b"ERROR: Invalid username/password format.\n")
                        continue
                    
                    username, password = parts[1], parts[2]

                    # Input Validation
                    if not username or not password or not username.isalnum():
                        conn.sendall(b"ERROR: Invalid username format.\n")
                        continue

                    users = load_users()
                    hashed_pw = hash_password(password)

                    with lock:
                        # Task 5: Failed Login Protection / Lockout
                        user_attempts = failed_attempts.get(username, {'count': 0, 'lockout_until': 0})
                        if time.time() < user_attempts['lockout_until']:
                            conn.sendall(b"ERROR: Account locked due to multiple failed attempts. Try again later.\n")
                            log_event(f"Attempted login to locked account: {username}")
                            continue

                        # Task 3: Duplicate Login Prevention
                        if username in active_sessions:
                            conn.sendall(b"ERROR: User already logged in elsewhere.\n")
                            log_event(f"Duplicate login attempt for user: {username}")
                            continue

                        # Authentication logic
                        if username in users and users[username] == hashed_pw:
                            # Successful Login
                            authenticated_user = username
                            active_sessions[username] = conn
                            failed_attempts[username] = {'count': 0, 'lockout_until': 0}
                            conn.sendall(b"SUCCESS: Login successful.\n")
                            log_event(f"Successful login for user: {username}")
                        else:
                            # Failed Login
                            user_attempts['count'] += 1
                            if user_attempts['count'] >= 5:
                                user_attempts['lockout_until'] = time.time() + 60 # Lock for 60 seconds
                                log_event(f"Account {username} locked due to 5 consecutive failed logins.")
                                conn.sendall(b"ERROR: 5 failed attempts. Account locked for 60s.\n")
                            else:
                                conn.sendall(b"ERROR: Invalid username or password.\n")
                                log_event(f"Failed login attempt for user: {username}")
                            failed_attempts[username] = user_attempts

                elif cmd == "MSG":
                    if not authenticated_user:
                        conn.sendall(b"ERROR: Unauthorized access. Please log in first.\n")
                        continue
                    
                    msg = parts[1] if len(parts) > 1 else ""
                    log_event(f"Message from {authenticated_user}: {msg}")
                    conn.sendall(f"ACK: Received message -> {msg}\n".encode('utf-8'))

                elif cmd == "LOGOUT":
                    if authenticated_user:
                        log_event(f"User {authenticated_user} logged out.")
                        conn.sendall(b"SUCCESS: Logged out.\n")
                        break
                    else:
                        conn.sendall(b"ERROR: Not logged in.\n")

                else:
                    conn.sendall(b"ERROR: Unsupported command.\n")

    except Exception as e:
        log_event(f"Error handling connection: {e}")
    finally:
        with lock:
            if authenticated_user and authenticated_user in active_sessions:
                del active_sessions[authenticated_user]
        conn.close()
        log_event(f"Connection closed for {addr}")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    log_event(f"Server started listening on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.daemon = True
        t.start()

if __name__ == "__main__":
    main()
