from flask import Flask, render_template, request, Response
from flask_cors import CORS
from werkzeug.routing import BaseConverter
import json
import pymongo


class RegexConverter(BaseConverter):
    def __init__(self, url_map,*items):
        super(RegexConverter,self).__init__(url_map)
        self.regex = items[0]


app = Flask(__name__)
CORS(app)
app.url_map.converters['reg'] = RegexConverter


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get/', methods=['POST'])
def get():
    a = request.form['url']
    print(a)
    return Response(a)


@app.route('/item/<reg("[0-9a-zA-Z]+"):code>')
def goto(code):
    return code


if __name__ == '__main__':
    app.run(debug=True)
