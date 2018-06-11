from util import Counter


class IDManager:

    def __init__(self):
        self._counter_map = {
            "Controller": Counter(),
            "Switch": Counter(),
            "Request": Counter(),
            "Scheduler": Counter(),
            "DataSource": Counter(),
        }

    def reset_all(self):
        for _counter in self._counter_map.values():
            _counter.reset()

    def reset_counter(self, _type_name):
        if _type_name in self._counter_map:
            self._counter_map[_type_name].reset()

    def get_next_id(self, _type_name):
        return self._counter_map[_type_name].inc_n_get()


id_manager = IDManager()
