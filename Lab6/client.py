import socket
import threading
import tkinter as tk
from time import sleep
from tkinter import messagebox, scrolledtext

from crc import crc_encode, crc_validate, introduce_error

# GLOBAL VARIABLES
client_socket = None
client_window = None
chat_area = None

def receive_messages():
    """Receives messages from the server and displays them in the chat area."""
    global chat_area

    while True:
        try:
            # Receive the encoded message from the server
            message = client_socket.recv(1024).decode()
            
            is_valid = crc_validate(message, "10011")

            # Parse the message for validity
            if is_valid:
                translated_message = ''.join(
                    chr(int(message[i:i+7], 2)) for i in range(0, len(message) - 4, 7)
                )
                
                valid_status = "Yes"
            else:
                translated_message = "N/A"
                valid_status = "No"
                
            
            sender_name = "SERVER"

            # Display message in the chat area
            chat_area.config(state=tk.NORMAL)
            chat_area.insert(
                tk.END,
                f"{sender_name}: {message}\n"
                f"\tValid: {valid_status}\n"
                f"\tTranslated: {translated_message}\n"
            )
            chat_area.config(state=tk.DISABLED)
            chat_area.yview(tk.END)
        except Exception as e:
            print(f"Error receiving message: {e}")
            handle_disconnection()
            break


def handle_disconnection():
    global client_socket
    try:
        # Send a "left the chat" message to the server
        client_socket.send(f"{name} left the chat.".encode())
    except Exception as e:
        print(f"Error during disconnection: {e}")
    finally:
        try:
            client_socket.close()  # Close the socket properly
        except:
            pass  # In case the socket is already closed
        chat_window.quit()  # Quit the chat window cleanly
        client_socket
        client_socket = None  # Ensure socket is cleaned up

    # Modify the part where the client window is closed
    chat_window.protocol("WM_DELETE_WINDOW", handle_disconnection)


def send_message(event=None):
    global name, client_socket

    message = message_entry.get("1.0", tk.END).strip()
    if message:
        try:
            # Convert ASCII to binary
            # binary_message = ''.join(format(ord(char), '07b') for char in message)

            # Encode with CRC
            crc_message = crc_encode(message, "10011")

            # Introduce a 5% error
            transmitted_message = introduce_error(crc_message)
            
            print(transmitted_message)
            print("yesmkj")

            # Send message to peer
            client_socket.send(transmitted_message.encode())

            # Display on GUI as sender
            chat_area.config(state=tk.NORMAL)
            chat_area.insert(
                tk.END,
                f"Sender > {message}\n\tSent: {transmitted_message}\n"
            )
            chat_area.config(state=tk.DISABLED)
            chat_area.yview(tk.END)
        except Exception as e:
            print(f"Error sending message: {e}")
            handle_disconnection()
        message_entry.delete("1.0", tk.END)
        if message == "[bye]":
            sleep(0.1)
            client_socket.close()
            chat_window.quit()


def start_client(ip : str, name : str):
    """ Starts the client connection. """
    
    # establish client connection
    global client_socket
    client_socket = socket.socket()
    port = 1234
    
    try:
        # connect to server
        client_socket.connect((ip, port))
        client_socket.send(name.encode()) 
        open_chatroom()  
        threading.Thread(target=receive_messages, daemon=True).start()
    except Exception as e:
        # handle connection error
        messagebox.showerror("Connection Error", f"Failed to connect to server: {e}")
        login_window.deiconify() 

def open_chatroom():
    global chat_window, chat_area, message_entry, name
    login_window.withdraw()  # Hide login window
    chat_window = tk.Toplevel()
    chat_window.title(f"Chatroom - {name}")
    chat_window.geometry("550x550")
    chat_window.configure(bg="#1e222b")

    chat_frame = tk.Frame(chat_window, bg="#1e222b")
    chat_frame.pack(pady=10, padx=10)

    tk.Label(chat_frame, text="Chat Area", bg="#1e222b", fg="white").pack(pady=5)
    chat_area = scrolledtext.ScrolledText(chat_frame, state='disabled', height=18, bg="#1e222b", fg='white')
    chat_area.pack(padx=10, pady=10)

    tk.Label(chat_window, text="Enter Message", bg="#1e222b", fg="white").pack(pady=5)
    message_entry = tk.Text(chat_window, height=4, bg="#1e222b", fg='white', pady=10, padx=10)
    message_entry.pack(pady=10, padx=20)
    message_entry.bind('<Return>', send_message)

    send_button = tk.Button(chat_window, text="Send", command=send_message, fg="#e4e7ec", bg="#212630", padx=20, pady=3)
    send_button.pack(pady=10)

def login():    
    """ Handles the login process. """
    
    # retrieve name and IP address
    global name 
    name = name_entry.get().strip()
    ip = ip_entry.get().strip()
    
    # start client connection
    if ip and name:
        start_client(ip, name)
    else:
        messagebox.showwarning("Input Error", "Please enter both IP address and name.")

# GUI SETUP for Login
login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("300x200")
login_window.configure(bg="#1e222b")

tk.Label(login_window, text="Enter Server IP:", bg="#1e222b", fg="white").pack(pady=5)
ip_entry = tk.Entry(login_window)
ip_entry.pack(pady=5)

tk.Label(login_window, text="Enter Your Name:", bg="#1e222b", fg="white").pack(pady=5)
name_entry = tk.Entry(login_window)
name_entry.pack(pady=5)

login_button = tk.Button(login_window, text="Login", command=login, fg="#e4e7ec", bg="#212630", padx=20, pady=3)
login_button.pack(pady=20)

login_window.mainloop()
