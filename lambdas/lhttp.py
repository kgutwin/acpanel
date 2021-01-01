import os
import re
import json
import base64
import random
import hashlib
import logging
import mimetypes
import traceback
import urllib.parse

mimetypes.add_type('application/json', '.map')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class Server:
    """Core server class.

    >>> s = Server()
    >>> s.mount('/.*', (lambda x: response('foo')))
    >>> s.handler({ # doctest: +NORMALIZE_WHITESPACE
    ...   'requestContext': {
    ...     'http': {'method': 'GET', 'path': '/bar'}
    ...   }
    ... }, None) 
    {'statusCode': 200,
     'statusDescription': 'OK',
     'body': 'foo',
     'headers': {'Content-Type': 'text/html'},
     'isBase64Encoded': False}

    """
    def __init__(self):
        self.mounts = []

    def mount(self, path_re, responder, method='ANY'):
        """Mount a responder to a path (and optional method).

        The responder should be a function that takes one argument --
        a Request() object. It should return the result from the response()
        function.

        The path_re is a regular expression that matches the path. Mounts
        will be processed in the order that they are created.

        """
        self.mounts.append((method, re.compile(path_re), responder))

    def default_route(self, request):
        body = f"sorry, dude, couldn't find the path {request.path}"
        return response(body, status_code=404)

    def error_route(self, request, exc):
        body = f"whoa, that failed: {exc}"
        return response(body, status_code=500)

    def handler(self, event, context):
        request = Request(event)
        route = self.default_route

        for method, rex, func in self.mounts:
            if method not in ('ANY', request.method):
                continue
            
            m = rex.match(request.path)
            if not m:
                continue
            
            request.path_match = m
            route = func
            break

        try:
            response = route(request)
            if not isinstance(response, dict):
                raise Exception(f'Bad response: {response}')
        except Exception as ex:
            logger.exception('Route handler failure')
            response = self.error_route(request, ex)

        return response


class Request:
    def __init__(self, event):
        self.event = event
        logger.debug(json.dumps(event))
        if 'body' in event:
            if event['isBase64Encoded']:
                self.data = base64.b64decode(event['body'])
            else:
                self.data = event['body']
            content_type = event['headers'].get('content-type', '').lower()
            if content_type == 'application/x-www-form-urlencoded':
                self.data = urllib.parse.parse_qs(self.data.decode('utf-8'))
                self.data = {
                    k: v[0] if len(v) == 1 else v
                    for k, v in self.data.items()
                }
            elif content_type == 'application/json':
                self.data = json.loads(self.data)
        else:
            self.data = None

        self.cookie = Cookie(event.get('cookies', {}))

    @property
    def raw_body(self):
        return self.event['body']
        
    @property
    def method(self):
        return self.event['requestContext']['http']['method']

    @property
    def path(self):
        return self.event['requestContext']['http']['path']


def response(body, status_code=200, headers={}, cookie=None, is_json=False):
    """Create an appropriate response object.

    >>> response('foo') # doctest: +NORMALIZE_WHITESPACE
    {'statusCode': 200, 'statusDescription': 'OK', 'body': 'foo',
     'headers': {'Content-Type': 'text/html'}, 'isBase64Encoded': False}
    
    Will automatically base64-encode bytes bodies.

    >>> response(b'foo') # doctest: +NORMALIZE_WHITESPACE
    {'statusCode': 200, 'statusDescription': 'OK', 'body': 'Zm9v',
     'headers': {'Content-Type': 'text/html'}, 'isBase64Encoded': True}

    """
    if isinstance(body, dict):
        body = json.dumps(body)
        is_json = True

    if 'Content-Type' not in headers:
        if is_json:
            headers['Content-Type'] = 'application/json'
        else:
            headers['Content-Type'] = 'text/html'

    if cookie is not None:
        headers.update(cookie.headers_out)

    b64 = False
    if isinstance(body, bytes):
        b64 = True
        body = base64.b64encode(body).decode('utf-8')

    return {
        'statusCode': status_code,
        'statusDescription': 'OK',
        'body': body,
        'headers': headers,
        'isBase64Encoded': b64
    }


class Static:
    """Basic static page server.

    >>> s = Static('lambdas/static')
    >>> from unittest.mock import MagicMock
    >>> r = MagicMock()
    >>> r.path = '/robots.txt'
    >>> response = s(r)
    >>> assert response['statusCode'] == 200
    >>> assert response['headers']['Content-Type'] == 'text/plain'

    """
    def __init__(self, basedir):
        self.basedir = basedir

    def path(self, filename):
        def _fixed_handler(request):
            return self._handle(filename)
        return _fixed_handler

    def __call__(self, request):
        return self._handle(request.path.lstrip('/'))

    def _handle(self, filepath):
        fn = os.path.join(self.basedir, filepath)
        logger.debug(f'Static request path: {fn}')
        try:
            mime_type = mimetypes.guess_type(fn)[0]
            headers = {'Content-Type': mime_type}
            fp = open(fn, 'rb')
            return response(fp.read(), headers=headers)
        except FileNotFoundError:
            return response('', status_code=404)


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
