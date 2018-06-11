from id_manager import id_manager
from buffer import Buffer
from data_source import DataSource
from generator import PROCS


class Switch:

    LOCAL_ADDR = -1

    def __init__(self, _config):
        _srv_gen = PROCS[_config["SRV_PROC"]](_config["SRV_RATE"], None)
        _comp_gen = PROCS[_config["COMP_PROC"]](_config["COMP_COST"], None)

        self.__id = id_manager.get_next_id("Switch")
        self.__arr_buffers = DataSource(_config)
        self.__arr_buffers.init_fillup()

        self.__proc_buffer = Buffer()  # processing buffer
        self.__srv_gen = _srv_gen
        self.__srv_cap = 0
        self.__assoc_elements = dict({self.LOCAL_ADDR: self})
        self.__cost_table = dict({self.LOCAL_ADDR: _comp_gen})

        self.__next_costs = dict({})
        self.__comm_cost = 0
        self.__comp_cost = 0

        self.generate_srv_rate()

    def add_assoc_controllers(self, _controllers, _comm_cost_gens):
        self.__assoc_elements.update(_controllers)
        self.__cost_table.update(_comm_cost_gens)
        self.generate_next_unit_costs()

    def admit_reqs(self):
        return self.__arr_buffers.slide()

    def forward(self, _addr, _num):
        _reqs = self.__arr_buffers.emit(_num)
        _actual_num = len(_reqs)
        self.__assoc_elements[_addr].store(_reqs)
        
        self.__clear_costs()

        # compute the corresponding communication and computational costs
        if _addr == self.LOCAL_ADDR:
            self.__comp_cost = _actual_num * self.next_unit_costs[self.LOCAL_ADDR]
        else:
            self.__comm_cost = _actual_num * self.next_unit_costs[_addr]

        self.generate_next_unit_costs()

    def store(self, _reqs):
        self.__proc_buffer.put(_reqs)

    def serve(self, _t):
        _actual_num = min(self.next_srv_rate, self.proc_buffer_size)
        _served_reqs = self.__proc_buffer.serve(_actual_num)

        self.generate_srv_rate()

        for req in _served_reqs:
            req.set_fin_time(_t)

        return _served_reqs

    def __clear_costs(self):
        self.__comm_cost = 0
        self.__comp_cost = 0

    def generate_next_unit_costs(self):
        self.__next_costs = {_addr: _gen.next for _addr, _gen in self.__cost_table.items()}

    def generate_srv_rate(self):
        self.__srv_cap = self.__srv_gen.next

    @property
    def incurred_costs(self):
        return self.__comp_cost, self.__comm_cost

    @property
    def next_unit_costs(self):
        return self.__next_costs.copy()

    @property
    def id(self):
        return self.__id

    @property
    def arr_buffer_sizes(self):
        return self.__arr_buffers.buffer_sizes

    @property
    def pred_win_size(self):
        return self.__arr_buffers.win_size

    @property
    def proc_buffer_size(self):
        return self.__proc_buffer.length

    @property
    def assoc_elements(self):
        return self.__assoc_elements.copy()

    @property
    def next_srv_rate(self):
        return self.__srv_cap
