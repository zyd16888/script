import requests
import socket
from urllib.parse import urlparse
from requests.auth import HTTPBasicAuth


def generate_upstream_format(url):
    # 解析URL获取主机和端口信息
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    port = (
        parsed_url.port
        if parsed_url.port
        else 80 if parsed_url.scheme == "http" else 443
    )

    # 生成符合upstream格式的字符串
    return f"server {host}:{port};"


def test_ip_connectivity(url, auth_username, auth_password):
    try:
        # 解析URL获取主机和端口信息
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        port = (
            parsed_url.port
            if parsed_url.port
            else 80 if parsed_url.scheme == "http" else 443
        )

        # 创建一个套接字对象
        sock = socket.create_connection((host, port), timeout=2)

        # 连接成功后，进行HTTP身份验证和文件访问测试
        auth = HTTPBasicAuth(auth_username, auth_password)
        response = requests.get(url + "/tvbox/cat/my_cat.json", auth=auth, timeout=2)

        if response.status_code == 200:
            # 连接成功且访问文件成功，返回upstream格式的信息
            return generate_upstream_format(url)
        else:
            # 访问文件失败，返回异常信息
            return f"# {url} 访问文件异常: {response.status_code}"
    except (socket.timeout, socket.error, requests.RequestException) as e:
        # 连接失败，返回异常信息
        return f"# {url} 连通异常: {str(e)}"


def test_url_list(url_list, auth_username, auth_password):
    successful_connections = []
    failed_connections = []

    for url in url_list:
        result = test_ip_connectivity(url, auth_username, auth_password)
        if "异常" in result:
            failed_connections.append(result)
        else:
            successful_connections.append(result)

    # 打印符合upstream格式的正常连接信息
    print("upstream配置格式（正常的地址）：")
    print("\n".join(successful_connections))

    # 打印全部异常连接信息
    print("\n异常的地址：")
    print("\n".join(failed_connections))


if __name__ == "__main__":
    # 你的URL列表，以列表形式提供
    url_list = [
        "http://218.201.52.7:5678/",
        "http://175.0.37.215:5678/",
        "http://221.232.197.114:5678/",
        "http://59.61.48.35:5678/",
    ]

    # HTTP身份验证的用户名和密码
    auth_username = "alist"
    auth_password = "alist"

    # 测试URL列表中的连通性
    test_url_list(url_list, auth_username, auth_password)
