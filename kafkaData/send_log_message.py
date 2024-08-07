import json
import time

from kafka import KafkaProducer


producer = KafkaProducer(bootstrap_servers="192.168.195.10:9093")

# 时间格式化为 yyyy-MM-dd'T'HH:mm:ss.SSS'Z'  2022-05-30T15:26:57.000Z
now_time_str_format = time.strftime(
    "%Y-%m-%dT%H:%M:%S.000Z", time.localtime(time.time())
)

data = {
    "stationId": "223",
    "stationGatewayId": "0",
    "deviceId": 0,
    "actionType": "sgyy",
    "parameterData": "{}",
    "resultData": "{}",
    "time": now_time_str_format,
}


# 转换为json格式
data_json = json.dumps(data, ensure_ascii=False)
data_byte = data_json.encode("utf-8")
# 发送消息
print(data_byte)
producer.send("messageLogBySgyyTopic", data_byte)
producer.flush()
