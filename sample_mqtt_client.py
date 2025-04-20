# mqtt_client.py
from mqtt_library import mqtt_connect, mqtt_publish
import time

host = "localhost"
client_id = "testclient"

sock = mqtt_connect(host, client_id)
print(sock, "Connected to broker")

mqtt_publish(sock, "test/topic", "Hello from client!")
print("Message published")

sock.close()
