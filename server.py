import socket
import os
import threading
from queue import Queue
import time

# Define global variables
MAX_CONCURRENT_REQUESTS = 5
MAX_QUEUED_REQUESTS = 5

def handle_client(client_socket, client_address, new_filename,request_queue):
   
            # Open file for writing
            with open(new_filename, 'wb') as file:
                i=1   
                while True:
                    if (i%1000==0):
                        # print(f"Receiving piece {i} from {client_address}")
                        time.sleep(1)
                    
                    data = client_socket.recv(1024)
                    if not data:
                        print("All pieces received!")
                        print("File", new_filename, "received successfully from", client_address)
                        break
                            
                    file.write(data)
                    i=i+1

            # Close client socket
            client_socket.close()

            if not request_queue.empty():
                client_socket, client_address, new_filename = request_queue.get()
                handle_client(client_socket, client_address, new_filename,request_queue)
            
            return

def main():
    try:
        # Create a socket object
        server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

        # Bind the socket to the server address and port
        # server_socket.bind(('127.0.0.1', 12345))
        
        interface_name = "enp7s0" 
        # Get the index of the network interface 
        interface_index = socket.if_nametoindex(interface_name) 
        # Bind host, port and the interface 
        server_socket.bind( ("fe80::1062:a9ff:fe09:c216", 12345, 0, interface_index) )

        # Listen for incoming connections
        server_socket.listen(MAX_CONCURRENT_REQUESTS)
        print("Server is listening...")
        # Queue for handling queued requests
        request_queue = Queue(maxsize=MAX_QUEUED_REQUESTS)

        while True:
            # Accept incoming connection
            print("Waiting for client.")

            client_socket, client_address = server_socket.accept()
            print("Connected to", client_address)

            # Receive file name from client
            filename = client_socket.recv(1024).decode().split('\n')[0].strip()
                
            print(f"Client {client_address} requests to send a file, name:{filename}")

            permission = input(f"Accept file transfer? (y/n) from {client_address}: ").strip().lower()
            client_socket.send(permission.encode())


            if permission == 'y':


                default_new_filename = f"rec_from_{client_address[0]}_{client_address[1]}_{filename}"
                new_filename = input(f"Please rename received file from {client_address}").strip() or default_new_filename

                print("NUMBER OF threads", threading.active_count())


                if threading.active_count() <= MAX_CONCURRENT_REQUESTS:
                    # if not request_queue.empty():
                    # client_socket, client_address, new_filename = request_queue.get()

                    # Start a new thread to handle client
                    threading.Thread(target=handle_client, args=(client_socket, client_address, new_filename,request_queue)).start()
                else:
                # Add client connection to the request queue
                    request_queue.put((client_socket, client_address, new_filename))

            else:
                print("File transfer declined.")


    except Exception as e:
        print("Error:", e)

    finally:
        # Close the server socket
        server_socket.close()

if __name__ == "__main__":
    main()
