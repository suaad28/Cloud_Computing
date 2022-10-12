from flask import render_template, request, redirect, url_for, flash, json
from werkzeug.utils import secure_filename
from web_app import web_app
import base64
from PIL import Image
import io
import requests

@web_app.route('/')
@web_app.route('/index')
def index():

    return render_template('index.html', title='Home')

@web_app.route('/upload', methods=['POST'])
def upload():
    url = 'http://127.0.0.1:5000/put'
    key = request.form.get('key')
    upload_file = request.files['file']

    img_file = Image.open(upload_file)
    data = io.BytesIO()
    img_file.save(data,img_file.format)

    value = base64.b64encode(data.getvalue())

    #print(value)

    req_data = {'key': key,
                'value': value}

    res = requests.post(url, data=req_data)
    #print('response from server', res.text)

    return render_template('upload.html')

@web_app.route('/find', methods=['POST'])
def find():
    url = 'http://127.0.0.1:5000/get'
    key = request.form.get('key')
    req_data = {'key': key}
    res = requests.post(url, data=req_data)

    if res.status_code == 200:      #Successful
        decoded_img_data = base64.b64decode(res.text)
        encoded_img_data = base64.b64encode(decoded_img_data)

        #print('response from server', encoded_img_data)
        return render_template("display.html", img_data=encoded_img_data.decode('utf-8'))

    else:
        return render_template("display.html" )
