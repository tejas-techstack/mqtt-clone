from mqtt_library import mqtt_connect, mqtt_publish, mqtt_disconnect
import time
import random

client_id = "temp-sensor-1"
sock = mqtt_connect("localhost", client_id)
print(f"[{client_id}] Connected to broker")

try:
    choice = True
    while choice:
        topic, message = eval(input("Enter input as (\"topic\", \"message\"):"))
        mqtt_publish(sock, topic, message)
        print(f"[{client_id}] Published: {message}")
        choice = input("Continue (y/n):")
        if choice == "n":
            break

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
