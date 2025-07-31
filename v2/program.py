from math import floor, ceil

from constants.farm import BananaFarm, upgrades, valuable_bananas_multi
from constants.farm.utils import calculate_price, calculate_cash_per_round, get_overall_tier, get_remaining_crosspath_options, many_farms_to_string
from constants.sim import Difficulty, DIFFICULTIES
from constants.towers import path_names, TowerCrosspath, TowerPath
from constants.towers_farm import FARM_UPGRADE_TREE
import tests
import plotter
thingamajig = -8
def get_point_from_farm(farm: BananaFarm):
        price = calculate_price(farm)
        cash_per_round = calculate_cash_per_round(farm)
        point = {}
        point["x"] = price
        point["y"] = cash_per_round
        global thingamajig
        if thingamajig < 4:
            if 0 <= thingamajig:
                print(point)
            thingamajig += 1
        return point

def get_points_from_line(line: str):
    points = []
    point_strs = line.split(";")
    for point_str in point_strs:
        coord_strs = point_str.split(",")
        xvalue = int(coord_strs[0])
        yvalue = int(coord_strs[1])
        points.append({ "x": xvalue, "y": yvalue })
    return points

def plot_cost_vs_gain():
    print("==plotting cost vs gain==")
    # cost_vs_gain_path = r"growth_sim_cache/cost_vs_gain.txt"
    # top path plot
    points_to_plot = [[],[]]
    # bottom path plot
    more_points_to_plot = [[],[]]
    # if os.path.isfile(cost_vs_gain_path):
    #     file_object = open(cost_vs_gain_path, "r")
    #     lines = file_object.readlines()
    #     points_to_plot[0] = get_points_from_line(lines[0])
    #     points_to_plot[1] = get_points_from_line(lines[1])
    #     more_points_to_plot[0] = get_points_from_line(lines[2])
    #     more_points_to_plot[1] = get_points_from_line(lines[3])
    # else:
    some_point={ "x": upgrades.initial_farm_price, "y": upgrades.cash_per_bunch_base*upgrades.bunches_per_round_base }
    some_other_point={ "x": upgrades.initial_farm_price, "y": upgrades.cash_per_bunch_base*valuable_bananas_multi*upgrades.bunches_per_round_base }
    points_to_plot[0].append(some_point)
    points_to_plot[1].append(some_other_point)
    more_points_to_plot[0].append(some_point)
    more_points_to_plot[1].append(some_other_point)
    for tier_middle in [0, 2]:
        for tier_focused in range(1,6):
            focused_top = TowerPath(path=FARM_UPGRADE_TREE.top,tier=tier_focused)
            focused_bottom = TowerPath(path=FARM_UPGRADE_TREE.bottom,tier=tier_focused)
            secondary_middle = [TowerPath(path=FARM_UPGRADE_TREE.middle,tier=tier_middle),TowerPath(path=FARM_UPGRADE_TREE.middle,tier=tier_middle)]
            farm = BananaFarm(upgrades=TowerCrosspath(focused_path=focused_top,secondary_path=secondary_middle[0],upgrade_tree=FARM_UPGRADE_TREE))
            points_to_plot[tier_middle//2].append(get_point_from_farm(farm))
            another_farm = BananaFarm(upgrades=TowerCrosspath(focused_path=focused_bottom,secondary_path=secondary_middle[1],upgrade_tree=FARM_UPGRADE_TREE))
            more_points_to_plot[tier_middle//2].append(get_point_from_farm(another_farm))

    plotter.draw_all(points_to_plot[0], "Top path focused (x/0/0)", ax_labels={ "xlabel": "Cost", "ylabel": "Cash/Round" }, title="Banana Farm Pathing", color="yellow")
    plotter.draw_all(points_to_plot[1], "Top path focused (x/2/0)", color="goldenrod")
    plotter.draw_all(more_points_to_plot[0], "Bottom path focused (0/0/x)", color="coral")
    plotter.draw_all(more_points_to_plot[1], "Bottom path focused (0/2/x)", color="orangered")

    plotter.show_plot()

def multiply_tower_price(price: int, multiplier: float = 1):
    meow = ((price * multiplier)/5.0)
    floormeow = floor(meow)
    return (floormeow if (meow-floormeow) < 0.5 else ceil(meow))*5

# the default strat places three 2/0/0 farms with upgrade order 0/0/0 -> 2/0/0 (e.g. it prefers getting 2/0/0 over placing the next farm),
# then goes for 5/2/0, in the order 2/0/0 -> 3/0/0 -> 3/2/0 -> 5/2/0
def sim_strat_decide_default(current_cash: float, current_farms: dict, difficulty: Difficulty):
    current_farms = current_farms.copy()
    current_cash = 0.0+current_cash
    result_actions = [""]
    next_result_action = ""

    lowest_free_farm_index = 0
    for farm_key in current_farms.keys():
        farm_index = current_farms[farm_key].string_index
        if farm_index == lowest_free_farm_index:
            lowest_free_farm_index = farm_index+1
    lowest_free_farm_key = "farm_" + str(lowest_free_farm_index)
    def upgrade(farm_to_upgrade: BananaFarm, path_to_upgrade_name: str = "meow", path_to_upgrade_index=-1, amount=1):
        if path_to_upgrade_name == "meow":
            if path_to_upgrade_index == -1:
                print("[WARN] sim_strat_decide_default(): no path_to_upgrade_* args were provided for upgrade()")
                return
            else:
                path_to_upgrade_name = path_names[path_to_upgrade_index]
        else:
            path_to_upgrade_index = path_names.index(path_to_upgrade_name)
        path_to_upgrade_current_tier = farm_to_upgrade.upgrades[path_to_upgrade_name].tier
        path_to_upgrade_target_tier = path_to_upgrade_current_tier+amount
        if path_to_upgrade_target_tier > 5:
            print("[WARN] sim_strat_decide_default(): invalid args were provided for upgrade(): path_to_upgrade_target_tier > 5")
            return
        next_upgrade_price = sum(upgrades.prices[path_to_upgrade_name][path_to_upgrade_current_tier:path_to_upgrade_target_tier])
        nonlocal current_cash
        if current_cash >= next_upgrade_price:
            # print("upgrade(" + str(farm_to_upgrade.string_index) + ", " + path_to_upgrade_name + ", " + str(path_to_upgrade_index) + ", " + str(amount) + ")")
            # print("current_cash >= next_upgrade_price: " + str(current_cash) + " >= " + str(next_upgrade_price))
            paths_to_not_upgrade_indices = get_remaining_crosspath_options(path_to_upgrade_index)
            # print("paths_to_not_upgrade_indices: " + str(paths_to_not_upgrade_indices))
            nonlocal next_result_action
            next_result_action = { 
                "action": "upgrade",
                "upgrade_index": farm_to_upgrade.string_index,
                "upgrade_delta": {
                    path_to_upgrade_name: amount,
                    path_names[paths_to_not_upgrade_indices[0]]: 0,
                    path_names[paths_to_not_upgrade_indices[1]]: 0
                }
            }
            # print("next_result_action: " + str(next_result_action))
            current_cash -= next_upgrade_price
            new_upgrades = farm_to_upgrade.upgrades.deep_copy()
            # print("new_upgrades before upgrading: " + str(new_upgrades.top.tier) + "/" + str(new_upgrades.middle.tier) + "/" + str(new_upgrades.bottom.tier))
            new_upgrades.upgrade(path_to_upgrade_name,amount)
            # print("new_upgrades after upgrading: " + str(new_upgrades.top.tier) + "/" + str(new_upgrades.middle.tier) + "/" + str(new_upgrades.bottom.tier))
            current_farms["farm_" + str(farm_to_upgrade.string_index)] = BananaFarm(upgrades=new_upgrades, is_first_farm=farm_to_upgrade.is_first_farm, string_index=farm_to_upgrade.string_index)
    def upgrade_top(farm_to_upgrade: BananaFarm, amount=1):
        upgrade(farm_to_upgrade, path_to_upgrade_name="top", amount=amount)
    def upgrade_middle(farm_to_upgrade: BananaFarm, amount=1):
        upgrade(farm_to_upgrade, path_to_upgrade_name="middle", amount=amount)
    def place_new_farm():
        nonlocal current_farms
        nonlocal current_cash
        nonlocal next_result_action
        nonlocal lowest_free_farm_index
        nonlocal lowest_free_farm_key
        next_farm_is_first_farm = (len(current_farms) == 0)
        next_farm_price = (multiply_tower_price(upgrades.initial_farm_price, difficulty.price_multiplier) - (upgrades.initial_farm_price_reduction if next_farm_is_first_farm else 0))
        if current_cash >= next_farm_price:
            next_result_action = { "action": "place_new_farm" }
            current_cash -= next_farm_price
            current_farms[lowest_free_farm_key] = BananaFarm(is_first_farm=next_farm_is_first_farm, string_index=lowest_free_farm_index)
    if len(current_farms.keys()) == 0:
        place_new_farm()
        result_actions.append(next_result_action)
        while len(result_actions) > 0 and result_actions[0] == '':
            result_actions = result_actions[1:]
        return { "updated_cash": current_cash, "updated_farms": current_farms, "actions": result_actions }
    while(True):
        lowest_overall_tier_so_far = 6
        lowest_overall_tier_subset = []
        lowest_middle_tier_so_far = 3
        lowest_middle_tier_subset = []
        highest_overall_tier_so_far = 0
        # for i in range(0, len(current_farms)):
        for farm_key in current_farms.keys():
            farm = current_farms[farm_key]
            farm_index = farm.string_index
            overall_tier = get_overall_tier(farm)
            if overall_tier < lowest_overall_tier_so_far:
                lowest_overall_tier_so_far = overall_tier
                lowest_overall_tier_subset = [farm]
            elif overall_tier == lowest_overall_tier_so_far:
                lowest_overall_tier_subset.append(farm)
            
            middle_tier = farm.upgrades.middle.tier
            if middle_tier < lowest_middle_tier_so_far:
                lowest_middle_tier_so_far = middle_tier
                lowest_middle_tier_subset = [farm]
            elif middle_tier == lowest_middle_tier_so_far:
                lowest_middle_tier_subset.append(farm)
            
            highest_overall_tier_so_far = max(highest_overall_tier_so_far, overall_tier)

        lowest_overall_tier = lowest_overall_tier_so_far
        lowest_middle_tier = lowest_middle_tier_so_far
        highest_overall_tier = highest_overall_tier_so_far

        def upgrade_lowest_tier_farm_top(amount=1):
            upgrade_top(lowest_overall_tier_subset[0], amount)
        def upgrade_lowest_tier_farm_middle(amount=1):
            upgrade_middle(lowest_middle_tier_subset[0], amount)
        def upgrade_lowest_tier_farm_middle_twice():
            upgrade_lowest_tier_farm_middle(amount=2)
        if lowest_overall_tier <= 2:
            if lowest_overall_tier < 2:
                upgrade_lowest_tier_farm_top()
            elif lowest_overall_tier == 2:
                if len(current_farms) < 3:
                    place_new_farm()
                elif len(current_farms) >= 3:
                    upgrade_lowest_tier_farm_top()
        # if the highest overall tier is 4, upgrading to 5 is allowed,
        # but if the highest overall tier is 4, upgrading to another 5 isn't allowed, thus (9 - highest_overall_tier).
        elif 2 < lowest_overall_tier < (9 - highest_overall_tier):
            if lowest_overall_tier == 3 and lowest_middle_tier < 2:
                if lowest_middle_tier == 0:
                    upgrade_lowest_tier_farm_middle_twice()
                elif lowest_middle_tier == 1:
                    print("[WARN] sim_strat_decide_default(): lowest_middle_tier == 1")
                    upgrade_lowest_tier_farm_middle()
            else:
                upgrade_lowest_tier_farm_top()
        else:
            place_new_farm()
        if next_result_action == "":
            break
        result_actions.append(next_result_action)
        next_result_action = ""
    # I'll do things a bit simpler but "unsafer" for now
    # return result_actions
    while len(result_actions) > 0 and result_actions[0] == '':
        result_actions = result_actions[1:]
    return { "updated_cash": current_cash, "updated_farms": current_farms, "actions": result_actions }
target_values_medium_boss = [
    {"cash":5_975+9_100+1_795,"sac":False,"rounds_remaining":100}, # 0/4/2 moab assassin & 2/0/4 sticky bomb & 3/0/2 glaive
    {"cash":28_000+3_000,"sac":False,"rounds_remaining":80}, # +0/1/0 moab eliminator & +1/0/0 moar glaives
    {"cash":24_580+40_000,"sac":False,"rounds_remaining":60}, # 2/0/5 tack zone & +0/0/1 master bomber
    {"cash":50_530,"sac":False,"rounds_remaining":40}, # 5/0/2 Inferno Ring
    {"cash":19_285,"sac":False,"rounds_remaining":30}, # 2/5/0 Super Maelstrom
    {"cash":100_000,"sac":True,"rounds_remaining":20} # paragon
]
def sim_farming(strat_decide_function=sim_strat_decide_default, limit_greed=False, use_bloon_cash: bool=True, difficulty: Difficulty = DIFFICULTIES["Medium_Boss"]):
    current_target_values_index = -1
    TARGET_CASH = None
    SAC_REMAINING_CASH = None # e.g. paragon cash injection
    TARGET_EXTRA_ROUNDS = None
    def update_target_values():
        nonlocal current_target_values_index, TARGET_CASH, SAC_REMAINING_CASH, TARGET_EXTRA_ROUNDS
        if (current_target_values_index+1) == len(target_values_medium_boss):
            return
        current_target_values_index += 1
        thingy = target_values_medium_boss[current_target_values_index]
        TARGET_CASH = thingy["cash"]
        SAC_REMAINING_CASH = thingy["sac"] # e.g. paragon cash injection
        TARGET_EXTRA_ROUNDS = thingy["rounds_remaining"]
    update_target_values()
    cash: float = difficulty.starting_cash
    cash_safe: float = 0 # for target stuff
    farms = {}
    print("==beginning sim_farming==")
    print("strat_decide_function: " + str(strat_decide_function) + ", difficulty: " + difficulty.name)
    print("starting cash: " + str(cash) + ", first round: " + str(difficulty.start_round) + ", last round: " + str(difficulty.end_round))
    print("--entering loop--")
    for current_round in difficulty.rounds:
        if current_round.index == 0:
            continue
        # current round index as a string, padded with spaces
        current_round_string = str(current_round.index)
        current_round_strlen = len(current_round_string)
        if current_round_strlen < 3:
            current_round_string = ((3-current_round_strlen) * " ") + current_round_string
        current_cr = 0
        for key in farms:
            farm = farms[key]
            current_cr += calculate_cash_per_round(farm)
        # "nah lass noch mehr greeden" - 700revlio 2025
        remaining_rounds = difficulty.end_round - current_round.index
        greed_limit_string = ""
        updated_data = None
        if limit_greed:
            if cash >= TARGET_CASH: # don't limit greed if target is reached
                greed_limit_string = " (saved)"
                cash -= TARGET_CASH
                cash_safe += TARGET_CASH
            elif cash_safe < TARGET_CASH:
                remaining_farming_rounds = (remaining_rounds - TARGET_EXTRA_ROUNDS - 1)
                cash_after_remaining_rounds = cash + (remaining_farming_rounds * current_cr)
                if (remaining_rounds > TARGET_EXTRA_ROUNDS) and cash_after_remaining_rounds >= TARGET_CASH:
                    greed_limit_string = " (greedlimit)"
            if remaining_rounds == TARGET_EXTRA_ROUNDS:
                if cash_safe < TARGET_CASH:
                    cash -= (TARGET_CASH - cash_safe)
                    cash_safe = TARGET_CASH
                    if cash < 0:
                        cash_safe += cash
                        cash = 0
                    print(f"cash: {cash}, cash_safe: {cash_safe}/{TARGET_CASH}")
                    cash_from_selling = 0
                    while len(farms) > 0 and cash_from_selling < (TARGET_CASH - cash_safe):
                        print("had to sell a farm")
                        farmf = farms.pop(str(len(farms)-1))
                        selling_value = .7 * calculate_price(farmf)
                        cash_from_selling += selling_value
                    cash += (cash_from_selling - (TARGET_CASH - cash_safe)) # remaining stuff goes into regular cash
                cash_safe = 0
                if SAC_REMAINING_CASH:
                    cash = 0
                update_target_values()
        if greed_limit_string != " (greedlimit)":
            updated_data = strat_decide_function(current_cash=cash, current_farms=farms, difficulty=difficulty)
            farms = updated_data["updated_farms"]
            cash = updated_data["updated_cash"]
            actions = updated_data["actions"]
            if len(actions) > 0:
                print("Actions for round " + current_round_string + ": " + str(actions))
        if updated_data is None:
            updated_data = {"updated_cash": cash} # just here for the logging to work; see the todo far below for more
        # generated moneeee
        cash_generated = 0
        for key in farms:
            farm = farms[key]
            cash_generated += calculate_cash_per_round(farm)
        end_of_round_cash = (current_round.index + 100) * difficulty.cash_gain_multiplier
        cash = cash + cash_generated + end_of_round_cash + (current_round.bloon_cash if use_bloon_cash else 0)
        if current_round.index >= 0:
            # if len(farms) >= 2:
            #     farm0 = "meow"
            #     farm1 = "meow"
            #     for farm_key in farms:
            #         print("farm_key: " + farm_key)
            #         if farm0 == "meow":
            #             farm0 = farms[farm_key]
            #         else:
            #             farm1 = farms[farm_key]
            #             break
            #     print('farm0.upgrades["top"].uid == farm1.upgrades["top"].uid: ' + str(farm0.upgrades["top"].uid == farm1.upgrades["top"].uid))
            #     print("farm0.upgrades.focused_path.uid == farm1.upgrades.focused_path.uid: " + str(farm0.upgrades.focused_path.uid == farm1.upgrades.focused_path.uid))
            # format cash
            cash_for_display = floor(cash*100)/100
            cash_string = str(cash_for_display*1.0)
            cash_strlen = len(cash_string)
            if cash_string.find(".") == (len(cash_string)-2):
                cash_string += "0"
            if cash_strlen < 8:
                cash_string = ((8-cash_strlen) * " ") + cash_string
            # format updated cash
            # This is kinda poor naming, updated_cash here means "cash before adding the end-of-round cash". TODO: fix "updated cash" naming
            updated_cash_for_display = floor(updated_data["updated_cash"]*100)/100
            updated_cash_string = str(updated_cash_for_display*1.0)
            updated_cash_strlen = len(updated_cash_string)
            if updated_cash_string.find(".") == (len(updated_cash_string)-2):
                updated_cash_string += "0"
            if updated_cash_strlen < 8:
                updated_cash_string = ((8-updated_cash_strlen) * " ") + updated_cash_string
            print(f"Cash at end of round {current_round_string}{greed_limit_string}: {cash_string} ({updated_cash_string}), cash_safe: {cash_safe}, cr: {cash_generated}, farms: {many_farms_to_string(farms)}")

def sim_market_routes(current_cash, current_farms, difficulty):
    want="NONE"
    first_run = True
    actions = []
    while want != "NONE" or first_run:
        # print("\nnewloop")
        if first_run:
            first_run = False
        latest_farm: BananaFarm = None
        latest_string_index: str = None
        latest_middle_tier: int = None
        latest_bottom_tier: int = None
        last_farm_string_index: str = None
        farmslen = len(current_farms)
        no_farms = (farmslen == 0)
        if no_farms:
            print("no farms")
            want="BUY_NEW_FARM"
        else:
            latest_farm: BananaFarm = current_farms["0"]
            latest_string_index = "0"
            latest_middle_tier = latest_farm.upgrades.middle.tier
            latest_bottom_tier = latest_farm.upgrades.bottom.tier
            last_farm_string_index = str(len(current_farms)-1)
            # finding least upgraded farm
            for farm_key in current_farms:
                if latest_middle_tier < 2:
                    if latest_bottom_tier > 3:
                        print("wat")
                    # always prefer upgrading middle if the farm is tier 3
                    if latest_bottom_tier >= 3:
                        want = "UPGRADE_LATEST_middle"
                        continue
                        # goto processing_wanted # goto would save like 3 levels of indentation in 10 places in this function # if it existed
                farm = current_farms[farm_key]
                farm_bottom_tier = farm.upgrades.bottom.tier
                if farm_bottom_tier < latest_bottom_tier or (farm_bottom_tier == latest_bottom_tier and farm.upgrades.middle.tier < 2):
                    latest_farm = farm
                    latest_string_index = farm_key
                    latest_middle_tier = latest_farm.upgrades.middle.tier
                    latest_bottom_tier = latest_farm.upgrades.bottom.tier
            if latest_bottom_tier >= 3 and latest_middle_tier < 2:
                want = "UPGRADE_LATEST_middle"
            elif farmslen < 3:
                if latest_bottom_tier == 3:
                    want = "BUY_NEW_FARM"
                else:
                    want = "UPGRADE_LATEST_bottom"
            elif farmslen >= 3:
                if farmslen == 6 and current_farms["0"].upgrades["bottom"].tier == 4 and latest_bottom_tier == 4:
                    want = "UPGRADE_FIRST_bottom"
                elif latest_bottom_tier == 4:
                    want = "BUY_NEW_FARM"
                else:
                    want = "UPGRADE_LATEST_bottom"
        if want == "NONE":
            break
        # ::processing_wanted::
        if want == "BUY_NEW_FARM":
            if current_cash >= upgrades.initial_farm_price:
                print(want)
                current_cash -= (upgrades.initial_farm_price - (upgrades.initial_farm_price_reduction if no_farms else 0))
                print("things: " + str(last_farm_string_index) + ", " + str(current_farms.keys()))
                new_string_index = "0" if no_farms else str(int(last_farm_string_index)+1)
                print(f", new_string_index: {new_string_index}")
                current_farms[new_string_index] = BananaFarm(string_index=new_string_index,is_first_farm=no_farms,upgrades=TowerCrosspath(focused_path=TowerPath(FARM_UPGRADE_TREE.bottom, 0),secondary_path=TowerPath(FARM_UPGRADE_TREE.middle, 0),upgrade_tree=FARM_UPGRADE_TREE))
                actions.append({"action": "buy_new_farm", "string_index": new_string_index})
            else:
                want = "NONE" # we don't have enough cash yet, so don't do anything till we do
        elif want.startswith("UPGRADE_"):
            farm_to_upgrade = None
            farm_to_upgrade_string_index = None
            if want.startswith("UPGRADE_LATEST"):
                farm_to_upgrade = latest_farm
                farm_to_upgrade_string_index = latest_string_index
            elif want.startswith("UPGRADE_FIRST"):
                farm_to_upgrade = current_farms["0"]
                farm_to_upgrade_string_index = "0"
            path_to_upgrade = want[(want.rfind("_")+1):]
            if path_to_upgrade not in path_names: # incase something silly happens
                print("path_to_upgrade: " + path_to_upgrade)
            next_price = upgrades.prices[path_to_upgrade][farm_to_upgrade.upgrades[path_to_upgrade].tier]
            if current_cash >= next_price:
                print(want)
                current_cash -= next_price
                farm_to_upgrade.upgrades.upgrade(path_to_upgrade,1)
                actions.append({"action": "upgrade", "index": farm_to_upgrade_string_index, "path": path_to_upgrade, "amount": 1}) # TODO: add higher amount upgrades
            else:
                want = "NONE" # same thing again here
    return { "updated_cash": current_cash, "updated_farms": current_farms, "actions": actions }

tests.test_farm_calculations(logging=False)
# plot_cost_vs_gain()
sim_farming(limit_greed=True)
# print(thingamajig)
stuff = {}
for path_name in path_names:
    if path_name == "middle":
        continue
    stuff[path_name] = {}
    for tier in range(3,6):
        stuff[path_name][str(tier)] = calculate_cash_per_round(BananaFarm(is_first_farm=False,upgrades=TowerCrosspath(focused_path=TowerPath(FARM_UPGRADE_TREE[path_name],tier),secondary_path=TowerPath(FARM_UPGRADE_TREE["middle"],2),upgrade_tree=FARM_UPGRADE_TREE)))

print(stuff)
