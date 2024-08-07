import json
from kafka import KafkaProducer
from kafka import KafkaConsumer

producer = KafkaProducer(bootstrap_servers="192.168.195.10:9093")

data = [
    {"id": "0100001", "name": "测试预装室配电室1",},
    {"id": "0100002", "name": "测试预装室配电室2",},
    {"id": "0100003", "name": "测试预装室配电室3",},
    {"id": "0100004", "name": "测试预装室配电室4",},
    {"id": "0100005", "name": "测试预装室配电室5",},
    {"id": "0100006", "name": "测试预装室配电室6",},
]
# 转换为json格式
data_json = json.dumps(data, ensure_ascii=False)
print(data_json)
# byte编码
data_byte = data_json.encode("utf-8")
# 发送消息
producer.send("send_station_info", data_byte)
# 提交
producer.flush()

