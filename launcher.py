from config import Config
from environment import Environment as Env
from util import Timer, create_err_gen
from buffer import Buffer
from generator import PROCS


class Launcher:

    def __init__(self, _config_path):
        self.__config = Config(_config_path)
        self.__envs = {}
        self.__timer = Timer()
        self.__repeat_times = self.__config.repeat_times
        Buffer.set_policy(self.__config.q_policy)

        for _V in self.__config.Vs:
            for _win_size in self.__config.win_sizes:
                _config = self.__config.copy()
                setattr(_config, "win_size", _win_size)
                self.__envs[(_V, _win_size)] = Env(_V, _config, self.__repeat_times)
                delattr(_config, "win_size")

    def prepare_data(self):
        _time_slot = int(self.__config.max_time / 2)
        _acc = self.__config.dp_config["PRED_ACC"]
        _num_switch = self.__config.dp_config["NUM_SWITCH"]

        # generate respective errors on the above arrivals
        for i in range(_num_switch):
            err_gen = create_err_gen("normal", _acc, "sources/err-{}".format(i), 'w')

            for _ in range(_time_slot):
                next(err_gen())

    def run(self):

        _acc = self.__config.dp_config["PRED_ACC"]
        if _acc in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]:
            self.prepare_data()
            print("*" * 20)
        else:
            pass

        with self.__timer:
            for _key, _env in self.__envs.items():
                _V, _win_size = _key

                print(
                    "Running simulation for V={} w/ win. size ({})".format(
                        _V, _win_size
                    )
                )

                _env.start()

        for _env in self.__envs.values():
            _env.join()

        print("Elapsed time in total: {} sec.".format(self.__timer.duration))
        print("Simulation ends.")


if __name__ == '__main__':
    launcher = Launcher("conf/setting_ft.yaml")
    launcher.run()
    # input()
