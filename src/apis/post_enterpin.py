from bottle import HTTPResponse, HTTPError

from common_functions.request_log_args import get_request_log_args
from log.log import log_inbound
from resources.global_resources.log_vars import logPass, logException
from resources.global_resources.variables import *


def post_enterpin(request, _virginmedia_tivo):
    #
    args = get_request_log_args(request)
    #
    try:
        #
        r = _virginmedia_tivo.sendPin()
        #
        if not bool(r):
            status = httpStatusFailure
        else:
            status = httpStatusSuccess
        #
        args['result'] = logPass
        args['http_response_code'] = status
        args['description'] = '-'
        log_inbound(**args)
        #
        response = HTTPResponse()
        response.status = status
        #
        return response
        #
    except Exception as e:
        status = httpStatusServererror
        #
        args['result'] = logException
        args['http_response_code'] = status
        args['description'] = '-'
        args['exception'] = e
        log_inbound(**args)
        #
        raise HTTPError(status)
