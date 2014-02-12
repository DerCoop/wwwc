"""streamhandler for wilmaa tv

    Python module to handle the wilmaa stream

    """

import logging as log
import subprocess
import os
import urllib2


def get_current_sequence(channel_url, session):
    """get the current sequence from the paylist"""
    proxy = session.get('proxy')
    uagent = session.get('uagent')
    resolution = session.get('resolution')
    url = str(channel_url) + '/index_' + str(resolution) + '_av-p.m3u8'

    header = {}
    header['User-Agent'] = uagent

    req = urllib2.Request(url, None, header)
    opener = urllib2.build_opener()
    opener.add_handler(urllib2.HTTPCookieProcessor(session.get_cookie()))
    if proxy:
        proxy = urllib2.ProxyHandler({'http': proxy, 'https': proxy})
        opener.add_handler(proxy)

    urllib2.install_opener(opener)

    response = urllib2.urlopen(req)
    stream = response.read()

    try:
        for line in stream.split('\n'):
            if line.startswith('#EXT-X-MEDIA-SEQUENCE'):
                return line.split(':')[1]
    except:
        return 0


def get_next_file(filename):
    from math import *
    filename += 1
    filename %= 2
    return int(filename)


def save_segment(stream, filename, main_config):
    """save a segment of a stream"""
    buffersize = main_config.get('buffer_size')
    tmppath = main_config.get('tmppath')

    tfile = os.path.join(tmppath, str(filename))
    try:
        fsize = os.stat(tfile).st_size
    except:
        fsize = 0
    if int(fsize) > int(buffersize):
        log.warn('filesize exceed, switch to next file')
        filename = get_next_file(filename)
        tfile = os.path.join(tmppath, str(filename))
        try:
            os.remove(tfile)
        except:
            pass
    with open(tfile, 'a') as fd:
        fd.write(stream)
    log.debug('wrote to %s', tfile)
    return filename


def get_stream(channel_url, seq, session):
    """get a segment of the stream"""
    proxy = session.get('proxy')
    uagent = session.get('uagent')
    resolution = session.get('resolution')
    url = str(channel_url) + '/segment' + str(seq) + '_' + str(resolution) + '_av-p.ts?sd=6'

    header = {}
    header['User-Agent'] = uagent

    req = urllib2.Request(url, None, header)
    opener = urllib2.build_opener()
    opener.add_handler(urllib2.HTTPCookieProcessor(session.get_cookie()))
    if proxy:
        proxy = urllib2.ProxyHandler({'http': proxy, 'https': proxy})
        opener.add_handler(proxy)

    urllib2.install_opener(opener)

    try:
        response = urllib2.urlopen(req)
        return response.read()
    except:
        return


def dump_to_file(channel_url, session):
    """get current pieces of the stream and save it into a file"""
    curseq = 0
    filename = 0
    counter = 0

    while True:
        sequence = get_current_sequence(channel_url, session)
        if not sequence:
            if counter == 3:
                return -1, 'stream not available'
            counter += 1
            break
        else:
            counter = 0
        # XXX session can be a class with session cookie, uid cookie? start and last sequence
        log.debug(sequence)
        # TDOD cleanup this shit
        startseq = int(sequence)
        endseq = int(sequence) + 10
        if curseq < startseq:
            curseq = startseq
        log.debug('cur: %i', curseq)
        for seq in range(curseq, endseq):
            stream = get_stream(channel_url, seq, session)
            if not stream:
                log.error('failed %i', seq)
                break
            else:
                filename = save_segment(stream, filename, session)
                log.debug('got %i', seq)
                curseq = seq + 1
    return