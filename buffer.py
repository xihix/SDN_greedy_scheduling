import numpy as np
from util import *
from collections import deque
from random import choice, sample


class Buffer:

    # Default queueing policy
    POLICY = Policy.FIFO

    """
    :param policy: queueing policy
    :param buffer: actual queue
    :param cap: queue backlog capacity
    """
    def __init__(self, _cap=None):
        self.__policy = Buffer.POLICY
        self.__buffer = deque(maxlen=_cap)

    @staticmethod
    def set_policy(_policy):
        if type(_policy) is Policy:
            Buffer.POLICY = _policy
        elif type(_policy) is str:
            Buffer.POLICY = Policy.get(_policy)
        else:
            raise Exception("Unknown type for queueing policy. [%s]" % (type(_policy),))

    @property
    def policy(self):
        return self.__policy

    @property
    def length(self):
        return len(self.__buffer)

    @property
    def cap(self):
        return self.__buffer.maxlen or np.inf

    def put(self, _new_reqs):
        _actual_num = min(len(_new_reqs), self.cap - self.length)
        _actual_reqs = _new_reqs[:_actual_num]
        _dropped_reqs = _new_reqs[_actual_num:]

        if self.__policy == Policy.FIFO:
            # appendleft and pop
            for _req in _actual_reqs:
                self.__buffer.appendleft(_req)

        elif self.__policy == Policy.LIFO:
            # append and pop
            for _req in _actual_reqs:
                self.__buffer.append(_req)

        elif self.__policy == Policy.RAND:
            # randomly insert
            for _req in _actual_reqs:
                _idx = 0
                if self.length > 0:
                    _idx = choice(range(self.length))
                self.__buffer.insert(_idx, _req)

        else:
            raise Exception("Unknown policy: [{}]".format(self.__policy))

        return len(_dropped_reqs)

    def serve(self, _num_reqs):
        _actual_num = min(_num_reqs, self.length)
        _served_reqs = []

        if self.__policy == Policy.FIFO:

            _served_reqs = [self.__buffer.pop() for _ in range(_actual_num)]

        elif self.__policy == Policy.LIFO:

            _served_reqs = [self.__buffer.pop() for _ in range(_actual_num)]

        elif self.__policy == Policy.RAND:

            _num = min(_actual_num, self.length)
            _served_reqs = sample(self.__buffer, _num)
            for _req in _served_reqs:
                self.__buffer.remove(_req)

        else:
            raise Exception("Unknown policy: [%s]" % (self.policy,))

        return _served_reqs
