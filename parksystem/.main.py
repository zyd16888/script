import paho.mqtt.client as mqtt
import json
import uuid
from datetime import datetime
import argparse

# 设置命令行参数解析
parser = argparse.ArgumentParser(description="MQTT message sender")
parser.add_argument("-u", "--uniqueKey", type=str, default="Kyjzxbgx2kt_2", help="The unique key for the message")
parser.add_argument("-s", "--setvalue", type=str, default="2", help="The set value for the message")
args = parser.parse_args()

# MQTT连接配置
mqtt_broker = "localhost"
mqtt_port = 1883
mqtt_topic = "requestYKDataByUniqueKeys"
mqtt_username = "admin"  # 替换为实际的用户名
mqtt_password = ""  # 替换为实际的密码

# 生成动态的 sendtime 和 uuid
sendtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
message_uuid = str(uuid.uuid4())

# 消息内容
message = {
    "setvalue": args.setvalue,
    "uniqueKey": args.uniqueKey,
    "sendtime": sendtime,
    "uuid": message_uuid
}

# 转换消息为JSON格式
message_json = json.dumps(message)

# 创建MQTT客户端
client = mqtt.Client()

# 设置MQTT用户名和密码
client.username_pw_set(mqtt_username, mqtt_password)

# 连接到MQTT Broker
client.connect(mqtt_broker, mqtt_port, 60)

# 发布消息
client.publish(mqtt_topic, message_json)

# 断开连接
client.disconnect()

print(f"已发送消息: {message_json}")

