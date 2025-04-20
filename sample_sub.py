# subscriber_client.py
from mqtt_library import mqtt_connect, mqtt_subscribe, mqtt_receive

client_id = "temp-display"
sock = mqtt_connect("localhost", client_id)
print(f"[{client_id}] Connected to broker")

mqtt_subscribe(sock, packet_id=1, topic="sensors/temp")
print(f"[{client_id}] Subscribed to 'sensors/temp'")

try:
    while True:
        msg = mqtt_receive(sock)
        if msg:
            print(f"[{client_id}] Received raw message: {msg}")
except KeyboardInterrupt:
    print(f"[{client_id}] Stopping subscriber.")
