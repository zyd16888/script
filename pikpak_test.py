import requests

# 设置请求的URL和头部信息
url = 'https://user.mypikpak.com/v1/auth/token'
headers = {'Content-Type': 'application/x-www-form-urlencoded'}

# 设置请求的数据
data = {
    'client_id': 'YNxT9w7GMdWvEOKa',
    'client_secret': 'dbw2OtmVEeuUvIptb1Coyg',
    'grant_type': 'password',
    'username': 'tangled.mist@email.ml',  # 替换为你的用户名
    'password': 'tangled.666'   # 替换为你的密码
}

# 发送POST请求
response = requests.post(url, headers=headers, data=data)

# 检查请求是否成功
if response.status_code == 200:
    print('请求成功:')
    print(response.json())  # 打印返回的JSON数据
else:
    print(f'请求失败，状态码: {response.status_code}')
    print(response.text)  # 打印返回的错误信息
