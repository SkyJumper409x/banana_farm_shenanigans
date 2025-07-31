BASE_ACTIONS = []
    

class BaseAction():
    idx: int
    name: str
    def __init__(self, name: str):
        self.idx = len(BASE_ACTIONS)
        self.name = name
        BASE_ACTIONS.append(self)
        
ACT_CONTINUE = BaseAction("continue")
ACT_BUY_FARM = BaseAction("buy_farm"),
ACT_UPGRADE_FARM = BaseAction("upgrade_farm")


class Action():
    base_action: BaseAction
    action_values: list = []
    name: str
    def __init__(self, _base_action: BaseAction, _action_values: list = None):
        if type(_base_action) is Action:
            _base_action = _base_action.base_action
        self.base_action = _base_action
        self.action_values = _action_values
        self.name = "{base_action.name: " + _base_action.name + ", action_values: " + str(_action_values) + "}"

_default_contained_actions: dict = {}
for action in BASE_ACTIONS:
    _default_contained_actions[Action(action).name] = False
    
class ActionList():
    elements_list = []
    elements_dict: dict
    contained_actions: dict
    def __init__(self):
        self.contained_actions = _default_contained_actions.copy()
    def add(self, action: Action):
        self.elements_list.append(action)
        self.elements_dict[action.name] = action
        self.contained_actions[action.name] = True
    def contains(self, action: Action):
        if type(action) is BaseAction:
            action = BaseAction
        return self.contained_actions[action.name]
    def get(self, action):
        if type(action) is BaseAction:
            action = Action(action)
        return self.elements_dict[action.name]
        
    # def containsBase(self, base_action: BaseAction):
    #     return self.contained_actions[Action(base_action).name]


mrow = ActionList()

print(mrow.contained_actions)
