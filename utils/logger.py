import logging.handlers
import os
from utils.config import get_config

config = get_config()

class Logger():
    '''
    Creates loggers for the various modules
    '''
    def __init__(self):
        self.__format = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        self.__log_level = logging.getLevelName(config['logs']['log_level'].upper())
        self.__log_path = os.path.dirname(os.path.split(os.path.abspath(__file__))[0])+'/Trailer-Technician.log'

    def get_log(self, name):
        log = logging.getLogger(name)
        log.setLevel(self.__log_level)
        
        sh = logging.StreamHandler()
        sh.setFormatter(self.__format)
        log.addHandler(sh)

        if config['logs']['log_to_file'].lower() == 'true':
            fh = logging.handlers.RotatingFileHandler(self.__log_path, mode='a', maxBytes=1000000, backupCount=5, encoding='UTF-8')
            fh.setLevel(self.__log_level)
            fh.setFormatter(self.__format)
            log.addHandler(fh)

        return log
