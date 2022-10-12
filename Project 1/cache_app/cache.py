from flask import render_template, url_for, request
from cache_app import cache_app, memcache, memcache_config
from flask import json, jsonify
import random
import base64
from PIL import Image
import io


@cache_app.route('/')
def main():
    print("size of dictionary is {} bytes".format(cache_size(memcache)))
    return render_template("main.html",memcache=memcache)

@cache_app.route('/get',methods=['POST'])
def get():
    key = request.form.get('key')

    if key in memcache:
        value = memcache[key]
        memcache.move_to_end(key)
        response = cache_app.response_class(
            response=json.dumps(value),
            status=200,
            mimetype='application/json'
        )
    else:
        response = cache_app.response_class(
            response=json.dumps("Unknown key"),
            status=400,
            mimetype='application/json'
        )

    return response

@cache_app.route('/put',methods=['POST'])
def put():
    key = request.form.get('key')
    value = request.form.get('value')

    # evict using LRU/random policy
    while cache_size(memcache) + len(value) > memcache_config['SIZE']:
        if memcache_config['POLICY'] == 'LRU':
            memcache.popitem(last=False)
        else:
            random_key = random.choice(list(memcache.keys()))
            memcache.pop(random_key, None)


    memcache[key] = value
    memcache.move_to_end(key)

    #print(memcache[key])

    response = cache_app.response_class(
        response=json.dumps("OK"),
        status=200,
        mimetype='application/json'
    )

    return response

@cache_app.route('/invalidate',methods=['POST'])
def invalidate():
    key = request.form.get('key')

    if key in memcache:
        value = memcache.pop(key, None)
        response = cache_app.response_class(
            response=json.dumps(key + " dropped"),
            status=200,
            mimetype='application/json'
        )
    else:
        response = cache_app.response_class(
            response=json.dumps("Unknown key"),
            status=400,
            mimetype='application/json'
        )

    return response

@cache_app.route('/clear',methods=['POST'])
def clear():
    memcache.clear()
    response = cache_app.response_class(
        response=json.dumps("Mem cache cleared successfully"),
        status=200,
        mimetype='application/json'
    )
    return response

@cache_app.route('/test')
def test():
    pic_dict = {}
    img_file = Image.open("cache_app\static\guo.jpg")
    data = io.BytesIO()
    img_file.save(data,"JPEG")

    pic_dict['first'] = data.getvalue()

    encoded_img_data = base64.b64encode(pic_dict['first'])
    #print(encoded_img_data)

    return render_template("test.html", img_data=encoded_img_data.decode('utf-8'))

def cache_size(d):
    #TODO: check with TA about cache capacity
    vlen = sum(len(v) for v in d.values())
    return vlen
