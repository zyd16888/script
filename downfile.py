import requests
import time

# 定义一个函数下载文件
def download_file(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f'{filename} 下载完成')
    else:
        print(f'无法下载 {filename}，状态码: {response.status_code}')

# 创建一个字典存储文件URL和文件名
files = {
    "六年级下册Lesson 19_源.mp3": "https://res.wx.qq.com/voice/getvoice?mediaid=MzkwMjI2NzQ4MV8yMjQ3NTY1ODQw",
    "六年级下册Lesson 19_含翻译.mp3": "https://res.wx.qq.com/voice/getvoice?mediaid=MzkwMjI2NzQ4MV8yMjQ3NTY1ODQx",
    "六年级下册Lesson 20_源.mp3": "https://res.wx.qq.com/voice/getvoice?mediaid=MzkwMjI2NzQ4MV8yMjQ3NTY2NjM0",
    "六年级下册Lesson 20_含翻译.mp3": "https://res.wx.qq.com/voice/getvoice?mediaid=MzkwMjI2NzQ4MV8yMjQ3NTY2NjM1",
    "六年级下册Lesson 21_源.mp3": "https://res.wx.qq.com/voice/getvoice?mediaid=MzkwMjI2NzQ4MV8yMjQ3NTY2Nzgz",
    "六年级下册Lesson 21_含翻译.mp3": "https://res.wx.qq.com/voice/getvoice?mediaid=MzkwMjI2NzQ4MV8yMjQ3NTY2Nzg0",
    "六年级下册Lesson 22_源.mp3": "https://res.wx.qq.com/voice/getvoice?mediaid=MzkwMjI2NzQ4MV8yMjQ3NTY3MTQ1",
    "六年级下册Lesson 22_含翻译.mp3": "https://res.wx.qq.com/voice/getvoice?mediaid=MzkwMjI2NzQ4MV8yMjQ3NTY3MTQ2",
    "六年级下册Lesson 23_源.mp3": "https://res.wx.qq.com/voice/getvoice?mediaid=MzkwMjI2NzQ4MV8yMjQ3NTY4MjY5",
    "六年级下册Lesson 23_含翻译.mp3": "https://res.wx.qq.com/voice/getvoice?mediaid=MzkwMjI2NzQ4MV8yMjQ3NTY4Mjcw",
    "六年级下册Lesson 24_源.mp3": "https://res.wx.qq.com/voice/getvoice?mediaid=MzkwMjI2NzQ4MV8yMjQ3NTY4MzI0",
    "六年级下册Lesson 24_含翻译.mp3": "https://res.wx.qq.com/voice/getvoice?mediaid=MzkwMjI2NzQ4MV8yMjQ3NTY4MzI1",
    "六年级下册Unit 4 Again_源.mp3": "https://res.wx.qq.com/voice/getvoice?mediaid=MzkwMjI2NzQ4MV8yMjQ3NTY4NDAw",
    "六年级下册Unit 4 Again_含翻译.mp3": "https://res.wx.qq.com/voice/getvoice?mediaid=MzkwMjI2NzQ4MV8yMjQ3NTY4NDAx"
}


# 循环下载所有文件
for filename, url in files.items():
    time.sleep(1)
    download_file(url, filename)
