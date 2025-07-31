import constants.settings as settings
from typing import NamedTuple

# starting cash for sims
starting_cash_base = 650
starting_cash_bonus = 0
if settings.mk[3]:
    starting_cash_bonus = 200


# Rounds & Difficulties
class Round(NamedTuple):
    index: int = 0
    bloon_cash: float = 0
    cash_per_pop_multiplier: float = 1

bloon_cashs_cached = {"cache_set": False}
def get_bloon_cashs():
    global bloon_cashs_cached
    if bloon_cashs_cached["cache_set"]:
        return bloon_cashs_cached.copy()
    bloon_cashs = {"cache_set": True}
    rounds_file = open("rounds.csv","r")
    lines = rounds_file.readlines()
    for line in lines:
        if line[-6:] == 'cash"\n':
            continue
        tokens = line.split(";")
        bloon_cashs[str(tokens[0])] = float(tokens[1][1:-1].replace(",",""))
    bloon_cashs_cached = bloon_cashs.copy()
    return bloon_cashs

def get_rounds(start, final):
    bloon_cashs = get_bloon_cashs()
    rounds = [Round(index=0,bloon_cash=0,cash_per_pop_multiplier=1)]
    cash_per_pop_multiplier = 1
    for i in range(start, final+1):
        if i == 51:
            cash_per_pop_multiplier = .5
        elif i == 61:
            cash_per_pop_multiplier = .2
        elif i == 86:
            cash_per_pop_multiplier = .1
        elif i == 101:
            cash_per_pop_multiplier = .05
        elif i == 121:
            cash_per_pop_multiplier = .02
        rounds.append(Round(index=i, bloon_cash=bloon_cashs[str(i)],cash_per_pop_multiplier=cash_per_pop_multiplier))
    return rounds

class Difficulty:
    name: str = "Medium"
    price_multiplier: float = 1
    start_round = 1
    end_round = 60
    round_count = 60
    rounds = []
    bloon_speed_multiplier: float = 1.1
    starting_lives: int = 150
    moab_health_multiplier: float = 1 # Easy and Double HP Moabs
    cash_gain_multiplier: float = 1     # half cash & deflation
    starting_cash: int = starting_cash_base # deflation 
    def __init__(self, name, price_multiplier, start_round, end_round, bloon_speed_multiplier=1.1, starting_lives=150, moab_health_multiplier=1, starting_cash=starting_cash_base, cash_gain_multiplier=1):
        self.name = name
        self.start_round = start_round
        self.end_round = end_round
        self.bloon_speed_multiplier = bloon_speed_multiplier
        self.starting_lives = starting_lives
        self.moab_health_multiplier = moab_health_multiplier
        self.round_count = end_round - start_round + 1
        self.rounds = get_rounds(start_round, end_round)
        self.starting_cash = starting_cash
        self.cash_gain_multiplier = cash_gain_multiplier

difficulty_names = ["Easy", "Medium", "Hard", "Impoppable", "Half Cash", "Medium_Boss"]

EASY =       Difficulty(name=difficulty_names[0], start_round=1, end_round= 40, price_multiplier=0.85, moab_health_multiplier=0.665)
MEDIUM =     Difficulty(name=difficulty_names[1], start_round=1, end_round= 60, price_multiplier=1,    bloon_speed_multiplier=1.1)
HARD =       Difficulty(name=difficulty_names[2], start_round=3, end_round= 80, price_multiplier=1.08)
IMPOPPABLE = Difficulty(name=difficulty_names[3], start_round=6, end_round=100, price_multiplier=1.2)
HALF_CASH =  Difficulty(name=difficulty_names[4], start_round=3, end_round= 80, price_multiplier=HARD.price_multiplier, starting_cash=HARD.starting_cash/2, cash_gain_multiplier=0.5)
# medium up to round 140
MEDIUM_BOSS= Difficulty(name=difficulty_names[5], start_round=1, end_round= 140, price_multiplier=1, bloon_speed_multiplier=1.1)

DIFFICULTIES = {
    0: EASY,
    1: MEDIUM,
    2: HARD,
    3: IMPOPPABLE,
    4: HALF_CASH,
    5: MEDIUM_BOSS,
}
for i in range(0,6):
    DIFFICULTIES[difficulty_names[i]] = DIFFICULTIES[i]
    DIFFICULTIES[difficulty_names[i].upper()] = DIFFICULTIES[i]
