import threading

from bottle import get, post
from bottle import request, run

from config.config import get_cfg_port_listener
from resources.lang.enGB.logs import *
from resources.global_resources.log_vars import logPass
from service.virginmedia_tivo import Virginmedia_tivo
from log.log import log_internal

from apis.uri_config import get_config
from apis.uri_get_commands import get_commands
from apis.uri_post_command import post_command
from apis.uri_get_channel import get_channel
from apis.uri_get_channels import get_channels
from apis.uri_post_channel import post_channel
from apis.uri_get_recordings import get_recordings
from apis.uri_post_enterpin import post_enterpin


def start_bottle(port_threads):

    ################################################################################################
    # Create device
    ################################################################################################

    _virginmedia_tivo = Virginmedia_tivo()

    log_internal(logPass, logDescDeviceObjectCreation, description='success')

    ################################################################################################
    # APIs
    ################################################################################################

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

    def bottle_run(x_host, x_port):
        log_internal(logPass, logDescPortListener.format(port=x_port), description='started')
        run(host=x_host, port=x_port, debug=True)

    ################################################################################################

    host = 'localhost'
    ports = get_cfg_port_listener()
    for port in ports:
        t = threading.Thread(target=bottle_run, args=(host, port,))
        port_threads.append(t)

    # Start all threads
    for t in port_threads:
        t.start()
    # Use .join() for all threads to keep main process 'alive'
    for t in port_threads:
        t.join()
