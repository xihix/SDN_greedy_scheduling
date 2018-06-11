from buffer import Buffer
from util import Policy, Counter, create_err_gen, create_gen
from request import Request
from id_manager import id_manager
from generator import PROCS
from random import randint


class DataSource:

    def __init__(self, _config):
        self.__id = id_manager.get_next_id("DataSource")
        self.__win_size = _config["WIN_SIZE"]

        self.__buffers = [Buffer() for _ in range(self.__win_size + 1)]
        self.__policy = Policy.get(_config["POLICY"])

        _ds_path = None
        if "DATA_SOURCE" in _config:
            _ds_path = "{}/ds-{}".format(_config["DATA_SOURCE"], self.__id)
            # _err_path = "{}/err-{}".format(_config["DATA_SOURCE"], self.__id)
            # _nums = [
            #     int(_el.strip())
            #     for _el in list(open(_err_path).readlines())
            #     if len(_el) > 0
            # ]
            # self.__err_gen = create_gen(_nums)
        else:
            # self.__err_gen = create_err_gen(_config["ERR_DIST"], _config["PRED_ACC"], None)
            pass

        self.__req_gen = \
            PROCS[_config["ARR_PROC"]](_config["ARR_RATE"], _ds_path)
        self.__cur_time = Counter()

    def init_fillup(self):
        for _t in range(self.win_size + 1):
            self.__cur_time.inc_n_get()
            _num_new_reqs = self.__req_gen.next
            _new_reqs = [Request(_t) for _ in range(_num_new_reqs)]
            self.__buffers[_t].put(_new_reqs)

    def slide(self):
        self.__buffers = self.__buffers[1:]
        self.__buffers.append(Buffer())

        _num_new_reqs = self.__req_gen.next
        _cur_time = self.__cur_time.inc_n_get()

        _new_reqs = [Request(_cur_time) for _ in range(_num_new_reqs)]
        self.__buffers[-1].put(_new_reqs)

        # _err = next(self.__err_gen())

        # if _err >= 0:
        #     return _err
        # else:
        #     self.__buffers[0].put([Request(_cur_time - self.win_size) for _ in range(abs(_err))])
        #     return _err
        return 0

    def emit(self, _num_reqs):

        _residual_num = _num_reqs
        assert _residual_num >= 0

        _buffers = self.__buffers.copy()
        _req_lst = _buffers[0].serve(_residual_num)
        _residual_num -= len(_req_lst)

        if self.__policy is Policy.FIFO:

            for _buf in _buffers:

                if _residual_num == 0:
                    break
                else:
                    _admitted_reqs = _buf.serve(_residual_num)
                    _req_lst.extend(_admitted_reqs)
                    _residual_num -= len(_admitted_reqs)

        elif self.__policy is Policy.LIFO:

            _buffers.reverse()

            for _buf in _buffers:

                if _residual_num == 0:
                    break
                else:
                    _admitted_reqs = _buf.serve(_residual_num)
                    _req_lst.extend(_admitted_reqs)
                    _residual_num -= len(_admitted_reqs)

        elif self.__policy is Policy.RAND:

            _count = 0

            while _count < _residual_num and len(_buffers) > 0:

                _num_buf = len(_buffers)
                _idx = randint(0, _num_buf - 1)

                if _buffers[_idx].length > 0:
                    _req_lst.extend(_buffers[_idx].serve(1))
                    _count += 1
                else:
                    _buf = _buffers[_idx]
                    _buffers.remove(_buf)

        else:
            raise Exception("Unknown Policy: {}".format(self.__policy))

        return _req_lst

    @property
    def buffer_sizes(self):
        return [buf.length for buf in self.__buffers]

    @property
    def size(self):
        return sum(self.buffer_sizes)

    @property
    def win_size(self):
        return self.__win_size

    @property
    def policy(self):
        return self.__policy

    @property
    def id(self):
        return self.__id
