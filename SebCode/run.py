import battlecode as bc
import random
import sys
import traceback
import time

import os
print(os.getcwd())

print("pystarting")

# A GameController is the main type that you talk to the game with.
# Its constructor will connect to a running game.
gc = bc.GameController()
directions = list(bc.Direction)

print("pystarted")

random.seed(6137)

gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Mage)

my_team = gc.team()

guardList = []
gathererList = []
builderList = []


#This function takes in a location and a unit and will automatically
# check to see if the unit can attack an opposing team unit around it. if it can, it attacks the closest to itself.

def attackIfCan(location, unit):
    if location.is_on_map():
        nearby = gc.sense_nearby_units(location.map_location(), unit.vision_range)
        if gc.is_attack_ready(unit.id):
            for other in nearby:
                if other.team != my_team and gc.can_attack(unit.id, other.id):
                    print('attacked a thing!')
                    gc.attack(unit.id, other.id)
                    return "attack"


#This function takes in a location and a unit and will automatically
# check to see if the unit can heal an ally unit around it. if it can, it heals the closest ally.

def healIfCan(location, unit):
    if location.is_on_map():
        nearby = gc.sense_nearby_units(location.map_location(), unit.vision_range)
        if gc.is_heal_ready(unit.id):
            for other in nearby:
                if other.team == my_team and gc.can_heal(unit.id, other.id):
                    print('healed a thing!')
                    gc.heal(unit.id, other.id)
                    return "heal"


#This function takes in a location and a unit and will automatically
# try to use it on the closest unit to it. It will check to see what kind of unit
# is being passed to it, and will check the right ability for said unit.
# returns ability used if the ability was able to be used,
# and could not use ability if it couldn't.

def useAbilityIfCan(location, unit):
    if unit.is_ability_unlocked():
        if unit.unit_type == gc.UnitType.Knight:
            if location.is_on_map():
                nearby = gc.sense_nearby_units(location.map_location(), unit.vision_range)
                if gc.is_javelin_ready(unit.id):
                    for other in nearby:
                        if other.team != my_team and gc.can_javelin(unit.id, other.id):
                            print('attacked a thing!')
                            gc.javelin(unit.id, other.id)
                            return "ability used"

        if unit.unit_type == gc.UnitType.Ranger:
            if location.is_on_map():
                nearby = gc.sense_nearby_units(location.map_location(), unit.vision_range)
                if gc.is_begin_snipe_ready(unit.id):
                    for other in nearby:
                        if other.team != my_team and gc.can_begin_snipe(unit.id, other.location):
                            print('attacked a thing!')
                            gc.begin_snipe(unit.id, other.location)
                            return "ability used"

        #need to remove this as blink requires a location.
        # if unit.unit_type == gc.UnitType.Mage:
        #     if location.is_on_map():
        #         nearby = gc.sense_nearby_units(location.map_location(), 2)
        #         if gc.is_blink_ready(unit.id):
        #             for other in nearby:
        #                 if other.team != my_team and gc.can_blink(unit.id, other.id):
        #                     print('attacked a thing!')
        #                     gc.blink(unit.id, other.id)
        #                     return "ability used"

        if unit.unit_type == gc.UnitType.Healer:
            if location.is_on_map():
                nearby = gc.sense_nearby_units(location.map_location(), unit.vision_range)
                if gc.is_overcharge_ready(unit.id):
                    for other in nearby:
                        if other.team != my_team  and gc.can_overcharge(unit.id, other.id):
                            print('attacked a thing!')
                            gc.overcharge(unit.id, other.id)
                            return "ability used"

    return "could not use ability"

#This function takes in a unit and a location, it will see if there are any units around it that
# if there are, it will attempt to move toward the closest opposing unit found.
def move_to_engage(location, unit):
        if location.is_on_map():
            nearby = gc.sense_nearby_units(location.map_location(), unit.vision_range)
            if gc.is_move_ready(unit.id):
                for other in nearby:
                    if other.team != my_team:
                        d = gc.direction_to(other.location)
                        if gc.can_move(unit.id, d):
                            print('attacked a thing!')
                            gc.move(unit.id, d)
                            return "moved toward opposition"
        return "No move possible"

def try_to_harvest(location, unit):
    
    for d in directions:
        if gc.can_harvest(unit.id, d):
            gc.harvest(unit.id, d)
            return "Harvested"
    return "nothing to harvest"

def move_random(unit, attempts):
    if unit.is_move_ready():
        d = random.choice(directions)
        if gc.can_move(unit.id, d):
            gc.move(unit.id, d)
            return "moved"
        elif attempts <= 4:
            move_random(unit, attempts + 1)
        else:
            return "move timed out"



while True:
    # We only support Python 3, which means brackets around print()
    print('pyround:', gc.round(), 'time left:', gc.get_time_left_ms(), 'ms')

    # frequent try/catches are a good idea
    try:
        for unit in gc.my_units():

            location = unit.location
            if unit.unit_type == bc.UnitType.Knight or unit.unit_type == bc.UnitType.Mage or unit.unit_type == bc.UnitType.Ranger:
                attackIfCan(location, unit)
                move_to_engage(location, unit)
                move_random(unit, 0)                

            if gc.round() <= 800:

                if unit.unit_type == bc.UnitType.Worker:
                    for d in directions:
                        if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
                            gc.blueprint(unit.id, bc.UnitType.Factory, d)
                        # and if that fails, try to move
                        elif location.is_on_map():
                                nearby = gc.sense_nearby_units(location.map_location(), 2)
                                for other in nearby:
                                    if gc.can_build(unit.id, other.id):
                                        gc.build(unit.id, other.id)
                                        print('built a factory!')
                                        # move onto the next unit
                                        continue
                        else: 
                            try_to_harvest(unit.location, unit)
                            move_random(unit, 0)
                            if gc.can_replicate(unit.id, d):
                                gc.replicate(unit.id, d)
                                continue

                if unit.unit_type == bc.UnitType.Factory:
                    garrison = unit.structure_garrison()
                    if len(garrison) > 0:
                        d = random.choice(directions)
                        if gc.can_unload(unit.id, d):
                            print('unloaded a Knight!')
                            gc.unload(unit.id, d)
                            guardList.append(unit.id)
                            continue
                    elif gc.can_produce_robot(unit.id, bc.UnitType.Knight):
                        gc.produce_robot(unit.id, bc.UnitType.Knight)
                        print('produced a Knight!')
                        continue

    except Exception as e:
        print('Error:', e)
        # use this to show where the error was
        traceback.print_exc()

    # send the actions we've performed, and wait for our next turn.
    gc.next_turn()

    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()
    sys.stderr.flush()

