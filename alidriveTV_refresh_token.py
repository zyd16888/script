import base64
import json
import time
from io import BytesIO

import requests
from Crypto.Cipher import AES
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
    print(f'https://www.aliyundrive.com/o/oauth/authorize?sid={sid}')
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
    # token_data = requests.post('http://api.extscreen.com/aliyundrive/token', data={
    #     'code': auth_code,
    # }).json()['data']
    # refresh_token = token_data['refresh_token']
    # # 已有refresh_token, 直接刷新access_token
    # token_info = requests.post('http://api.extscreen.com/aliyundrive/token', data={
    #     'refresh_token': refresh_token,
    # }).json()['data']
    # 原接口404，现更新为新的加密接口
    key = '^(i/x>>5(ebyhumz*i1wkpk^orIs^Na.'.encode()
    # 使用code换refresh_token
    data = requests.post('http://api.extscreen.com/aliyundrive/v2/token', data={
        'code': auth_code,
    }).json()['data']
    plain_data = AES.new(key, AES.MODE_CBC, iv=bytes.fromhex(data['iv'])).decrypt(
        base64.b64decode(data['ciphertext']))
    token_data = json.loads(plain_data[:-plain_data[-1]])
    refresh_token = token_data['refresh_token']
    print('Refresh token:', refresh_token)
    # 已有refresh_token, 直接刷新access_token
    data = requests.post('http://api.extscreen.com/aliyundrive/v2/token', data={
        'refresh_token': refresh_token,
    }).json()['data']

    print("-*-" * 20)
    plain_data = AES.new(key, AES.MODE_CBC, iv=bytes.fromhex(data['iv'])).decrypt(
        base64.b64decode(data['ciphertext']))
    token_data = json.loads(plain_data[:-plain_data[-1]])
    access_token = token_data['access_token']
    print('Access token:', access_token)