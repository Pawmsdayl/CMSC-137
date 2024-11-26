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

    generator = "10011"  # Example generator polynomial

    while True:
        try:
            # Receive the encoded message from the server
            message = client_socket.recv(1024).decode()

            # Parse the message for validity
            if crc_validate(message, generator):
                original_message_binary = message[:-(len(generator) - 1)]
                translated_message = ''.join(
                    chr(int(original_message_binary[i:i + 7], 2)) for i in range(0, len(original_message_binary), 7)
                )
                display_message = (
                    f"Valid Message\n"
                    f"server > {translated_message}\n"
                    f"\tValid: Yes\n"
                    f"\tTranslated: {translated_message}"
                )
            else:
                display_message = (
                    f"Invalid Message\n"
                    f"server > {message}\n"
                    f"\tValid: No"
                )

            # Display the message in the chat area
            chat_area.config(state=tk.NORMAL)
            chat_area.insert(tk.END, display_message + "\n")
            chat_area.config(state=tk.DISABLED)
            chat_area.yview(tk.END)

        except Exception as e:
            print(e)
            handle_disconnection()
            break

def handle_disconnection():
    """ Handles disconnection from the server. """
    
    messagebox.showerror("Error", "An error occurred or the server closed the connection.")
    chat_window.quit()  

from crc import crc_encode, introduce_error


def send_message():
    global name
    
    message = message_entry.get("1.0", tk.END).strip()
    if message:
        try:
            generator = "10011"  # Example generator polynomial
            # binary_message = ''.join(format(ord(c), '07b') for c in message)
            encoded_message = crc_encode(message, generator)
            transmitted_message = introduce_error(encoded_message)  # Simulate errors
            
            client_socket.send(transmitted_message.encode())
            
            chat_area.config(state=tk.NORMAL)
            chat_area.insert(tk.END, f"Sender > {message}\n\tSent: {transmitted_message}\n")
            chat_area.config(state=tk.DISABLED)
            chat_area.yview(tk.END)
        
        except Exception as e:
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
    """ Creates and opens the chatroom interface. """
    # GUI SETUP for Chat Room
    
    global chat_window, chat_area, message_entry, name
    
    # create chatroom window
    login_window.withdraw()  # Hide login window
    chat_window = tk.Toplevel()
    chat_window.title(f"Chatroom - {name}")
    chat_window.geometry("550x550")
    chat_window.configure(bg="#1e222b")
    
    chat_frame = tk.Frame(chat_window, bg="#1e222b")
    chat_frame.pack(pady=10, padx=10)
    
    # chat area
    tk.Label(chat_frame, text="Chat Area", bg="#1e222b", fg="white").pack(pady=5)
    chat_area = scrolledtext.ScrolledText(chat_frame, state='disabled', height=18, bg="#1e222b", fg='white')
    chat_area.pack(padx=10, pady=10)
    
    
    # message entry
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
# login window
login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("300x200")
login_window.configure(bg="#1e222b")

# login entries
tk.Label(login_window, text="Enter Server IP:", bg="#1e222b", fg="white").pack(pady=5)
ip_entry = tk.Entry(login_window)
ip_entry.pack(pady=5)

tk.Label(login_window, text="Enter Your Name:", bg="#1e222b", fg="white").pack(pady=5)
name_entry = tk.Entry(login_window)
name_entry.pack(pady=5)

login_button = tk.Button(login_window, text="Login", command=login, fg="#e4e7ec", bg="#212630", padx=20, pady=3)
login_button.pack(pady=20)

# start login window
login_window.mainloop()