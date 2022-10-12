#Imports the executable .py file from the folder

from flask import Flask

web_app = Flask(__name__)

from web_app import web_routes
