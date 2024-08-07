# 清除kafka topic中的消息
import json
from kafka import KafkaProducer
from kafka import KafkaConsumer

producer = KafkaProducer(bootstrap_servers="192.168.195.10:9093")

# 删除topic
producer.send("sgyyDeviceSensorDataStorageTopic", b"delete_topic")
producer.flush()
