from dataclasses import dataclass
import json
import time

from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers="192.168.195.10:9093")


time_int = int(time.time() * 1000)


data = [
    {"id": "0100002", "time": time_int, "Tmp": "36.5",},
    {"id": "0100002", "time": time_int, "EnvHum": "27.6",},
    {"id": "0100002", "time": time_int, "cable_sandwich_temp": "32.36",},
    {"id": "0100003", "time": time_int, "cable_sandwich_hum": "29.6",},
    {"id": "0100005", "time": time_int, "Lev": "0.23",},
]

data2 = {
    "id": "11223",
    "time": time_int,
    "Tmp": "36.5",
    "EnvHum": "27.6",
    "cable_sandwich_temp": "32.36",
    "cable_sandwich_hum": "29.6",
}

# 转换为json格式
data_json = json.dumps(data, ensure_ascii=False)
data_byte = data_json.encode("utf-8")
# 发送消息
print(data_byte)
# producer.send("send_device_sensor_measure_data", data_byte)
# producer.flush()
