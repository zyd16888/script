import json
import time

from kafka import KafkaProducer


producer = KafkaProducer(bootstrap_servers="192.168.195.10:9093")

# 时间格式化为 yyyy-MM-dd'T'HH:mm:ss.SSS'Z'  2022-05-30T15:26:57.000Z
now_time_str_format = time.strftime(
    "%Y-%m-%dT%H:%M:%S.000Z", time.localtime(time.time())
)

data = {
    "stationId": 223333,
    "sgyyDeviceId": 55555,
    "sgyyDeviceModuleId": 5555,
    "moduleTypeId": 66666,
    "data": 569.686,
    "time": now_time_str_format,
    "status": 1,
}


# 转换为json格式
data_json = json.dumps(data, ensure_ascii=False)
data_byte = data_json.encode("utf-8")
# 发送消息
print(data_byte)
producer.send("sgyyDeviceSensorDataStorageTopic", data_byte)
producer.flush()
