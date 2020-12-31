import os
import boto3
import logging
from lhttp import response as http_response

logger = logging.getLogger()
iot = boto3.client('iot-data')


def get_shadow(request):
    response = iot.get_thing_shadow(thingName=os.environ['THING_NAME'])
    payload = response['payload'].read()
    return http_response(
        payload,
        headers={'Content-Type': 'application/json'}
    )


def put_shadow(request):
    logger.debug(f'Put shadow: {request.data}')
    return http_response('')
