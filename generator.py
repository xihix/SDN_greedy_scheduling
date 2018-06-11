import random

PROCS = {
    # "CONST": (lambda rate: (lambda: rate))
    "CONST": (lambda rate, source: Generator("CONST", rate, source)),
    "EXP": (lambda rate, source: Generator("EXP", rate, source)),
    "TRACE": (lambda rate, source: Generator("TRACE", rate, source))
}


class Generator:
    def __init__(self, _proc_name, _rate, _src):
        self.__proc_name = _proc_name
        self.__src = None

        if _src is not None:
            with open(_src) as f:
                self.__src = [int(line.strip()) for line in f.readlines() if line != "\n"]

        self.__pre_t_point = 0
        self.__next_time = 1
        self.__rate = float(_rate)
        assert self.__rate > 0

    @property
    def next(self):

        if self.__src is not None:

            if len(self.__src) == 0:
                return 0
            else:
                _num = self.__src[0]
                self.__src = self.__src[1:]
                return _num

        if self.__proc_name == 'CONST':
            return int(self.__rate)

        else:
            count = 1
            cur_t_point = self.__pre_t_point

            if cur_t_point == 0:
                count = 0

            while True:
                interval = 0
                if self.__proc_name == 'EXP':
                    interval = random.expovariate(self.__rate)
                elif self.__proc_name == "TRACE":
                    interval = TraceGen.next()
                else:
                    raise Exception("No such generating policy!")

                cur_t_point += interval
                if cur_t_point >= self.__next_time:
                    break
                count += 1

            self.__pre_t_point = cur_t_point
            self.__next_time += 1
            return count


class TraceGen:

    __td = [
        0, 0.08514851485148515, 0.15247524752475247, 0.19603960396039605, 0.2297029702970297, 0.2514851485148515,
        0.26732673267326734, 0.28316831683168314, 0.2891089108910891, 0.297029702970297, 0.299009900990099,
        0.30297029702970296, 0.3069306930693069, 0.41386138613861384, 0.49504950495049505, 0.592079207920792,
        0.7346534653465346, 0.8138613861386138, 0.9603960396039604, 1.0
    ]
    __xs = [
        0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 250, 400, 450, 650, 1000, 1600, 8000, 25000
    ]

    @staticmethod
    def next():

        rand = random.random()

        for _i in range(1, len(TraceGen.__td)):

            if rand <= TraceGen.__td[_i]:
                return 0.7 * (TraceGen.__xs[_i] + TraceGen.__xs[_i - 1]) / 1e4
            else:
                continue

        raise Exception("It shouldn't reach here..")

if __name__ == '__main__':

    from config import Config

    config = Config("conf/setting.yaml")

    time_slot = int(config.max_time / 2)
    num_switch = config.dp_config["NUM_SWITCH"]
    rate = config.dp_config["ARR_RATE"]
    arr_proc = config.dp_config["ARR_PROC"]

    # generate predicted arrivals on switches
    for i in range(num_switch):
        with open("sources/ds-{}".format(i), "w+") as f:
            gen = PROCS[arr_proc](rate, None)
            f.writelines([str(gen.next) + "\n" for _ in range(time_slot)])
