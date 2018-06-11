from util import Constant
from id_manager import id_manager


class Request:

    def __init__(self, _gen_time):  # , _root_id=None):
        self.__id = id_manager.get_next_id("Request")
        self.__gen_time = _gen_time
        self.__fin_time = Constant.NOT_FINISHED
        # self.__root_id = _root_id or self.__id

    # @property
    # def root_id(self):
    #     return self.__root_id

    @property
    def id(self):
        return self.__id

    @property
    def is_finished(self):
        return self.__fin_time >= 0

    @property
    def duration(self):
        if self.is_finished:
            return max(0, self.__fin_time - self.__gen_time)
        else:
            raise Exception("Not finished?")
            # return Constant.NOT_FINISHED

    @property
    def gen_time(self):
        return self.__gen_time

    def set_fin_time(self, t):
        if self.__fin_time < 0:
            self.__fin_time = t
