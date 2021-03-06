from argparse import Namespace
from dataclasses import dataclass


def convert_dict_to_ns(x):
    if isinstance(x, dict):
        for k in x:
            x[k] = convert_dict_to_ns(x)
        return Namespace(x)


@dataclass
class UnitConfig:
    METAL_COST: int = 100
    POWER_COST: int = 500
    CARGO_SPACE: int = 1000
    BATTERY_CAPACITY: int = 1500
    CHARGE: int = 1
    INIT_POWER: int = 50
    MOVE_COST: int = 1
    RUBBLE_MOVEMENT_COST: int = 1
    DIG_COST: int = 5
    DIG_RUBBLE_REMOVED: int = 1
    DIG_RESOURCE_GAIN: int = 2
    DIG_LICHEN_REMOVED: int = 10
    SELF_DESTRUCT_COST: int = 10
    RUBBLE_AFTER_DESTRUCTION: int = 1



@dataclass
class EnvConfig:
    ## various options that can be configured if needed


    ### Variable parameters that don't affect game logic much ###
    max_episode_length: int = 1000
    map_size: int = 64

    ### Constants ###
    # you can only ever transfer in/out 1000 as this is the max cargo space.
    max_transfer_amount = 10000 
    MAX_FACTORIES = 5
    CYCLE_LENGTH = 50
    DAY_LENGTH = 30
    UNIT_ACTION_QUEUE_SIZE = 10 # when set to 1, then no action queue is used
    UNITS_CONTROLLED = 20 # when set to -1, all units can be controlled at once
    MAX_RUBBLE = 100
    FACTORY_RUBBLE_AFTER_DESTRUCTION = 50

    #### LICHEN ####
    MIN_LICHEN_TO_SPREAD = 20
    LICHEN_LOST_WITHOUT_WATER = 1
    LICHEN_GAINED_WITH_WATER = 1
    LICHEN_WATERING_COST_FACTOR = 10

    #### Bidding System ####
    BIDDING_SYSTEM: bool = True

    #### Factores ####
    FACTORY_PROCESSING_RATE_WATER: int = 50
    ICE_WATER_RATIO: int = 10
    FACTORY_PROCESSING_RATE_METAL: int = 50
    ORE_METAL_RATIO: int = 10
    FACTORY_CHARGE: int = 50
    FACTORY_WATER_CONSUMPTION: int = 1


    #### Units ####
    # TODO FILL IN POWER COSTS FOR ACTIONS
    ROBOTS = dict(
        LIGHT=UnitConfig(
            METAL_COST=10, POWER_COST=50, INIT_POWER=50, CARGO_SPACE=100, BATTERY_CAPACITY=50, CHARGE=1, MOVE_COST=1, RUBBLE_MOVEMENT_COST=1,
            DIG_COST=5,
            SELF_DESTRUCT_COST=5,
            DIG_RUBBLE_REMOVED=1,
            DIG_RESOURCE_GAIN=2,
            DIG_LICHEN_REMOVED=10,
            RUBBLE_AFTER_DESTRUCTION=1,
        ),
        
        HEAVY=UnitConfig(
            METAL_COST=100, POWER_COST=500, INIT_POWER=500, CARGO_SPACE=1000, BATTERY_CAPACITY=1500, CHARGE=10, MOVE_COST=20, RUBBLE_MOVEMENT_COST=5,
            DIG_COST=100,
            SELF_DESTRUCT_COST=100,
            DIG_RUBBLE_REMOVED=10,
            DIG_RESOURCE_GAIN=20,
            DIG_LICHEN_REMOVED=100,
            RUBBLE_AFTER_DESTRUCTION=10,
        ),
    )

    #### Map Generation ####
    # TODO

    #### Weather ####
    WEATHER_ID_TO_NAME = {
        0: "NONE",
        1: "MARS_QUAKE",
        1: "COLD_SNAP",
        2: "DUST_STORM",
        3: "SOLAR_FLARE",
    }
    WEATHER = dict(
        MARS_QUAKE=dict(
            # amount of rubble generated under each robot
            RUBBLE=dict(LIGHT=1, HEAVY=10)
        ),
        COLD_SNAP=dict(
            # power multiplier required per robot action. 2 -> requires 2x as much power to execute the same action
            POWER_CONSUMPTION=2
        ),
        DUST_STORM=dict(
            # power multiplier required per robot action. .5 -> requires .5x as much power to execute the same action
            POWER_CONSUMPTION=0.5
        ),
        SOLAR_FLARE=dict(
            # power gain multiplier. 2 -> gain 2x as much power per turn
            POWER_GAIN=2
        ),
    )