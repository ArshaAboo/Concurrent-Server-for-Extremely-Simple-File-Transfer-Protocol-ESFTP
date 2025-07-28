import socket
import sys
import os
import time

def main():
    # Get server IP address and filename from user
    if len(sys.argv) != 4:
        print("Usage: python server.py <server_ip> <server_port> <filename>")
        return

    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    filename = sys.argv[3]

    # Define chunk size
    chunk_size = 1024

    try:
        # Create a socket object
        client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        
        
        interface_name = "enp7s0" 
        # Get the index of the network interface 
        interface_index = socket.if_nametoindex(interface_name) 
        # Bind host, port and the interface 
        client_socket.bind( ("fe80::20cd:bfff:fea3:b2db", 12345, 0, interface_index) )

        # Connect to the server
        client_socket.connect((server_ip, server_port))

        # Send filename to server
        client_socket.send(f"{filename}\n".encode())

        print("Waiting for server's permission...")

        permission = client_socket.recv(1024).decode()
        if permission.strip().lower() != 'y':
            print("Server denied permission. Aborting file transfer.")
            return

        # Open the file and send data in chunks
        print("Permission granted, sending file!")
        with open(filename, 'rb') as file:
            while True:
                data = file.read(chunk_size)
                if not data:
                    print("File sent successfully.")
                    break
                    
                client_socket.send(data)
                

    except Exception as e:
        print("Error:", e)

    finally:
        # Close the client socket
        client_socket.close()

if __name__ == "__main__":
    main()
