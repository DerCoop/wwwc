"""Config file for watch wilmaa

    Python module for parsing the configuration

    """

import ConfigParser
import optparse
import logging as log


class WwwcConfig:
    """config class"""
    def __init__(self, filename, section):
        self.config = {}
        self._parse_cfg(filename, section)

    def _parse_cfg(self, filename, section):
        """parse the config file"""
        config = ConfigParser.ConfigParser()
        config.read(filename)
        for key, value in config.items(section):
            self.set(key, value)

    def get(self, key):
        try:
            value = self.config[key]
        except:
            value = None
        return value

    def set(self, key, value):
        self.config[key] = value


def get_config_section(filename, section):
    """parse defined section of a config file
    :rtype : object class WwwcConfig
    """
    return WwwcConfig(filename, section)


def create_stream_session(config):
    """create stream session class from given config"""
    from sessionhandler import WilmaaSession
    return WilmaaSession(config, 'main')


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