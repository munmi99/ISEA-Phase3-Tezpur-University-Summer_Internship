import socket
import json
import time
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

# Task 4: Load Configuration
with open("config.json", "r") as f:
    config = json.load(f)

HOST = "10.0.0.1"
PORT = config["PORT"]
BUFFER_SIZE = config["BUFFER_SIZE"]

class ChatClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Client Chat App")
        self.sock = None
        self.connected = False

        self.chat_area = scrolledtext.ScrolledText(root, state='disabled', width=50, height=20)
        self.chat_area.pack(padx=10, pady=10)

        self.msg_entry = tk.Entry(root, width=40)
        self.msg_entry.pack(side=tk.LEFT, padx=10, pady=10)
        self.msg_entry.bind("<Return>", lambda event: self.send_message())

        self.send_btn = tk.Button(root, text="Send", command=self.send_message)
        self.send_btn.pack(side=tk.LEFT, pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.connect_to_server()

    def connect_to_server(self, max_retries=3):
        """Task 2: Automatic Reconnection Logic with Retries."""
        retry_count = 0
        while retry_count < max_retries and not self.connected:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((HOST, PORT))
                self.sock.sendall(f"User_{id(self)}".encode('utf-8'))
                self.connected = True
                self.display_message("Connected to server successfully.")
                threading.Thread(target=self.receive_messages, daemon=True).start()
                return
            except Exception as e:
                retry_count += 1
                self.display_message(f"Connection failed. Retrying ({retry_count}/{max_retries})...")
                time.sleep(2)

        messagebox.showerror("Error", "Unable to connect to server after multiple attempts.")

    def send_message(self):
        msg = self.msg_entry.get().strip()
        if msg and self.connected:
            try:
                self.sock.sendall(msg.encode('utf-8'))
                self.display_message(f"You: {msg}")
                self.msg_entry.delete(0, tk.END)
            except Exception as e:
                self.display_message("Failed to send message.")
                self.connected = False

    def receive_messages(self):
        while self.connected:
            try:
                data = self.sock.recv(BUFFER_SIZE).decode('utf-8')
                if not data:
                    break
                self.display_message(data)
            except Exception:
                break
        self.connected = False
        self.display_message("Disconnected from server.")

    def display_message(self, msg):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, msg + "\n")
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

    def on_closing(self):
        self.connected = False
        if self.sock:
            self.sock.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClientGUI(root)
    root.mainloop()
