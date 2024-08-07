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
    {"id": "0100005", "time": time_int, "Lev": "0.23",} ,
    {"id": "0100002", "time": time_int, "fire_alarm": "1",},
    {"id": "0100001", "time": time_int, "smoke_alarm": "1",},
    {"id": "0100001", "time": time_int, "temp_alarm": "1",},
    {"id": "0100001", "time": time_int, "is_gas_spray": "1",},
    {"id": "0100001", "time": time_int, "is_gas_out_poweroff": "1",},
    {"id": "0100001", "time": time_int, "is_gas_out_error": "1",},
    {"id": "0100001", "time": time_int, "is_gas_out_offline": "1",},
    {"id": "0100001", "time": time_int, "fan_state": "1",},
    {"id": "0100001", "time": time_int, "is_fan_poweroff": "1",},
    {"id": "0100001", "time": time_int, "low_waterlevel_alarm": "1",},
    {"id": "0100001", "time": time_int, "high_waterlevel_alarm": "1",},
    {"id": "0100001", "time": time_int, "wpump_state": "1",},
    {"id": "0100001", "time": time_int, "is_wpump_poweroff": "1",},
    {"id": "0100001", "time": time_int, "is_door_open": "1",},
    {"id": "0100001", "time": time_int, "is_monitor_error": "1",},
    {"id": "0100001", "time": time_int, "is_monitor_poweroff": "1",},
    {"id": "0100001", "time": time_int, "sug_wl_higher_alarm": "1",},
]

data2 = [{
    "id": "11223",
    "time": time_int,
    "Tmp": "36.5",
    "EnvHum": "27.6",
    "cable_sandwich_temp": "32.36",
    "cable_sandwich_hum": "29.6",
    "fire_alarm": "1",
    "smoke_alarm": "1",
    "temp_alarm": "1",
    "is_gas_spray": "1",
    "is_gas_out_poweroff": "1",
    "is_gas_out_error": "1",
    "is_gas_out_offline": "1",
    "fan_state": "1",
    "is_fan_poweroff": "1",
    "low_waterlevel_alarm": "1",
    "high_waterlevel_alarm": "1",
    "wpump_state": "1",
    "is_wpump_poweroff": "1",
    "is_door_open": "1",
    "is_monitor_error": "1",
    "is_monitor_poweroff": "1",
    "sug_wl_higher_alarm": "1", 
}]
# 转换为json格式
data_json = json.dumps(data, ensure_ascii=False)
data_byte = data_json.encode("utf-8")
# 发送消息
print(data_byte)
producer.send("send_device_sensor_signal_data", data_byte)
producer.flush()



