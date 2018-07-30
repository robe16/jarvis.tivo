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
    @route('/recordings', method=['OPTIONS'])
    @route('/enterpin', method=['OPTIONS'])
    def api_cors_options():
        return response_options()

    @get('/config')
    def api_get_config():
        return get_config(request)

    @get('/commands')
    def api_get_commands():
        return get_commands(request, _virginmedia_tivo)

    @post('/command')
    def api_post_command():
        return post_command(request, _virginmedia_tivo)

    @get('/channel')
    def api_get_channel():
        return get_channel(request, _virginmedia_tivo)

    @get('/channels')
    def api_get_channels():
        return get_channels(request, _virginmedia_tivo)

    @post('/channel')
    def api_post_channel():
        return post_channel(request, _virginmedia_tivo)

    @get('/recordings')
    def api_get_recordings():
        return get_recordings(request, _virginmedia_tivo)

    @post('/enterpin')
    def api_post_enterpin():
        return post_enterpin(request, _virginmedia_tivo)

    ################################################################################################

    host = '0.0.0.0'
    port = get_cfg_port()
    run(host=host, port=port, server='paste', debug=True)

    log_internal(logPass, logDescPortListener.format(port=port), description='started')

    ################################################################################################
