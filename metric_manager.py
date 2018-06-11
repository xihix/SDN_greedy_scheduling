import numpy as np
from random import shuffle
from util import locate_folders
from copy import deepcopy


class MetricManager:

    def __init__(self, _V, _win_size, _acc, _metrics, _round):
        self.__params = (_V, _win_size)
        self.__acc = _acc
        self.__round = _round
        self.__metrics = {
            # "fin_reqs": [],
            # "delays": [],
            "delays": {},
        }
        self.__time_avg_metrics = {}

        for _metric in _metrics:
            self.create_metric_save_method(_metric)

    def save_fin_reqs(self, _fin_reqs):
        for _req in _fin_reqs:
            _gen_time = _req.gen_time
            _dur = _req.duration

            if _gen_time not in self.__metrics["delays"]:
                self.__metrics["delays"][_gen_time] = []

            self.__metrics["delays"][_gen_time].append(_dur)

    def remove_misest_reqs(self, _recall_lst):

        for _t, _num in enumerate(_recall_lst):

            if _t in self.__metrics["delays"]:

                shuffle(self.__metrics["delays"][_t])
                self.__metrics["delays"][_t] = self.__metrics["delays"][_t][_num:]

    def dump(self, _to_path="results"):

        _delay_lsts = list(self.__metrics["delays"].values())
        self.__metrics["delays"] = sum(_delay_lsts, [])

        locate_folders(
            ["{}/{}".format(_to_path, self.__acc)] +
            ["{}/{}/{}".format(_to_path, self.__acc, _metric)
             for _metric in self.metrics]
        )

        _V, _w_size = self.__params

        for _metric in self.metrics:
            np.save("{}/{}/{}/{}_{}_r_{}.npy".format(
                _to_path, self.__acc, _metric, _V, _w_size, self.__round),
                self.__metrics[_metric]
            )

        for _metric in self.__time_avg_metrics:
            np.save("{}/{}/{}/{}_{}_tavg_r_{}.npy".format(
                _to_path, self.__acc, _metric, _V, _w_size, self.__round),
                self.__time_avg_metrics[_metric]
            )

    @property
    def metrics(self):
        return list(self.__metrics.keys())

    @property
    def delay_lst(self):
        return deepcopy(self.__metrics["delays"])

    def create_metric_save_method(self, _metric):

        self.__metrics[_metric] = []
        self.__time_avg_metrics[_metric] = []

        def _save_method(_new_stats):
            self.__metrics[_metric].append(_new_stats)
            self.__time_avg_metrics[_metric].append(
                np.average(self.__metrics[_metric] + [_new_stats])
            )

        def _get_method():
            return self.__metrics[_metric].copy()

        def _get_avg_method():
            return self.__time_avg_metrics[_metric].copy()

        setattr(self, "save_{}".format(_metric), _save_method)
        setattr(self, "get_{}".format(_metric), _get_method)
        setattr(self, "get_time_avg_{}".format(_metric), _get_avg_method)

