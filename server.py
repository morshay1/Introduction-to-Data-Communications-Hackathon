import socket
import threading
import struct
import time

def broadcast_offers(udp_port, tcp_port):
    MAGIC_COOKIE = 0xabcddcba
    OFFER_TYPE = 0x2
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as udp_sock:
            udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            message = struct.pack('!IBHH', MAGIC_COOKIE, OFFER_TYPE, udp_port, tcp_port)
            udp_sock.sendto(message, ('<broadcast>', udp_port))
            time.sleep(1)  # Send offer every second

def handle_client(client_socket):
    # Placeholder for handling client requests (TCP or UDP)
    pass

def start_server():
    udp_port = 13117
    tcp_port = 50000

    # Start broadcasting offers
    threading.Thread(target=broadcast_offers, args=(udp_port, tcp_port), daemon=True).start()

    # Handle TCP connections
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind(('', tcp_port))
        tcp_socket.listen()
        print(f"Server started, listening on IP address {socket.gethostbyname(socket.gethostname())}")

        while True:
            client_socket, client_address = tcp_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()

if __name__ == '__main__':
    start_server()
