from flask import Flask, render_template, request, Response, redirect
from pymongo import MongoClient
from flask_cors import CORS
from werkzeug.routing import BaseConverter


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


tinyURL = Flask(__name__)
CORS(tinyURL)
tinyURL.url_map.converters['reg'] = RegexConverter


db = MongoClient('mongodb://localhost:27017').chuangji
HEX62 = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


@tinyURL.route('/')
def index():
    return render_template('index.html')


@tinyURL.route('/get/', methods=['POST'])
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
            return Response('http://baicaichi.com/item/' + code)
    else:
        return Response(None)


@tinyURL.route('/item/<reg("[0-9a-zA-Z]+"):code>')
def goto(code):
    url_id = 0

    for i in code:
        key = HEX62.find(i)
        if key >= 0:
            url_id = url_id * 62 + key

    url = db.shurl.find_one({
        'id': url_id
    })['url']

    return redirect(url)


if __name__ == '__main__':
    tinyURL.run()
