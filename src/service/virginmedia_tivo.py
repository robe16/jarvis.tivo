from datetime import datetime, timedelta
import time
import xml.etree.ElementTree as ET
import telnetlib
import requests as requests
from requests.auth import HTTPDigestAuth
from multiprocessing import Manager, Process

from resources.lang.enGB.logs import *
from resources.global_resources.log_vars import logPass, logFail, logException
from parameters import recordings_check_period
from log.log import log_outbound, log_internal
from config.config import get_cfg_details_ip, get_cfg_details_mak, get_cfg_details_pin, get_cfg_details_package

from service.commands import commands
from service.channels_functions import get_channels
from service.channels_functions import get_channel_details_from_key, get_channel_key_from_id


import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Virginmedia_tivo():

    _port = 31339

    tivoSession = requests.Session()

    recordings_dict = Manager().dict()

    def __init__(self):
        #
        self.recordings_timestamp = 0
        self.recordings = False
        #
        self.create_session()
        #
        Process(target=self._start_instance).start()

    def _start_instance(self):
        self.get_recordings()

    def create_session(self):
        with requests.Session() as s:
            s.auth = HTTPDigestAuth('tivo', get_cfg_details_mak())
            s.verify = False
        self.tivoSession = s

    def _check_recordings(self, loop=0):
        if loop > 1:
            return
        if self.recordings_timestamp == 0 or datetime.now() > (self.recordings_timestamp + timedelta(minutes=recordings_check_period)):
            self.get_recordings()
            loop += 1
            self._check_recordings(loop=loop)
        else:
            return

    def get_recordings(self):
        # Reset value
        self.recordings = False
        #
        try:
            #
            ############
            #
            folders = self._retrieve_recordings('No')
            folders = folders.replace(' xmlns="http://www.tivo.com/developer/calypso-protocol-1.6/"', '')
            folders = ET.fromstring(folders)
            xml_folders = []
            for item in folders.iter('Item'):
                xml_folders.append(item.find('Details'))
            #
            ############
            #
            retrieve_items = 50
            #
            files_repeat = True
            loop_count = 0
            itemCount = '&ItemCount={retrieve_items}'.format(retrieve_items=retrieve_items)
            xml_files = []
            #
            while files_repeat:
                files_count = 0
                files = self._retrieve_recordings('Yes', itemCount=itemCount).replace(' xmlns="http://www.tivo.com/developer/calypso-protocol-1.6/"','')
                files = ET.fromstring(files)
                # Run through individual items
                for item in files.iter('Item'):
                    xml_files.append(item.find('Details'))
                    files_count += 1
                #
                if files_count < 50:
                    files_repeat = False
                else:
                    loop_count += 1
                    itemCount = '&ItemCount={retrieve_items}&AnchorOffset={AnchorOffset}'.format(retrieve_items=retrieve_items,
                                                                                                 AnchorOffset=(retrieve_items*loop_count))
            #
            ############
            #
            self.recordings_timestamp = datetime.now()
            self.recordings = self._create_recordings_json(self.recordings_timestamp, xml_folders, xml_files)
            #
            ############
            #
            log_internal(logPass, logDescDeviceGetRecordings)
            #
        except Exception as e:
            log_internal(logException, logDescDeviceGetRecordings, exception=e)
            self.recordings_timestamp = 0
            self.recordings = False

    def _create_recordings_json(self, _timestamp, _folders, _files):
        #
        json_recordings = {}

        #
        if len(_folders) == 0 or len(_files) == 0:
            return False
        #
        try:
            #
            folderCount = 0
            for itemFolder in _folders:
                if itemFolder.find('Title').text != 'Suggestions' and itemFolder.find('Title').text != 'HD Recordings':
                    json_recordings[str(folderCount)] = {}
                    json_recordings[str(folderCount)]['folderName'] = itemFolder.find('Title').text
                    json_recordings[str(folderCount)]['type'] = '-'
                    #
                    json_recordings[str(folderCount)]['items'] = {}
                    #
                    # Run through individual items
                    itemCount = 0
                    for itemFile in _files:
                        #
                        if itemFile.find('Title').text == itemFolder.find('Title').text:
                            #
                            json_recordings[str(folderCount)]['items'][str(itemCount)] = {}
                            #
                            try:
                                json_recordings[str(folderCount)]['items'][str(itemCount)]['episodeTitle'] = itemFile.find('EpisodeTitle').text
                            except Exception as e:
                                json_recordings[str(folderCount)]['items'][str(itemCount)]['episodeTitle'] = ''
                            #
                            json_recordings[str(folderCount)]['items'][str(itemCount)]['channel'] = {}
                            #
                            recordedChannel = int(itemFile.find('SourceChannel').text)
                            c = get_channel_details_from_key(recordedChannel)
                            if c:
                                json_recordings[str(folderCount)]['items'][str(itemCount)]['channel']['id'] = c['id']
                                json_recordings[str(folderCount)]['items'][str(itemCount)]['channel']['name'] = c['name']
                                json_recordings[str(folderCount)]['items'][str(itemCount)]['channel']['quality'] = c['quality']
                                json_recordings[str(folderCount)]['items'][str(itemCount)]['channel']['plus1'] = c['plus1']
                            else:
                                json_recordings[str(folderCount)]['items'][str(itemCount)]['channel']['id'] = '-'
                                json_recordings[str(folderCount)]['items'][str(itemCount)]['channel']['name'] = '-'
                                json_recordings[str(folderCount)]['items'][str(itemCount)]['channel']['quality'] = '-'
                                json_recordings[str(folderCount)]['items'][str(itemCount)]['channel']['plus1'] = '-'
                            #
                            try:
                                json_recordings[str(folderCount)]['items'][str(itemCount)]['description'] = itemFile.find('Description').text
                            except Exception as e:
                                json_recordings[str(folderCount)]['items'][str(itemCount)]['description'] = ''
                            #
                            try:
                                date = int(itemFile.find('CaptureDate').text, 0)
                                date = datetime.fromtimestamp(date)
                                json_recordings[str(folderCount)]['items'][str(itemCount)]['recordingDate'] = date.strftime('%d-%m-%Y')
                            except Exception as e:
                                json_recordings[str(folderCount)]['items'][str(itemCount)]['recordingDate'] = '-'
                            #
                            json_recordings[str(folderCount)]['items'][str(itemCount)]['episodeNumber'] = {}
                            #
                            try:
                                episodenumber = itemFile.find('EpisodeNumber').text
                                json_recordings[str(folderCount)]['items'][str(itemCount)]['episodeNumber']['series'] = episodenumber[:-2]
                                json_recordings[str(folderCount)]['items'][str(itemCount)]['episodeNumber']['episode'] = episodenumber[-2:]
                            except:
                                json_recordings[str(folderCount)]['items'][str(itemCount)]['episodeNumber']['series'] = ''
                                json_recordings[str(folderCount)]['items'][str(itemCount)]['episodeNumber']['episode'] = ''
                            #
                            try:
                                if itemFile.find('ProgramId').text.startswith('EP'):
                                    json_recordings[str(folderCount)]['type'] = 'tv'
                                    json_recordings[str(folderCount)]['items'][str(itemCount)]['mpaaRating'] = ''
                                elif itemFile.find('ProgramId').text.startswith('MV'):
                                    json_recordings[str(folderCount)]['type'] = 'movie'
                                    json_recordings[str(folderCount)]['items'][str(itemCount)]['mpaaRating'] = itemFile.find('MpaaRating').text
                            except:
                                json_recordings[str(folderCount)]['items'][str(itemCount)]['mpaaRating'] = ''
                                #
                            itemCount += 1
                #
                folderCount += 1
            #
            return json_recordings
            #
        except Exception as e:
            log_internal(logException, logDescDeviceCreateRecordingsHtml, exception=e)
            return False

    def _retrieve_recordings(self, recurse, itemCount=''):
        #
        url = 'https://{ipaddress}'.format(ipaddress=get_cfg_details_ip())
        uri = '/TiVoConnect?Command=QueryContainer&Container=%2FNowPlaying&Recurse={recurse}{itemCount}'.format(recurse=recurse,
                                                                                                                itemCount=itemCount)
        try:
            #
            r = self.tivoSession.get('{url}{uri}'.format(url=url, uri=uri))
            r_pass = True if r.status_code == requests.codes.ok else False
            #
            result = logPass if r_pass else logFail
            #
            log_outbound(result,
                         get_cfg_details_ip(), self._port, 'GET', uri,
                         '-', '-',
                         r.status_code)
            #
            if r.status_code == requests.codes.ok:
                try:
                    return r.content.decode()
                except:
                    return r.content
            else:
                return False
        except Exception as e:
            #
            log_outbound(logException,
                         get_cfg_details_ip(), self._port, 'GET', uri,
                         '-', '-',
                         '-',
                         exception=e)
            return False

    def _send_telnet(self, ipaddress, port, data='', response=False):
        try:
            tn = telnetlib.Telnet(ipaddress, port)
            time.sleep(0.1)
            output = tn.read_eager() if response else None
            if data:
                tn.write((str(data) + "\n").encode('ascii'))
                time.sleep(0.1)
                op = tn.read_eager()
                if op == '':
                    output = True
                elif response:
                    output = op if op else True
                else:
                    output = bool(op)
            tn.close()
            return output
        except Exception as e:
            #
            log_outbound(logException,
                         get_cfg_details_ip(), self._port, 'TELNET', '',
                         '-', '-',
                         '-',
                         description=data,
                         exception=e)
            return False

    def getRecordings(self):
        try:
            self._check_recordings()
            #
            return {'recordings': self.recordings,
                    'timestamp': self.recordings_timestamp.strftime('%d/%m/%Y %H:%M')}
        except Exception as e:
            log_internal(logException, logDescDeviceGetRecordings, exception=e)
            return {'recordings': False,
                    'timestamp': 'n/a'}

    def getChan(self):
        #
        response = self._send_telnet(get_cfg_details_ip(), self._port, response=True)
        #
        if not bool(response):
            return False
        #
        nums = [int(s) for s in response.split() if s.isdigit()]
        #
        if len(nums) > 0:
            chan_no = nums[0]
            if bool(chan_no):
                #
                chan_details = get_channel_details_from_key(chan_no)
                #
                json_channel = {}
                json_channel['channel'] = {}
                json_channel['channel']['id'] = chan_details['id']
                json_channel['channel']['name'] = chan_details['name']
                json_channel['channel']['number'] = str(chan_no)
                json_channel['channel']['quality'] = chan_details['quality']
                json_channel['channel']['plus1'] = chan_details['plus1']
                #
                return json_channel
        return False

    def getCommands(self):
        #
        try:
            cmds = []
            #
            for c in commands:
                cmds.append(c)
            #
            return {'commands': cmds}
        except Exception as e:
            log_internal(logException, logDescDeviceGetCommand, exception=e)
            return {'commands': []}

    def sendPin(self):
        #
        pin = get_cfg_details_pin()
        #
        try:
            rsp = []
            for num in pin:
                code = commands[num]
                rsp.append(self._send_telnet(get_cfg_details_ip(), self._port, data=code))
            #
            result = logPass if not (False in rsp) else logFail
            log_internal(result, logDescDeviceSendPin)
            return not (False in rsp)
        except Exception as e:
            log_internal(logException, logDescDeviceSendPin, exception=e)
            return False

    def getChannels(self):
        try:
            r_pass = get_channels(get_cfg_details_package())
            #
            result = logPass if r_pass else logFail
            log_internal(result, logDescDeviceGetChannelsForPackage)
            return r_pass
        except Exception as e:
            log_internal(logException, logDescDeviceGetChannelsForPackage, exception=e)
            return False

    def sendChannel(self, chan_id, plus1=False):
        try:
            chan_key = get_channel_key_from_id(chan_id, plus1)
            if chan_key:
                response = self._send_telnet(ipaddress=get_cfg_details_ip(),
                                             port=self._port,
                                             data=("SETCH {chan_key}\r").format(chan_key=chan_key),
                                             response=True)
                if not isinstance(response, bool):
                    if response.startswith('CH_FAILED'):
                        log_internal(logFail, logDescDeviceSendChannel)
                        return False
                    else:
                        log_internal(logPass, logDescDeviceSendChannel)
                        return True
            log_internal(logFail, logDescDeviceSendChannel)
            return False
        except Exception as e:
            log_internal(logException, logDescDeviceSendChannel, exception=e)
            return False

    def sendCmd(self, command):
        try:
            r_pass = self._send_telnet(get_cfg_details_ip(), self._port, data=commands[command])
            #
            result = logPass if r_pass else logFail
            log_internal(result, logDescDeviceSendCommand)
            return r_pass
        except Exception as e:
            log_internal(logException, logDescDeviceSendCommand, exception=e)
            return False
