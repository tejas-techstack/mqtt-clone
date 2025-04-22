from mqtt_library import mqtt_connect, mqtt_subscribe, mqtt_receive, mqtt_disconnect

client_id = "water-level-monitor"
sock = mqtt_connect("localhost", client_id)
print(f"[{client_id}] Connected to broker")

mqtt_subscribe(sock, packet_id=1, topic="sensors/water-level")
print(f"[{client_id}] Subscribed to sensors/water-level")

try:
    while True:
        data = mqtt_receive(sock)
        if data:
            topic_len = (data[2] << 8) + data[3]
            topic = data[4:4+topic_len].decode()
            message = data[4+topic_len:].decode()
            print(f"[{client_id}] Received on '{topic}': {message}")
except BrokenPipeError as brokenPipe:
    print(f"Error occured : {brokenPipe}, this means the server crashed.")
    print("Disconnected by default.")
except:
    print(f"\nExiting (simulates clean exit)")
    mqtt_disconnect(sock)
    print(f"[{client_id}] Disconnected")
else:
    mqtt_disconnect(sock)
    print(f"[{client_id}] Disconnected")
