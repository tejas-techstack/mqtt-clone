# run_broker.py
from mqtt_broker import start_broker

if __name__ == "__main__":
    start_broker(host='localhost', port=1883)
