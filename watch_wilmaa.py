#!/usr/bin/env python

"""
    get wilmaa stream and store it into 2 buffer files (with defined length)
    """
import os
import subprocess

__author__ = 'cooper'
__version__ = '0.1'

import sys
from xml.dom import minidom


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


def die(rc, message):
    """print message and exit"""
    print(message)
    sys.exit(rc)


def get_user_data(username, passwd, uagent, tmppath, proxy=None):
    """get userdata from wilmaa server"""
    _POST_ = 'username=' + username + '&password=' + passwd
    _URL_ = 'https://box.wilmaa.com/web/loginUser?host=www.wilmaa.com'
    print('get user data')
    if proxy:
        os.putenv('http_proxy',proxy)
        os.putenv('https_proxy', proxy)
    cmd = ['wget', '-U', uagent, '--quiet', '--save-cookies',
            tmppath + '/php_session_id' , '--keep-session-cookies',
            '--post-data', _POST_, '-O', '-', _URL_]
    stream = subprocess.check_output(cmd)
    userdata = minidom.parseString(stream)
    for entry in userdata.firstChild.childNodes:
        if entry.nodeName == 'authenticated':
            if entry.firstChild.data == 'false':
                die(-1, 'login failure, check your data')
        elif entry.nodeName == 'user':
            for subentry in entry.childNodes:
                if subentry.nodeName == 'user_id':
                    user_id = subentry.firstChild.data
                    return user_id

    return


def create_user_id_cookie(user_id, tmppath):
    """create cookie with the userid"""
    # www.wilmaa.com	FALSE	/	FALSE	0	wilmaUserID	userid
    cookie = tmppath + 'wilmaa_user_id'
    with open(cookie, 'w+') as fd:
        fd.write('www.wilmaa.com\tFALSE\t/\tFALSE\t0\twilmaUserID\t' + user_id + '\n')
    return cookie


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

        :param: cookie with UIID
        :return: channel_list[id] : channel object
        """
    import json
    #URL = 'http://www.wilmaa.com/channels/ch/webfree_en.xml'
    URL = 'http://www.wilmaa.com/channels/ch/webfree_en.json'
    print('get channel list')
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
    # TODO return dict with {channelname: url}
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
        #print id + ' - ' + name + ' - '  + url + ' - ' + lang

    return channel_list


def get_config_section(file, section):
    """parse config file"""
    # TODO ignore obsolete fields
    import ConfigParser
    dict = {}
    config = ConfigParser.ConfigParser()
    config.read(file)
    for key, value in config.items(section):
        dict[key] = value

    return dict


def select_channel(channel_list, lang=None):
    """ask for a channel to play"""
    tmp_list = {}
    for channel in channel_list:
        name = channel_list[channel].get_name()
        tmp_list[name] = channel
        print name
    selected = raw_input('select a channel: ')
    return channel_list[tmp_list[selected]].get_url()


def get_url_from_channel(channel_list, channel):
    # TODO
    pass


def get_current_sequence(channel_url, uid_cookie, tmppath, uagent, resolution, proxy=None):
    """get the current sequence from the paylist"""
    url = str(channel_url) + '/index_' + str(resolution) + '_av-p.m3u8'
    if proxy:
        os.putenv('http_proxy',proxy)
        os.putenv('https_proxy', proxy)
    cmd = ['wget', '-U', uagent, '--quiet', '--save-cookies',
            tmppath + '/session_cookie', '--load-cookies', uid_cookie,
            '--keep-session-cookies', '-O', '-', url]
    stream = subprocess.check_output(cmd)
    for line in stream.split('\n'):
        if line.startswith('#EXT-X-MEDIA-SEQUENCE'):
            return line.split(':')[1]
    return


def get_stream(channel_url, tmppath, uagent, seq, resolution, proxy):
    """get a segment of the stream"""
    url = str(channel_url) + '/segment' + str(seq) + '_' + str(resolution) + '_av-p.ts?sd=6'
    if proxy:
        os.putenv('http_proxy',proxy)
        os.putenv('https_proxy', proxy)
    cmd = ['wget', '-U', uagent, '--quiet', '--load-cookies', tmppath + '/session_cookie',
            '--keep-session-cookies', '-O', '-', url]
    try:
        return subprocess.check_output(cmd)
    except:
        return


def save_segment(stream, tmppath, filename, buffersize):
    """save a segment of a stream"""
    from math import *
    tfile = os.path.join(tmppath, str(filename))
    try:
        fsize = os.stat(tfile).st_size
    except:
        fsize = 0
    if int(fsize) > int(buffersize):
        print 'filesize exceed'
        filename += 1
        filename %= 2
        tfile = os.path.join(tmppath, str(filename))
        try:
            os.remove(tfile)
        except:
            pass
    with open(tfile, 'a') as fd:
        fd.write(stream)
    print 'wrote to %s' % tfile
    return filename


def dump_to_file(tmppath, channel_url, uid_cookie, uagent, resolution, buffersize, proxy=None):
    """get current pieces of the stream and save it into a file"""
    curseq = 0
    filename = 0
    while True:
        sequence = get_current_sequence(channel_url, uid_cookie, tmppath, uagent, resolution, proxy=proxy)
        if not sequence:
            die(-1, 'stream not available')
        # XXX session can be a class with session cookie, uid cookie? start and last sequence
        print sequence
        # TDOD cleanup this shit
        startseq = int(sequence)
        endseq = int(sequence) + 10
        if curseq < startseq:
            curseq = startseq
        print 'cur', curseq
        for seq in range(curseq, endseq):
            stream = get_stream(channel_url, tmppath, uagent, seq, resolution, proxy=None)
            if not stream:
                print 'failed %i' % seq
                break
            else:
                filename = save_segment(stream, tmppath, filename, buffersize)
                print 'got %i' % seq
                curseq = seq + 1


def main():
    """main"""
    import optparse
    configfile = 'config.ini'

    parser = optparse.OptionParser(usage=optparse.SUPPRESS_USAGE)
    parser.add_option('--loglevel', action='store',
                      help='<critical | error | warning | info | debug | notset>')
    parser.add_option('--config-file', action='store',
                      help='the name of the configfile')
    parser.add_option('--channel', action='store',
                      help='select a channel')
    opts, args = parser.parse_args()

    if opts.config_file:
        configfile = opts.config_file

    # TODO create logger

    main_config = get_config_section(configfile, 'main')
    userdata = get_config_section(configfile, 'userdata')

    username = userdata['username']
    passwd = userdata['passwd']

    proxy = main_config['proxy']
    uagent = main_config['uagent']
    tmppath = main_config['tmppath']
    buffersize = main_config['buffer_size']
    resolution = main_config['resolution']

    if not tmppath:
        tmppath = os.mkdtemp()
    # TODO get this from config!

    try:
        os.mkdir(tmppath)
    except:
        pass
    user_id = get_user_data(username, passwd, uagent, tmppath=tmppath, proxy=proxy)
    if not user_id:
        die(-1, 'unknown user ID')

    # TODO if userID is given, start here? check this out
    uid_cookie = create_user_id_cookie(user_id, tmppath)
    channel_list = get_channel_list(uid_cookie, uagent, tmppath=tmppath, proxy=proxy)

    if opts.channel:
        channel = opts.channel
        print 'comming soon'
        channel_url = select_channel(channel_list)
        #channel_url = get_url_from_channel(channel_list, channel)
    else:
        channel_url = select_channel(channel_list)

    dump_to_file(tmppath, channel_url, uid_cookie, uagent, resolution, buffersize, proxy=proxy)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Abort by user.')
        raise

# vim: ft=py:tabstop=4:et