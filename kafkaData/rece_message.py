from enum import auto
from kafka import KafkaConsumer

# 接收消息
consumer = KafkaConsumer(
    "send_station_info",
    group_id="rece_station_info",
    bootstrap_servers="192.168.195.10:9093",
    auto_commit_interval_ms=1000,
    enable_auto_commit=True,
)
consumer.commit()
# consumer.commit()
# for message in consumer:
#     print(
#         "%s:%d:%d: key=%s value=%s"
#         % (
#             message.topic,
#             message.partition,
#             message.offset,
#             message.key,
#             message.value.decode("utf-8"),
#         )
#     )
# consumer.commit()
consumer.close()

# # 消费历史消息
# consumer = KafkaConsumer(bootstrap_servers="192.168.195.10:9093")
# consumer.subscribe(["send_station_info"])
# # 设置消费位置
# consumer.seek_to_end()

# for message in consumer:
#     print(message)
#     print("*" * 20)
#     print(message.value.decode("utf-8"))
#     # 确认消息已经消费
#     consumer.commit()
