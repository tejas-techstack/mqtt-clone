from mqtt_library import mqtt_connect, mqtt_subscribe, mqtt_receive, mqtt_disconnect

client_id = "temp-monitor"
sock = mqtt_connect("localhost", client_id)
print(f"[{client_id}] Connected to broker")

suback = mqtt_subscribe(sock, packet_id=1, topic="sensors/temp")
if not suback:
    print("Error with suback")
    exit(0)

print(f"[{client_id}] Subscribed to sensors/temp")

try:
    while True:
        data = mqtt_receive(sock)
        if data:
            topic_len = (data[2] << 8) + data[3]
            topic = data[4:4+topic_len].decode()
            message = data[4+topic_len:].decode()
            print(f"[{client_id}] Received on '{topic}': {message}")
finally:
    mqtt_disconnect(sock)
    print(f"[{client_id}] Disconnected")
