import os
import json
import base64
import random
import hashlib
import traceback
import urllib.parse

from lambdas import admin, user, templates


def route(method, path, data, cookie):
    if path == '/admin':
        if method == 'GET':
            return admin.render(cookie)
        elif method == 'POST':
            return admin.update(cookie, data)

    return user.render()


def http(body, status_code=200, cookie=None):
    headers = {
        'Content-Type': 'text/html'
    }
    if cookie is not None:
        headers.update(cookie.headers_out)
        
    return {
        'statusCode': status_code,
        'statusDescription': 'OK',
        'body': body,
        'headers': headers,
        'isBase64Encoded': False
    }


def handler(event, context):
    print(json.dumps(event))
    if 'body' in event:
        if event['isBase64Encoded']:
            data = base64.b64decode(event['body'])
        else:
            data = event['body']
        if event['headers'].get('content-type', '').lower() == 'application/x-www-form-urlencoded':
            data = urllib.parse.parse_qs(data.decode('utf-8'))
            data = {
                k: v[0] if len(v) == 1 else v
                for k, v in data.items()
            }
    else:
        data = None

    cookie = Cookie(event.get('cookies', {}))
        
    try:
        result = route(
            event['requestContext']['http']['method'],
            event['requestContext']['http']['path'],
            data,
            cookie
        )
        if result:
            return http(result, cookie=cookie)
        else:
            return http(templates.error(str(result)), 400)
    except Exception as ex:
        traceback.print_exc()
        return http(templates.error(str(ex)), 500)


class Cookie:
    def __init__(self, cookies_in):
        self.cookies_in = {
            k: v for k, v in [c.split('=') for c in cookies_in]
        }
        self.headers_out = {}

    def add(self):
        i = hex(random.getrandbits(64))[2:]
        cookie_plain = os.environ.get('MASTER_KEY', 'abcd1234') + i
        cookie_baked = hashlib.sha256()
        cookie_baked.update(cookie_plain.encode('utf-8'))
        self.headers_out = {
            'Set-Cookie': f'auth_key={i}.{cookie_baked.hexdigest()}'
        }

    def check(self):
        if 'auth_key' not in self.cookies_in:
            return False

        value = self.cookies_in['auth_key']
        i, test_cookie = value.split('.')
        cookie_plain = os.environ.get('MASTER_KEY', 'abcd1234') + i
        cookie_baked = hashlib.sha256()
        cookie_baked.update(cookie_plain.encode('utf-8'))
        return test_cookie == cookie_baked.hexdigest()
