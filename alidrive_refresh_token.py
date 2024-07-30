import requests
from flask import Flask
from flask import request

app = Flask(__name__)


@app.post('/refresh')
def refresh():
    app.logger.info(request.json)
    refresh_token = request.json.get('refresh_token')
    resp = requests.post('http://api.extscreen.com/aliyundrive/token', data={
        'refresh_token': refresh_token,
    })
    resp.raise_for_status()
    data = resp.json()['data']
    app.logger.info(data)
    return {
        'token_type': 'Bearer',
        'access_token': data['access_token'],
        'refresh_token': data['refresh_token'],
        'expires_in': data['expires_in'],
    }

if __name__ == '__main__':
    app.run(debug=True, port=5001)