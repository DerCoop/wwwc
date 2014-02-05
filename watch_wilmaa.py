#!/usr/bin/env python

"""
    get wilmaa stream and store it into 2 buffer files (with defined length)
    """

__author__ = 'cooper'

import os
import subprocess
import sys
import logging as log
from xml.dom import minidom
import wwwc.config as config
import wwwc.streamhandler as streamhandler
import wwwc.channelhandler as channelhandler


def die(rc, message):
    """print message and exit"""
    log.error(message)
    sys.exit(rc)


def get_user_data(userdata, main_config):
    """get userdata from wilmaa server"""
    username = userdata.get('username')
    passwd = userdata.get('passwd')

    proxy = main_config.get('proxy')
    uagent = main_config.get('uagent')
    tmppath = main_config.get('tmppath')

    _POST_ = 'username=' + username + '&password=' + passwd
    _URL_ = 'https://box.wilmaa.com/web/loginUser?host=www.wilmaa.com'
    print 'get user data'
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


def cleanup_tmpdir(tmppath):
    import shutil

    for root, dirs, files in os.walk(tmppath):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


def main():
    """main"""
    configfile = '/usr/local/wwwc/config/default_config.ini'

    opts, args = config.get_cli_options()

    # configure logger
    # reset old log settings
    if log.root:
        del log.root.handlers[:]

    formatstring = '[%(levelname)s]: %(message)s'
    # get loglevel, commandline || default value

    if opts.loglevel:
        loglevel = log.getLevelName(opts.loglevel.upper())
    else:
        loglevel = log.WARN

    log.basicConfig(format=formatstring, level=loglevel)

    # parse config
    if opts.config_file:
        configfile = opts.config_file

    if not os.path.isfile(configfile):
        msg = 'config file did not exist (' + configfile + ')'
        die(-1, msg)

    main_config = config.get_config_section(configfile, 'main')
    userdata = config.get_config_section(configfile, 'userdata')

    tmppath = main_config.get('tmppath')

    if not tmppath:
        tmppath = os.mkdtemp()

    try:
        os.mkdir(tmppath)
    except:
        pass

    # cleanup the tmpdir
    cleanup_tmpdir(tmppath)

    main_config.set('tmppath', tmppath)

    user_id = get_user_data(userdata, main_config)
    if not user_id:
        die(-1, 'unknown user ID')

    # TODO if userID is given, start here? check this out
    uid_cookie = create_user_id_cookie(user_id, tmppath)
    channel_list = channelhandler.get_channel_list(uid_cookie, main_config)

    if opts.channel:
        channel = opts.channel
        channel_url = channelhandler.get_url_from_channel(channel_list, channel)
    else:
        channel_url = channelhandler.select_channel(channel_list)

    rc, msg = streamhandler.dump_to_file(channel_url, uid_cookie, main_config)

    if int(rc) < 0:
        die(rc, msg)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Abort by user.')

# vim: ft=py:tabstop=4:et