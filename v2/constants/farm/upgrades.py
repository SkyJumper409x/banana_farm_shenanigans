from constants.settings import mk
import math
# prices
initial_farm_price_base = 1250
initial_farm_price = initial_farm_price_base
if mk[0]:
    initial_farm_price = math.floor(initial_farm_price_base - 0.02*initial_farm_price_base)
initial_farm_price_reduction_with_mk = 100
initial_farm_price_reduction = 0
if mk[2]:
    initial_farm_price_reduction = initial_farm_price_reduction_with_mk

prices = {
    "top": [500, 600, 3000, 19000, 115000],
    "middle": [300, 800, 3650, 7200, 100000],
    "bottom": [250, 400, 2700, 15000, 70000]
}
# for displaying stuff
names = {
    "top": ["Increased Production", "Greater Production", "Banana Plantation", "Banana Research Facility", "Banana Central"],
    "middle": ["Long Life Bananas", "Valuable Bananas", "Monkey Bank", "IMF Loan", "Monkey-Nomics"],
    "bottom": ["EZ Collect", "Banana Salvage", "Marketplace", "Central Market", "Monkey Wall Street"]
}
base_and_upgrade_cash_per_bunch = {}
cash_per_bunch_base = 20
def init_cb(): # init cash/bunch
    cash_per_bunch_values = {
        "brf": 300, # Banana Research Facility
        "bc": 1200, # Banana Central
        "cm":   70  # Central Market
    }
    base_and_upgrade_cash_per_bunch["top"]    = [cash_per_bunch_base, cash_per_bunch_base, cash_per_bunch_base, cash_per_bunch_base, cash_per_bunch_values["brf"], cash_per_bunch_values["bc"]]
    base_and_upgrade_cash_per_bunch["middle"] = [cash_per_bunch_base, 0, 0, 0, 0, 0] # TODO
    base_and_upgrade_cash_per_bunch["bottom"] = [cash_per_bunch_base, cash_per_bunch_base, cash_per_bunch_base, cash_per_bunch_base, cash_per_bunch_values["cm"], cash_per_bunch_values["cm"]]
init_cb()

# bunches per round
bunches_per_round_base = 4
bunches_per_round_tier3_base = 16
bfr_crates_per_round = 5

base_and_upgrade_bunches_per_round = {
    "top": [bunches_per_round_base, bunches_per_round_base+2, bunches_per_round_base+4, bunches_per_round_tier3_base, bfr_crates_per_round, bfr_crates_per_round],
    "middle": [bunches_per_round_base,bunches_per_round_base,bunches_per_round_base,0,0,0], # TODO
    "bottom": [bunches_per_round_base, bunches_per_round_base, bunches_per_round_base, bunches_per_round_tier3_base, bunches_per_round_tier3_base, bunches_per_round_tier3_base]
}
