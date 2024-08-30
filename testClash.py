import requests
import pandas as pd


def test_versions_from_csv(csv_file, token):
    # 读取CSV文件
    df = pd.read_csv(csv_file)

    # 循环遍历每一行，获取IP和Port并调用get_version函数
    for index, row in df.iterrows():
        ip = row["ip"]
        port = row["port"]
        print(f"Testing IP: {ip}, Port: {port}")
        result = get_version(ip, port, token)
        print(f"Result for {ip}:{port} -> {result}\n")


def get_version(address, port, token):
    url = f"http://{address}:{port}/version"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()  # 假设返回的是JSON格式的数据
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"


# 示例调用
csv_file = "a44dd5f6f3_202408271410资产数据.csv"
token = "123456"


test_versions_from_csv(csv_file, token)
