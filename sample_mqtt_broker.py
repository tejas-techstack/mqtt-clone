# mqtt_broker.py
import socket
from mqtt_helpers import decode_string, unpack_fixed_header

def start_broker(host='0.0.0.0', port=1883):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Broker listening on {host}:{port}")

    client_socket, addr = server_socket.accept()
    print(f"Client connected from {addr}")

    # Receive CONNECT
    data = client_socket.recv(1024)
    packet_type, remaining_length, index = unpack_fixed_header(data)
    print("Packet type:", hex(packet_type))

    if packet_type == 0x10:  # CONNECT
        print("Received CONNECT packet")

        # Send CONNACK
        connack = bytes([0x20, 0x02, 0x00, 0x00])
        client_socket.sendall(connack)
        print("Sent CONNACK")

    # Wait for PUBLISH
    data = client_socket.recv(1024)
    packet_type, remaining_length, index = unpack_fixed_header(data)

    if packet_type == 0x30:  # PUBLISH
        topic, i = decode_string(data, index)
        message = data[i:].decode()
        print(f"Received message on topic '{topic}': {message}")

    client_socket.close()
    server_socket.close()

if __name__ == "__main__":
    start_broker()

