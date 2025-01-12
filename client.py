import socket
import struct
import time

MAGIC_COOKIE = 0x12345678  # Example magic cookie, make sure it matches the one in the server
MSG_TYPE_OFFER = 1         # Offer message type identifier
BROADCAST_PORT = 12345     # UDP port where offers are broadcast
TIMEOUT = 5                # Timeout for waiting for offers (seconds)
BUFFER_SIZE = 1024        # Buffer size for receiving UDP messages

def listen_for_offers():
    """Listen for UDP offers broadcasted by servers."""
    # Create a UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_socket.bind(('', BROADCAST_PORT))  # Bind to the broadcast port

    udp_socket.settimeout(TIMEOUT)  # Set a timeout for listening to offers

    while True:
        try:
            # Receive data from the UDP broadcast
            data, addr = udp_socket.recvfrom(BUFFER_SIZE)
            
            # Unpack the received message
            magic_cookie, msg_type, udp_port, tcp_port = struct.unpack('!IBHH', data)
            
            # Check if the magic cookie and message type are valid
            if magic_cookie == MAGIC_COOKIE and msg_type == MSG_TYPE_OFFER:
                print(f"Received offer from {addr}: UDP port = {udp_port}, TCP port = {tcp_port}")
                connect_to_tcp_server(tcp_port)
                break
            else:
                print("Invalid message received")
        except socket.timeout:
            print("Timeout reached, no offers received.")
            break
        except Exception as e:
            print(f"Error receiving offer: {e}")
            break

def connect_to_tcp_server(tcp_port):
    """Connect to the TCP server."""
    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_ip = '127.0.0.1'  # Assuming server is running locally, modify as needed
        tcp_socket.connect((server_ip, tcp_port))
        
        print(f"Connected to TCP server on port {tcp_port}")
        
        # Example of sending a message to the server
        tcp_socket.sendall(b"Hello from the client!")
        
        # Receive a response from the server
        response = tcp_socket.recv(1024)
        print(f"Server response: {response.decode('utf-8')}")
        
        tcp_socket.close()
    except Exception as e:
        print(f"Error connecting to TCP server: {e}")

if __name__ == "__main__":
    listen_for_offers()
