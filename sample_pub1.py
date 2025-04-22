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
        time.sleep(2)
except BrokenPipeError as brokenPipe:
    print(f"Error occured : {brokenPipe}, this means the server crashed.")
    print("Disconnected by default.")
except (Exception, KeyboardInterrupt) as e:
    print(f"\nExiting due to {e}: (simulates clean exit)")
    mqtt_disconnect(sock)
    print(f"[{client_id}] Disconnected")
else:
    mqtt_disconnect(sock)
    print(f"[{client_id}] Disconnected")
