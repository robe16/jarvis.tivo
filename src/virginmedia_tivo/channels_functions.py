from config.config import get_cfg_details_package
from log.log import log_internal

# Issue with IDE and production running of script - resolved with try/except below
try:
    # IDE
    from virginmedia_tivo.channels import channels
except:
    # Production
    from channels import channels


def get_channel_name_from_key(key):
    #
    try:
        k = int(key)
        #
        for chan in channels:
            if channels[chan]['sd']:
                if channels[chan]['sd']['key'] == k:
                    return chan
            if channels[chan]['hd']:
                if channels[chan]['hd']['key'] == k:
                    return chan
        #
        return False
    except Exception as e:
        log_internal(False, 'Attempted get channel name from key - \'{key}\''.format(key=key), desc='fail', exception=e)
        return False


def get_channel_details_from_key(key):
    #
    try:
        for chan in channels:
            if channels[chan]['sd']:
                if channels[chan]['sd']['key'] == key:
                    return {'name': chan, 'quality': 'sd'}
            if channels[chan]['hd']:
                if channels[chan]['hd']['key'] == key:
                    return {'name': chan, 'quality': 'hd'}
        #
        return False
    except Exception as e:
        log_internal(False, 'Attempted get channel details from key - \'{key}\''.format(key=key), desc='fail', exception=e)
        return False


def get_channel_key_from_name(name):
    #
    try:
        if name in channels.keys():
            #
            package = get_cfg_details_package()
            #
            # Do HD first as preference
            if channels[name]['hd']:
                if check_package(name, 'hd', package):
                    return channels[name]['hd']['key']
            #
            # If HD does not yield results, fall back to SD
            if channels[name]['sd']:
                if check_package(name, 'sd', package):
                    return channels[name]['sd']['key']
        #
        return False
    except Exception as e:
        log_internal(False, 'Attempted get channel key from name - \'{name}\''.format(name=name), desc='fail', exception=e)
        return False


def get_channels(package):
    #
    try:
        #
        chans = []
        #
        for chan in channels:
            #
            c = {chan: {'sd': check_package(chan, 'sd', package),
                        'hd': check_package(chan, 'hd', package)}
                 }
            #
            chans.append(c)
        #
        return {'channels': chans}
    except Exception as e:
        log_internal(False, 'Attempted get channel list from package - \'{package}\''.format(package=package), desc='fail', exception=e)
        return False


def check_package(name, quality, package):
    if channels[name][quality]:
        chan_package = channels[name][quality]['package']
        for p in package:
            if p in chan_package:
                return True
    #
    return False
