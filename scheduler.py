from id_manager import id_manager
from switch import Switch


class Scheduler:

    def __init__(self, _V, _cp, _dp):
        self.__id = id_manager.get_next_id("Scheduler")
        self.__V = _V
        self.__cp = _cp
        self.__dp = _dp
        self.__num_scheduled_req = 0

    def __collect_stats(self):
        return [self.__cp.collect_stats(), self.__dp.collect_stats()]

    def present_stats(self):
        _cp_stats, _dp_stats = self.__collect_stats()
        _arr_buffer_sizes, _proc_buffer_sizes_dp, _ = _dp_stats
        _proc_buffer_sizes_cp = _cp_stats

        print("Updated queue backlogs:")
        print("Q_p:", _arr_buffer_sizes)
        print("Q_s:", _proc_buffer_sizes_dp)
        print("Q_c:", _proc_buffer_sizes_cp)

        print(self.__collect_stats())

    def make_decisions(self, _weights):
        # the data structure of scheduling decisions
        # by default, each switch forwards 0 requests
        # to its local processing queue

        _unit_assoc_costs = self.__dp.unit_assoc_costs

        # print("Collecting unit costs:", _unit_assoc_costs)

        _decisions = {
            _sid: {"ADDR": Switch.LOCAL_ADDR, "NUM": 0}
            for _sid, _s in self.__dp.switches.items()
        }

        _alpha, _gamma = _weights
        _cp_stats, _dp_stats = self.__collect_stats()
        _arr_buffer_sizes, _proc_buffer_sizes_dp, _ = _dp_stats
        _proc_buffer_sizes_cp = _cp_stats

        # print("Collecting queue backlogs:")
        # print("Q_p:", _arr_buffer_sizes)
        # _switch = list(self.__dp.switches.values())[0]
        # print(_switch.id, _switch.arr_buffer_sizes, _switch.pred_win_size)
        # print("Q_s:", _proc_buffer_sizes_dp)
        # print("Q_c:", _proc_buffer_sizes_cp)

        for _sid, _s in self.__dp.switches.items():

            _l_i = \
                sum(_arr_buffer_sizes[_sid]) - \
                _alpha * _proc_buffer_sizes_dp[_sid] - \
                self.__V * _gamma * _unit_assoc_costs[_sid][Switch.LOCAL_ADDR]

            _willingness_lst = [
                (
                    _cid,
                    _alpha * _proc_buffer_sizes_dp[_sid] - _proc_buffer_sizes_cp[_cid] +
                    self.__V * _gamma * _unit_assoc_costs[_sid][Switch.LOCAL_ADDR] -
                    self.__V * _unit_assoc_costs[_sid][_cid]
                )
                for _cid in _s.assoc_elements if _cid != Switch.LOCAL_ADDR
            ]

            # find the j^{*} among all available controllers
            _opt_cid, _opt_w_ij = max(_willingness_lst, key=lambda e: e[1])

            if _opt_w_ij < 0:

                if _l_i > 0:

                    # _local_buf_size = _s.proc_buffer_size
                    # _srv_rate = _s.next_srv_rate
                    # _diff = \
                    #     _srv_rate - (_local_buf_size + _arr_buffer_sizes[_sid][0])
                    # if _diff > 0:
                    #     _decisions[_sid]["NUM"] = \
                    #         min(sum(_arr_buffer_sizes[_sid]), _arr_buffer_sizes[_sid][0] + _diff)
                    #
                    # else:
                    #     _decisions[_sid]["NUM"] = _arr_buffer_sizes[_sid][0]

                    _decisions[_sid]["NUM"] = sum(_arr_buffer_sizes[_sid])

                else:
                    _decisions[_sid]["NUM"] = _arr_buffer_sizes[_sid][0]

                _decisions[_sid]["ADDR"] = Switch.LOCAL_ADDR

            else:

                if _opt_w_ij + _l_i > 0:

                    # _c = self.__cp.controllers[_opt_cid]
                    # _proc_buf_size = _c.proc_buffer_size
                    # _srv_rate = _c.next_srv_rate
                    #
                    # _diff = \
                    #     _srv_rate - (_proc_buf_size + _arr_buffer_sizes[_sid][0])
                    #
                    # if _diff > 0:
                    #     _decisions[_sid]["NUM"] = \
                    #         min(sum(_arr_buffer_sizes[_sid]), _arr_buffer_sizes[_sid][0] + _diff)
                    # else:
                    #     _decisions[_sid]["NUM"] = _arr_buffer_sizes[_sid][0]
                    _decisions[_sid]["NUM"] = sum(_arr_buffer_sizes[_sid])

                else:
                    _decisions[_sid]["NUM"] = _arr_buffer_sizes[_sid][0]

                _decisions[_sid]["ADDR"] = _opt_cid

            self.__num_scheduled_req += _decisions[_sid]["NUM"]

        return _decisions

    @property
    def num_scheduled_req(self):
        return self.__num_scheduled_req
