import socket
import threading
import tkinter as tk
from tkinter import messagebox

class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure TCP Client")
        self.sock = None
        self.is_connected = False

        # GUI Components
        tk.Label(root, text="Server IP:").grid(row=0, column=0, sticky="e")
        self.ip_entry = tk.Entry(root)
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.grid(row=0, column=1)

        tk.Label(root, text="Username:").grid(row=1, column=0, sticky="e")
        self.user_entry = tk.Entry(root)
        self.user_entry.grid(row=1, column=1)

        tk.Label(root, text="Password:").grid(row=2, column=0, sticky="e")
        self.pass_entry = tk.Entry(root, show="*")
        self.pass_entry.grid(row=2, column=1)

        self.login_btn = tk.Button(root, text="Login", command=self.login)
        self.login_btn.grid(row=3, column=0)

        self.logout_btn = tk.Button(root, text="Logout", command=self.logout, state=tk.DISABLED)
        self.logout_btn.grid(row=3, column=1)

        tk.Label(root, text="Message:").grid(row=4, column=0, sticky="e")
        self.msg_entry = tk.Entry(root, state=tk.DISABLED)
        self.msg_entry.grid(row=4, column=1)

        self.send_btn = tk.Button(root, text="Send", command=self.send_msg, state=tk.DISABLED)
        self.send_btn.grid(row=5, column=0, columnspan=2)

        self.chat_display = tk.Text(root, height=10, width=40)
        self.chat_display.grid(row=6, column=0, columnspan=2)

    def log(self, text):
        self.chat_display.insert(tk.END, text + "\n")
        self.chat_display.see(tk.END)

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.ip_entry.get(), 5000))
            self.is_connected = True
            threading.Thread(target=self.receive_loop, daemon=True).start()
            return True
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            return False

    def login(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        # Input validation
        if not username or not password:
            messagebox.showwarning("Validation Error", "Username/Password cannot be empty.")
            return

        if not self.is_connected:
            if not self.connect():
                return

        cmd = f"LOGIN {username} {password}\n"
        self.sock.sendall(cmd.encode('utf-8'))

    def send_msg(self):
        msg = self.msg_entry.get()
        if msg:
            cmd = f"MSG {msg}\n"
            self.sock.sendall(cmd.encode('utf-8'))
            self.msg_entry.delete(0, tk.END)

    def logout(self):
        if self.is_connected and self.sock:
            self.sock.sendall(b"LOGOUT\n")

    def receive_loop(self):
        while self.is_connected:
            try:
                data = self.sock.recv(1024).decode('utf-8')
                if not data:
                    break
                
                self.log(f"Server: {data.strip()}")

                if "SUCCESS: Login successful." in data:
                    self.login_btn.config(state=tk.DISABLED)
                    self.logout_btn.config(state=tk.NORMAL)
                    self.msg_entry.config(state=tk.NORMAL)
                    self.send_btn.config(state=tk.NORMAL)
                elif "SUCCESS: Logged out." in data or "Inactivity timeout" in data:
                    self.reset_gui()
                    break
            except Exception:
                break
        self.reset_gui()

    def reset_gui(self):
        self.is_connected = False
        if self.sock:
            self.sock.close()
            self.sock = None
        self.login_btn.config(state=tk.NORMAL)
        self.logout_btn.config(state=tk.DISABLED)
        self.msg_entry.config(state=tk.DISABLED)
        self.send_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientGUI(root)
    root.mainloop()
