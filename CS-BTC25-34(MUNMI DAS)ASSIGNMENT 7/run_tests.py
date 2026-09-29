import socket
import time

SERVER_IP = '10.0.0.1'
PORT = 5000

def send_req(cmd):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER_IP, PORT))
        s.sendall((cmd + "\n").encode())
        res = s.recv(1024).decode().strip()
        s.close()
        return res
    except Exception as e:
        return f"Error: {e}"

print("\n--- RUNNING ALL LAB TEST CASES ---")

# Test 1: Successful Login
print("1. Successful Login Test:")
print("   Response:", send_req("LOGIN alice password"))

# Test 2: Authenticated Message Exchange
print("\n2. Authenticated Message Test:")
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_IP, PORT))
    s.sendall(b"LOGIN alice password\n")
    print("   Login Response:", s.recv(1024).decode().strip())
    s.sendall(b"MSG Hello From Client\n")
    print("   Msg Response:  ", s.recv(1024).decode().strip())
    s.close()
except Exception as e:
    print("   Error:", e)

# Test 3: Duplicate Login Test
print("\n3. Duplicate Login Test:")
try:
    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s1.connect((SERVER_IP, PORT))
    s1.sendall(b"LOGIN alice password\n")
    s1.recv(1024)

    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s2.connect((SERVER_IP, PORT))
    s2.sendall(b"LOGIN alice password\n")
    print("   Duplicate Response:", s2.recv(1024).decode().strip())
    s1.close()
    s2.close()
except Exception as e:
    print("   Error:", e)

# Test 4: Logout Test
print("\n4. Logout Test:")
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_IP, PORT))
    s.sendall(b"LOGIN alice password\n")
    s.recv(1024)
    s.sendall(b"LOGOUT\n")
    print("   Logout Response:", s.recv(1024).decode().strip())
    s.close()
except Exception as e:
    print("   Error:", e)

# Test 5: Failed Login & Lockout Test
print("\n5. Failed Login & Lockout Test (5 Wrong Attempts):")
for i in range(1, 6):
    res = send_req("LOGIN alice wrongpassword")
    print(f"   Attempt {i}: {res}")

print("\n--- ALL TESTS COMPLETED ---")
