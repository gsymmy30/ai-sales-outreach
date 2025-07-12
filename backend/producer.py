import os
import json
from dotenv import load_dotenv
from confluent_kafka import Producer

load_dotenv()

TOPIC_NAME = os.getenv("KAFKA_TOPIC", "email-events")

conf = {
    'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    'security.protocol': os.getenv("KAFKA_SECURITY_PROTOCOL", "SASL_SSL"),
    'sasl.mechanisms': os.getenv("KAFKA_MECHANISM", "SCRAM-SHA-256"),
    'sasl.username': os.getenv("KAFKA_USERNAME"),
    'sasl.password': os.getenv("KAFKA_PASSWORD"),
}

producer = Producer(conf)

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def send_email_event(data: dict):
    producer.produce(
        topic=TOPIC_NAME,
        value=json.dumps(data).encode("utf-8"),
        callback=delivery_report
    )
    producer.flush()
