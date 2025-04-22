import socket
import ssl

MQTT_PORT = 8883
MQTT_KEEPALIVE = 60

def mqtt_connect(host, client_id):
    raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE  # Change to CERT_REQUIRED in production
    ssl_sock = context.wrap_socket(raw_sock, server_hostname=host)

    ssl_sock.connect((host, MQTT_PORT))
    ssl_sock.sendall(pack_connect(client_id))

    connack = ssl_sock.recv(4)
    if len(connack) != 4 or connack[0] != 0x20 or connack[3] != 0x00:
        raise Exception("Connection failed or malformed CONNACK")
    print("Received Connack")

    print(f"Socket type: {type(ssl_sock)}")
    if hasattr(ssl_sock, 'cipher'):
        print("[SSL] Secure connection established.")
        print("Cipher used:", ssl_sock.cipher())
    else:
        print("[WARNING] Connection is not using SSL!")
    return ssl_sock

def mqtt_disconnect(sock):
    sock.sendall(bytes([0xE0, 0x00]))
    sock.close()

def mqtt_publish(sock, topic, message):
    packet = pack_publish(topic, message)
    sock.sendall(packet)

# Returns true if succeded and false if not.
def mqtt_subscribe(sock, packet_id, topic):
    packet = pack_subscribe(packet_id, topic)
    sock.sendall(packet)

    suback = mqtt_receive(sock)
    if suback[0] != 0x90:
        print(f"Error: Invalid packet type:{suback[0]}")
        return False
    return True

def mqtt_connack(sock):
    connack = bytes([0x20, 0x02, 0x00, 0x00])
    sock.sendall(connack)
    print("Sent CONNACK")

def mqtt_suback(sock):
    suback = bytes([0x90, 3, 0x00, 0x00])
    sock.sendall(suback)
    print("Sent SUBACK")

def mqtt_receive(sock, buffer_size=1024):
    return sock.recv(buffer_size)

def encode_remaining_length(length):
    encoded = bytearray()
    while True:
        byte = length % 128
        length //= 128
        if length > 0:
            byte |= 0x80
        encoded.append(byte)
        if length == 0:
            break
    return bytes(encoded)

def pack_fixed_header(packet_type, remaining_length):
    return bytes([packet_type]) + encode_remaining_length(remaining_length)

def unpack_fixed_header(data):
    packet_type = data[0]
    multiplier = 1
    value = 0
    index = 1
    while True:
        if index >= len(data):
            raise ValueError("Malformed fixed header: incomplete remaining length")

        byte = data[index]
        value += (byte & 127) * multiplier
        index += 1
        if (byte & 128) == 0:
            break
        multiplier *= 128
    return packet_type, value, index

def encode_string(s):
    encoded = s.encode()
    length = len(encoded)
    return bytes([length >> 8, length & 0xFF]) + encoded

def decode_string(data, index):
    length = (data[index] << 8) + data[index + 1]
    index += 2
    return data[index:index+length].decode(), index + length

def pack_connect(client_id):
    protocol_name = "MQTT"
    keepalive = MQTT_KEEPALIVE

    payload = encode_string(client_id)
    variable_header = (
        encode_string(protocol_name) +
        bytes([4]) +
        bytes([2]) +
        bytes([keepalive >> 8, keepalive & 0xFF])
    )

    remaining_length = len(variable_header) + len(payload)
    fixed_header = pack_fixed_header(0x10, remaining_length)

    return fixed_header + variable_header + payload

def pack_publish(topic, message):
    topic_encoded = encode_string(topic)
    message_encoded = message.encode()

    variable_header = topic_encoded
    payload = message_encoded

    remaining_length = len(variable_header) + len(payload)
    fixed_header = pack_fixed_header(0x30, remaining_length)

    return fixed_header + variable_header + payload

def pack_subscribe(packet_id, topic):
    topic_encoded = encode_string(topic) + bytes([0])
    variable_header = bytes([packet_id >> 8, packet_id & 0xFF])

    remaining_length = len(variable_header) + len(topic_encoded)
    fixed_header = pack_fixed_header(0x82, remaining_length)

    return fixed_header + variable_header + topic_encoded

