import os
import sys
from configparser import ConfigParser, MissingSectionHeaderError, NoSectionError

def get_config():
    config = ConfigParser()
    config_path = os.path.abspath(os.path.dirname(os.path.split(os.path.abspath(__file__))[0])+'/settings.ini')
    if not os.path.isfile(config_path):
        raise IOError('Could not find the settings.ini file. Create one using the example "settings.ini.example"')
    try:
        config.read(config_path)
    except Exception as e:
        raise IOError('Could not read settings.ini. {}'.format(e))
    return config