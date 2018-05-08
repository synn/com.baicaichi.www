import re
import json
from pymongo import MongoClient
from flask import Flask, render_template, request, Response
from flask_cors import CORS
from werkzeug.routing import BaseConverter


class RegexConverter(BaseConverter):
    def __init__(self, url_map,*items):
        super(RegexConverter,self).__init__(url_map)
        self.regex = items[0]


app = Flask(__name__)
CORS(app)
app.url_map.converters['reg'] = RegexConverter


database = MongoClient('mongodb://localhost:27017').chuangji
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
                url_id = database.shurl.find_one({
                    'url': package['url']
                })['id']
            except:
                database.shurl.save({
                    'id': database.counter.find_one_and_update(
                        {
                            'name': 'counter'
                        },
                        {
                            '$inc': {
                                'id': 1
                            }
                        }
                    )['id'],
                    'url': package['url'],
                    'detail_url': package['detail_url']
                })
                url_id = database.shurl.find_one({
                    'url': package['url']
                })['id']

            if url_id != None:
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
    else:
        return Response(None)


@app.route('/item/<reg("[0-9a-zA-Z]+"):code>')
def goto(code):
    return code


if __name__ == '__main__':
    app.run(debug=True)
