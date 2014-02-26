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


def dump_to_file(session):
    """get current pieces of the stream and save it into a file"""
    curseq = 0
    counter = 0

    fifoname = os.path.join(session.get('tmppath'), 'streamfifo')

    stream_thread = Stream(fifoname)
    stream_thread.setDaemon(True)
    stream_thread.start()

    while True:
        sequence = session.get_current_sequence()
        if not sequence:
            if counter == 3:
                return -1, 'stream not available'
            counter += 1
            break
        else:
            counter = 0

        log.debug('cur: %i', int(sequence))
        startseq = int(sequence)
        endseq = int(sequence) + 10
        if curseq < startseq:
            log.debug('skip %i to %i', curseq, startseq - 1)
            curseq = startseq
        log.debug('next: %i', curseq)
        for seq in range(curseq, endseq):
            stream = session.get_stream(seq)
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