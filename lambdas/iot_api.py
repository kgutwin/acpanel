import os
import json
import boto3
import logging
from lhttp import response as http_response

logger = logging.getLogger()
iot = boto3.client('iot-data')


def get_shadow(request):
    response = iot.get_thing_shadow(thingName=os.environ['THING_NAME'])
    payload = response['payload'].read()
    return http_response(payload, is_json=True)


def put_shadow(request):
    logger.debug(f'Put shadow: {request.data}')
    if not request.cookie.check():
        return http_response({'state': 'ERROR', 'msg': 'missing auth cookie'},
                             status_code=400)

    payload = json.dumps(request.data).encode('utf-8')
    response = iot.update_thing_shadow(thingName=os.environ['THING_NAME'],
                                       payload=payload)
    response = iot.get_thing_shadow(thingName=os.environ['THING_NAME'])
    payload = response['payload'].read()

    return http_response(payload, is_json=True)


def do_auth(request):
    if request.cookie.check():
        request.cookie.add() # regenerate
        return http_response({'state': 'OK'}, cookie=request.cookie)

    if not request.data or 'access_token' not in request.data:
        return http_response({'state': 'ERROR', 'msg': 'missing access_token'},
                             status_code=400)

    if request.data['access_token'] == os.environ['ACCESS_TOKEN']:
        request.cookie.add()
        return http_response({'state': 'OK'}, cookie=request.cookie)

    return http_response({'state': 'ERROR', 'msg': 'access_token incorrect'},
                         status_code=400)


def check_auth(request):
    if request.cookie.check():
        return http_response({'state': 'OK'}, cookie=request.cookie)

    return http_response({'state': 'ERROR', 
                          'msg': 'missing or invalid cookie'})
