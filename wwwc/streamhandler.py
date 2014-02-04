"""streamhandler for wilmaa tv

    Python module to handle the wilmaa stream

    """

import logging as log
import subprocess
import os


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


def get_next_file(filename):
    from math import *
    filename += 1
    filename %= 2
    return int(filename)


def save_segment(stream, tmppath, filename, buffersize):
    """save a segment of a stream"""
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


def dump_to_file(tmppath, channel_url, uid_cookie, uagent, resolution, buffersize, proxy=None):
    """get current pieces of the stream and save it into a file"""
    curseq = 0
    filename = 0
    while True:
        sequence = get_current_sequence(channel_url, uid_cookie, tmppath, uagent, resolution, proxy=proxy)
        if not sequence:
            return -1, 'stream not available'
        # XXX session can be a class with session cookie, uid cookie? start and last sequence
        log.debug(sequence)
        # TDOD cleanup this shit
        startseq = int(sequence)
        endseq = int(sequence) + 10
        if curseq < startseq:
            curseq = startseq
        log.debug('cur: %i', curseq)
        for seq in range(curseq, endseq):
            stream = get_stream(channel_url, tmppath, uagent, seq, resolution, proxy=None)
            if not stream:
                log.error('failed %i', seq)
                break
            else:
                filename = save_segment(stream, tmppath, filename, buffersize)
                log.debug('got %i', seq)
                curseq = seq + 1
    return