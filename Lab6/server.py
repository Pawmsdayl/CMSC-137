import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

from crc import crc_encode, crc_validate

# GLOBAL VARIABLES
clients = []

# CORE FUNCTIONS
def handle_client(client_socket: socket.socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected.")
    name = client_socket.recv(1024).decode()
    message =f"{name} has joined the chat."
    welcome_message = crc_encode(message, "10011")
    broadcast(welcome_message)
    
    while True:
        try:
            generator = "10011"  # Example generator polynomial
            transmitted_message = client_socket.recv(1024).decode()
            
            if crc_validate(transmitted_message, generator):
                original_message_binary = transmitted_message[:-(len(generator) - 1)]
                original_message = ''.join(
                    chr(int(original_message_binary[i:i+8], 2)) for i in range(0, len(original_message_binary), 8)
                )
                broadcast(original_message, client_socket, sender_name=name, valid=True)
            else:
                broadcast(transmitted_message, client_socket, sender_name=name, valid=False)
            
        except Exception as e:
            break
    
    client_socket.close()
    clients.remove(client_socket)
    broadcast(f"{name} has left the chat.")

def broadcast(
    message: str,
    client_socket: socket.socket = None,
    sender_name: str = "SERVER",
    valid: bool = None
):
    """Handles broadcasting messages to all clients."""

    if valid is not None:
        if valid:
            # Extract the binary message and decode to ASCII (7 bits per character)
            original_message_binary = message[:-(len("10011") - 1)]
            translated_message = ''.join(
                chr(int(original_message_binary[i:i + 7], 2)) for i in range(0, len(original_message_binary), 7)
            )
            message = (
                f"Valid Message\n"
                f"{sender_name} > {translated_message}\n"
                f"\tValid: Yes\n"
                f"\tTranslated: {translated_message}"
            )
        else:
            message = (
                f"Invalid Message\n"
                f"{sender_name} > {message}\n"
                f"\tValid: No"
            )


    # Display message in the server chat area
    chat_area.config(state=tk.NORMAL)           # Enable editing
    chat_area.insert(tk.END, message + "\n")    # Insert message
    chat_area.config(state=tk.DISABLED)         # Disable editing
    chat_area.yview(tk.END)                     # Scroll to end

    # Send message to all clients except sender
    for client in clients:
        if client != client_socket:
            client.send(message.encode())


def send_server_message(event=None):
    """Sends messages from the server to all clients."""
    global chat_area
    generator = "10011"  # Example generator polynomial

    # Retrieve the server message from the input area
    message = server_message_entry.get("1.0", tk.END).strip()

    # Encode with CRC and broadcast
    if message:
        #binary_message = ''.join(format(ord(c), '07b') for c in message)
        encoded_message = crc_encode(message, generator)

        # Broadcast the encoded message to clients
        broadcast(encoded_message, sender_name="SERVER", valid=True)

        # Display the server message in the server's GUI
        chat_area.config(state=tk.NORMAL)
        chat_area.insert(tk.END, f"server > {message}\n")
        chat_area.config(state=tk.DISABLED)
        chat_area.yview(tk.END)

        # Clear the server input field
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
# chat_area.tag_config("green", foreground="green")  
# chat_area.tag_config("red", foreground="red")       
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