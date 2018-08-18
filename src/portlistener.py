from bottle import request, run, route, get, post

from config.config import get_cfg_port
from common_functions.request_enable_cors import response_options
from resources.lang.enGB.logs import *
from resources.global_resources.log_vars import logPass
from service.virginmedia_tivo import Virginmedia_tivo
from log.log import log_internal

from apis.get_config import get_config
from apis.get_commands import get_commands
from apis.post_command import post_command
from apis.get_channel import get_channel
from apis.get_channels import get_channels
from apis.get_checkchannels import get_checkchannels
from apis.post_channel import post_channel
from apis.get_recordings import get_recordings
from apis.post_enterpin import post_enterpin


def start_bottle():

    ################################################################################################
    # Create device
    ################################################################################################

    _virginmedia_tivo = Virginmedia_tivo()

    log_internal(logPass, logDescDeviceObjectCreation, description='success')

    ################################################################################################
    # APIs
    ################################################################################################

    @route('/config', method=['OPTIONS'])
    @route('/commands', method=['OPTIONS'])
    @route('/command', method=['OPTIONS'])
    @route('/channel', method=['OPTIONS'])
    @route('/channels', method=['OPTIONS'])
    @route('/checkchannels', method=['OPTIONS'])
    @route('/recordings', method=['OPTIONS'])
    @route('/enterpin', method=['OPTIONS'])
    def api_cors_options(**kwargs):
        return response_options()

    @get('/config')
    def api_get_config():
        response = get_config(request)
        return response

    @get('/commands')
    def api_get_commands():
        response = get_commands(request, _virginmedia_tivo)
        return response

    @post('/command')
    def api_post_command():
        response = post_command(request, _virginmedia_tivo)
        return response

    @get('/channel')
    def api_get_channel():
        response = get_channel(request, _virginmedia_tivo)
        return response

    @get('/channels')
    def api_get_channels():
        response = get_channels(request, _virginmedia_tivo)
        return response

    @get('/checkchannels')
    def api_get_checkchannels():
        response = get_checkchannels(request)
        return response

    @post('/channel')
    def api_post_channel():
        response = post_channel(request, _virginmedia_tivo)
        return response

    @get('/recordings')
    def api_get_recordings():
        response = get_recordings(request, _virginmedia_tivo)
        return response

    @post('/enterpin')
    def api_post_enterpin():
        response = post_enterpin(request, _virginmedia_tivo)
        return response

    ################################################################################################

    host = '0.0.0.0'
    port = get_cfg_port()
    run(host=host, port=port, server='paste', debug=True)

    log_internal(logPass, logDescPortListener.format(port=port), description='started')

    ################################################################################################
