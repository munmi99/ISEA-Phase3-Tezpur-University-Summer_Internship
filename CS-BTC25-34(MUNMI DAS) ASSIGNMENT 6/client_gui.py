import socket
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

class ChatClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TCP Chat Client - ISEA Phase 3")
        self.root.geometry("850x600")
        self.root.configure(bg="#f0f2f5")

        self.client_socket = None
        self.connected = False
        self.username = ""

        self.create_login_frame()

    def create_login_frame(self):
        self.login_frame = tk.Frame(self.root, bg="#ffffff", bd=2, relief="groove")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=300)

        tk.Label(self.login_frame, text="Chat Login", font=("Arial", 16, "bold"), bg="#ffffff", fg="#333333").pack(pady=20)

        tk.Label(self.login_frame, text="Username:", font=("Arial", 11), bg="#ffffff").pack(anchor="w", padx=40)
        self.username_entry = tk.Entry(self.login_frame, font=("Arial", 12), width=25)
        self.username_entry.pack(pady=5, padx=40)

        tk.Label(self.login_frame, text="Server IP:", font=("Arial", 11), bg="#ffffff").pack(anchor="w", padx=40)
        self.ip_entry = tk.Entry(self.login_frame, font=("Arial", 12), width=25)
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.pack(pady=5, padx=40)

        self.connect_btn = tk.Button(self.login_frame, text="Connect", font=("Arial", 11, "bold"), bg="#4CAF50", fg="white", width=20, command=self.connect_to_server)
        self.connect_btn.pack(pady=20)

    def connect_to_server(self):
        self.username = self.username_entry.get().strip()
        host = self.ip_entry.get().strip()
        port = 5000

        if not self.username:
            messagebox.showerror("Error", "Username cannot be empty!")
            return

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))
            
            self.client_socket.send(self.username.encode('utf-8'))
            response = self.client_socket.recv(1024).decode('utf-8')

            if response.startswith("ACCEPT"):
                self.connected = True
                self.login_frame.destroy()
                self.create_chat_interface()
                
                receive_thread = threading.Thread(target=self.receive_messages)
                receive_thread.daemon = True
                receive_thread.start()
            else:
                messagebox.showerror("Connection Refused", "Username already taken or invalid server response.")
                self.client_socket.close()
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server: {e}")

    def create_chat_interface(self):
        self.main_frame = tk.Frame(self.root, bg="#f0f2f5")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        left_panel = tk.Frame(self.main_frame, bg="#f0f2f5")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        top_bar = tk.Frame(left_panel, bg="#ffffff", height=40, bd=1, relief="solid")
        top_bar.pack(fill="x", pady=(0, 5))
        self.status_label = tk.Label(top_bar, text=f"Logged in as: {self.username} | Status: Connected", font=("Arial", 10, "bold"), bg="#ffffff", fg="green")
        self.status_label.pack(side="left", padx=10, pady=8)

        self.disconnect_btn = tk.Button(top_bar, text="Disconnect", font=("Arial", 9, "bold"), bg="#f44336", fg="white", command=self.disconnect_from_server)
        self.disconnect_btn.pack(side="right", padx=10, pady=5)

        self.chat_display = scrolledtext.ScrolledText(left_panel, wrap=tk.WORD, font=("Arial", 11), state="disabled", bg="#ffffff")
        self.chat_display.pack(fill="both", expand=True, pady=(0, 5))

        input_frame = tk.Frame(left_panel, bg="#f0f2f5")
        input_frame.pack(fill="x")

        self.msg_entry = tk.Entry(input_frame, font=("Arial", 12))
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=5)
        self.msg_entry.bind("<Return>", lambda event: self.send_message())

        send_btn = tk.Button(input_frame, text="Send", font=("Arial", 10, "bold"), bg="#2196F3", fg="white", width=10, command=self.send_message)
        send_btn.pack(side="right")

        right_panel = tk.Frame(self.main_frame, width=200, bg="#ffffff", bd=1, relief="solid")
        right_panel.pack(side="right", fill="y")

        tk.Label(right_panel, text="Online Users", font=("Arial", 11, "bold"), bg="#ffffff", fg="#333333").pack(pady=10)
        
        self.user_listbox = tk.Listbox(right_panel, font=("Arial", 10), bg="#fafafa", selectmode=tk.SINGLE)
        self.user_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.user_listbox.bind("<Double-Button-1>", self.on_user_select)

        tk.Label(right_panel, text="Double click user\nto Private Message", font=("Arial", 8, "italic"), bg="#ffffff", fg="#666666").pack(pady=5)

    def receive_messages(self):
        while self.connected:
            try:
                message = self.client_socket.recv(4096).decode('utf-8')
                if not message:
                    break
                
                if message.startswith("USERLIST:"):
                    users = message[9:].split(",")
                    self.update_user_list(users)
                else:
                    self.display_message(message)
            except:
                break
        if self.connected:
            self.disconnect_from_server()

    def update_user_list(self, users):
        self.user_listbox.delete(0, tk.END)
        for user in users:
            if user:
                self.user_listbox.insert(tk.END, user)

    def display_message(self, message):
        self.chat_display.configure(state="normal")
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see(tk.END)

    def send_message(self):
        msg = self.msg_entry.get().strip()
        if msg and self.connected:
            try:
                self.client_socket.send(msg.encode('utf-8'))
                if not msg.startswith("@"):
                    self.display_message(f"You: {msg}")
                self.msg_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send message: {e}")

    def on_user_select(self, event):
        selection = self.user_listbox.curselection()
        if selection:
            selected_user = self.user_listbox.get(selection[0])
            if selected_user != self.username:
                self.msg_entry.delete(0, tk.END)
                self.msg_entry.insert(0, f"@{selected_user} ")

    def disconnect_from_server(self):
        self.connected = False
        try:
            if self.client_socket:
                self.client_socket.close()
        except:
            pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClientGUI(root)
    root.mainloop()
