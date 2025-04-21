from mqtt_library import mqtt_connect, mqtt_publish, mqtt_disconnect
import time
import random

client_id = "water-level-sensor-1"
sock = mqtt_connect("localhost", client_id)
print(f"[{client_id}] Connected to broker")

try:
    while True:
        water_level = round(40 + random.random() * 5, 2)
        message = f"{water_level}m"
        mqtt_publish(sock, "sensors/water-level", message)
        print(f"[{client_id}] Published: {message}")
        time.sleep(5)
finally:
    mqtt_disconnect(sock)
    print(f"[{client_id}] Disconnected")
