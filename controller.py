from id_manager import id_manager
from buffer import Buffer


class Controller:

    def __init__(self, _srv_gen):
        self.__id = id_manager.get_next_id("Controller")
        self.__proc_buffer = Buffer()
        self.__srv_gen = _srv_gen
        self.__srv_cap = 0

        self.generate_srv_rate()

    def receive(self, _reqs):
        self.__proc_buffer.put(_reqs)

    def store(self, _reqs):
        self.__proc_buffer.put(_reqs)

    def serve(self, _t):
        _actual_num = min(self.next_srv_rate, self.proc_buffer_size)
        _served_reqs = self.__proc_buffer.serve(_actual_num)

        self.generate_srv_rate()

        for req in _served_reqs:
            req.set_fin_time(_t)

        return _served_reqs

    def generate_srv_rate(self):
        self.__srv_cap = self.__srv_gen.next

    @property
    def id(self):
        return self.__id

    @property
    def proc_buffer_size(self):
        return self.__proc_buffer.length

    @property
    def next_srv_rate(self):
        return self.__srv_cap
