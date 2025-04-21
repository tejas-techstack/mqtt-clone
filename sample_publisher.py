# publisher_client.py
from mqtt_library import mqtt_connect, mqtt_publish, mqtt_disconnect
import time
import random

client_id = "temp-sensor"
sock = mqtt_connect("localhost", client_id)
print(f"[{client_id}] Connected to broker")

try:
    for i in range(5):  # publish 5 readings
        temp = round(20 + random.random() * 5, 2)
        message = f"{temp}°C"
        mqtt_publish(sock, "sensors/temp", message)
        print(f"[{client_id}] Published: {message}")
        time.sleep(2)
finally:
    mqtt_disconnect(sock)
    print(f"[{client_id}] Disconnected")
