import socket
from mqtt_helpers import pack_connect, pack_publish, pack_subscribe

broker_host = '127.0.0.1'
broker_port = 1883

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((broker_host, broker_port))

# Send CONNECT
sock.sendall(pack_connect("client1"))
print("Sent CONNECT")

# Wait for CONNACK
print("CONNACK:", sock.recv(1024))

# Subscribe to a topic
sock.sendall(pack_subscribe(1, "hello/topic"))
print("Sent SUBSCRIBE")

# Wait for SUBACK
print("SUBACK:", sock.recv(1024))

# Send a message
sock.sendall(pack_publish("hello/topic", "Hiii MQTT world! 💫"))
print("Sent PUBLISH")

# Wait for the published message (echoed back by broker)
print("Incoming PUBLISH:", sock.recv(1024))

# Disconnect
sock.sendall(bytes([0xE0, 0x00]))
print("Sent DISCONNECT")
sock.close()
