import socket
import struct
import threading
import time

# Constants
MAGIC_COOKIE = 0xabcddcba
MSG_TYPE_OFFER = 0x2
MSG_TYPE_REQUEST = 0x3
MSG_TYPE_PAYLOAD = 0x4
BROADCAST_INTERVAL = 1  # Seconds
BUFFER_SIZE = 1024

def broadcast_offers(udp_broadcast_socket, udp_port, tcp_port):
    """Continuously broadcast offer messages over UDP."""
    while True:
        try:
            offer_message = struct.pack('!IBHH', MAGIC_COOKIE, MSG_TYPE_OFFER, udp_port, tcp_port)
            udp_broadcast_socket.sendto(offer_message, ('<broadcast>', udp_port))
            time.sleep(BROADCAST_INTERVAL)
        except Exception as e:
            print(f"Error broadcasting offer: {e}")

def handle_tcp_client(client_socket, file_data):
    """Handle file transfer over TCP."""
    try:
        # Receive file size from the client
        requested_size = client_socket.recv(BUFFER_SIZE).decode().strip()
        requested_size = int(requested_size)

        # Send the requested data back to the client
        client_socket.sendall(file_data[:requested_size])
    except Exception as e:
        print(f"TCP client error: {e}")
    finally:
        client_socket.close()

def start_server(file_path):
    """Start the server to handle UDP and TCP communication."""
    # Load file data
    with open(file_path, 'rb') as f:
        file_data = f.read()

    # Create UDP broadcast socket
    udp_broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp_broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_broadcast_socket.bind(("0.0.0.0", 0))  # Bind to a random available port
    udp_port = udp_broadcast_socket.getsockname()[1]

    # Create TCP socket
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(("0.0.0.0", 0))  # Bind to a random available port
    tcp_port = tcp_socket.getsockname()[1]
    tcp_socket.listen(5)

    server_ip = socket.gethostbyname(socket.gethostname())
    print(f"Server started, listening on IP address {server_ip}")

    # Start broadcasting offers
    threading.Thread(target=broadcast_offers, args=(udp_broadcast_socket, udp_port, tcp_port), daemon=True).start()

    def udp_handler():
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(("0.0.0.0", udp_port))
        while True:
            # Receive message from client
            data, client_address = udp_socket.recvfrom(BUFFER_SIZE)

            # Parse offer request
            magic_cookie, msg_type = struct.unpack('!IB', data[:5])
            if magic_cookie != MAGIC_COOKIE or msg_type != MSG_TYPE_REQUEST:
                print("Invalid request received")
                continue

            # Extract requested file size
            requested_size = struct.unpack('!Q', data[5:13])[0]
            print(f"Received request for {requested_size} bytes from {client_address}")

            # Send payload messages
            segment_size = 1024
            total_segments = (requested_size + segment_size - 1) // segment_size

            for segment_num in range(total_segments):
                start = segment_num * segment_size
                end = min(start + segment_size, requested_size)

                payload = struct.pack(
                    '!IBQQ', MAGIC_COOKIE, MSG_TYPE_PAYLOAD, total_segments, segment_num + 1
                ) + file_data[start:end]

                udp_socket.sendto(payload, client_address)

    def tcp_handler():
        while True:
            client_socket, addr = tcp_socket.accept()
            print(f"TCP connection established with {addr}")
            client_thread = threading.Thread(target=handle_tcp_client, args=(client_socket, file_data))
            client_thread.start()

    # Start UDP and TCP handlers in separate threads
    threading.Thread(target=udp_handler, daemon=True).start()
    threading.Thread(target=tcp_handler, daemon=True).start()

    # Keep the server running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        udp_broadcast_socket.close()
        tcp_socket.close()

if __name__ == "__main__":
    file_path = "example_file.txt"  # Replace with your file path
    start_server(file_path)
