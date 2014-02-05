"""Config file for watch wilmaa

    Python module for parsing the configuration

    """

import ConfigParser
import optparse


class WwwcConfig:
    """config class"""
    def __init__(self):
        self.config = {}

    def get(self, key):
        try:
            value = self.config[key]
        except:
            value = None
        return value

    def set(self, key, value):
        self.config[key] = value


def get_config_section(file, section):
    """parse defined section of a config file"""
    cfg = WwwcConfig()
    config = ConfigParser.ConfigParser()
    config.read(file)
    for key, value in config.items(section):
        cfg.set(key, value)

    return cfg


def get_cli_options():
    """parse the command line options and arguments"""
    parser = optparse.OptionParser(usage=optparse.SUPPRESS_USAGE)
    parser.add_option('--loglevel', action='store',
                      help='<critical | error | warning | info | debug | notset>')
    parser.add_option('--config-file', action='store',
                      help='the name of the configfile')
    parser.add_option('--channel', action='store',
                      help='select a channel')

    return parser.parse_args()