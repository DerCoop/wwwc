"""streamhandler for wilmaa tv

    Python module to handle the wilmaa stream

    """

import logging as log
import threading
import os
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
        while self.queue.is_empty():
            time.sleep(1)
        try:
            os.mkfifo(self.fifo)
        except:
            pass

        with open(self.fifo, 'a+') as fifo:
            while self.queue.is_empty():
                time.sleep(1)
            while True:
                while self.queue.is_empty():
                    time.sleep(1)
                segment = self.queue.pop()
                fifo.write(segment)


class Segments(threading.Thread):
    def __init__(self, session, segment):
        threading.Thread.__init__(self)
        self.segment = segment
        # the cookie is changing if we get a new segment list
        self.session = session

    def run(self):
        self.stream = self.session.get_stream(self.segment)

    def get_stream_segment(self):
        return self.stream


def dump_to_file(session):
    """get current pieces of the stream and save it into a file"""
    curseq = 0
    counter = 0

    fifoname = session.get('stream_file')

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

        log.debug('get %i to %i', curseq, endseq)
        streams = {}
        for seq in range(curseq, endseq):
            seg = Segments(session, seq)
            seg.setDaemon(True)
            seg.start()
            streams[seq] = seg

            #stream = session.get_stream(seq)
        for seq in range(curseq, endseq):
            streams[seq].join()
            stream = streams[seq].get_stream_segment()
            if not stream:
                # XXX if we have <8 segments at the queue, we can try to get it again
                log.error('failed %i', seq)
                #break
            else:
                # write segment to queue
                Stream.queue.push(stream)
                log.debug('got %i', seq)
                curseq = seq + 1

    return 0, 'quit'