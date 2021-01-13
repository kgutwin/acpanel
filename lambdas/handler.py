import os
import json
import base64
import random
import hashlib
import traceback
import urllib.parse

import iot_api

# nc -kluw 0 0.0.0.0 8347

# TODO:
# - build a static page server
# - build a rudimentary API
#   - get status JSON
#   - send a command


import lhttp


server = lhttp.Server()

server.mount('^/api/shadow$', iot_api.get_shadow, method='GET')
server.mount('^/api/shadow$', iot_api.put_shadow, method='PUT')
server.mount('^/api/auth$', iot_api.check_auth, method='GET')
server.mount('^/api/auth$', iot_api.do_auth, method='POST')

static = lhttp.Static('static')
server.mount('^/$', static.path('index.html'))
server.mount('^/.*$', static)

handler = server.handler
