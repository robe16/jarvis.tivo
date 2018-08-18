import requests
from service.channels import dataSources, channels

# https://my.virginmedia.com/content/dam/virgoBrowse/docs/VirginMediaTVChannelGuide.pdf
# https://web-api-pepper.horizon.tv/oesp/v3/GB/eng/web/channels?byLocationId=65535&includeInvisible=true


def get_data_horizon():
    url = 'https://web-api-pepper.horizon.tv/oesp/v3/GB/eng/web/channels'
    queryString = ['byLocationId=65535', 'includeInvisible=true']
    #
    r = requests.get(url + '?' + '&'.join(queryString))
    #
    horizon_data = r.json()
    #
    temp_chans = {}
    #
    for chan in horizon_data['channels']:
        #
        serviceId = chan['stationSchedules'][0]['station']['serviceId']
        channelName = chan['title']
        channelNumber = chan['channelNumber']
        channelPackages = chan['stationSchedules'][0]['station']['entitlements']
        #
        # station-logo-large
        # station-logo-medium
        # station-logo-small
        try:
            channelImage = ''
            for asset in chan['stationSchedules'][0]['station']['images']:
                if 'assetType' in asset:
                    if asset['assetType'] == 'station-logo-medium':
                        channelImage = asset['url']
                        break
        except Exception as e:
            channelImage = ''
        #
        temp_chans[serviceId] = {'name': channelName,
                                 'number': channelNumber,
                                 'packages': channelPackages,
                                 'image': channelImage}
    #
    return temp_chans


def stored_channels_info():
    #
    total = 0
    plus = 0
    sd = 0
    hd = 0
    for channel in channels:
        if 'sd' in channels[channel]:
            total += 1
            sd += 1
        if 'hd' in channels[channel]:
            total += 1
            hd += 1
        if 'plus1' in channels[channel]:
            plus += 1
            if 'sd' in channels[channel]['plus1']:
                total += 1
                sd += 1
            if 'hd' in channels[channel]['plus1']:
                total += 1
                hd += 1
    #
    return {'namedChannels': len(channels),
            'totalChannels': total,
            'sd': sd,
            'hd': hd,
            'nonPlus1': len(channels) - plus,
            'plus1': plus}


def no_sources():

    result = []

    def invalidNumber(id, quality, plus1, storedName, storedNum, actualName, actualNum):
        return {'id': id,
                'details': {'quality': quality, 'isPlus1': plus1},
                'stored': {'name': storedName, 'number': storedNum},
                'actual': {'name': actualName, 'number': actualNum}}

    def noSources(id, quality, plus1, storedName, storedNum):
        return {'id': id,
                'details': {'quality': quality, 'isPlus1': plus1},
                'stored': {'name': storedName, 'number': storedNum}}

    def check_channel(chan_id, quality):
        nonlocal result
        #
        if quality in channels[chan_id]:
            stored_number = channels[chan_id][quality]['key']
            if 'dataSources' in channels[chan_id][quality]:
                if not len(channels[chan_id][quality]['dataSources']):
                    result.append(noSources(chan_id, quality, False,
                                            channels[chan_id]['name'],
                                            stored_number))
            else:
                result.append(noSources(chan_id, quality, False,
                                        channels[chan_id]['name'],
                                        stored_number))

    def check_channel_plus(chan_id, quality):
        nonlocal result
        #
        if quality in channels[chan_id]['plus1']:
            stored_number = channels[chan_id]['plus1'][quality]['key']
            if 'dataSources' in channels[chan_id]['plus1'][quality]:
                if not len(channels[chan_id]['plus1'][quality]['dataSources']):
                    result.append(noSources(chan_id, quality, False,
                                            channels[chan_id]['plus1']['name'],
                                            stored_number))
            else:
                result.append(noSources(chan_id, quality, False,
                                        channels[chan_id]['plus1']['name'],
                                        stored_number))
    #
    #
    for chan_id in channels:
        #
        try:
            check_channel(chan_id, 'sd')
            check_channel(chan_id, 'hd')
            #
            if 'plus1' in channels[chan_id]:
                check_channel_plus(chan_id, 'sd')
                check_channel_plus(chan_id, 'hd')
        except Exception as e:
            pass
    #
    #
    return result


def compareHorizon(chans_horizon):
    #
    temp_used_horizon_keys = []
    sources_key = dataSources['web-api-pepper.horizon.tv']
    #
    result = {'invalidNumber': [],
              'unusedHorizon': [],
              'noSources': []}
    #
    count_invalidNumber = 0
    count_horizonUsed = 0
    count_noSources = 0

    def invalidNumber(id, quality, plus1, storedName, storedNum, actualName, actualNum):
        return {'id': id,
                'details': {'quality': quality, 'isPlus1': plus1},
                'stored': {'name': storedName, 'number': storedNum},
                'actual': {'name': actualName, 'number': actualNum}}

    def noSources(id, quality, plus1, storedName, storedNum):
        return {'id': id,
                'details': {'quality': quality, 'isPlus1': plus1},
                'stored': {'name': storedName, 'number': storedNum}}

    def check_channel(chan_id, quality):
        nonlocal result
        nonlocal count_invalidNumber
        nonlocal count_horizonUsed
        nonlocal count_noSources
        #
        if quality in channels[chan_id]:
            stored_number = channels[chan_id][quality]['key']
            if 'dataSources' in channels[chan_id][quality]:
                if len(channels[chan_id][quality]['dataSources']):
                    if sources_key in channels[chan_id][quality]['dataSources']:
                        horizon_key = channels[chan_id][quality]['dataSources'][sources_key]
                        temp_used_horizon_keys.append(horizon_key)
                        if not stored_number==chans_horizon[horizon_key]['number']:
                            result['invalidNumber'].append(invalidNumber(chan_id, quality, False,
                                                                         channels[chan_id]['name'],
                                                                         stored_number,
                                                                         chans_horizon[horizon_key]['name'],
                                                                         chans_horizon[horizon_key]['number']))
                            count_invalidNumber += 1
                        count_horizonUsed += 1
                    else:
                        result['noSources'].append(noSources(chan_id, quality, False,
                                                             channels[chan_id]['name'],
                                                             stored_number))
                        count_noSources += 1
                else:
                    result['noSources'].append(noSources(chan_id, quality, False,
                                                         channels[chan_id]['name'],
                                                         stored_number))
                    count_noSources += 1
            else:
                result['noSources'].append(noSources(chan_id, quality, False,
                                                     channels[chan_id]['name'],
                                                     stored_number))
                count_noSources += 1

    def check_channel_plus(chan_id, quality):
        nonlocal result
        nonlocal count_invalidNumber
        nonlocal count_horizonUsed
        nonlocal count_noSources
        #
        if quality in channels[chan_id]['plus1']:
            stored_number = channels[chan_id]['plus1'][quality]['key']
            if 'dataSources' in channels[chan_id]['plus1'][quality]:
                if len(channels[chan_id]['plus1'][quality]['dataSources']):
                    if sources_key in channels[chan_id]['plus1'][quality]['dataSources']:
                        horizon_key = channels[chan_id]['plus1'][quality]['dataSources'][sources_key]
                        temp_used_horizon_keys.append(horizon_key)
                        if not stored_number==chans_horizon[horizon_key]['number']:
                            result['invalidNumber'].append(invalidNumber(chan_id, quality, False,
                                                                         channels[chan_id]['plus1']['name'],
                                                                         stored_number,
                                                                         chans_horizon[horizon_key]['name'],
                                                                         chans_horizon[horizon_key]['number']))
                            count_invalidNumber += 1
                        count_horizonUsed += 1
                    else:
                        result['noSources'].append(noSources(chan_id, quality, False,
                                                             channels[chan_id]['plus1']['name'],
                                                             stored_number))
                        count_noSources += 1
                else:
                    result['noSources'].append(noSources(chan_id, quality, False,
                                                         channels[chan_id]['plus1']['name'],
                                                         stored_number))
                    count_noSources += 1
            else:
                result['noSources'].append(noSources(chan_id, quality, False,
                                                     channels[chan_id]['plus1']['name'],
                                                     stored_number))
                count_noSources += 1
    #
    #
    for chan_id in channels:
        #
        try:
            check_channel(chan_id, 'sd')
            check_channel(chan_id, 'hd')
            #
            if 'plus1' in channels[chan_id]:
                check_channel_plus(chan_id, 'sd')
                check_channel_plus(chan_id, 'hd')
        except Exception as e:
            pass
    #
    #
    for key in chans_horizon:
        try:
            if not key in temp_used_horizon_keys:
                result['unusedHorizon'].append({'key': key,
                                                'name': chans_horizon[key]['name'],
                                                'number': chans_horizon[key]['number']})
        except Exception as e:
            pass
    #
    #
    return result


def checkChannels():
    #
    try:
        chans_horizon = get_data_horizon()
        #
        compare_horizon = compareHorizon(chans_horizon)
        noSources = no_sources()
        stored_channels = stored_channels_info()
        stored_channels['noSources'] = len(noSources)
        #
        return {'storedChannelsInfo': stored_channels,
                'noSources': compare_horizon['noSources'],
                'horizon': {'comparison': compare_horizon,
                            'data': {'entryCount': len(chans_horizon),
                                     'invalidNumber': compare_horizon['invalidNumber'],
                                     'unusedHorizon': compare_horizon['unusedHorizon']}}}
        #
    except Exception as e:
        return False
