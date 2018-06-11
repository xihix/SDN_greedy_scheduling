from enum import Enum
from time import time
import os
from scipy.stats import norm
from random import gauss


def create_gen(_lst):
    _tmp_lst = _lst[::-1]

    def _gen():
        while True:
            if len(_tmp_lst) == 0:
                yield 0
            else:
                yield _tmp_lst.pop()

    return _gen


def create_err_gen(_dist_name, _acc, _path, _mode="r"):
    _sigma = 0.5 / norm.ppf((_acc + 1) / 2)
    _gen = None

    if _path is not None:
        if _mode == "r":
            _path = open(_path, "r")

        elif _mode == "w":
            _path = open(_path, "w+")

    if _dist_name == "normal":

        def _normal_gen():
            while True:
                _err = 0

                if _acc < 1:
                    _err = int(round(gauss(0, _sigma)))

                if _path is None:
                    yield _err
                else:
                    if _mode == "r":
                        _num = _path.readline().strip()
                        if len(_num) > 0:
                            yield int(_num)
                        else:
                            yield 0
                    elif _mode == "w":
                        _path.write("{}\n".format(_err))
                        yield
                    else:
                        raise Exception("Unknown mode: {}".format(_mode))

        _gen = _normal_gen

    else:
        raise Exception("dist. unsupported.")

    return _gen


class Timer:

    def __init__(self):
        self.__start_time = None
        self.__end_time = None
        self.reset()

    def reset(self):
        self.__start_time = -1
        self.__end_time = -1

    def __enter__(self):
        self.reset()
        self.__start_time = time()

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        self.__end_time = time()

    @property
    def has_ended(self):
        return self.__end_time > 0

    @property
    def duration(self):
        if self.has_ended:
            return self.__end_time - self.__start_time
        else:
            return -1


class Policy(Enum):
    FIFO = 1
    LIFO = 2
    RAND = 3

    @staticmethod
    def get(_policy_name):
        return getattr(Policy, _policy_name)


class Constant:
    INPUT_QUEUE = 0
    OUTPUT_QUEUE = 1
    NOT_FINISHED = -1
    ARR = 0
    SRV = 1


class Counter:

    def __init__(self, _val=-1):
        self.__val = _val
        self.__init = _val

    def inc_n_get(self):
        self.__val += 1
        return self.__val

    def get_val(self):
        return self.__val

    def reset(self):
        self.__val = self.__init


def locate_folders(_paths):
    for _path in _paths:
        try:
            if not os.path.exists(_path):
                os.makedirs(_path)
        except FileExistsError:
            pass


def count(_el, _lst):
    if len(_lst) == 0:
        return 0
    else:
        return len(list(filter(lambda _other: _other == _el, _lst)))


if __name__ == '__main__':
    _acc = 0.5
    _sigma = 0.5 / norm.ppf((_acc + 1) / 2)

    print(_sigma)

    samples = [round(gauss(0, _sigma)) for _ in range(100000)]
    import numpy as np
    import math
    print(np.average(samples), math.sqrt(np.var(samples)))
