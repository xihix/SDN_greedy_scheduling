from util import locate_folders
from config import Config
from matplotlib import pyplot as plt
import os
import numpy as np


class Plotter:

    def __init__(self, _path, _dest, _config):

        if not os.path.exists(_path):
            raise Exception("Given path doesn't exist. [{}]".format(_path))

        self.__path = _path
        self.__dest = _dest
        self.__Vs = _config.Vs
        self.__acc = _config.dp_config["PRED_ACC"]
        self.__win_sizes = _config.win_sizes
        self.__post_fix = ".png"
        self.__repeat_times = _config.repeat_times

        locate_folders([_dest])

    def plot_total_cost_over_time(self):

        for _V in self.__Vs:
            for _w_size in self.__win_sizes:
                _total_costs = []

                for _round in range(self.__repeat_times):

                    _total_costs.append(
                        list(np.load(
                            "{}/total_costs/{}_{}_r_{}.npy".format(self.__path, _V, _w_size, _round)
                        ))
                    )

                _time_range = range(len(_total_costs[-1]))
                _avg_total_costs = list(map(lambda e: np.average(e), zip(*_total_costs)))

                plt.figure()
                plt.title("({}, {}): Total cost over time".format(_V, _w_size))
                plt.xlabel("Time slot")
                plt.ylabel("Total cost")
                plt.plot(_time_range, _avg_total_costs)
                plt.savefig(
                    "{}/total_cost_{}_{}{}".format(self.__dest, _V, _w_size, self.__post_fix)
                )

                plt.close()

    def plot_queue_backlogs_over_time(self):
        for _V in self.__Vs:
            for _w_size in self.__win_sizes:
                _total_qbsizes = []

                for _round in range(self.__repeat_times):

                    _total_qbsizes.append(
                        list(np.load(
                            "{}/queue_backlogs/{}_{}_r_{}.npy".format(self.__path, _V, _w_size, _round)
                        ))
                    )

                _time_range = range(len(_total_qbsizes[-1]))
                _avg_total_qbsize = list(map(lambda e: np.average(e), zip(*_total_qbsizes)))

                plt.figure()
                plt.title("({}, {}): Total queue backlog size over time".format(_V, _w_size))
                plt.xlabel("Time slot")
                plt.ylabel("Total queue backlog size")
                plt.plot(_time_range, _avg_total_qbsize)
                plt.savefig(
                    "{}/total_qbacklog_{}_{}{}".format(self.__dest, _V, _w_size, self.__post_fix)
                )

                plt.close()

    def plot_cost_avg_over_time(self):
        for _V in self.__Vs:
            for _w_size in self.__win_sizes:

                _total_costs = []

                for _round in range(self.__repeat_times):
                    _total_costs.append(
                        list(np.load(
                            "{}/total_costs/{}_{}_tavg_r_{}.npy".format(
                                self.__path, _V, _w_size, _round
                            )
                        ))
                    )

                _time_range = range(len(_total_costs[-1]))
                _avg_total_costs = list(map(lambda e: np.average(e), zip(*_total_costs)))

                plt.figure()
                plt.title("({}, {}): Time-average cost over time".format(_V, _w_size))
                plt.xlabel("Time slot")
                plt.ylabel("Time-average cost")
                plt.plot(_time_range, _avg_total_costs)
                plt.savefig(
                    "{}/avg_cost_{}_{}{}".format(self.__dest, _V, _w_size, self.__post_fix)
                )

                plt.close()

    def plot_backlog_avg_over_time(self):
        for _V in self.__Vs:
            for _w_size in self.__win_sizes:
                _qbacklogs = []

                for _round in range(self.__repeat_times):
                    _qbacklogs.append(
                        list(np.load(
                            "{}/queue_backlogs/{}_{}_tavg_r_{}.npy".format(
                                self.__path, _V, _w_size, _round
                            )
                        ))
                    )

                _time_range = range(len(_qbacklogs[-1]))
                _avg_qbsize = list(map(lambda e: np.average(e), zip(*_qbacklogs)))

                plt.figure()
                plt.title("({}, {}): Time-average queue backlog size over time".format(_V, _w_size))
                plt.xlabel("Time slot")
                plt.ylabel("Time-average queue backlog size")
                plt.plot(_time_range, _avg_qbsize)
                plt.savefig(
                    "{}/avg_qb_{}_{}{}".format(self.__dest, _V, _w_size, self.__post_fix)
                )

                plt.close()

    def plot_delay_dist(self):
        for _V in self.__Vs:
            print()

            for _w_size in self.__win_sizes:
                # _delays = {}
                _avgs = []

                for _round in range(self.__repeat_times):
                    _delays = {}

                    _durs, _counts = np.load("{}/delays/{}_{}_r_{}.npy".format(
                            self.__path, _V, _w_size, _round
                        )).tolist()

                    for _pair in zip(_durs, _counts):
                        _dur, _count = _pair

                        if _dur not in _delays:
                            _delays[_dur] = 0

                        _delays[_dur] += _count

                    # print("|>>", _V, _w_size, _delays)

                    _max_dur = max(_delays.keys())
                    _total_count = sum(_delays.values())

                    for _dur in range(_max_dur + 1):

                        if _dur not in _delays:
                            _delays[_dur] = 0

                    _avg = sum(
                        [_dur * _count for _dur, _count in _delays.items()]
                    ) / _total_count

                    _avgs.append(_avg)

                # print("[V={}, win_size={}] # of finished requests: {}".format(
                #     _V, _w_size, _total_count / self.__repeat_times)
                # )
                print("[V={}, win_size={}] Average delays: {}".format(
                    _V, _w_size, np.average(_avgs))
                )

                # plt.figure()
                # plt.title("({}, {}): Delay distribution ({})".format(_V, _w_size, np.average(_avg)))
                # plt.xlabel("Delay")
                # plt.ylabel("# of requests")
                #
                # _rng = range(min(_delays.keys()), max(_delays.keys()) + 1)
                #
                # plt.bar(list(_rng), sorted(_delays.values()))
                # plt.savefig(
                #     "{}/delay_{}_{}{}".format(self.__dest, _V, _w_size, self.__post_fix)
                # )

                plt.close()

    # plot the curve of V vs cost for each window size
    def plot_V_vs_cost(self):
        for _w_size in self.__win_sizes:
            _costs = []

            for _V in self.__Vs:
                _total_costs = []

                for _round in range(self.__repeat_times):
                    _total_costs.append(
                        list(np.load(
                            "{}/total_costs/{}_{}_tavg_r_{}.npy".format(
                                self.__path, _V, _w_size, _round
                            )
                        ))[-1]
                    )

                _costs.append(np.average(_total_costs))

            plt.figure()
            plt.title("V vs. total cost (win. size {})".format(_w_size))
            plt.xlabel("V")
            plt.ylabel("Total cost")
            plt.plot(self.__Vs, _costs)
            plt.savefig("{}/V_vs_cost_win_{}{}".format(self.__dest, _w_size, self.__post_fix))

            plt.close()

    def plot_V_vs_qbsize(self):
        for _w_size in self.__win_sizes:
            _costs = []

            for _V in self.__Vs:
                _total_costs = []

                for _round in range(self.__repeat_times):
                    _total_costs.append(
                        list(np.load(
                            "{}/queue_backlogs/{}_{}_tavg_r_{}.npy".format(
                                self.__path, _V, _w_size, _round
                            )
                        ))[-1]
                    )

                _costs.append(np.average(_total_costs))

            plt.figure()
            plt.title("V vs. total queue backlog size (win. size {})".format(_w_size))
            plt.xlabel("V")
            plt.ylabel("Total queue backlog size")
            plt.plot(self.__Vs, _costs)
            plt.savefig("{}/V_vs_qbsize_win_{}{}".format(self.__dest, _w_size, self.__post_fix))

            plt.close()

    # plot the curve of wsize vs delay for each V
    def plot_wsize_vs_delay(self):

        for _V in self.__Vs:
            _avg_delays = []
            print()

            for _w_size in self.__win_sizes:
                _all_delays = []

                for _round in range(self.__repeat_times):

                    _delays = np.load("{}/delays/{}_{}_r_{}.npy".format(
                        self.__path, _V, _w_size, _round
                    )).tolist()

                    _all_delays.extend(_delays)

                _avg = np.average(_all_delays)
                _avg_delays.append(_avg)

                print("[V={}, win_size={}] # of finished requests: {}".format(
                    _V, _w_size, len(_all_delays) / self.__repeat_times)
                )
                print("[V={}, win_size={}] Average delays: {}".format(
                    _V, _w_size, _avg)
                )

            plt.figure()
            plt.title("Win. size vs. avg. delay (V {})".format(_V))
            plt.xlabel("Win. size")
            plt.ylabel("Response Time")
            plt.plot(self.__win_sizes, _avg_delays)
            plt.savefig("{}/wsize_vs_delay_V_{}{}".format(self.__dest, _V, self.__post_fix))

            plt.close()

if __name__ == '__main__':
    config = Config("conf/setting.yaml")
    plotter = Plotter("results", "figures", config)

    # plotter.plot_total_cost_over_time()
    # plotter.plot_cost_avg_over_time()
    # plotter.plot_queue_backlogs_over_time()
    # plotter.plot_backlog_avg_over_time()
    # plotter.plot_delay_dist()
    # plotter.plot_V_vs_cost()
    plotter.plot_wsize_vs_delay()
    # plotter.plot_V_vs_qbsize()
