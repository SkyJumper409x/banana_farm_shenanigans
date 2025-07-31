from constants.towers import Tower, TowerPath, TowerCrosspath
import constants.tower_types as tower_types
import constants.settings as settings
from constants.towers_farm import FARM_UPGRADE_TREE

# cash per bunch multipliers
valuable_bananas_multi = 1.25
if settings.mk[1]:
    valuable_bananas_multi = 1.3
banana_central_multi = 1.25
geraldo_multi = 1.2
village_multi = 1.2 # stacks additively with valuable bananas, multiplicatively with geraldo

FARM_DEFAULT_CROSSPATH = TowerCrosspath(focused_path=TowerPath(path=FARM_UPGRADE_TREE.top), secondary_path=TowerPath(path=FARM_UPGRADE_TREE.middle), upgrade_tree=FARM_UPGRADE_TREE)
# banana farm data structure
class BananaFarm(Tower):
    is_first_farm: bool
    # index: int # for sims (was replaced by string_index)
    string_index: str # for sims
    # upgrades: TowerCrosspath
    def __init__(self, is_first_farm: bool = False, string_index: str = "-1", upgrades: TowerCrosspath = FARM_DEFAULT_CROSSPATH.deep_copy()):
        # Tower.__init__(self, "Banana Farm", tower_types.SUPPORT, upgrades)
        super().__init__(name="Banana Farm", upgrades=upgrades, type=tower_types.SUPPORT)
        self.is_first_farm = is_first_farm
        self.string_index = string_index
        # self.upgrades = upgrades
