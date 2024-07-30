import time
from io import BytesIO

import requests
from PIL import Image

if __name__ == '__main__':
    data = requests.post('http://api.extscreen.com/aliyundrive/qrcode', data={
        'scopes': ','.join(["user:base", "file:all:read", "file:all:write"]),
        "width": 500,
        "height": 500,
    }).json()['data']
    qr_link = data['qrCodeUrl']
    sid = data['sid']
    # 两种登录方式都可以
    # web登录, 打开链接登录
    print(f'点击此链接授权阿里云盘TV：https://www.aliyundrive.com/o/oauth/authorize?sid={sid}')
    # 手机阿里云盘扫描登录
    Image.open(BytesIO(requests.get(qr_link).content)).show()
    while True:
        time.sleep(3)
        status_data = requests.get(f'https://openapi.alipan.com/oauth/qrcode/{sid}/status').json()
        status = status_data['status']
        if status == 'LoginSuccess':
            auth_code = status_data['authCode']
            break
    # 使用code换refresh_token
    token_data = requests.post('http://api.extscreen.com/aliyundrive/token', data={
        'code': auth_code,
    }).json()['data']
    refresh_token = token_data['refresh_token']
    print(f'refresh_token: {refresh_token}')