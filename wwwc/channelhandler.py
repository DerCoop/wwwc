"""channelhandler for wilmaa tv

    Python module to handle the wilmaa channels

    """

import os
import sys
import subprocess


class ChannelList:
    """channel list class"""
    def __init__(self, id=None, name=None, url=None, lang=None):
        self.id = id
        self.name = name
        self.url = url
        self.lang = lang

    def det_id(self):
        return self.url

    def get_url(self):
        return self.url

    def get_name(self):
        return self.name

    def get_lang(self):
        return self.lang


def parse_path(path):
    return str(path.split('/')[2])


def get_url(url):
    """strip the network location from a url"""
    from urlparse import urlparse
    # we need the special subpart because the extracted path
    # is from wrong codec
    _subpath_ = 'i'
    uri = urlparse(url)
    path = parse_path(uri.path)
    return uri.scheme + '://' +  uri.netloc + '/' + _subpath_ + '/' + path


def get_channel_list(uid_cookie, uagent, tmppath, proxy=None):
    """get channel list

    :rtype : channel_list[id]
    :param uid_cookie:
    :param uagent:
    :param tmppath:
    :param proxy:

    """
    import json
    #URL = 'http://www.wilmaa.com/channels/ch/webfree_en.xml'
    URL = 'http://www.wilmaa.com/channels/ch/webfree_en.json'
    print 'get channel list'
    # TODO set proxy settings global?!
    if proxy:
        os.putenv('http_proxy', proxy)
        os.putenv('https_proxy', proxy)
    # TODO add proxy only if set
    cmd = ['wget', '-U', uagent, '--quiet', '--save-cookies',
            tmppath + '/cookie', '--load-cookies', uid_cookie,
            '--keep-session-cookies', '-O', '-', URL]
    stream = subprocess.check_output(cmd)
    # TODO sort by language
    channels = json.loads(stream)
    channel_list = {}
    for channel in channels['channelList']['channels']:
        id = channel['id']
        name = channel['label']['name']
        # get only the first URL (with lang)
        # atm there are not more
        url = channel['streams'][0]['url']
        url = get_url(url)
        lang = channel['streams'][0]['lang']
        channel_list[id] = ChannelList(id=id, name=name, url=url, lang=lang)

    return channel_list


def select_channel(channel_list, lang=None):
    """ask for a channel to play"""
    # TODO make it more readable
    tmp_list = {}
    for channel in channel_list:
        name = channel_list[channel].get_name()
        tmp_list[name] = channel
        print name
    sys.stdin.flush()
    selected = raw_input('select a channel: ')
    return channel_list[tmp_list[selected]].get_url()


def get_url_from_channel(channel_list, channel):
    # TODO
    pass
