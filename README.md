# mqtt-clone
A simple clone of mqtt library for a college project

### how to use

Generate Certificates:
`openssl req -x509 -newkey rsa:2048 -nodes -keyout server.key -out server.crt -days 365`

Start the broker first:
`python3 mqtt_broker.py`

Run the clients:
  There are a pair of two test clients, each pair has a publisher and subscriber.
  These two pairs each send data at a 2 second interval.
  There is also `sample_pub3.py` which allows user input for publishing data.

Run the publisher:
`python3 sample_pub1.py`

Run the subscriber:
`python3 sample_sub1.py`

You can safely exit by causing a keyboard interrupt.
