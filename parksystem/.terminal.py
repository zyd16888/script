import paho.mqtt.client as mqtt
import json
import uuid
from datetime import datetime
import argparse


# 配置MQTT连接信息
MQTT_BROKER = "127.0.0.1"  # MQTT 代理地址
MQTT_PORT = 1883                  # MQTT 端口
MQTT_TOPIC = "requestYKDataByTerminalKey"          # 发布的主题
MQTT_USERNAME = "admin"    # MQTT 用户名
MQTT_PASSWORD = ""    # MQTT 密码

# 定义所有可能的消息
messages = {
    "5": {
        "terminalKey": "5",
        "list": [
            {"setvalue": "0", "uniqueKey": "Kyjzxd2dg_04", "sendtime": "2024-09-20 20:34:47"},
            {"setvalue": "0", "uniqueKey": "Kyjzxd2dg_03", "sendtime": "2024-09-20 20:34:47"},
            {"setvalue": "0", "uniqueKey": "Kyjzxd2dg_02", "sendtime": "2024-09-20 20:34:47"},
            {"setvalue": "0", "uniqueKey": "Kyjzxd2dg_01", "sendtime": "2024-09-20 20:34:47"}
        ],
        "uuid": "8a040214-29d5-46e0-ac28-c33d16745d5e"
    },
    "6": {
        "terminalKey": "6",
        "list": [
            {"setvalue": "0", "uniqueKey": "Kyjzxd1dg_03", "sendtime": "2024-09-20 20:33:47"},
            {"setvalue": "0", "uniqueKey": "Kyjzxd1dg_02", "sendtime": "2024-09-20 20:33:47"},
            {"setvalue": "0", "uniqueKey": "Kyjzxd1dg_01", "sendtime": "2024-09-20 20:33:47"},
            {"setvalue": "0", "uniqueKey": "Kyjzxd1_06", "sendtime": "2024-09-20 20:33:47"},
            {"setvalue": "0", "uniqueKey": "Kyjzxd1_04", "sendtime": "2024-09-20 20:33:47"}
        ],
        "uuid": "5d7227eb-0841-4e9c-a7f9-fbf53d4c7e32"
    },
    "7": {
        "terminalKey": "7",
        "list": [
            {"setvalue": "0", "uniqueKey": "Kyjzxbgx1dg_3", "sendtime": "2024-09-20 20:33:08"},
            {"setvalue": "0", "uniqueKey": "Kyjzxbgx1dg_2", "sendtime": "2024-09-20 20:33:08"},
            {"setvalue": "0", "uniqueKey": "Kyjzxbgx1dg_1", "sendtime": "2024-09-20 20:33:08"}
        ],
        "uuid": "abdd56a9-7bca-4e4c-9ff2-7e2b004b0d61"
    },
    "8": {
        "terminalKey": "8",
        "list": [
            {"setvalue": "0", "uniqueKey": "Kyjzxbgx2dg_4", "sendtime": "2024-09-20 20:32:08"},
            {"setvalue": "0", "uniqueKey": "Kyjzxbgx2dg_3", "sendtime": "2024-09-20 20:32:08"},
            {"setvalue": "0", "uniqueKey": "Kyjzxbgx2dg_2", "sendtime": "2024-09-20 20:32:08"},
            {"setvalue": "0", "uniqueKey": "Kyjzxbgx2dg_1", "sendtime": "2024-09-20 20:32:08"}
        ],
        "uuid": "85fb80b2-4376-4227-a415-6553c32213fc"
    },
    "9": {
        "terminalKey": "9",
        "list": [
            {"setvalue": "0", "uniqueKey": "Kpxs1dg_06", "sendtime": "2024-09-20 20:31:08"},
            {"setvalue": "0", "uniqueKey": "Kpxs1dg_05", "sendtime": "2024-09-20 20:31:08"},
            {"setvalue": "0", "uniqueKey": "Kpxs1dg_04", "sendtime": "2024-09-20 20:31:08"},
            {"setvalue": "0", "uniqueKey": "Kpxs1dg_03", "sendtime": "2024-09-20 20:31:08"},
            {"setvalue": "0", "uniqueKey": "Kpxs1dg_02", "sendtime": "2024-09-20 20:31:08"},
            {"setvalue": "0", "uniqueKey": "Kpxs1dg_01", "sendtime": "2024-09-20 20:31:08"},
            {"setvalue": "0", "uniqueKey": "Kpxs1_02", "sendtime": "2024-09-20 20:31:08"}
        ],
        "uuid": "1ab2b596-d551-47d2-9c76-927e213ab2f9"
    },
    "10": {
        "terminalKey": "10",
        "list": [
            {"setvalue": "1", "uniqueKey": "Kblqdg_08", "sendtime": "current_time"},
            {"setvalue": "1", "uniqueKey": "Kblqdg_07", "sendtime": "current_time"},
            {"setvalue": "1", "uniqueKey": "Kblqdg_06", "sendtime": "current_time"},
            {"setvalue": "1", "uniqueKey": "Kblqdg_05", "sendtime": "current_time"},
            {"setvalue": "1", "uniqueKey": "Kblqdg_04", "sendtime": "current_time"},
            {"setvalue": "1", "uniqueKey": "Kblqdg_03", "sendtime": "current_time"},
            {"setvalue": "1", "uniqueKey": "Kblqdg_02", "sendtime": "current_time"},
            {"setvalue": "1", "uniqueKey": "Kblqdg_01", "sendtime": "current_time"}
        ],
        "uuid": "123456789"
    }
}


def build_message(terminal_key, setvalue):
    message = messages.get(terminal_key)
    if message:
        # 更新每个列表项的 setvalue 和 sendtime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for item in message['list']:
            item['setvalue'] = str(setvalue)
            item['sendtime'] = current_time  # 使用当前时间

        # 生成新的随机 UUID
        message['uuid'] = str(uuid.uuid4())

        return json.dumps(message)
    return None


# 连接到MQTT并发布消息
def publish_message(terminal_key, setvalue):
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)  # 设置用户名和密码
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    message = build_message(terminal_key, setvalue)
    if message:
        client.publish(MQTT_TOPIC, message)
        print(f"Published message: {message}")
    else:
        print(f"No message found for terminalKey: {terminal_key}")

    client.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send MQTT messages based on terminalKey and setvalue")
    parser.add_argument("-t", "--terminalKey", required=True, help="Specify the terminalKey to send the message for")
    parser.add_argument("-s", "--setvalue", required=True, type=int, help="Specify the setvalue (0 or 1)")
    
    args = parser.parse_args()
    
    publish_message(args.terminalKey, args.setvalue)
