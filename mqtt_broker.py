# mqtt_broker.py
import socket
import threading
from mqtt_library import *

#mappings
topics ={} #topic -> [message array] 
subscribers ={} #topic -> set of client sockets
client_subs = {} #client socket->set of topics subscribed
connected_clients = set()

# When a publish message with a new topic arives just
# add it to a new queue.
def create_topic(topic):
    topics[topic] = []
    subscribers[topic] = set()
    print(f"New Topic Created : {topic}")


# if publish message comes to existing topic add it to
# that topics queue. if topic does not exist call create_topic
def append_to_topic(topic, message):
    if topic in topics:
        topics[topic].append(message)
    else:
        print(f"Topic {topic} does not exist, creating new topic")
        create_topic(topic)
        topics[topic].append(message)

    republish_topics(topic)

# whenever you get a new publish message after appending to queue.
# publish the queues messages to its respective subscribers.
def republish_topics(topic):
    for subscriber in subscribers.get(topic, []):
        try:
            message= topics[topic][-1] #the last message in a given topic
            mqtt_publish(subscriber, topic, message)
        except Exception as e:
            print(f"Failed to send to subscriber: {e}")

# when receive a subscribe message add the client to that subscriber.
# if that topic doesnt exist call create_topic and add subscriber to it.
def add_subscriber(topic, client_socket):
    if topic not in topics:
        create_topic(topic)
    subscribers[topic].add(client_socket)
    if client_socket not in client_subs:
        client_subs[client_socket] = set()

    client_subs[client_socket].add(topic)
    print("Client subscribed to topic!")

# need to edit this such that it takes in multiple
# requests.
# Some work is left in the library so that the client can send
# a disconnect request, will implement. - done somewhat
# also make it such that the client breaks connection only when a 
# disconnect message comes.
def handle_client(client_socket, addr):
    print(f"Client connected from {addr}")
    connected_clients.add(client_socket)
    try:
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break

                packet_type, remaining_length, index = unpack_fixed_header(data)

                # CONNECT
                if packet_type == 0x10:  
                    print("Received CONNECT packet")
                    # Send CONNACK
                    mqtt_connack(client_socket)

                # PUBLISH
                elif packet_type == 0x30: 
                    topic, i = decode_string(data, index)
                    message = data[i:].decode()
                    append_to_topic(topic, message)
                    print(f"Received message on topic '{topic}': {message}")
 
                # SUBSCRIBE
                elif packet_type == 0x82:
                    topic, i = decode_string(data, index + 2)
                    print(f"Received SUBSCRIBE for topic '{topic}'")
                    add_subscriber(topic, client_socket)

                    # Send SUBACK
                    mqtt_suback(client_socket)

                    # send last message of topic.
                    if topics[topic]:
                        last_message = topics[topic][-1]
                        mqtt_publish(client_socket, topic, last_message)

                # DISCONNECT
                elif packet_type == 0xE0: 
                        print("Received DISCONNECT")
                        for topic in client_subs.get(client_socket, []):
                            subscribers[topic].discard(client_socket)
                        client_subs.pop(client_socket, None)
                        client_socket.close()
                        break
                else:
                    print(f"Unknown packet type: {hex(packet_type)}")

            except Exception as e:
                print("Error here:", e)
                break
    finally:
        connected_clients.discard(client_socket)
        client_socket.close()

def start_broker(host='0.0.0.0', port=1883):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Broker listening on {host}:{port}")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            thread.start()
    except KeyboardInterrupt:
        print("\nBroker shutting down. (simulates clean exit for broker)")
    finally:
        print("Disconnecting all clients")
        for client in list(connected_clients):
            try:
                client.shutdown(socket.SHUT_RDWR)
                client.close()
            except Exception as e:
                print(f"Error disconnecting client: {e}")
        server_socket.close()
        print("Server socket closed.")
        return

if __name__ == "__main__":
    start_broker()

