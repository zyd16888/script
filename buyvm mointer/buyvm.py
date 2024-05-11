import datetime
import datetime
from time import sleep
import requests
import re
from lxml import html
from sendNotify import send

# 打印当前时间
timenow = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print("当前时间：" + timenow)

# 发起 HTTP 请求
url = "https://my.frantech.ca/cart.php?gid=46"
server_urls = {
    "拉斯维加斯":"https://my.frantech.ca/cart.php?gid=37",
    "纽约":"https://my.frantech.ca/cart.php?gid=38",
    "迈阿密":"https://my.frantech.ca/cart.php?gid=48",
    "卢森堡":"https://my.frantech.ca/cart.php?gid=39"
}

block_storage = {
    "拉斯维加斯":"https://my.frantech.ca/cart.php?gid=42",
    "纽约":"https://my.frantech.ca/cart.php?gid=45",
    "迈阿密":"https://my.frantech.ca/cart.php?gid=49",
    "卢森堡":"https://my.frantech.ca/cart.php?gid=46"
}

message = ""
sendmsg = False
def get_server_url(name, url, xpath):
    global message  # Add this line to access the global variable 'message' within the function
    global sendmsg  # Also add this line to access the global variable 'sendmsg'

    response = requests.get(url)

    # 检查响应状态码
    if response.status_code == 200:
        # 使用 lxml 解析 HTML
        tree = html.fromstring(response.content)
        
        # 使用 XPath 查询匹配的元素
        packages = tree.xpath(xpath)
        
        # 输出匹配到的元素
        for index, package in enumerate(packages):
            # print(html.tostring(package, pretty_print=True, encoding='unicode'))
            try:
                package_name = package.xpath(".//h3[@class='package-name']/text()")[0].strip()
                package_qty_text = package.xpath(".//div[@class='package-qty']/text()")[0].strip()
            except:
                print("url {url} : Error: Unable to extract package quantity text")
                break
            # 使用正则表达式提取数字部分
            package_qty = re.search(r'\d+', package_qty_text).group()

            if index < 5 :
                print("Package Name:", package_name)
                print("Package Quantity:", package_qty)
                print("-" * 20)
                sendmsg = True
                if int(package_qty) > 0:
                    message += f"{name} : {package_name}, 数量: {package_qty} \n"
    else:
        print("Failed to fetch the page")

for key, value in server_urls.items():
    get_server_url(key, value, "//*[@class='package ']")
    sleep(1)

for key, value in block_storage.items():
    get_server_url(key, value, "//*[@class='package package-featured']")
    sleep(1)

if sendmsg:
    message += timenow
    message += timenow
    send("buyvm 补货提醒", message)
