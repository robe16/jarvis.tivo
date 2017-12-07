serviceName = 'Jarvis: TiVo'
serviceType = 'virginmedia_tivo'

logFileNameTimeformat = '%Y-%m-%d'

# NOTE: delimiter-separated value in log files is '::'
logMsg_Inbound_Info = ':{timestamp}::{serviceid}::{servicetype}::INBOUND::{result}::{client}::{uri}::{method}::{httpresponse}::{desc}'
logMsg_Inbound_Error = ':{timestamp}::{serviceid}::{servicetype}::INBOUND::{result}::{exception}::{client}::{uri}::{method}::{httpresponse}::{desc}'
logMsg_Internal_Info = ':{timestamp}::{serviceid}::{servicetype}::INTERNAL::{result}::{operation}::{desc}'
logMsg_Internal_Error = ':{timestamp}::{serviceid}::{servicetype}::INTERNAL::{result}::{exception}::{operation}::{desc}'
logMsg_Outbound_Info = ':{timestamp}::{serviceid}::{servicetype}::OUTBOUND::{result}::{ip}::{uri}::{method}::{httpresponse}::{desc}'
logMsg_Outbound_Error = ':{timestamp}::{serviceid}::{servicetype}::OUTBOUND::{result}::{exception}::{ip}::{uri}::{method}::{httpresponse}::{desc}'

logPass = 'PASS'
logFail = 'FAIL'
logException = 'EXCEPTION'

logDescDeviceGetrecordings = 'Get recordings'
logDescDeviceGetcurrentchannel = 'Get current channel'
logDescDeviceSendchannel = 'Send channel'
logDescDeviceSendcommand = 'Send command'

timeformat = '%Y/%m/%d %H.%M.%S.%f'

uri_config = '/config'
uri_commands = '/commands'
uri_command = '/command'
uri_channel = '/channel'
uri_channels = '/channels'
uri_recordings = '/recordings'
uri_enterpin = '/enterpin'

service_header_clientid_label = 'jarvis.client-service'

httpStatusSuccess = 200
httpStatusBadrequest = 400
httpStatusForbidden = 404
httpStatusFailure = 420
httpStatusServererror = 500

jarvis_broadcastPort = 5000
jarvis_broadcast_msg = 'jarvis::discovery::{service_id}::{service_type}::{port}'
