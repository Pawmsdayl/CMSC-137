import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from crc import crc_encode, crc_validate, introduce_error

# GLOBAL VARIABLES
clients = []

# CORE FUNCTIONS
def handle_client(client_socket: socket.socket, client_address: tuple):
    """Handles client connections, messages, and disconnection."""
    
    # broadcast connection
    print(f"[NEW CONNECTION] {client_address} connected.")
    name = client_socket.recv(1024).decode() 
    connect_message = f"{name} has joined the chat."
    broadcast(received_message=connect_message, client_socket=client_socket, is_join_message=True)
    
    while True:
        try:
            # Receive the transmitted message (in binary)
            received_message = client_socket.recv(1024).decode()
            
            print("weh")
            print(received_message)
            
            # Validate the received message using CRC
            is_valid = crc_validate(received_message, "10011")
            
            if is_valid:
                # Translate the message from binary to ASCII
                translated_message = ''.join(
                    chr(int(received_message[i:i+7], 2)) for i in range(0, len(received_message) - 4, 7)
                )
                valid_status = "Yes"
            else:
                translated_message = "N/A"
                valid_status = "No"
            
            # Broadcast the message to all other clients
            broadcast(received_message, translated_message, valid_status, name, client_socket)
            
        except Exception as e:
            print(f"Error handling client message: {e}")
            break
    
    # Clean up client connection
    client_socket.close()
    clients.remove(client_socket)
    print(f"[CLIENT DISCONNECTED] {client_address} disconnected.")

def broadcast(
        received_message: str, 
        translated_message: str = None, 
        valid_status: str = None, 
        sender_name: str = None,
        client_socket: socket.socket = None, 
        is_join_message: bool = False
    ):
    """Broadcasts messages to all clients."""
    
    chat_area.config(state=tk.NORMAL)
    
    # If it's a join message, do not apply CRC checks or translation
    if is_join_message:
        chat_area.insert(tk.END, f"{received_message}\n")
    else:
        # Otherwise, apply CRC validation and translation
        print(f"Message: {received_message}")
        
        chat_area.insert(
            tk.END,
            f"Name: {sender_name}\n"
            f"Messagez: {received_message}\n"
            f"Valid: {valid_status}\n"
            f"Translated: {translated_message}\n\n"
        )
    
    chat_area.config(state=tk.DISABLED)
    chat_area.yview(tk.END)
    
    # Send the message to all clients except the sender
    for client in clients:
        if client != client_socket:
            # Send the message as binary (after CRC encoding and error introduction)
            binary_message = ''.join(format(ord(char), '07b') for char in received_message)
            crc_message = crc_encode(binary_message, )
            transmitted_message = introduce_error(crc_message)
            client.send(transmitted_message.encode())

def send_server_message():
    """Sends a message from the server to all clients."""
    global clients
    
    # Retrieve the message from the input
    message = server_message_entry.get("1.0", tk.END).strip()
    if message:
        try:
            
            message = f"[SERVER]: {message}"
            
            # Encode with CRC
            crc_message = crc_encode(message, "10011")
            
            # Introduce a 5% error to the message
            transmitted_message = introduce_error(crc_message)
            
            # Send the message to all clients
            for client in clients:
                client.send(transmitted_message.encode())
            
            # Display the sent message in the server GUI as the sender
            chat_area.config(state=tk.NORMAL)
            chat_area.insert(
                tk.END,
                f"{message}\n\tSent: {transmitted_message}\n"
            )
            chat_area.config(state=tk.DISABLED)
            chat_area.yview(tk.END)
        except Exception as e:
            print(f"Error broadcasting server message: {e}")
        
        # Clear the server input area
        server_message_entry.delete("1.0", tk.END)

# SERVER SETUP
def start_server():
    """Starts the server and listens for client connections."""
    
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
clients = []
server_window = tk.Tk()
server_window.title("Server")
server_window.geometry("550x500")
server_window.configure(bg="#1e222b")

chat_frame = tk.Frame(server_window, bg="#1e222b")
chat_frame.pack(pady=10, padx=10)

chat_area = scrolledtext.ScrolledText(chat_frame, state='disabled', height=18, bg="#1e222b", fg='white')
chat_area.pack(padx=10, pady=10)

server_message_entry = tk.Text(server_window, height=4, bg="#1e222b", fg='white', pady=10, padx=10)
server_message_entry.pack(pady=10, padx=20)
server_message_entry.bind('<Return>', send_server_message)

send_button = tk.Button(server_window, text="Send to Clients", command=send_server_message, fg="#e4e7ec", bg="#212630", padx=8, pady=3)
send_button.pack(pady=10)

# Start the server in a separate thread
threading.Thread(target=start_server, daemon=True).start()

server_window.mainloop()
