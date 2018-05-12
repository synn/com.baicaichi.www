from flask import Flask, render_template, request, Response, redirect
from pymongo import MongoClient
from flask_cors import CORS
from werkzeug.routing import BaseConverter
import time
import json
import base64


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app = Flask(__name__)
app.url_map.converters['reg'] = RegexConverter
CORS(app)

db = MongoClient('mongodb://entry:120903@syver.xyz:27017', connect=False).chuangji
HEX62 = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get/', methods=['POST'])
def get():
    package = request.form
    urlCheck = 's.click.taobao.com' in package['url']
    detailCheck = package['detailURL'] is not None
    nameCheck = '白菜池' in package['name']
    if request.method == 'POST':
        if urlCheck and detailCheck and nameCheck:
            try:
                url_id = db.shurl.find_one({
                    'url': package['url']
                })['id']
            except:
                db.counter.update({
                    'name': 'counter'
                },
                {
                    '$inc': {
                        'id': 1
                    }
                })

                item_id = db.counter.find_one({
                    'name': 'counter'
                })['id']

                db.shurl.save({
                    'id': item_id,
                    'url': package['url'],
                    'detail_url': package['detailURL']
                })

                url_id = db.shurl.find_one({
                    'url': package['url']
                })['id']

            url_id = int(url_id)
            code = ''
            if url_id >= 62:
                while url_id >= 62:
                    index = url_id % 62
                    code = HEX62[index] + code
                    url_id = url_id // 62
                code = HEX62[url_id] + code
            return Response('http://baicaichi.com/url/' + code)
    else:
        return Response(None)


@app.route('/url/<reg("[0-9a-zA-Z]+"):code>')
def goto(code):
    return render_template('url.html', code=base64.b64encode(code.encode(encoding='utf-8')).decode('utf-8'))


@app.route('/item/<reg("[0-9a-zA-Z]+"):code>')
def opentb(code):
    url_id = 0

    for i in code:
        key = HEX62.find(i)
        if key >= 0:
            url_id = url_id * 62 + key

    try:
        url = db.shurl.find_one({
            'id': url_id
        })['url']
        time.sleep(2)
        return redirect(url)
    except:
        return Response('找不到页面地址，可能页面已过期')


@app.route('/read/', methods=['POST'])
def read():
    if request.method == 'POST':
        userAgent = str(request.user_agent)
        code = json.loads(request.data)['code']

        if 'Android' in userAgent or 'iPhone' in userAgent or 'iPad' in userAgent:
            url = 'taobao://baicaichi.com/item/' + code
        else:
            url = 'http://baicaichi.com/item/' + code

        return Response(url)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
