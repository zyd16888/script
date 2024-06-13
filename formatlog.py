import re

def extract_low_latency_ips(filepath, threshold=145):
    # 读取文档内容
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()

    # 使用正则表达式匹配IP地址、端口号和延迟信息
    ip_port_latency_pattern = r"发现有效IP (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) 端口 (\d{1,5}) 位置信息 .*? 延迟 (\d+) 毫秒"
    matches = re.findall(ip_port_latency_pattern, content)

    # 筛选延迟低于阈值的IP地址和端口号
    low_latency_ips = [(ip, port) for ip, port, latency in matches if int(latency) < threshold]

    # 将结果写入文件
    with open("low_latency_ips.txt", "w", encoding="utf-8") as output_file:
        for ip, port in low_latency_ips:
            output_file.write("IP地址: " + ip + ", 端口号: " + port + "\n")

# 调用函数并传递文件路径参数
extract_low_latency_ips(r"C:\Users\zyd47\Downloads\20240409085155.log")



