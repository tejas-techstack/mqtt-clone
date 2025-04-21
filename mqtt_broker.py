# mqtt_broker.py
import socket
from mqtt_helpers import decode_string, unpack_fixed_header

# implement queue management for the topics.

# also keep track of clients, their subscriptions and the last messsage recieved from that 
# particular topic.
# when the client joins make sure that the new messages from those particular queues are
# published to the client

#mappings
topics ={} #topic -> [message array] 
subscribers ={} #topic -> set of client sockets
client_subs = {} #client socket->set of topics subscribed



# When a publish message with a new topic arives just
# add it to a new queue.
def create_topic(topic):
    if topic not in topics:
        topics[topic] = []
        subscribers[topic] = set()
        print(f"New Topic Created : {topic}")


# if publish message comes to existing topic add it to
# that topics queue. if topic does not exist call create_topic
def append_to_topic(topic, message):
    if topic in topics:
        topics[topic].append(message)
        print("Appended message to existing topic")
    else:
        print("Topic does not exist, creating new topic")
        create_topic(topic)
        topics[topic].append(message)

    republish_topics(topic)

# whenever you get a new publish message after appending to queue.
# publish the queues messages to its respective subscribers.
def republish_topics(topic):
    for subscriber in subscribers.get(topic, []):
        try:
            message= topics[topic][-1] #the last message in a given topic
            fire_publish(subscriber, topic, message)
            print("sent message to subscriber, on given topic")
        except Exception as e:
            print("FAILURE")

# when receive a subscribe message add the client to that subscriber.
# if that topic doesnt exist call create_topic and add subscriber to it.
def add_subscriber(topic, client_socket):
    create_topic(topic)
    subscribers[topic].add(client_socket)
    if client_socket not in client_subs:
        client_subs[client_socket] = set()
    
    client_subs[client_socket].add(topic)
    print("client subbed to topic congrats")
    # if client alrd subscribed, do not send the last message
    if client_socket in client_subs and topic in client_subs[client_socket]:
        print("Already subscribed to topic")
        return

#sending last message acc mqtt spec
    if topics[topic]:
        last_message = topics[topic][-1]
        fire_publish(client_socket, topic, last_message)



def fire_publish(client_socket, topic, message):
    topic_encoded = topic.encode()
    topic_length = len(topic_encoded)
    payload = topic_encoded + message.encode()
    fixed_header = bytes([0x30, 2 + topic_length + len(message)])
    variable_header = len(topic_encoded).to_bytes(2, 'big') + topic_encoded
    packet = fixed_header + variable_header + message.encode()
    client_socket.sendall(packet)

# need to edit this such that it takes in multiple
# requests.
# Some work is left in the library so that the client can send
# a disconnect request, will implement. - done somewhat
# also make it such that the client breaks connection only when a 
# disconnect message comes.
def start_broker(host='0.0.0.0', port=1883):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #allows multiple req
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Broker listening on {host}:{port}")

    client_socket, addr = server_socket.accept()
    print(f"Client connected from {addr}")

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("Client disconnected")
                break

            packet_type, remaining_length, index = unpack_fixed_header(data)

            # CONNECT
            if packet_type == 0x10:  
                print("Received CONNECT packet")
                # Send CONNACK
                connack = bytes([0x20, 0x02, 0x00, 0x00])
                client_socket.sendall(connack)
                print("Sent CONNACK")

             # PUBLISH
            elif packet_type == 0x30: 
                topic, i = decode_string(data, index)
                message = data[i:].decode()
                print(f"Received message on topic '{topic}': {message}")
                append_to_topic(topic, message)
            
              # SUBSCRIBE
            elif packet_type == 0x82:
                #skipping packet id, only 2 bytes, QoS not really impl here
                # only  single-topic subscription implemented
                topic, i = decode_string(data, index + 2)
                print(f"Received SUBSCRIBE for topic '{topic}'")
                add_subscriber(topic, client_socket)
                # Send SUBACK
                suback = bytes([0x90, 3, 0x00, 0x00])
                client_socket.sendall(suback)
                print("Sent SUBACK")
                _, i = decode_string(data, index + 2)
                topic, _ = decode_string(data, i)
                add_subscriber(topic, client_socket)

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
            
        # client_socket.close()
        # server_socket.close()   
        except Exception as e:  
            print("Error:", e)
            break

if __name__ == "__main__":
    start_broker()

