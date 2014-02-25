__author__ = 'coop'


import collections


class RingBuffer():
    """a ringbuffer implementation for wwwc"""
    def __init__(self, maxlen=10):
        self.queue = collections.deque(maxlen=maxlen)

    def push(self, segment):
        '''add a segment at the end of the queue'''
        self.queue.append(segment)

    def pop(self):
        '''get the oldest element of the queue or None if the queue is empty'''
        try:
            return self.queue.popleft()
        except:
            return

    def is_empty(self):
        '''returns true if the que is empty or None if not'''
        if self._len() == 0:
            return True
        else:
            return

    def length(self):
        '''returns the length of the queue'''
        return self._len()

    def _len(self):
        return len(self.queue)