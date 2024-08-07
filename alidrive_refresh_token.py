import base64
import json

import requests
from Crypto.Cipher import AES
from flask import Flask
from flask import request

app = Flask(__name__)

# 原接口404，现更新为新的加密接口
key = '^(i/x>>5(ebyhumz*i1wkpk^orIs^Na.'.encode()


@app.post('/refresh')
def refresh():
    app.logger.info(request.json)
    refresh_token = request.json.get('refresh_token')
    resp = requests.post('http://api.extscreen.com/aliyundrive/v2/token', data={
        'refresh_token': refresh_token,
    })
    resp.raise_for_status()
    print(resp.json())
    data = resp.json()['data']
    app.logger.info(data)
    plain_data = AES.new(key, AES.MODE_CBC, iv=bytes.fromhex(data['iv'])).decrypt(
        base64.b64decode(data['ciphertext']))
    token_data = json.loads(plain_data[:-plain_data[-1]])
    app.logger.info(token_data)
    return {
        'token_type': 'Bearer',
        'access_token': token_data['access_token'],
        'refresh_token': token_data['refresh_token'],
        'expires_in': token_data['expires_in'],
    }


if __name__ == '__main__':
    app.run(debug=True, port=5001)