from mqtt_library import mqtt_connect, mqtt_publish, mqtt_disconnect
import time
import random

client_id = "temp-sensor-1"
sock = mqtt_connect("localhost", client_id)
print(f"[{client_id}] Connected to broker")

try:
    while True:
        temp = round(20 + random.random() * 5, 2)
        message = f"{temp}°C"
        mqtt_publish(sock, "sensors/temp", message)
        print(f"[{client_id}] Published: {message}")
        time.sleep(5)
finally:
    mqtt_disconnect(sock)
    print(f"[{client_id}] Disconnected")
