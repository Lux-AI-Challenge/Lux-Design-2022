from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Callable

import numpy as np
from typing import TYPE_CHECKING
from luxai2022.config import EnvConfig
if TYPE_CHECKING:
    from luxai2022.factory import Factory
    from luxai2022.state import State
from luxai2022.map.position import Position


import luxai2022.unit as luxai_unit


# (0 = move, 1 = transfer X amount of R, 2 = pickup X amount of R, 3 = dig, 4 = self destruct, 5 = recharge X, 6 = repeat)
class Action:
    def __init__(self, act_type: str) -> None:
        self.act_type = act_type
        self.repeat = False

    def state_dict():
        raise NotImplementedError("")


class FactoryBuildAction(Action):
    def __init__(self, unit_type: int) -> None:
        super().__init__("factory_build")
        self.unit_type = unit_type

    def state_dict(self):
        return self.unit_type


class FactoryWaterAction(Action):
    def __init__(self) -> None:
        super().__init__("factory_water")
        self.water_cost = None

    def state_dict():
        return 2


class MoveAction(Action):
    def __init__(self, move_dir: int, dist: int = 1, repeat=False) -> None:
        super().__init__("move")
        # a[1] = direction (0 = center, 1 = up, 2 = right, 3 = down, 4 = left)
        self.move_dir = move_dir
        self.dist = dist
        self.repeat = repeat

    def state_dict(self):
        return np.array([0, self.move_dir, self.dist, 0, self.repeat])


class TransferAction(Action):
    def __init__(self, transfer_dir: int, resource: int, transfer_amount: int, repeat=False) -> None:
        super().__init__("transfer")
        # a[2] = R = resource type (0 = ice, 1 = ore, 2 = water, 3 = metal, 4 power)
        self.transfer_dir = transfer_dir
        self.resource = resource
        self.transfer_amount = transfer_amount
        self.repeat = repeat

    def state_dict(self):
        return np.array([1, self.transfer_dir, self.resource, self.transfer_amount, self.repeat])


class PickupAction(Action):
    def __init__(self, resource: int, pickup_amount: int, repeat=False) -> None:
        super().__init__("pickup")
        # a[2] = R = resource type (0 = ice, 1 = ore, 2 = water, 3 = metal, 4 power)
        self.resource = resource
        self.pickup_amount = pickup_amount
        self.repeat = repeat

    def state_dict(self):
        return np.array([2, 0, self.resource, self.pickup_amount, self.repeat])


class DigAction(Action):
    def __init__(self, repeat=False) -> None:
        super().__init__("dig")
        self.repeat = repeat

    def state_dict(self):
        return np.array([3, 0, 0, 0, self.repeat])


class SelfDestructAction(Action):
    def __init__(self, repeat=False) -> None:
        super().__init__("self_destruct")
        self.repeat = repeat

    def state_dict(self):
        return np.array([4, 0, 0, 0, self.repeat])


class RechargeAction(Action):
    def __init__(self, power: int, repeat=False) -> None:
        super().__init__("recharge")
        self.power = power
        self.repeat = repeat

    def state_dict(self):
        return np.array([5, 0, 0, self.power, self.repeat])


def format_factory_action(a: int):
    if a == 0 or a == 1:
        return FactoryBuildAction(unit_type=a)
    elif a == 2:
        return FactoryWaterAction()
    else:
        raise ValueError(f"Action {a} for factory is invalid")


def format_action_vec(a: np.ndarray):
    # (0 = move, 1 = transfer X amount of R, 2 = pickup X amount of R, 3 = dig, 4 = self destruct, 5 = recharge X, 6 = repeat)
    a_type = a[0]
    if a_type == 0:
        return MoveAction(a[1], dist=1, repeat=a[4])
    elif a_type == 1:
        return TransferAction(a[1], a[2], a[3], repeat=a[4])
    elif a_type == 2:
        return PickupAction(a[2], a[3], repeat=a[4])
    elif a_type == 3:
        return DigAction(repeat=a[4])
    elif a_type == 4:
        return SelfDestructAction(repeat=a[4])
    elif a_type == 5:
        return RechargeAction(a[3], repeat=a[4])
    else:
        raise ValueError(f"Action {a} is invalid type, {a[0]} is not valid")


# a[1] = direction (0 = center, 1 = up, 2 = right, 3 = down, 4 = left)
move_deltas = np.array([[0, 0], [0, -1], [1, 0], [0, 1], [-1, 0]])


def validate_actions(env_cfg: EnvConfig, state: 'State', actions_by_type, verbose=1):
    """
    validates actions and logs warnings for any invalid actions. Invalid actions are subsequently not evaluated
    """
    actions_by_type_validated = defaultdict(list)
    valid_action = True

    def invalidate_action(msg):
        nonlocal valid_action
        valid_action = False
        if verbose > 0: print(msg)

    for unit, transfer_action in actions_by_type["transfer"]:
        valid_action = True
        unit: luxai_unit.Unit
        transfer_action: TransferAction
        if transfer_action.resource > 4 or transfer_action.resource < 0:
            invalidate_action(
                f"Invalid Transfer Action for unit {unit}, transferring invalid resource id {transfer_action.resource}"
            )
            continue
        # if transfer_action.transfer_amount < 0: do not need to check as action space permits range of [0, max_transfer_amount] anyway
        # TODO - check what happens if transferring with direction center?
        resource_id = transfer_action.resource
        amount = transfer_action.transfer_amount
        if resource_id == 0:
            if unit.cargo.ice < amount:
                invalidate_action(
                    f"Invalid Transfer Action for unit {unit} - Tried to transfer {amount} ice but only had {unit.cargo.ice}"
                )
                continue
        elif resource_id == 1:
            if unit.cargo.ore < amount:
                invalidate_action(
                    f"Invalid Transfer Action for unit {unit} - Tried to transfer {amount} ore but only had {unit.cargo.ore}"
                )
                continue
        elif resource_id == 2:
            if unit.cargo.water < amount:
                invalidate_action(
                    f"Invalid Transfer Action for unit {unit} - Tried to transfer {amount} water but only had {unit.cargo.water}"
                )
                continue
        elif resource_id == 3:
            if unit.cargo.metal < amount:
                invalidate_action(
                    f"Invalid Transfer Action for unit {unit} - Tried to transfer {amount} metal but only had {unit.cargo.metal}"
                )
                continue
        elif resource_id == 4:
            if unit.power < amount:
                invalidate_action(
                    f"Invalid Transfer Action for unit {unit} - Tried to transfer {amount} power but only had {unit.power}"
                )
                continue

        if valid_action:
            actions_by_type_validated["transfer"].append((unit, transfer_action))

    for unit, dig_action in actions_by_type["dig"]:
        valid_action = True
        dig_action: DigAction
        if unit.unit_cfg.DIG_COST > unit.power:
            invalidate_action(
                f"Invalid Dig Action for unit {unit} - Tried to dig requiring {unit.unit_cfg.DIG_COST} power but only had {unit.power} power"
            )
            continue
        if valid_action:
            actions_by_type_validated["dig"].append((unit, dig_action))

    for unit, pickup_action in actions_by_type["pickup"]:
        valid_action = True
        pickup_action: PickupAction
        unit: luxai_unit.Unit
        factory = state.board.get_factory_at(unit.pos)
        if factory is None:
            invalidate_action(f"No factory to pickup from for unit {unit}")
            continue
        resource_id = pickup_action.resource
        amount = pickup_action.pickup_amount
        if resource_id == 0:
            if factory.cargo.ice < amount:
                invalidate_action(
                    f"Invalid Pickup Action for unit {unit} - Tried to pickup {amount} ice but factory only had {factory.cargo.ice}"
                )
                continue
        elif resource_id == 1:
            if factory.cargo.ore < amount:
                invalidate_action(
                    f"Invalid Pickup Action for unit {unit} - Tried to pickup {amount} ore but factory only had {factory.cargo.ore}"
                )
                continue
        elif resource_id == 2:
            if factory.cargo.water < amount:
                invalidate_action(
                    f"Invalid Pickup Action for unit {unit} - Tried to pickup {amount} water but factory only had {factory.cargo.water}"
                )
                continue
        elif resource_id == 3:
            if factory.cargo.metal < amount:
                invalidate_action(
                    f"Invalid Pickup Action for unit {unit} - Tried to pickup {amount} metal but factory only had {factory.cargo.metal}"
                )
                continue
        elif resource_id == 4:
            if factory.power < amount:
                invalidate_action(
                    f"Invalid Pickup Action for unit {unit} - Tried to pickup {amount} power but factory only had {factory.power}"
                )
                continue
        if valid_action:
            actions_by_type_validated["pickup"].append((unit, pickup_action))

    for unit, move_action in actions_by_type["move"]:
        valid_action = True
        move_action: MoveAction
        target_pos: Position = unit.pos + move_action.dist * move_deltas[move_action.move_dir]
        if (
            target_pos.x < 0
            or target_pos.y < 0
            or target_pos.x >= state.board.width
            or target_pos.y >= state.board.height
        ):
            invalidate_action(
                f"Invalid movement action for unit {unit} - Tried to move to {target_pos} which is off the map"
            )
            continue
        if state.board.factory_occupancy_map[target_pos.y, target_pos.x] != -1:
            factory_id = state.board.factory_occupancy_map[target_pos.y, target_pos.x]
            print(factory_id, state.factories[unit.team.agent].keys())
            if f"factory_{factory_id}" not in state.factories[unit.team.agent]:
                # if there is a factory but not same team
                invalidate_action(
                    f"Invalid movement action for unit {unit} - Tried to move to {target_pos} which is on an opponent factory"
                )
                continue
        rubble = state.board.rubble[target_pos.y, target_pos.x]
        power_required = unit.move_power_cost(rubble)
        if power_required > unit.power:
            invalidate_action(
                f"Invalid movement action for unit {unit} - Tried to move to {target_pos} requiring {power_required} power but only had {unit.power} power"
            )
            continue
        if valid_action:
            actions_by_type_validated["move"].append((unit, move_action))

    for factory, build_action in actions_by_type["factory_build"]:
        valid_action = True
        build_action: FactoryBuildAction
        factory: 'Factory'
        
        if build_action.unit_type == 0:
            unit_cfg = env_cfg.ROBOTS["LIGHT"]
            # Light
        elif build_action.unit_type == 1:
            unit_cfg = env_cfg.ROBOTS["HEAVY"]
        if factory.cargo.metal < unit_cfg.METAL_COST:
            invalidate_action(f"Invalid factory build action for factory {factory} - Insufficient metal {factory.cargo.metal}")
            continue
        if factory.power < unit_cfg.POWER_COST:
            invalidate_action(f"Invalid factory build action for factory {factory} - Insufficient metal {factory.cargo.metal}")
            continue
        if valid_action:
            actions_by_type_validated["factory_build"].append((factory, build_action))
        pass
    
    
    for factory, water_action in actions_by_type["factory_water"]:
        valid_action = True
        # compute the cost of watering
        if valid_action:
            actions_by_type_validated["factory_water"].append((factory, water_action))

    return actions_by_type_validated
