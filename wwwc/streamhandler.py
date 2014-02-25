"""streamhandler for wilmaa tv

    Python module to handle the wilmaa stream

    """

import logging as log
import threading
import os
import urllib2
import time
from ringbuffer import RingBuffer


class Stream(threading.Thread):
    """class to store the stream in a fifo (as daemon)"""
    queue = RingBuffer()

    def __init__(self, fifo):
        threading.Thread.__init__(self)
        self.fifo = fifo


    def run(self):
        """write all segments from queue to fifo"""
        try:
            os.mkfifo(self.fifo)
        except:
            pass

        with open(self.fifo, 'a+') as fifo:
            while True:
                while self.queue.is_empty():
                    time.sleep(1)
                segment = self.queue.pop()
                fifo.write(segment)


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
    counter = 0

    fifoname = os.path.join(session.get('tmppath'), 'streamfifo')

    stream_thread = Stream(fifoname)
    stream_thread.setDaemon(True)
    stream_thread.start()

    while True:
        sequence = get_current_sequence(channel_url, session)
        if not sequence:
            if counter == 3:
                return -1, 'stream not available'
            counter += 1
            break
        else:
            counter = 0
        log.debug(sequence)

        startseq = int(sequence)
        endseq = int(sequence) + 10
        if curseq < startseq:
            curseq = startseq
        log.debug('cur: %i', curseq)
        for seq in range(curseq, endseq):
            stream = get_stream(channel_url, seq, session)
            if not stream:
                # XXX if we have <8 segments at the queue, we can try to get it again
                log.error('failed %i', seq)
                break
            else:
                # write segment to queue
                Stream.queue.push(stream)
                log.debug('got %i', seq)
                curseq = seq + 1
    return