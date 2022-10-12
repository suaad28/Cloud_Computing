from flask import Flask
from collections import OrderedDict

global memcache
global memcache_config

cache_app = Flask(__name__)
memcache = OrderedDict()

#cache default config
memcache_config = {
        "POLICY" : "RANDOM",
        "SIZE"   : 10000000
}


from cache_app import cache
