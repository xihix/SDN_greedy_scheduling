import yaml
import copy
import os


class Config:

    def __init__(self, src_file):

        _params = None

        if type(src_file) is str:
            with open("{}/{}".format(os.getcwd(), src_file), "r") as f:
                _params = yaml.load(f)
        elif hasattr(src_file, "read"):
            _params = yaml.load(src_file)

        print("Loading simulation settings...")

        self.cp_config = _params["CONTROL_PLANE"]
        self.dp_config = _params["DATA_PLANE"]
        self.Vs = _params["Vs"]
        self.repeat_times = _params["REPEAT"]
        self.max_time = _params["MAX_SIM_LEN"]
        self.q_policy = _params["Q_POLICY"]
        self.associations = _params["ASSOC"]
        self.assoc_costs = _params["ASSOC_COST"]
        self.win_sizes = self.dp_config["WIN_SIZES"]
        self.comp_cost = self.dp_config["COMP_COST"]
        self.alpha = _params["ALPHA"]
        self.gamma = _params["GAMMA"]

        # print("Loading completed. Configs are as follows:")
        # print("Max sim. time:", self.max_time)
        # print("Policy:", self.q_policy)
        # print("Vs:", self.Vs)
        # print("Win. sizes:", self.dp_config["WIN_SIZES"])
        # print("Prediction accuracy:", self.dp_config["PRED_ACC"])
        # print("# of controllers:", self.cp_config["NUM_CONTROLLER"])
        # print("# of switches:", self.dp_config["NUM_SWITCH"])
        # print("Associations:", self.associations)
        # print("Weight of data plane queue backlog size:", self.alpha)
        # print("Weight of computational cost:", self.gamma)

    def copy(self):
        return copy.deepcopy(self)


if __name__ == '__main__':
    with open("conf/setting.yaml", "r") as f:
        config = Config(f)
        config2 = config.copy()

        print(config, config2)
