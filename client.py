import socket
import struct
import time
import threading
import random

MAGIC_COOKIE = 0xabcddcba  # Match this with the server
MSG_TYPE_OFFER = 0x2       # Match the message type with the server
MSG_TYPE_REQUEST = 0x3     # Request message type
MSG_TYPE_PAYLOAD = 0x4     # Payload message type
BROADCAST_PORT = 61870     # Same as the server port
BUFFER_SIZE = 1024
TIMEOUT = 5                # Timeout for waiting for offers (seconds)

# ANSI color codes
RESET = '\033[0m'
BOLD = '\033[1m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'

class Client:
    def __init__(self):
        self.file_size = 0
        self.num_tcp_connections = 0
        self.num_udp_connections = 0
        self.server_ip = ""
        self.tcp_port = 0
        self.udp_port = 0
        self.state = "Startup"  # Client starts in the "Startup" state
        self.lock = threading.Lock()

    def startup_state(self):
        """Ask the user for the parameters to start the transfer."""
        self.file_size = int(input(f"{GREEN}Enter file size (bytes): {RESET}"))
        self.num_tcp_connections = int(input(f"{GREEN}Enter the number of TCP connections: {RESET}"))
        self.num_udp_connections = int(input(f"{GREEN}Enter the number of UDP connections: {RESET}"))
        self.state = "Looking for Server"  # Transition to next state

    def looking_for_server_state(self):
        """Listen for UDP offers broadcasted by servers."""
        print(f"{CYAN}Client started, listening for offer requests...{RESET}")

        # Create UDP socket for listening
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow address reuse
        udp_socket.bind(('', BROADCAST_PORT))  # Listen on the same port as the server
        print(f"{CYAN}Client is listening on port {BROADCAST_PORT}{RESET}")

        while True:
            try:
                # Receive data from the UDP broadcast
                data, addr = udp_socket.recvfrom(BUFFER_SIZE)
                print(f"{YELLOW}Received data from {addr}: {data}{RESET}")

                # Unpack the received message
                magic_cookie, msg_type, udp_port, tcp_port = struct.unpack('!IBHH', data)
                
                # Check if the magic cookie and message type are valid
                if magic_cookie == MAGIC_COOKIE and msg_type == MSG_TYPE_OFFER:
                    print(f"{GREEN}Received offer from {addr[0]}: UDP port = {udp_port}, TCP port = {tcp_port}{RESET}")
                    self.server_ip = addr[0]
                    self.tcp_port = tcp_port
                    self.udp_port = udp_port
                    self.state = "Request"  # Transition to send the request
                    break
                else:
                    print(f"{RED}Invalid message received{RESET}")
            except socket.timeout:
                print(f"{RED}Timeout reached, no offers received.{RESET}")
                break
            except Exception as e:
                print(f"{RED}Error receiving offer: {e}{RESET}")
                break

    def request_state(self):
        """Send a request message to the server with the file size."""
        try:
            request_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            request_socket.connect((self.server_ip, self.tcp_port))

            # Send request message: Magic cookie, request type, file size
            request_message = struct.pack('!IBQ', MAGIC_COOKIE, MSG_TYPE_REQUEST, self.file_size)
            request_socket.sendall(request_message)

            print(f"{GREEN}Sent request to {self.server_ip}:{self.tcp_port} with file size {self.file_size}{RESET}")

            self.state = "Speed Test"  # Transition to speed test
            request_socket.close()
        except Exception as e:
            print(f"{RED}Error in sending request: {e}{RESET}")
            self.state = "Looking for Server"

    def speed_test_state(self):
        """Start the TCP and UDP file transfers using multiple threads."""
        print(f"{CYAN}Starting speed test...{RESET}")

        # Launch multiple threads for TCP and UDP connections
        tcp_threads = []
        udp_threads = []
        
        for i in range(self.num_tcp_connections):
            tcp_thread = threading.Thread(target=self.transfer_file_tcp, args=(i + 1,))
            tcp_threads.append(tcp_thread)
            tcp_thread.start()

        for i in range(self.num_udp_connections):
            udp_thread = threading.Thread(target=self.transfer_file_udp, args=(i + 1,))
            udp_threads.append(udp_thread)
            udp_thread.start()

        # Wait for all threads to finish
        for thread in tcp_threads + udp_threads:
            thread.join()

        print(f"{GREEN}All transfers complete.{RESET}")

    def transfer_file_tcp(self, transfer_num):
        """Simulate transferring a file using TCP."""
        print(f"{MAGENTA}TCP transfer #{transfer_num} started...{RESET}")
        start_time = time.time()  # Start the timer for the transfer

        # Simulate transfer with a randomized delay for TCP (longer due to protocol overhead)
        delay = random.uniform(1.0, 1.5)  # Simulate a transfer time between 1 and 1.5 seconds
        time.sleep(delay)

        # Calculate elapsed time and transfer speed
        elapsed_time = time.time() - start_time
        transfer_speed = (self.file_size * 8) / elapsed_time  # Speed in bits per second

        print(f"{GREEN}TCP transfer #{transfer_num} finished, total time: {elapsed_time:.2f} seconds, total speed: {transfer_speed:.2f} bits/second{RESET}")

    def transfer_file_udp(self, transfer_num):
        """Simulate transferring a file using UDP."""
        print(f"{MAGENTA}UDP transfer #{transfer_num} started...{RESET}")
        start_time = time.time()  # Start the timer for the transfer

        # Simulate transfer with a randomized delay for UDP (faster than TCP)
        delay = random.uniform(0.5, 1.0)  # Simulate a transfer time between 0.5 and 1.0 seconds
        time.sleep(delay)

        # Calculate elapsed time and transfer speed
        elapsed_time = time.time() - start_time
        transfer_speed = (self.file_size * 8) / elapsed_time  # Speed in bits per second
        packet_loss_percentage = 0  # Dummy value for packet loss (adjust as needed)

        print(f"{GREEN}UDP transfer #{transfer_num} finished, total time: {elapsed_time:.2f} seconds, total speed: {transfer_speed:.2f} bits/second, percentage of packets received successfully: {100 - packet_loss_percentage}%{RESET}")

def main():
    client = Client()

    # Simulate client states in a sequential manner
    client.startup_state()
    client.looking_for_server_state()
    client.request_state()
    client.speed_test_state()

if __name__ == "__main__":
    main()
