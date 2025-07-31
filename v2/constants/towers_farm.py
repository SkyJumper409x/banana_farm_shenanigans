from constants.towers import Upgrade, Path, UpgradeTree, path_names
import constants.farm.upgrades as upgrades_const
import constants.towers as towers

class BananaFarmUpgrade(Upgrade):
    cash_per_bunch: int = 20
    bunches_per_round: int = 4
    cash_per_round: int = 80
    def __init__(self, tier, price, cash_per_bunch, bunches_per_round):
        Upgrade.__init__(self, tier, price)
        self.cash_per_bunch = cash_per_bunch
        self.bunches_per_round = bunches_per_round
        self.cash_per_round = cash_per_bunch * bunches_per_round
towers.BananaFarmUpgrade = BananaFarmUpgrade
def __get_farm_path_list(path_name):
    path_list = []
    for i in range(1, 6):
        path_list.append(BananaFarmUpgrade(i,upgrades_const.prices[path_name][i-1], upgrades_const.base_and_upgrade_cash_per_bunch[path_name][i], upgrades_const.base_and_upgrade_bunches_per_round[path_name][i]))
    return path_list
zero: int = 0
FARM_UPGRADE_TREE = UpgradeTree(
    base_upgrade=BananaFarmUpgrade(zero, upgrades_const.initial_farm_price, upgrades_const.cash_per_bunch_base, upgrades_const.bunches_per_round_base),
    top=Path(index=0,name=path_names[0],upgrades=__get_farm_path_list(path_names[0])),
    middle=Path(index=1,name=path_names[1],upgrades=__get_farm_path_list(path_names[1])),
    bottom=Path(index=2,name=path_names[2],upgrades=__get_farm_path_list(path_names[2]))
)