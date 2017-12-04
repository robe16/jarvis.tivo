from tivo.channels import channels
from config.config import get_cfg_details_package

def get_channel_name_from_key(key):
    for chan in channels:
        if channels[chan]['sd']:
            if channels[chan]['sd']['key'] == key:
                return chan
        elif channels[chan]['hd']:
            if channels[chan]['hd']['key'] == key:
                return chan
    #
    return False

def get_channel_key_from_name(name):
    #
    if name in channels.keys():
        #
        package = get_cfg_details_package()
        #
        # Do HD first as preference
        if channels[name]['hd']:
            if _check_package(name, 'hd', package):
                return channels[name]['hd']['key']
        #
        # If HD does not yield results, fall back to SD
        if channels[name]['sd']:
            if _check_package(name, 'sd', package):
                return channels[name]['sd']['key']
    #
    return False

def _check_package(name, quality, package):
    chan_package = channels[name][quality]['package']
    for p in package:
        if p in chan_package:
            return True
    #
    return False
