"""session handler for wilmaa tv

    Python module to handle the wilmaa session

    """

import cookielib
def get_user_data(userdata, main_config):
    """get userdata from wilmaa server"""
    import urllib
    import urllib2

    username = userdata.get('username')
    passwd = userdata.get('passwd')
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
    response = urllib2.urlopen(req)
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
