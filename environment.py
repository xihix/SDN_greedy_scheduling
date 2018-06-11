from planes import DataPlane, ControlPlane
from scheduler import Scheduler
from metric_manager import MetricManager
from id_manager import id_manager
from util import Timer
from generator import PROCS
from multiprocessing import Process


class Environment(Process):

    def __init__(self, _V, _config, _repeat=1):
        super(Environment, self).__init__()
        self.__id = _V
        self.__config = _config
        self.__win_size = _config.win_size
        self.__repeat_times = _repeat
        _config.dp_config["WIN_SIZE"] = self.__win_size

        self.__alpha = _config.alpha
        self.__gamma = _config.gamma
        self.__cp_config = _config.cp_config
        self.__dp_config = _config.dp_config
        self.__acc = self.__dp_config["PRED_ACC"]
        self.__max_time = _config.max_time
        self.__metrics = ["comm_costs", "comp_costs", "total_costs", "queue_backlogs"]
        self.__assoc = _config.associations
        self.__assoc_costs = _config.assoc_costs

        _weights = (_config.alpha, _config.gamma)

        self.__cp = None
        self.__dp = None
        self.__scheduler = None
        self.__mm = None

    def run(self):

        for _round in range(self.__repeat_times):

            print("Simulation repeat for {} time.".format(_round + 1))
            self.__initialize_all(_round)

            _switches = self.__dp.switches
            _controllers = self.__cp.controllers
            _timer = Timer()

            with _timer:

                _total_num_misest = 0
                _recall_lst = []

                for _cur_time in range(self.__max_time):

                    if (_cur_time + 1) % 1000 == 0:
                        print("[pid:{}]@time-slot: {}".format(self.pid, _cur_time))

                    _weights = (self.__alpha, self.__gamma)
                    # print("@time-{}".format(_cur_time))
                    # print("Making decision..")
                    _decisions = self.__scheduler.make_decisions(_weights)
                    # print("End of making decision.")
                    # print("Decision: ", _decisions)
                    # print()

                    # self.__scheduler.present_stats()

                    # proceed to serve the requests in the processing buffers
                    _fin_reqs = []

                    for _switch in _switches.values():
                        _fin_reqs.extend(_switch.serve(_cur_time))

                    for _controller in _controllers.values():
                        _fin_reqs.extend(_controller.serve(_cur_time))
                    # end of request processing

                    # forward requests according to decisions
                    for _sid, _dec in _decisions.items():
                        _switches[_sid].forward(_dec["ADDR"], _dec["NUM"])

                    # print([(_req.id, _req.duration) for _req in _fin_reqs])
                    # print()

                    # save the metrics of interest into metric managers
                    self.__mm.save_fin_reqs(_fin_reqs)
                    _arr_buffer_sizes_dp, _proc_buffer_sizes_dp, _incurred_costs = self.__dp.collect_stats()
                    _proc_buffer_sizes_cp = self.__cp.collect_stats()

                    _total_arr_buffer_size = sum(map(lambda e: sum(e), _arr_buffer_sizes_dp.values()))
                    _total_comp_cost = sum(map(lambda e: e[0], _incurred_costs.values()))
                    _total_comm_cost = sum(map(lambda e: e[1], _incurred_costs.values()))
                    _total_cost = _total_comm_cost + _total_comp_cost * self.__gamma

                    # print("Controllers' processing buffer sizes:\t", _proc_buffer_sizes_cp)
                    # print("Switches' processing buffer sizes:\t\t", _proc_buffer_sizes_dp)
                    # print("incurred cost w.r.t. each switch:\t\t", _incurred_costs)

                    self.__mm.save_queue_backlogs(
                        # _total_arr_buffer_size +
                        self.__alpha *
                        sum(_proc_buffer_sizes_dp.values()) +
                        sum(_proc_buffer_sizes_cp.values())
                    )
                    self.__mm.save_comp_costs(_total_comp_cost)
                    self.__mm.save_comm_costs(_total_comm_cost)
                    self.__mm.save_total_costs(_total_cost)

                    _num_misest = 0  # number of under-est. requests
                    _num_to_recall = 0

                    for _switch in _switches.values():
                        _err_est = _switch.admit_reqs()
                        _num_misest += abs(_err_est)
                        if _err_est > 0:
                            _num_to_recall += _err_est

                    _recall_lst.append(_num_to_recall)
                    _total_num_misest += _num_misest

                self.__mm.remove_misest_reqs(_recall_lst)
                print("{}-{} # of requests to recall:".format(self.__id, self.__win_size),
                      sum(_recall_lst) / self.__dp.num_of_switches)
                print("{}-{} # of mis-estimated requests:".format(self.__id, self.__win_size),
                      _total_num_misest / self.__dp.num_of_switches)

                # self.__mm.dump()
                self.__mm.dump(_to_path="results/{}".format(self.__dp_config["ARR_PROC"]))

            print("Time elapsed: {}".format(_timer.duration))

    def __initialize_all(self, _round):
        id_manager.reset_all()
        self.__cp = ControlPlane(self.__cp_config)
        self.__dp = DataPlane(self.__dp_config)
        self.__scheduler = Scheduler(self.__id, self.__cp, self.__dp)
        self.__mm = MetricManager(
            self.__id,
            self.__win_size,
            self.__acc,
            self.__metrics,
            _round
        )
        _switches = self.__dp.switches

        assert len(_switches) == len(self.__assoc)

        for _id, _controller_id_set in enumerate(self.__assoc):
            _assoc_controllers = self.__cp.get_controllers_by_ids(_controller_id_set)
            _rates = self.__assoc_costs["RATES"][_id]
            _assoc_costs = {
                _cid: PROCS[self.__assoc_costs["PROC"]](_rates[_idx], None)
                for _idx, _cid in enumerate(_controller_id_set)}
            _switches[_id].add_assoc_controllers(_assoc_controllers, _assoc_costs)
