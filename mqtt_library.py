import socket
from mqtt_helpers import *

MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

def mqtt_connect(host, client_id):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, 1883))
    s.sendall(pack_connect(client_id))

    connack = s.recv(4)
    if connack[0] != 0x20 or connack[3] != 0x00:
        raise Exception("Connection failed")

    return s

def mqtt_disconnect(sock):
    sock.sendall(bytes([0xE0, 0x00]))
    sock.close()

def mqtt_publish(sock, topic, message):
    packet = pack_publish(topic, message)
    sock.sendall(packet)

def mqtt_subscribe(sock, packet_id, topic):
    packet = pack_subscribe(packet_id, topic)
    sock.sendall(packet)

def mqtt_receive(sock, buffer_size=1024):
    return sock.recv(buffer_size)
