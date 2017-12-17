import sys
from multiprocessing import Process

from config.config import get_cfg_serviceid
from discovery.broadcast import broadcast_service
from log.log import log_internal, set_logfile
from portlistener import start_bottle

try:

    ################################
    # Set logfile

    set_logfile()

    ################################

    log_internal(True, logDescStartingService, desc='started')

    ################################
    # Receive sys arguments

    # Argument 1: Port of self exposed on host
    try:
        self_port = sys.argv[1]
    except Exception as e:
        raise Exception('self_port not available - {e}'.format(e=e))

    ################################
    # Initiate service broadcast

    process_broadcast = Process(target=broadcast_service, args=(get_cfg_serviceid(), self_port, ))
    process_broadcast.start()

    ################################
    # Port_listener

    log_internal(True, logDescPortListener.format(port=self_port), desc='starting')

    start_bottle(self_port)

    process_broadcast.terminate()

    log_internal(True, logDescPortListener.format(port=self_port), desc='stopped')

except Exception as e:
    log_internal(True, logDescStartingService, desc='fail', exception=e)
