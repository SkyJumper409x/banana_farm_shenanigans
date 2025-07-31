from constants.farm import BananaFarm
from constants.farm.utils import farm_upgrades_to_string, calculate_price,calculate_cash_per_bunch, calculate_bunches_per_round, calculate_cash_per_round, get_crosspath, get_focused_path, get_remaining_crosspath_options
import constants.farm.utils as utils # for util methods that are only used once
from constants.towers import TowerCrosspath, TowerPath, path_names
from constants.towers_farm import FARM_UPGRADE_TREE
import constants.farm.upgrades as upgrades
import json
import sys

def test_and_print_farm(farm: BananaFarm):
    print("The farm is a " + str(farm_upgrades_to_string(farm)) + " farm. It is " + ("" if farm.is_first_farm else "not ") + "the first farm")
    print("Total price:         " + str(calculate_price(farm)))
    print("Total upgrade price: " + str(calculate_price(farm, False)))
    print("Cash per bunch:      " + str(calculate_cash_per_bunch(farm)))
    print("Bunches per round:   " + str(calculate_bunches_per_round(farm)))
    print("Cash per round:      " + str(calculate_cash_per_round(farm)))
    print("get_crosspath(farm): " + str(get_crosspath(farm)))

def test_farm_asserts(farm: BananaFarm):
    # this just runs all farm-related functions and more or less validates the output for each of them
    # human-readable upgrades
    farm_string = farm_upgrades_to_string(farm, jsonFormat=False)
    assert farm_string.count("/") == 2
    assert len(farm_string) == 5
    # json'd upgrades
    farm_json_string = farm_upgrades_to_string(farm, jsonFormat=True)
    try:
        farm_json = json.loads(farm_json_string)
        str(farm_json).count("0")
    except ValueError as e:
        # json parse failed, so json is invalid
        print(e, file=sys.stderr)
        assert False
    # focused path
    focused_path = utils.get_focused_path(farm)
    assert type(focused_path) is TowerPath
    assert focused_path == farm.upgrades.focused_path
    focused_tier = focused_path.tier
    # secondary path
    secondary_path = farm.upgrades.secondary_path
    secondary_tier = secondary_path.tier
    # for the case that (focused_tier < secondary_tier), which is still valid if secondary_tier < 3
    maxed_tier = max(focused_tier, secondary_tier)
    # ensure the tiers make sense
    assert farm.upgrades[farm.upgrades.unused_path_name].tier == 0
    assert not ((focused_tier >= 3) and (secondary_tier >= 3))
    assert focused_tier >= secondary_tier or secondary_tier < 3, f"focused_tier: {focused_tier}, secondary_tier: {secondary_tier}" # just incase i forget how things work: no check for focused_tier < 3 because either focused >= secondary (in which case the statement is true regardless) or secondary > focused, in which case secondary < 3 implies focused < 3, since focused < secondary_tier < 3
    assert utils.get_overall_tier(farm) == maxed_tier
    # copy methods stuff
    upgrades_copy = farm.upgrades.deep_copy()
    assert upgrades_copy != farm.upgrades
    assert upgrades_copy.focused_path != focused_path
    # crosspath
    crosspath = get_crosspath(farm)
    assert ((type(crosspath) is dict) == (focused_tier >= 3))
    if type(crosspath) is dict:
        assert ("focused_path" in crosspath) and ("secondary_path" in crosspath)
    # price calculation
    total_price = calculate_price(farm)
    upgrades_price = calculate_price(farm, include_initial_price=False)
    assert (1000 < (total_price - upgrades_price) < 1400)
    assert (upgrades_price > 200) == (maxed_tier > 0), f"upgrades_price: {upgrades_price}, focused_tier: {focused_tier}"
    assert (upgrades_price - ((upgrades_price//10)*10) == 0)
    # cash per bunch and bunches per round calculation
    cb = calculate_cash_per_bunch(farm)
    br = calculate_bunches_per_round(farm)
    cr = calculate_cash_per_round(farm)
    assert cr == (cb * br)
    assert (cb >= 20)
    assert (br >= 4)
    focused_name = focused_path.path.name
    if focused_name == "top":
        assert (br == 16) == (focused_tier == 3), f"br: {br}, focused_tier: {focused_tier}"
    elif focused_name == "bottom" and focused_tier >= 3:
        extra = 0
        if secondary_path.path.name == "top":
            extra = 2 * secondary_tier
        assert br == (16 + extra), f"br: {br}, extra: {extra}"
def test_farm_calculations(logging=True, enable_asserts=True):
    test_access_methods()
    test_upgrades = [[0,0,0],[1,0,0],[2,0,0],[3,0,0],[4,0,0],[3,0],[4,0],[0,2,0],[0,0,3],[0,3],[0,4],[2,3]]
    farms = []
    for i in range(0,len(test_upgrades)):
        if len(test_upgrades[i]) == 2:
            test_upgrades[i].insert(1, (2 if (test_upgrades[i][0]+test_upgrades[i][1] == max(test_upgrades[i])) else 0))
        focused_path=TowerPath(path=FARM_UPGRADE_TREE.top,tier=test_upgrades[i][0])
        if test_upgrades[i][2] > 0:
            focused_path = TowerPath(path=FARM_UPGRADE_TREE.bottom,tier=test_upgrades[i][2])
        secondary_index = 1
        if test_upgrades[i][1] == 0:
            if test_upgrades[i][2] >= 3 and test_upgrades[i][0] >= 1:
                secondary_index = 0
            if test_upgrades[i][2] >= 1 and test_upgrades[i][0] >= 3:
                secondary_index = 2
        # print("FARM_UPGRADE_TREE[secondary_index]: FARM_UPGRADE_TREE[" + str(secondary_index) + "]: " + str(FARM_UPGRADE_TREE[secondary_index]))
        farm_to_test = BananaFarm(upgrades=TowerCrosspath(focused_path=focused_path, secondary_path=TowerPath(path=FARM_UPGRADE_TREE[secondary_index],tier=test_upgrades[i][secondary_index]),upgrade_tree=FARM_UPGRADE_TREE), is_first_farm=False)
        if logging:
            print("==test_farm_" + str(i) + "==")
            test_and_print_farm(farm_to_test)
            # if we're logging, then do the assert tests once logging has finished,
            # so, in case an assert will fail,* it only does once all information has been logged
            farms.append(farm_to_test)
        elif enable_asserts:
            # if we aren't logging anything, just assert test everything immediately
            test_farm_asserts(farm_to_test)
    if enable_asserts:
        for farm in farms:
            # * which would happen here,
            test_farm_asserts(farm)
        test_farm_asserts_misc()

def test_farm_asserts_misc():
    # testing crosspath options
    # this method accepts a number from 0-2 (top, middle or bottom as focused paths)
    # so it can be tested once, (unlike almost all other functions)
    opts_0 = get_remaining_crosspath_options(0)
    opts_1 = get_remaining_crosspath_options(1)
    opts_2 = get_remaining_crosspath_options(2)
    assert (opts_0 == [1,2]) or (opts_0 == [2,1])
    assert (opts_1 == [0,2]) or (opts_1 == [2,0])
    assert (opts_2 == [0,1]) or (opts_2 == [1,0])

def test_access_methods():
    # [focused index, focused tier, secondary index, secondary tier]
    # not ideal by any means but it works
    test_upgrades=[[0,0,1,0],[0,2,1,0],[0,3,1,2],[2,4,0,1]]
    for test_upgrade in test_upgrades:
        farm = BananaFarm(string_index=str(test_upgrades.index(test_upgrade)),upgrades=TowerCrosspath(focused_path=TowerPath(path=FARM_UPGRADE_TREE[test_upgrade[0]],tier=test_upgrade[1]),secondary_path=TowerPath(path=FARM_UPGRADE_TREE[test_upgrade[2]],tier=test_upgrade[3]),upgrade_tree=FARM_UPGRADE_TREE),is_first_farm=False)
        assert get_focused_path(farm) == farm.upgrades.focused_path
        gotten_crosspath = get_crosspath(farm)
        assert gotten_crosspath == -2 if test_upgrade[1] <= 2 and test_upgrade[3] <= 2 else (gotten_crosspath["focused_path"]["path_index"] == test_upgrade[0]
            and gotten_crosspath["focused_path"]["path_tier"] == test_upgrade[1]
            and gotten_crosspath["secondary_path"]["path_index"] == test_upgrade[2]
            and gotten_crosspath["secondary_path"]["path_tier"] == test_upgrade[3])
        for i in range(0,3):
            path_name = path_names[i]
            path_byname = farm.upgrades.top if i == 0 else (farm.upgrades.middle if i == 1 else farm.upgrades.bottom)
            assert farm.upgrades[path_name] == farm.upgrades[i] == path_byname
            assert path_byname.index == path_byname.path.index
    print("test_access_methods() finished")
