import datetime
import time
import xml.etree.ElementTree as ET
import telnetlib
import requests as requests
from requests.auth import HTTPDigestAuth
from multiprocessing import Manager, Process

from resources.global_resources.variables import *
from parameters import recordings_check_period
from log.log import log_outbound
from config.config import get_cfg_details_ip, get_cfg_details_mak, get_cfg_details_pin

# Issue with IDE and production running of script - resolved with try/except below
try:
    # IDE
    from virginmedia_tivo.commands import commands
    from virginmedia_tivo.channels_functions import get_channel_name_from_key, get_channel_details_from_key, get_channel_key_from_name
except:
    # Production
    from commands import commands
    from channels_functions import get_channel_name_from_key, get_channel_details_from_key, get_channel_key_from_name

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


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
        if self.recordings_timestamp == 0 or datetime.datetime.now() > (self.recordings_timestamp + datetime.timedelta(minutes=recordings_check_period)):
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
            folders = self._retrieve_recordings('No').replace(' xmlns="http://www.tivo.com/developer/calypso-protocol-1.6/"', '')
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
            self.recordings_timestamp = datetime.datetime.now()
            self.recordings = self._create_recordings_json(self.recordings_timestamp, xml_folders, xml_files)
            #
            ############
            #
            #TODO - log entry
            #
        except Exception as e:
            #TODO - log entry
            self.recordings_timestamp = 0
            self.recordings = False

    def _create_recordings_json(self, _timestamp, _folders, _files):
        #
        json_recordings = {}
        json_recordings["recordings"] = {}
        json_recordings["timestamp"] = _timestamp.strftime('%d/%m/%Y %H:%M:%S')

        #
        if len(_folders) == 0 or len(_files) == 0:
            return False
        #
        try:
            #
            folderCount = 0
            for itemFolder in _folders:
                if itemFolder.find('Title').text != 'Suggestions' and itemFolder.find('Title').text != 'HD Recordings':
                    json_recordings['recordings'][str(folderCount)] = {}
                    json_recordings['recordings'][str(folderCount)]['folderName'] = itemFolder.find('Title').text
                    json_recordings['recordings'][str(folderCount)]['type'] = '-'
                    #
                    json_recordings['recordings'][str(folderCount)]['items'] = {}
                    #
                    # Run through individual items
                    itemCount = 0
                    for itemFile in _files:
                        #
                        if itemFile.find('Title').text == itemFolder.find('Title').text:
                            #
                            json_recordings['recordings'][str(folderCount)]['items'][str(itemCount)] = {}
                            #
                            try:
                                json_recordings['recordings'][str(folderCount)]['items'][str(itemCount)][
                                    'episodeTitle'] = itemFile.find('EpisodeTitle').text
                            except Exception as e:
                                json_recordings['recordings'][str(folderCount)]['items'][str(itemCount)][
                                    'episodeTitle'] = ''
                            #
                            json_recordings['recordings'][str(folderCount)]['items'][str(itemCount)]['channel'] = {}
                            #
                            try:
                                json_recordings['recordings'][str(folderCount)]['items'][str(itemCount)]['channel'][
                                    'name'] = get_channel_name_from_key(int(itemFile.find('SourceChannel').text))
                            except Exception as e:
                                print (int(itemFile.find('SourceChannel').text))
                                json_recordings['recordings'][str(folderCount)]['items'][str(itemCount)]['channel'][
                                    'name'] = '-'
                            #
                            try:
                                json_recordings['recordings'][str(folderCount)]['items'][str(itemCount)][
                                    'description'] = itemFile.find('Description').text
                            except Exception as e:
                                json_recordings['recordings'][str(folderCount)]['items'][str(itemCount)][
                                    'description'] = ''
                            #
                            try:
                                date = int(itemFile.find('CaptureDate').text, 0)
                                date = datetime.datetime.fromtimestamp(date)
                                json_recordings['recordings'][str(folderCount)]['items'][str(itemCount)][
                                    'recordingDate'] = date.strftime('%d-%m-%Y')
                            except Exception as e:
                                json_recordings['recordings'][str(folderCount)]['items'][str(itemCount)][
                                    'recordingDate'] = '-'
                            #
                            json_recordings['recordings'][str(folderCount)]['items'][str(itemCount)][
                                'episodeNumber'] = {}
                            #
                            try:
                                episodenumber = itemFile.find('EpisodeNumber').text
                                json_recordings['recordings'][str(folderCount)]['items'][str(itemCount)][
                                    'episodeNumber']['series'] = episodenumber[:-2]
                                json_recordings['recordings'][str(folderCount)]['items'][str(itemCount)][
                                    'episodeNumber']['episode'] = episodenumber[-2:]
                            except:
                                json_recordings['recordings'][str(folderCount)]['items'][str(itemCount)][
                                    'episodeNumber']['series'] = ''
                                json_recordings['recordings'][str(folderCount)]['items'][str(itemCount)][
                                    'episodeNumber']['episode'] = ''
                            #
                            try:
                                if itemFile.find('ProgramId').text.startswith('EP'):
                                    json_recordings['recordings'][str(folderCount)]['type'] = 'tv'
                                    json_recordings['recordings'][str(folderCount)]['items'][str(itemCount)][
                                        'mpaaRating'] = ''
                                elif itemFile.find('ProgramId').text.startswith('MV'):
                                    json_recordings['recordings'][str(folderCount)]['type'] = 'movie'
                                    json_recordings['recordings'][str(folderCount)]['items'][str(itemCount)][
                                        'mpaaRating'] = itemFile.find('MpaaRating').text
                            except:
                                json_recordings['recordings'][str(folderCount)]['items'][str(itemCount)][
                                    'mpaaRating'] = ''
                                #
                            itemCount += 1
                #
                folderCount += 1
            #
            return json_recordings
            #
        except Exception as e:
            #TODO - log entry
            return False

    def _retrieve_recordings(self, recurse, itemCount=''):
        #
        url = 'https://{ipaddress}'.format(ipaddress=get_cfg_details_ip())
        uri = '/TiVoConnect?Command=QueryContainer&Container=%2FNowPlaying&Recurse={recurse}{itemCount}'.format(recurse=recurse,
                                                                                                                itemCount=itemCount)
        try:
            #
            r = self.tivoSession.get('{url}{uri}'.format(url=url, uri=uri))
            #
            # TODO - log entry
            #
            if r.status_code == requests.codes.ok:
                return r.content
            else:
                return False
        except Exception as e:
            log_outbound(False, url, uri, 'GET', '-', exception=e)
            return False

    def _send_telnet(self, ipaddress, port, data='', response=False):
        try:
            tn = telnetlib.Telnet(ipaddress, port)
            time.sleep(0.1)
            output = tn.read_eager() if response else None
            if data:
                tn.write(str(data) + "\n")
                time.sleep(0.1)
                op = tn.read_eager()
                if op == '':
                    output = True
                else:
                    output = op if (response and not bool(op)) else True
            tn.close()
            return output
        except:
            # TODO - log entry
            return False

    def getRecordings(self):
        try:
            self._check_recordings()
            return self.recordings
        except Exception as e:
            # TODO - log entry
            return False

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
                json_channel['channel']['number'] = str(chan_no)
                json_channel['channel']['name'] = chan_details['name']
                json_channel['channel']['quality'] = chan_details['quality']
                #
                return json_channel
        return False

    def getCommands(self):
        #
        cmds = []
        #
        for c in commands['commands']:
            cmds.append(c)
        #
        return {'commands': cmds}

    def sendPin(self):
        #
        pin = get_cfg_details_pin()
        #
        try:
            rsp = []
            for num in pin:
                code = commands[num]
                rsp.append(self._send_telnet(get_cfg_details_ip(), self._port, data=code))
                #TODO - log entry
            return not (False in rsp)
        except Exception as e:
            # TODO - log entry
            return False

    def sendChannel(self, chan_name):
        try:
            chan_key = get_channel_key_from_name(chan_name)
            response = self._send_telnet(ipaddress=get_cfg_details_ip(),
                                         port=self._port,
                                         data=("SETCH {chan_key}\r").format(chan_key=chan_key),
                                         response=True)
            if response.startswith('CH_FAILED'):
                return False
            else:
                return True
        except Exception as e:
            # TODO - log entry
            return False

    def sendCmd(self, command):
        try:
            return self._send_telnet(get_cfg_details_ip(), self._port, data=commands[command])
        except:
            # TODO - log entry
            return False