from config.config import get_cfg_details_package
from resources.global_resources.log_vars import logPass, logFail, logException
from resources.lang.enGB.logs import *
from log.log import log_internal
from service.channels import channels


def get_channel_id_from_key(key):
    #
    try:
        k = int(key)
        #
        for chan_id in channels:
            if 'sd' in channels[chan_id]:
                if channels[chan_id]['sd']['key'] == k:
                    return chan_id
            if 'hd' in channels[chan_id]:
                if channels[chan_id]['hd']['key'] == k:
                    return chan_id
            if 'plus1' in channels[chan_id]:
                if 'sd' in channels[chan_id]['plus1']:
                    if channels[chan_id]['sd']['plus1']['key'] == k:
                        return chan_id
                if 'hd' in channels[chan_id]:
                    if channels[chan_id]['hd']['plus1']['key'] == k:
                        return chan_id
        #
        return False
    except Exception as e:
        log_internal(logException, logDesChannel_NameFromKey.format(key=key), description='fail', exception=e)
        return False


def get_channel_name_from_key(key):
    #
    try:
        k = int(key)
        #
        for chan_id in channels:
            if 'sd' in channels[chan_id]:
                if channels[chan_id]['sd']['key'] == k:
                    return channels[chan_id]['name']
            if 'hd' in channels[chan_id]:
                if channels[chan_id]['hd']['key'] == k:
                    return channels[chan_id]['name']
            if 'plus1' in channels[chan_id]:
                if 'sd' in channels[chan_id]['plus1']:
                    if channels[chan_id]['plus1']['sd']['key'] == k:
                        return channels[chan_id]['plus1']['hd']['key']['name']
                if 'hd' in channels[chan_id]:
                    if channels[chan_id]['plus1']['hd']['key'] == k:
                        return channels[chan_id]['plus1']['hd']['key']['name']
        #
        return False
    except Exception as e:
        log_internal(logException, logDesChannel_NameFromKey.format(key=key), description='fail', exception=e)
        return False


def get_channel_details_from_key(key):
    #
    try:
        for chan_id in channels:
            #
            if 'sd' in channels[chan_id]:
                if channels[chan_id]['sd']['key'] == key:
                    return {'id': chan_id,
                            'name': channels[chan_id]['name'],
                            'quality': 'sd',
                            'plus1': False}
            #
            if 'hd' in channels[chan_id]:
                if channels[chan_id]['hd']['key'] == key:
                    return {'id': chan_id,
                            'name': channels[chan_id]['name'],
                            'quality': 'hd',
                            'plus1': False}
            #
            if 'plus1' in channels[chan_id]:
                #
                if 'sd' in channels[chan_id]['plus1']:
                    if channels[chan_id]['plus1']['sd']['key'] == key:
                        return {'id': chan_id,
                                'name': channels[chan_id]['plus1']['sd']['name'],
                                'quality': 'sd',
                                'plus1': True}
                #
                if 'hd' in channels[chan_id]['plus1']:
                    if channels[chan_id]['plus1']['hd']['key'] == key:
                        return {'id': chan_id,
                                'name': channels[chan_id]['plus1']['sd']['name'],
                                'quality': 'hd',
                                'plus1': True}
        #
        return False
    except Exception as e:
        log_internal(logException, logDesChannel_DetailsFromKey.format(key=key), description='fail', exception=e)
        return False


def get_channel_key_from_name(name, plus1=False):
    #
    try:
        for chan_id in channels:
            #
            package = get_cfg_details_package()
            #
            # Do HD first as preference
            # If HD does not yield results, fall back to SD
            # then, check plus 1 channels, repeating hd preference over sd
            #
            if name == channels[chan_id]['name']:
                #
                if 'hd' in channels[chan_id]:
                    if check_package(chan_id, 'hd', package):
                        return channels[chan_id]['hd']['key']
                #
                if 'sd' in channels[chan_id]:
                    if check_package(chan_id, 'sd', package):
                        return channels[chan_id]['sd']['key']
            #
            if plus1:
                if 'plus1' in channels[chan_id]:
                    #
                    if name == channels[chan_id]['plus1']['name']:
                        if 'hd' in channels[chan_id]['plus1']:
                            if check_package_plus1(chan_id, 'hd', package):
                                return channels[chan_id]['plus1']['hd']['key']
                        #
                        if 'sd' in channels[chan_id]['plus1']:
                            if check_package_plus1(chan_id, 'sd', package):
                                return channels[chan_id]['plus1']['sd']['key']
        #
        return False
    except Exception as e:
        log_internal(logException, logDesChannel_KeyFromName.format(name=name), description='fail', exception=e)
        return False


def get_channel_key_from_id(chan_id, plus1=False):
    #
    try:
        package = get_cfg_details_package()
        #
        # Do HD first as preference
        # If HD does not yield results, fall back to SD
        # then, check plus 1 channels, repeating hd preference over sd
        #
        if plus1:
            if 'plus1' in channels[chan_id]:
                #
                if 'hd' in channels[chan_id]['plus1']:
                    if check_package_plus1(chan_id, 'hd', package):
                        return channels[chan_id]['plus1']['hd']['key']
                #
                if 'sd' in channels[chan_id]['plus1']:
                    if check_package_plus1(chan_id, 'sd', package):
                        return channels[chan_id]['plus1']['sd']['key']
            #
        else:
            if 'hd' in channels[chan_id]:
                if check_package(chan_id, 'hd', package):
                    return channels[chan_id]['hd']['key']
            #
            if 'sd' in channels[chan_id]:
                if check_package(chan_id, 'sd', package):
                    return channels[chan_id]['sd']['key']
        #
        return False
    except Exception as e:
        log_internal(logException, logDesChannel_KeyFromId.format(id=chan_id, plus1=plus1), description='fail', exception=e)
        return False


def get_channels(package):
    #
    chans = {}
    #
    for chan_id in channels:
        #
        try:
            #
            chans[chan_id] = {}
            chans[chan_id]['quality'] = []
            chans[chan_id]['name'] = channels[chan_id]['name']
            #
            if check_package(chan_id, 'sd', package):
                chans[chan_id]['quality'].append('sd')
            if check_package(chan_id, 'hd', package):
                chans[chan_id]['quality'].append('hd')
            #
            if 'plus1' in channels[chan_id]:
                chans[chan_id]['plus1'] = {}
                chans[chan_id]['plus1']['quality'] = []
                chans[chan_id]['plus1']['name'] = channels[chan_id]['plus1']['name']
                #
                if check_package_plus1(chan_id, 'sd', package):
                    chans[chan_id]['plus1']['quality'].append('sd')
                if check_package_plus1(chan_id, 'hd', package):
                    chans[chan_id]['plus1']['quality'].append('hd')
            #
        except Exception as e:
            log_internal(logException, logDesChannel_ListFromPackage.format(package=package), description='fail', exception=e)
    #
    return {'channels': chans}


def check_package(chan_id, quality, packages):
    if quality in channels[chan_id]:
        for p in packages:
            if p in channels[chan_id][quality]['package']:
                return True
    #
    return False


def check_package_plus1(chan_id, quality, packages):
    if 'plus1' in channels[chan_id]:
        if quality in channels[chan_id]['plus1']:
            for p in packages:
                if p in channels[chan_id][quality]['package']:
                    return True
    #
    return False
