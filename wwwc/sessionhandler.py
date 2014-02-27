"""session handler for wilmaa tv

    Python module to handle the wilmaa session

    """

import cookielib
import urllib2
import misc
from config import WwwcConfig
from xml.dom import minidom
import logging as log


class WilmaaSession(WwwcConfig):
    """class for wilmaa sessions"""

    def __init__(self, filename, section):
        WwwcConfig.__init__(self, filename, section)
        self.header = {}
        self.header['User-Agent'] = self.config.get('uagent')
        #self.tmppath = self.config.get('tmppath')
        self.cookie = cookielib.CookieJar()
        try:
            _proxy = self.config.get('proxy')
            self.proxy = urllib2.ProxyHandler({'http': _proxy, 'https': _proxy})
        except:
            # TODO add handling for separate proxies
            self.proxy = None

    def add_cookie(self, cookie):
        """add a netscape cookie by hand"""
        self.cookie.set_cookie(cookie)

    def get_cookie(self):
        """get the cookie"""
        return self.cookie

    def get_header(self):
        """get the header"""
        return self.header

    def get_proxy(self):
        return self.proxy

    def get_segment_url(self, seq):
        _res = self.config.get('resolution')
        _channel = self.config.get('channel')
        return str(_channel) + '/segment' + str(seq) + '_' + str(_res) + '_av-p.ts?sd=6'

    def get_sequence_url(self):
        _res = self.config.get('resolution')
        _channel = self.config.get('channel')
        return str(_channel) + '/index_' + str(_res) + '_av-p.m3u8'

    def get_stream(self, seq):
        """get a segment of the stream"""
        url = self.get_segment_url(seq)
        header = self.get_header()

        req = urllib2.Request(url, None, header)
        opener = urllib2.build_opener()
        opener.add_handler(urllib2.HTTPCookieProcessor(self.get_cookie()))
        try:
            opener.add_handler(self.get_proxy())
        except:
            log.warning('can not add proxy')

        urllib2.install_opener(opener)

        try:
            response = urllib2.urlopen(req, timeout=10)
            return response.read()
        except:
            return

    def get_current_sequence(self):
        """get the current sequence from the paylist"""
        url = self.get_sequence_url()
        header = self.get_header()

        req = urllib2.Request(url, None, header)
        opener = urllib2.build_opener()
        opener.add_handler(urllib2.HTTPCookieProcessor(self.get_cookie()))
        try:
            opener.add_handler(self.get_proxy())
        except:
            log.warning('can not add proxy')

        urllib2.install_opener(opener)

        try:
            response = urllib2.urlopen(req, timeout=10)
            stream = response.read()
        except:
            return 0

        try:
            for line in stream.split('\n'):
                if line.startswith('#EXT-X-MEDIA-SEQUENCE'):
                    return line.split(':')[1]
        except:
            return 0


def get_user_data(username, passwd, main_config):
    """get userdata from wilmaa server"""
    import urllib
    import urllib2

    proxy = main_config.get('proxy')
    uagent = main_config.get('uagent')

    values = {}
    values['host'] = 'www.wilmaa.com'
    values['username'] = username
    values['password'] = passwd
    data = urllib.urlencode(values)

    header = {}
    header['User-Agent'] = uagent

    url = 'https://box.wilmaa.com/web/loginUser'
    req = urllib2.Request(url, data, header)

    opener = urllib2.build_opener()
    if proxy:
        proxy = urllib2.ProxyHandler({'http': proxy, 'https': proxy})
        opener.add_handler(proxy)

    urllib2.install_opener(opener)

    print 'get user data'
    response = urllib2.urlopen(req,timeout=10)
    stream = response.read()

    userdata = minidom.parseString(stream)
    for entry in userdata.firstChild.childNodes:
        if entry.nodeName == 'authenticated':
            if entry.firstChild.data == 'false':
                misc.die(-1, 'login failure, check your data')
        elif entry.nodeName == 'user':
            for subentry in entry.childNodes:
                if subentry.nodeName == 'user_id':
                    user_id = subentry.firstChild.data
                    return user_id
    return


def create_cookie(name, value):
    """create netscape formatted cookie

        format specification
        Domain	not_complete_url	/	only_https	expire_time	name	value

        :param name: the name of the cookie
        :param value: value of the cookie
        :return: the cookie

        """

    return cookielib.Cookie(
        domain="www.wilmaa.com",
        domain_specified=False,
        domain_initial_dot=False,
        path="/",
        secure=False,
        expires=None,
        name=name,
        value=value,
        version=0,
        port=None,
        port_specified=False,
        path_specified=True,
        discard=False,
        comment=None,
        comment_url=None,
        rest=None
    )


def create_uid_cookie(user_id, session):
    if not user_id:
        import getpass
        print 'No user_id found in config file'
        username = raw_input('Username: ')
        passwd = getpass.getpass()
        user_id = get_user_data(username, passwd, session)
        print 'user id:', user_id
        if not user_id:
            misc.die(-1, 'unknown user ID')

    return create_cookie('wilmaUserID', user_id)