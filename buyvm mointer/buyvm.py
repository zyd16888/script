import datetime
import datetime
from time import sleep
import requests
import re
from lxml import html
from sendNotify import send
import schedule



# Function to save current results to file
def save_results_to_file(results):
    with open("previous_results.txt", "w") as file:
        file.write(results)

def run_task():
    # 打印当前时间
    timenow = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("当前时间：" + timenow)
    message = ""

    # Load previous results from file
    try:
        with open("previous_results.txt", "r") as file:
            previous_results = file.read()
    except FileNotFoundError:
        previous_results = ""

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

    
    for key, value in server_urls.items():
        current_results = get_server_url(key, value, "//*[@class='package ']")
        message += current_results
        sleep(1)

    for key, value in block_storage.items():
        current_results = get_server_url(key, value, "//*[@class='package package-featured']")
        message += current_results
        sleep(1)
    
    if message != previous_results:
        save_results_to_file(message)
        message += timenow
        send("buyvm 补货提醒", message)
        

def get_server_url(name, url, xpath):
    # global message  # Add this line to access the global variable 'message' within the function
    # global sendmsg  # Also add this line to access the global variable 'sendmsg'

    response = requests.get(url)
    current_results = ""

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
                if int(package_qty) > 0:
                    # sendmsg = True
                    # message += f"{name} : {package_name}, 数量: {package_qty} \n"
                    current_results += f"{name} : {package_name}, 数量: {package_qty} \n"
    else:
        print("Failed to fetch the page")
    return current_results

# Schedule the task to run every hour
schedule.every(3).minutes.do(run_task)

# Infinite loop to keep the script running
while True:
    schedule.run_pending()
    sleep(1)
