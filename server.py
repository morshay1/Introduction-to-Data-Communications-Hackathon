import socket
import struct
import time
import threading

# Constants
MAGIC_COOKIE = 0xabcddcba  # Magic cookie to match client
MSG_TYPE_OFFER = 0x2       # Message type for offer
MSG_TYPE_REQUEST = 0x3     # Message type for request
MSG_TYPE_PAYLOAD = 0x4     # Message type for payload
BROADCAST_PORT = 61870     # Client's listening port
UDP_PORT = 50563           # UDP port used for data transfer
TCP_PORT = 52368           # TCP port for file transfer
BUFFER_SIZE = 1024

# ANSI color codes
GREEN = '\033[32m'
RED = '\033[31m'
YELLOW = '\033[33m'
MAGENTA = '\033[35m'
RESET = '\033[0m'

def start_server():
    """Start the server to listen for incoming offers and broadcast UDP announcements."""
    # Create a UDP socket for broadcasting offers
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_socket.bind(('', 0))  # Bind to any available port

    # Create a TCP socket for handling client connections
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(('', TCP_PORT))
    tcp_socket.listen(5)

    print(f"{YELLOW}Server started, listening on IP address {get_ip()}, UDP port = {BROADCAST_PORT}, TCP port = {TCP_PORT}{RESET}")

    # Start the broadcast offer thread
    offer_thread = threading.Thread(target=broadcast_offers, args=(udp_socket,))
    offer_thread.daemon = True  # Daemonize the thread so it exits when the main program exits
    offer_thread.start()

    # Accept TCP connections from clients
    while True:
        client_socket, client_address = tcp_socket.accept()
        print(f"{MAGENTA}Accepted TCP connection from {client_address}{RESET}")

        # Start a new thread to handle the client speed test (TCP/UDP)
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.daemon = True  # Daemonize the thread
        client_thread.start()

def broadcast_offers(udp_socket):
    """Broadcast offer messages every second in a separate thread."""
    while True:
        offer_data = struct.pack('!IBHH', MAGIC_COOKIE, MSG_TYPE_OFFER, UDP_PORT, TCP_PORT)
        udp_socket.sendto(offer_data, ('<broadcast>', BROADCAST_PORT))
        print(f"{GREEN}Offer broadcasted{RESET}")
        time.sleep(1)  # Broadcast offer every 1 second

def handle_client(client_socket, client_address):
    """Handle an individual client request (either TCP or UDP speed test)."""
    try:
        # Receive request message (expecting Magic Cookie, Message Type, and File Size)
        request_data = client_socket.recv(13)
        if len(request_data) < 13:
            print(f"{RED}Incomplete request received from {client_address}, expected 16 bytes, got {len(request_data)}{RESET}")
            return
        
        magic_cookie, msg_type, file_size = struct.unpack('!IBQ', request_data)

        if magic_cookie != MAGIC_COOKIE or msg_type != MSG_TYPE_REQUEST:
            print(f"{RED}Invalid request received from {client_address}")
            print(f"Received magic_cookie: {magic_cookie}, Expected: {MAGIC_COOKIE}")
            print(f"Received msg_type: {msg_type}, Expected: {MSG_TYPE_REQUEST}")
            return

        print(f"{MAGENTA}Received file size: {file_size} from {client_address}{RESET}")

        # Print the details of the file being transferred
        print(f"{MAGENTA}Starting file transfer of {file_size} bytes from {client_address}{RESET}")

        # Start file transfer (handle your file transfer logic here)
        start_time = time.time()  # Log the start time for TCP
        transfer_file(client_socket, file_size, start_time, client_address)

    except Exception as e:
        print(f"{RED}Error handling client {client_address}: {e}{RESET}")
    finally:
        client_socket.close()

def transfer_file(client_socket, file_size, start_time, client_address):
    """Simulate a file transfer over TCP."""
    total_segments = (file_size + BUFFER_SIZE - 1) // BUFFER_SIZE  # Calculate total segments
    data_sent = 0

    while data_sent < file_size:
        # Simulate sending a file in chunks
        chunk = min(BUFFER_SIZE, file_size - data_sent)
        current_segment = (data_sent // BUFFER_SIZE) + 1  # Calculate current segment number

        # Create payload message
        payload_data = struct.pack('!IBQQ', MAGIC_COOKIE, MSG_TYPE_PAYLOAD, total_segments, current_segment) + b'A' * chunk
        client_socket.sendall(payload_data)

        data_sent += chunk

        print(f"{YELLOW}Sent segment {current_segment}/{total_segments} for {client_address}{RESET}")

    total_time = time.time() - start_time
    if total_time == 0:
        total_time = 0.01  # Avoid division by zero, set a very small value
    transfer_rate = file_size * 8 / total_time  # in bits/second
    print(f"{GREEN}TCP transfer finished for {client_address}, total time: {total_time:.2f} seconds, total speed: {transfer_rate:.2f} bits/second{RESET}")

def get_ip():
    """Get the IP address of the server."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('8.8.8.8', 0))
    ip = s.getsockname()[0]
    s.close()
    return ip

if __name__ == "__main__":
    start_server()