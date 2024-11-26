from kafka import KafkaConsumer
import json

KAFKA_TOPIC = 'pcap_stream_new'  # Use the topic name from your producer
KAFKA_SERVER = 'localhost:9092'  # Ensure this matches your Kafka server configuration

# Create a Kafka consumer
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=[KAFKA_SERVER],
    value_deserializer=lambda x: x.decode('utf-8'),#json.loads(x.decode('utf-8')),
    auto_offset_reset='earliest',  # Ensures it starts reading from the beginning
    enable_auto_commit=True
)



print("Consuming messages from topic:", KAFKA_TOPIC)

# Consume and print messages

for message in consumer:
    print(type(message))


