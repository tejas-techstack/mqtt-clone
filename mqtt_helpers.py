import socket

MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

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

