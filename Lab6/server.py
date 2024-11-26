import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from crc import crc_validate

# GLOBAL VARIABLES
clients = []

# CORE FUNCTIONS
def handle_client(client_socket: socket.socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected.")
    name = client_socket.recv(1024).decode()
    broadcast(f"{name} has joined the chat.", color="green")
    
    while True:
        try:
            generator = "1101"  # Example generator polynomial
            transmitted_message = client_socket.recv(1024).decode()
            
            if crc_validate(transmitted_message, generator):
                original_message_binary = transmitted_message[:-(len(generator) - 1)]
                original_message = ''.join(
                    chr(int(original_message_binary[i:i+8], 2)) for i in range(0, len(original_message_binary), 8)
                )
                broadcast(f"[{name}] {original_message}", client_socket)
            else:
                broadcast(f"[{name}] Sent Invalid Message!", client_socket, color="red")
            
        except Exception as e:
            break
    
    client_socket.close()
    clients.remove(client_socket)
    broadcast(f"{name} has left the chat.", color="red")

def broadcast(
        message : str, 
        client_socket : socket.socket = None, 
        color : str = "white"
    ):
    """ Handles broadcasting messages to all clients. """
    
    # insert message into chat area
    chat_area.config(state=tk.NORMAL)                   # enable editing
    chat_area.insert(tk.END, message + "\n", color)     # insert message
    chat_area.config(state=tk.DISABLED)                 # disable editing
    chat_area.yview(tk.END)                             # scroll to end
    
    # format message with color
    formatted_message = f"color:{color}|{message}"
    
    # send message to all clients except sender
    for client in clients:
        if client != client_socket:
            client.send(formatted_message.encode())

def send_server_message(event=None):
    """ Sends messages from the server to all clients. """
    
    # retrieve message from server message entry
    message = server_message_entry.get("1.0", tk.END).strip()
    
    # broadcast, and clear server message entry
    if message:
        broadcast(f"[SERVER] {message}")
        server_message_entry.delete("1.0", tk.END)

# SERVER SETUP
def start_server():
    """ Starts the server and listens for client connections. """
    
    # establish server connection
    server = socket.socket()
    host_name = socket.gethostname()
    ip = socket.gethostbyname(host_name)
    port = 1234
    server.bind((host_name, port))
    server.listen(5)
    print("[STARTING] Server is starting...")
    print(f"{host_name}: {ip}")
    
    # accept client connections
    while True:
        client_socket, client_address = server.accept()
        clients.append(client_socket)
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()

# GUI SETUP
# server window
server_window = tk.Tk()
server_window.title("Server")
server_window.geometry("550x500")
server_window.configure(bg="#1e222b")

# chat area
chat_frame = tk.Frame(server_window, bg="#1e222b")
chat_frame.pack(pady=10, padx=10)
chat_area = scrolledtext.ScrolledText(chat_frame, state='disabled', height=18, bg="#1e222b", fg='white')
chat_area.tag_config("green", foreground="green")  
chat_area.tag_config("red", foreground="red")       
chat_area.pack(padx=10, pady=10)

# server message entry
server_message_entry = tk.Text(server_window, height=4, bg="#1e222b", fg='white', pady=10, padx=10)
server_message_entry.pack(pady=10, padx=20)
server_message_entry.bind('<Return>', send_server_message)

send_button = tk.Button(server_window, text="Send to Clients", command=send_server_message, fg="#e4e7ec", bg="#212630", padx=8, pady=3)
send_button.pack(pady=10)

# start server
threading.Thread(target=start_server, daemon=True).start()
server_window.mainloop()