# coding=utf-8

import pickle
import random
import requests
from flask import Flask, render_template, request, redirect, url_for
from flask.ext.bootstrap import Bootstrap
from redis import Redis

app = Flask(__name__)
redis = Redis()
Bootstrap(app)


def create_key(length=8):
    """create a random key
    :param length: length of key
    """
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join([random.choice(chars) for _ in range(length)])


@app.route(u'/')
def index():
    lang = [(u'Apache', u'apache'), (u'Bash', u'bash'), (u'C#', u'cs'),
            (u'C++', u'cpp'), (u'CSS', u'css'),
            (u'CoffeeScript', u'coffeescript'), (u'Diff', u'diff'),
            (u'HTTP', u'http'), (u'Ini', u'ini'), (u'JSON', u'json'),
            (u'Java', u'java'), (u'JavaScript', u'javascript'),
            (u'Makefile', u'makefile'), (u'Markdown', u'markdown'),
            (u'Nginx', u'nginx'), (u'Objective C', u'objectivec'),
            (u'PHP', u'php'), (u'Perl', u'perl'), (u'Python', u'python'),
            (u'Ruby', u'ruby'), (u'SQL', u'sql')]
    return render_template(u'index.html', lang=lang)


@app.route(u'/c/<key>')
def get_code(key):
    url_type = request.args.get('url')
    if url_type == 'normal':
        url = request.host_url.rstrip('/') + url_for(u'.get_code', key=key)
    elif url_type == 'short':
        url = request.host_url.rstrip('/') + url_for(u'.get_code', key=key)
        res = requests.get('http://api.weibo.com/2/short_url/shorten.json'
                           '?source=2849184197&url_long={url}'
                           .format(url=url))
        res_json = res.json()
        url = res_json['urls'][0]['url_short']
    else:
        url = None
    redis_data = redis.get(u'codeclip_{0}'.format(key))
    if not redis_data:
        return 'Not Found', 404
    code_data = pickle.loads(redis_data)
    code = code_data['code']
    lang = code_data['lang']
    if code:
        return render_template(u'clip.html', code=code, lang=lang, url=url)
    else:
        return 'Not Found', 404


@app.route(u'/post', methods=['POST'])
def post():
    code = request.form.get(u'code')
    lang = request.form.get(u'lang')
    short = request.form.get(u'short')
    if short == 'on':
        url = 'short'
    else:
        url = 'normal'
    if not code:
        return 'Bad Request', 400
    key = create_key()
    code_data = dict(code=code, lang=lang)
    redis.set(u'codeclip_{0}'.format(key), pickle.dumps(code_data))
    return redirect(url_for(u'.get_code', key=key, url=url))


if __name__ == '__main__':
    app.run(u'0.0.0.0', port=8001, debug=True)
