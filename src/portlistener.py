from bottle import HTTPError
from bottle import get, post
from bottle import request, run, HTTPResponse

from virginmedia_tivo.virginmedia_tivo import Virginmedia_tivo
from resources.global_resources.variables import *
from config.config import get_cfg_serviceid, get_cfg_name_long, get_cfg_name_short, get_cfg_groups, get_cfg_subservices
from validation.validation import validate_command, validate_channel
from log.log import log_inbound, log_internal


def start_bottle(self_port):

    ################################################################################################
    # Create device
    ################################################################################################

    _device = Virginmedia_tivo()

    log_internal(True, 'Device object created', desc='success')

    ################################################################################################
    # Enable cross domain scripting
    ################################################################################################

    def enable_cors(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET'
        return response

    ################################################################################################
    # Service info & Groups
    ################################################################################################

    @get(uri_config)
    def get_config():
        #
        try:
            client = request.headers[service_header_clientid_label]
        except:
            client = request['REMOTE_ADDR']
        #
        try:
            #
            data = {'service_id': get_cfg_serviceid(),
                    'name_long': get_cfg_name_long(),
                    'name_short': get_cfg_name_short(),
                    'subservices': get_cfg_subservices(),
                    'groups': get_cfg_groups()}
            #
            status = httpStatusSuccess
            #
            log_inbound(True, client, request.url, 'GET', status)
            #
            return HTTPResponse(body=data, status=status)
            #
        except Exception as e:
            status = httpStatusServererror
            log_inbound(False, client, request.url, 'GET', status, exception=e)
            raise HTTPError(status)

    ################################################################################################
    # Recordings
    ################################################################################################

    @get(uri_recordings)
    def get_recordings():
        #
        try:
            client = request.headers[service_header_clientid_label]
        except:
            client = request['REMOTE_ADDR']
        #
        try:
            #
            r = _device.getRecordings()
            #
            if not bool(r):
                status = httpStatusFailure
            else:
                status = httpStatusSuccess
            #
            log_inbound(True, client, request.url, 'GET', status)
            #
            if isinstance(r, bool):
                return HTTPResponse(status=status)
            else:
                return HTTPResponse(body=r, status=status)
            #
        except Exception as e:
            status = httpStatusServererror
            log_inbound(False, client, request.url, 'GET', status, exception=e)
            raise HTTPError(status)

    ################################################################################################
    # Get channel
    ################################################################################################

    @get(uri_channel)
    def get_channel():
        #
        try:
            client = request.headers[service_header_clientid_label]
        except:
            client = request['REMOTE_ADDR']
        #
        try:
            #
            r = _device.getChan()
            #
            if not bool(r):
                status = httpStatusFailure
            else:
                status = httpStatusSuccess
            #
            log_inbound(True, client, request.url, 'GET', status)
            #
            if isinstance(r, bool):
                return HTTPResponse(status=status)
            else:
                return HTTPResponse(body=r, status=status)
            #
        except Exception as e:
            status = httpStatusServererror
            log_inbound(False, client, request.url, 'GET', status, exception=e)
            raise HTTPError(status)

    ################################################################################################
    # Get channel
    ################################################################################################

    @get(uri_channels)
    def get_channels():
        #
        try:
            client = request.headers[service_header_clientid_label]
        except:
            client = request['REMOTE_ADDR']
        #
        try:
            #
            r = _device.getChannels()
            #
            if not bool(r):
                status = httpStatusFailure
            else:
                status = httpStatusSuccess
            #
            log_inbound(True, client, request.url, 'GET', status)
            #
            if isinstance(r, bool):
                return HTTPResponse(status=status)
            else:
                return HTTPResponse(body=r, status=status)
            #
        except Exception as e:
            status = httpStatusServererror
            log_inbound(False, client, request.url, 'GET', status, exception=e)
            raise HTTPError(status)

    ################################################################################################
    # Post channel
    ################################################################################################

    @post(uri_channel)
    def post_channel():
        #
        try:
            client = request.headers[service_header_clientid_label]
        except:
            client = request['REMOTE_ADDR']
        #
        try:
            #
            data_dict = request.json
            #
            if validate_channel(data_dict):
                #
                channel = data_dict['channel']
                r = _device.sendChannel(channel)
                #
                if not bool(r):
                    status = httpStatusFailure
                else:
                    status = httpStatusSuccess
            else:
                status = httpStatusBadrequest
            #
            log_inbound(True, client, request.url, 'POST', status, desc=request.json)
            #
            return HTTPResponse(status=status)
            #
        except Exception as e:
            status = httpStatusServererror
            log_inbound(False, client, request.url, 'GET', status, exception=e)
            raise HTTPError(status)

    ################################################################################################
    # Get commands
    ################################################################################################

    @get(uri_commands)
    def get_commands():
        #
        try:
            client = request.headers[service_header_clientid_label]
        except:
            client = request['REMOTE_ADDR']
        #
        try:
            #
            data = _device.getCommands()
            #
            status = httpStatusSuccess
            #
            log_inbound(True, client, request.url, 'GET', status)
            #
            return HTTPResponse(body=data, status=status)
            #
        except Exception as e:
            status = httpStatusServererror
            log_inbound(False, client, request.url, 'GET', status, exception=e)
            raise HTTPError(status)

    ################################################################################################
    # Post commands
    ################################################################################################

    @post(uri_command)
    def post_command():
        #
        try:
            client = request.headers[service_header_clientid_label]
        except:
            client = request['REMOTE_ADDR']
        #
        try:
            #
            data_dict = request.json
            #
            if validate_command(data_dict):
                #
                command = data_dict['command']
                r = _device.sendCmd(command)
                #
                if not bool(r):
                    status = httpStatusFailure
                else:
                    status = httpStatusSuccess
            else:
                status = httpStatusBadrequest
            #
            log_inbound(True, client, request.url, 'POST', status, desc=request.json)
            #
            return HTTPResponse(status=status)
            #
        except Exception as e:
            status = httpStatusServererror
            log_inbound(False, client, request.url, 'POST', status, desc=request.json, exception=e)
            raise HTTPError(status)

    ################################################################################################
    # Pin
    ################################################################################################

    @post(uri_enterpin)
    def post_enterpin():
        #
        try:
            client = request.headers[service_header_clientid_label]
        except:
            client = request['REMOTE_ADDR']
        #
        try:
            #
            r = _device.sendPin()
            #
            if not bool(r):
                status = httpStatusFailure
            else:
                status = httpStatusSuccess
            #
            log_inbound(True, client, request.url, 'POST', status)
            #
            return HTTPResponse(status=status)
            #
        except Exception as e:
            status = httpStatusServererror
            log_inbound(False, client, request.url, 'POST', status, exception=e)
            raise HTTPError(status)

    ################################################################################################

    host='0.0.0.0'
    log_internal(True, 'Port listener', desc='started')
    run(host=host, port=self_port, debug=True)
