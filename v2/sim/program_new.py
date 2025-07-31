from math import floor, ceil

from constants.farm import BananaFarm, upgrades, valuable_bananas_multi
from constants.farm.utils import calculate_price, calculate_cash_per_round, get_overall_tier, get_remaining_crosspath_options, many_farms_to_string
from constants.sim import Difficulty, DIFFICULTIES
from constants.towers import path_names, TowerCrosspath, TowerPath
from constants.towers_farm import FARM_UPGRADE_TREE
from sim.actions import Action, ActionList
import sim.actions as acts

target_values_medium_boss = [
    {"cash":5_975+9_100+1_795,"sac":False,"rounds_remaining":100}, # 0/4/2 moab assassin & 2/0/4 sticky bomb & 3/0/2 glaive
    {"cash":28_000+3_000,"sac":False,"rounds_remaining":80}, # +0/1/0 moab eliminator & +1/0/0 moar glaives
    {"cash":24_580+40_000,"sac":False,"rounds_remaining":60}, # 2/0/5 tack zone & +0/0/1 master bomber
    {"cash":50_530,"sac":False,"rounds_remaining":40}, # 5/0/2 Inferno Ring
    {"cash":19_285,"sac":False,"rounds_remaining":30}, # 2/5/0 Super Maelstrom
    {"cash":100_000,"sac":True,"rounds_remaining":20} # paragon
]
def sim_strat_decide_default(cash, farms, available_actions: ActionList, difficulty: Difficulty):
    want_actions = [acts.ACT_BUY_FARM] # TODO
    farms
    for action in want_actions:
        if available_actions.contains(action):
            return available_actions.get(action)
    return acts.ACT_CONTINUE
def sim_farming(strat_decide_function=sim_strat_decide_default, limit_greed=False, use_bloon_cash: bool=True, diff: Difficulty = DIFFICULTIES["Medium_Boss"]):
    curr_cash = diff.starting_cash
    curr_round = diff.start_round
    
