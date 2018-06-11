from switch import Switch
from controller import Controller
from generator import PROCS


class DataPlane:

    def __init__(self, _config):
        self.__switches = {}
        _num_switches = _config["NUM_SWITCH"]

        self.add_switches([Switch(_config) for _ in range(_num_switches)])

    def __add_switch(self, _switch):
        self.__switches[_switch.id] = _switch

    def add_switches(self, _switches):
        for _switch in _switches:
            self.__add_switch(_switch)

    def collect_stats(self):
        return {
            _id: _switch.arr_buffer_sizes
            for _id, _switch in self.__switches.items()
        }, {
            _id: _switch.proc_buffer_size
            for _id, _switch in self.__switches.items()
        }, {
            _id: _switch.incurred_costs
            for _id, _switch in self.__switches.items()
        }

    @property
    def unit_assoc_costs(self):
        return {
            _id: _switch.next_unit_costs
            for _id, _switch in self.__switches.items()
        }

    @property
    def switches(self):
        return self.__switches.copy()

    @property
    def num_of_switches(self):
        return len(self.__switches)


class ControlPlane:

    def __init__(self, _config):
        self.__controllers = {}
        _num_controllers = _config["NUM_CONTROLLER"]
        _srv_gen = PROCS[_config["SRV_PROC"]](_config["SRV_RATE"], None)

        self.add_controllers([Controller(_srv_gen) for _ in range(_num_controllers)])

    def __add_controller(self, _controller):
        self.__controllers[_controller.id] = _controller

    def add_controllers(self, _controllers):
        for _controller in _controllers:
            self.__add_controller(_controller)

    def get_controllers_by_ids(self, _id_lst):
        return {_cid: _controller
                for _cid, _controller in self.controllers.items()
                if _controller.id in _id_lst}

    def collect_stats(self):
        return {_id: _controller.proc_buffer_size
                for _id, _controller in self.__controllers.items()}

    @property
    def controllers(self):
        return self.__controllers.copy()

    @property
    def num_of_controllers(self):
        return len(self.__controllers)


if __name__ == '__main__':
    cp = ControlPlane({
        "NUM_CONTROLLER": 3,
        "SRV_PROC": "CONST",
        "SRV_RATE": 3
    })
    print(cp.controllers)
    print(cp.get_controllers_by_ids([2, 1]))

    dp = DataPlane({
        "NUM_SWITCH": 3,
        "ARR_PROC": "CONST",
        "ARR_RATE": 3,
        "SRV_PROC": "CONST",
        "SRV_RATE": 4,
        "WIN_SIZE": 5
    })
    print(dp.switches)
