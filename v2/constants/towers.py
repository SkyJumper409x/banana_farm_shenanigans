from typing import NamedTuple
# import uuid

# general "constants" for path accessing
# strings are preferred for accessing (together with dicts)
# but numerical values are still present if needed
top = 0
middle = 1
bottom = 2
path_names = ["","",""]
path_names[top] = "top"
path_names[middle] = "middle"
path_names[bottom] = "bottom"

# the classes

# Paths & Upgrades
# Upgrades are used to hold constant states
class Upgrade:
    tier: int = 0
    price: int = 0
    def __init__(self, tier, price):
        self.tier = tier
        self.price = price

BananaFarmUpgrade = "stub" # class, defined in towers_farm.py
# Paths are used to hold constant Data and stored in UpgradeTrees
class Path(NamedTuple):
    index: int = -1
    name: str = ""
    upgrades: list = []
    # def __init__(self, index: int, name: str, upgrades: list):
    #     self.index = index
    #     self.name = name
    #     self.upgrades = upgrades

    def get_upgrade(self, tier: int):
        return self.upgrades[tier-1]
# TODO: this is not necessary
    def __setattr__(self, name, value):
        if name == "index":
            assert 0 <= value < 3
            if self.name != "":
                assert self.name == path_names[value]
        if name == "name":
            assert value in path_names
            if self.index != -1:
                assert value == path_names[self.index]
        if name == "upgrades":
            assert len(value) == 5
            for upgrade in value:
                assert upgrade is Upgrade
        NamedTuple.__setattr__(self, name, value)

# UpgradeTrees are used to store the constant information about each tower (class)'s upgrade paths
class UpgradeTree(NamedTuple):
    base_upgrade: Upgrade
    top: Path
    middle: Path
    bottom: Path
    def get(self, key):
        if type(key) is int:
            key = path_names[key]
        if type(key) is not str:
            return
        # print("key: " + key)
        if key == "top":
            return self.top
        elif key == "middle":
            return self.middle
        elif key == "bottom":
            return self.bottom
    def __getitem__(self, key):
        return self.get(key)

UPGRADE_TREE_NULL = UpgradeTree(0,0,0,0)

# FARM_UPGRADE_TREE = UPGRADE_TREE_NULL # defined in towers_farm.py

# TowerPath and TowerCrosspath are used for keeping track of the upgrades a tower has (e.g. not constant)
class TowerPath(object):
    path: Path
    tier: int = 0
    # uid: str = ""
    def __init__(self, path:Path=Path(), tier:int=0):
        # self.uid=str(uuid.uuid4())
        self.path=path
        self.tier=tier
    # allow accessing self.path.[...] directly, for convenience
    def __getattr__(self, name):
        if name == "index" or name == "name" or name == "upgrades":
            return self.path.__getattribute__(name)
    def copy(self):
        return TowerPath(path=self.path, tier=self.tier)

class TowerCrosspath(object):
    focused_path: TowerPath
    secondary_path: TowerPath
    unused_path_name: str
    UPGRADE_TREE: UpgradeTree
    path_dict: dict
    getattr_log_thing=0
    # TODO: fix everything
    def __init__(self, focused_path: TowerPath, secondary_path: TowerPath, upgrade_tree: UpgradeTree):
        if focused_path == -1:
            self.focused_path = TowerPath(path=upgrade_tree.top)
            self.secondary_path = TowerPath(path=upgrade_tree.middle)
        else:
            self.focused_path = focused_path
            self.secondary_path = secondary_path
        self.path_dict = {}
        # print("self.focused_path.path: " + str(self.focused_path.path))
        # print("self.secondary_path.path: " + str(self.secondary_path.path))
        self.path_dict[self.focused_path.path.name] = self.focused_path
        self.path_dict[self.secondary_path.path.name] = self.secondary_path
        self._check_path_order()
        # print("self.focused_path.path.index: " + str(self.focused_path.path.index))
        # print("self.secondary_path.path.index: " + str(self.secondary_path.path.index))
        self.path_dict[self.unused_path_name] = TowerPath(upgrade_tree[self.unused_path_name],0)
        self.UPGRADE_TREE = upgrade_tree
    # allow accessing path_dict with attributes (e.g. crosspath.top)
    def __getattr__(self,name):
        if name in path_names:
            return self.path_dict[name]
        return
    def upgrade(self, path_name: str, amount: int):
        # print("upgrade(" + path_name + ", " + str(amount) + ")")
        if path_name == self.unused_path_name:
            print("tried to upgrade invalid path")
        if amount <= 0:
            print("invalid upgrade amount (too small): " + str(amount))
        if (amount + self.path_dict[path_name].tier) > 5:
            print("invalid upgrade amount (too large): " + str(amount) + " (path tier: " + str(self.path_dict[path_name].tier) + ")")
        self.path_dict[path_name].tier += amount
        self._check_path_order()
    def __getitem__(self, item):
        if type(item) is int:
            item = path_names[item]
        return self.path_dict[item]
    def _checkUnused(self):
        # print("self.secondary_path.path.index: " + str(self.secondary_path.path.index))
        if not (0 <= (3 - (self.focused_path.path.index + self.secondary_path.path.index)) < 3):
            print("3 - (self.focused_path.path.index + self.secondary_path.path.index): " + str(3 - (self.focused_path.path.index + self.secondary_path.path.index)))
        self.unused_path_name = path_names[3 - (self.focused_path.path.index + self.secondary_path.path.index)]
    def _check_path_order(self):
        self._checkUnused()
        if self.secondary_path.tier >= 3 and self.secondary_path.tier > self.focused_path.tier:
            tmp_path = self.focused_path
            self.focused_path = self.secondary_path
            self.secondary_path = tmp_path
    # method for deep copy of crosspath
    def deep_copy(self):
        # print("self.UPGRADE_TREE: " + str(self.UPGRADE_TREE))
        return TowerCrosspath(focused_path=TowerPath(path=self.UPGRADE_TREE[self.focused_path.index],tier=self.focused_path.tier),secondary_path=TowerPath(path=self.secondary_path.path,tier=self.secondary_path.tier),upgrade_tree=self.UPGRADE_TREE)
    # def __setattr__(self, name, value):
    #     print("setattr(self, " + str(name) + ", " + str(value) + ")")
    #     object.__setattr__(self, name, value)
class Tower(object):
    name: str
    TYPE: str = "meow"
    UPGRADE_TREE: UpgradeTree
    # UPGRADE_TREE: UpgradeTree
    upgrades: TowerCrosspath
    def __init__(self, name: str, type: str, upgrades:TowerCrosspath, upgrade_tree:UpgradeTree=UPGRADE_TREE_NULL):
        self.name = name
        self.TYPE = type
        self.UPGRADE_TREE = upgrade_tree
        self.upgrades = upgrades

    def set_tower_type(self, type):
        if self.TYPE != "meow":
            return
        self.TYPE = type
    def set_upgrade_tree(self, upgrade_tree: UpgradeTree):
        if self.get_upgrade_tree() != UPGRADE_TREE_NULL:
            return
        self.UPGRADE_TREE = upgrade_tree
    def get_upgrade_tree(self):
        return self.UPGRADE_TREE
