import constants.farm.upgrades as upgrades
from constants.farm import BananaFarm, valuable_bananas_multi
from constants.towers import TowerCrosspath, TowerPath, path_names, top, middle, bottom  # noqa: F401
import math

# returns the "overall tier" of the farm, which is the furthest tier that any path has been upgraded to, so the tier of the focused path
def get_overall_tier(farm: BananaFarm):
    return max(farm.upgrades.focused_path.tier,farm.upgrades.secondary_path.tier)

# returns:
# if the farm uses an invalid crosspath (for example 5/3/0 or 1/4/1): -1
# if the farm's overall tier is less than 3: -2
# otherwise: the path index of the "focused path", which is the path that has a tier that's higher than 2.
def get_focused_path(farm: BananaFarm):
    return farm.upgrades.focused_path

# returns the path indices of the paths that aren't focused,
# or -1 if the supplied argument is not a valid path index
# For example: If the focused path is top, this returns the array [middle, bottom]
def get_remaining_crosspath_options(focused_path_index: int):
    if focused_path_index < 0 or focused_path_index > 3:
        return -1
    # math moment incoming
    return [1 - math.ceil(focused_path_index/2), 2 - math.floor(focused_path_index/2)] # yes, I figured this out myself

# returns:
# if the farm's upgrade data is deemed invalid by get_focused_path: the value that was returned by get_focused_path
# otherwise: a dictionary with keys "focused_path" and "secondary_path", with each corresponding value being the numerical index for that path;
# if there is no secondary path, the value corresponding to "secondary_path" is -3
def get_crosspath_indices(farm: BananaFarm):
    focused: TowerPath = get_focused_path(farm)
    if focused.tier < 3:
        return -2
    elif focused.path.index > 2:
        return -135

    secondary = -3
    options = get_remaining_crosspath_options(focused.path.index)
    # print("options: " + str(options))
    for option in options:
        # print("farm.upgrades[path_names[option]].tier: farm.upgrades[path_names[" + str(option) + "]].tier: " + str(farm.upgrades[path_names[option]].tier))
        if farm.upgrades[path_names[option]].tier > 0:
            if secondary != -3: 
                # If we are here, the farm's upgrades are invalid.
                # This is already checked by get_focused_path, so if we get here, something went completely wrong.
                print("this code should be unreachable, how did you even do this")
                this_is_supposed_to_error = 1/0
                print(this_is_supposed_to_error)
                return -123
            secondary = option
    return { "focused_path": focused.path.index, "secondary_path": secondary }

# returns get_crosspath_indices(farm), but, (if a dictionary is returned) instead of the dictionary values being the crosspath indices,
# the returned dictionary's values are dictoinaries which each have a "path_index" key and a "path_tier" key.
# the full structure of the returned dictionary looks like this for a 3/2/0 farm:
# { 
#   "focused_path":   { "path_index": 0, "path_tier": 3 }, 
#   "secondary_path": { "path_index": 1, "path_tier": 2 } 
# }
def get_crosspath(farm: BananaFarm): 
    crosspath_indices = get_crosspath_indices(farm)
    if type(crosspath_indices) is not type({}):
        # print("[dbg] crosspath_indices is " + str(crosspath_indices))
        return crosspath_indices
    focused_index = crosspath_indices["focused_path"]
    secondary_index = crosspath_indices["secondary_path"]
    # print("path_names[secondary_index]: path_names[" + str(secondary_index) + "]: " + path_names[secondary_index])
    return {
        "focused_path":   { "path_index": focused_index,   "path_tier": farm.upgrades[path_names[focused_index]].tier   },
        "secondary_path": { "path_index": secondary_index, "path_tier": farm.upgrades[path_names[secondary_index]].tier }
    }

def farm_upgrades_to_string(farm: BananaFarm, jsonFormat: bool = False):
    if jsonFormat:
        return '{ "focused_path": { "name": "' + farm.upgrades.focused_path.path.name + '", "tier": ' + str(farm.upgrades.focused_path.tier) + " }, " + '"secondary_path": { "name": "' + farm.upgrades.secondary_path.path.name + '", "tier": ' + str(farm.upgrades.secondary_path.tier) + ' } }'
    return str(farm.upgrades.top.tier) + "/" + str(farm.upgrades.middle.tier) + "/" + str(farm.upgrades.bottom.tier)

# returns the price for all upgrades in a path up to (including) the path's tier
# I don't feel like writing input validation for this rn so uh behaviour is undefined for invalid inputs
def calculate_path_price(path: dict, include_farm_price: bool = False, first_farm: bool = False):
    # print("[dbg] path: " + str(path))
    upgrades_price = sum(upgrades.prices[path_names[path["path_index"]]][0:path["path_tier"]])
    # print("[dbg] " + str(upgrades_price))
    total_cost = upgrades_price
    if include_farm_price:
        total_cost += upgrades.initial_farm_price
        if first_farm:
            total_cost -= upgrades.initial_farm_price_reduction
    return total_cost

# returns
# if the supplied argument is invalid (for ex. impossible crosspath): the result of get_crosspath(farm)
# otherwise: the price of the farm and all its upgrades
def calculate_price(farm: BananaFarm, include_initial_price: bool = True):
    crosspath = get_crosspath(farm)
    # print("[dbg] crosspath is " + str(crosspath))
    if (crosspath != -2) and (type(crosspath) is not type({})) and (crosspath < 0):
        return crosspath
    #
    initial_price = 0
    if include_initial_price:
        # print("initial_price = " + str(upgrades.initial_farm_price))
        initial_price = upgrades.initial_farm_price
        if farm.is_first_farm:
            initial_price -= upgrades.initial_farm_price_reduction
    focused_price = 0
    secondary_price = 0
    if crosspath == -2:
        other_path_tier = 0
        for i in range(0,3):
            path_tier = farm.upgrades[path_names[i]].tier
            if path_tier > 0:
                path_price = calculate_path_price({ "path_index": i, "path_tier": path_tier })
                if focused_price == 0:
                    focused_price = path_price
                    other_path_tier = path_tier
                elif secondary_price == 0:
                    if other_path_tier < path_tier:
                        secondary_price = focused_price
                        focused_price = path_price
                    else:
                        secondary_price = path_price
                else:
                    # if we are here, the farm has upgrades on all three paths.
                    # that should've caused crosspath to be -1, so something's fishy here
                    return -320
    elif type(crosspath) is int: # only one path has upgrades the upgrade tier is less than 3
        if crosspath < 0:
            print("crosspath < 0")
            thisIsSupposedToError = 1/0
            print(thisIsSupposedToError)
        pathTier = farm.upgrades[path_names[crosspath]].tier
        if pathTier == 0:
            return initial_price
        return initial_price + upgrades.prices[path_names[crosspath]][pathTier-1]
    else:
        focused_price = calculate_path_price(crosspath["focused_path"])
        secondary_price = calculate_path_price(crosspath["secondary_path"])

    total_price = initial_price + focused_price + secondary_price
    return total_price

def calculate_cash_per_bunch(farm: BananaFarm):
    focused_path = get_focused_path(farm)
    focused_path_index = focused_path.path.index
    # -2 is returned by get_focused_path if the farm's overall tier is below 3 (because in that case there is no focused path)
    cash_per_bunch_no_multi = 0
    if focused_path_index == -2:
        # cash_per_bunch_base can be assumed because there is no change to the cash per bunch for tier < 4
        cash_per_bunch_no_multi = upgrades.cash_per_bunch_base
    else:
        cash_per_bunch_no_multi = upgrades.base_and_upgrade_cash_per_bunch[path_names[focused_path_index]][farm.upgrades.focused_path.tier]
    return cash_per_bunch_no_multi * (1 if farm.upgrades.middle.tier < 2 else valuable_bananas_multi) * 1.0
def calculate_bunches_per_round(farm: BananaFarm):
    # print("farm thing: " + str(farm.upgrades.top.tier) + ", " + str(upgrades.base_and_upgrade_bunches_per_round["top"][farm.upgrades.top.tier]))
    return upgrades.base_and_upgrade_bunches_per_round["top"][farm.upgrades.top.tier] + upgrades.base_and_upgrade_bunches_per_round["bottom"][farm.upgrades.bottom.tier] - upgrades.base_and_upgrade_bunches_per_round["bottom"][0]
def calculate_cash_per_round(farm: BananaFarm):
    return calculate_cash_per_bunch(farm) * calculate_bunches_per_round(farm)

def many_farms_to_string(farms: dict):
    result = "[ "
    for farm_key in farms:
        farm = farms[farm_key]
        result += farm_upgrades_to_string(farm, jsonFormat=False)
        result += ", "
    result = result[0:-2] + " ]"
    return result
