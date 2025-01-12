import socket
import struct
import threading

def listen_for_offers():
    MAGIC_COOKIE = 0xabcddcba
    OFFER_TYPE = 0x2

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        udp_sock.bind(('', 13117))
        print("Client started, listening for offer requests...")

        while True:
            data, addr = udp_sock.recvfrom(1024)
            magic_cookie, message_type, udp_port, tcp_port = struct.unpack('!IBHH', data[:9])
            if magic_cookie == MAGIC_COOKIE and message_type == OFFER_TYPE:
                print(f"Received offer from {addr[0]}, UDP port {udp_port}, TCP port {tcp_port}")

if __name__ == '__main__':
    listen_for_offers()
