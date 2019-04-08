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
gc.queue_research(bc.UnitType.Knight)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Ranger)

my_team = gc.team()

guardList = []
gathererList = []
builderList = []
nearest_enemy_location = None


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
        if unit.unit_type == bc.UnitType.Knight:
            if location.is_on_map():
                nearby = gc.sense_nearby_units(location.map_location(), unit.vision_range)
                if gc.is_javelin_ready(unit.id):
                    for other in nearby:
                        if other.team != my_team and gc.can_javelin(unit.id, other.id):
                            print('attacked a thing!')
                            gc.javelin(unit.id, other.id)
                            return "ability used"

        if unit.unit_type == bc.UnitType.Ranger:
            if location.is_on_map():
                nearby = gc.sense_nearby_units(location.map_location(), unit.vision_range)
                if gc.is_begin_snipe_ready(unit.id):
                    for other in nearby:
                        if other.team != my_team and gc.can_begin_snipe(unit.id, other.location.map_location()):
                            print('attacked a thing!')
                            gc.begin_snipe(unit.id, other.location.map_location())
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

        if unit.unit_type == bc.UnitType.Healer:
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
                        d = unit.location.map_location().direction_to(other.location.map_location())
                        if gc.can_move(unit.id, d):
                            print('attacked a thing!')
                            gc.move_robot(unit.id, d)
                            return True
        return False

#This function takes in a unit and a location, it will see if there are any units around it that
# if there are, it will return the map_location of the first enemy found.
def sense_opposition(location, unit):
        if location.is_on_map():
            if location.is_in_garrison() or location.is_in_space():
                return nearest_enemy_location
            nearby = gc.sense_nearby_units(location.map_location(), unit.vision_range)
            if gc.is_move_ready(unit.id):
                for other in nearby:
                    if other.team != my_team:
                        return other.location.map_location()
        return nearest_enemy_location

#This function takes in a unit and a location, it will see if there are any units around it that
# if there are, it will return the map_location of the first enemy found.
def sense_opposition_factories(location, unit):
        if location.is_on_map():
            if location.is_in_garrison() or location.is_in_space():
                return nearest_enemy_location
            nearby = gc.sense_nearby_units_by_type(location.map_location(), unit.vision_range, bc.UnitType.Factory)
            if gc.is_move_ready(unit.id):
                for other in nearby:
                    if other.team != my_team:
                        return other.location.map_location()
        return nearest_enemy_location
       

def move_toward_location(location, unit, destination):
        
        if location.is_on_map():
            if gc.is_move_ready(unit.id):
                d = unit.location.map_location().direction_to(destination)
                if gc.can_move(unit.id, d):
                    gc.move_robot(unit.id, d)
                    return "moved toward destination"

        return "No move possible"

def try_to_harvest(location, unit):
    
    for d in directions:
        if gc.can_harvest(unit.id, d):
            gc.harvest(unit.id, d)
            return "Harvested"
    return "nothing to harvest"

def move_random(unit, attempts):
    if gc.is_move_ready(unit.id):
        d = random.choice(directions)
        if gc.can_move(unit.id, d):
            gc.move_robot(unit.id, d)
            return "moved"
        elif attempts <= 4:
            move_random(unit, attempts + 1)
        else:
            return "move timed out"

#move_and_expand is a method taken from https://github.com/AnPelec/Battlecode-2018/blob/master/Project%20Achilles/run.py
#changes were made to add more explosive exploration the later the game gets, while keeping it easy and grouped(ish) in the early game
def move_and_expand(unit, expand):
	# makes the robot move to the least crowded square
	# hoping that this is expanding the crowd
	moves = []
	
	location = unit.location
	for temp in range(9):
		dir = bc.Direction(temp)
		# center is direction 8 so it will always be last
		try:
			new_location = (location.map_location()).add(dir)
			expanding = expand
			if gc.round() > 100:
                            expanding = random.randint(1, expand)
			nearby_units = gc.sense_nearby_units_by_team(new_location, expanding, my_team)
			moves.append((len(nearby_units), temp))
		except Exception as e:
			print('Error:', e)
			# use this to show where the error was
			traceback.print_exc()			
				
	moves.sort()
	for tup in moves:
		if gc.is_move_ready(unit.id) and gc.can_move(unit.id, bc.Direction(tup[1])):
			gc.move_robot(unit.id, bc.Direction(tup[1]))
			print('Moved successfully!')
			continue

while True:
    # We only support Python 3, which means brackets around print()
    print('pyround:', gc.round(), 'time left:', gc.get_time_left_ms(), 'ms')
    expansion = 1
    if gc.round() > 299 and gc.round()%100 == 0:
        expansion = expansion + 2
    # frequent try/catches are a good idea
    try:
        for unit in gc.my_units():

            if gc.round() <= 1:
                if unit.unit_type == bc.UnitType.Worker:
                    nearest_enemy_location = unit.location.map_location()

            location = unit.location
            nearest_enemy_location = sense_opposition(location, unit)

            if unit.unit_type == bc.UnitType.Knight or unit.unit_type == bc.UnitType.Mage or unit.unit_type == bc.UnitType.Ranger:
                if location.is_in_garrison() or location.is_in_space():
                    continue
                useAbilityIfCan(location, unit)
                attackIfCan(location, unit)
                if move_to_engage(location, unit):
                    continue
                if (nearest_enemy_location != location.map_location()):
                    move_toward_location(location, unit, nearest_enemy_location)
                #move_random(unit, 0)
                move_and_expand(unit, expansion)

            if gc.round() <= 30:

                if unit.unit_type == bc.UnitType.Worker:
                    for d in directions:
                            try_to_harvest(unit.location, unit)
                            if gc.can_replicate(unit.id, d):
                                gc.replicate(unit.id, d)
                                continue
                    move_random(unit, 0)
                    #move_and_expand(unit, 2)


            elif gc.round() <= 195:

                if unit.unit_type == bc.UnitType.Worker:
                    for d in directions:
                        if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
                            gc.blueprint(unit.id, bc.UnitType.Factory, d)
                        # and if that fails, try to move
                        elif location.is_on_map():
                                nearby = gc.sense_nearby_units_by_type(location.map_location(), unit.vision_range, bc.UnitType.Factory)
                                for other in nearby:
                                    if gc.can_build(unit.id, other.id) and other.structure_is_built() == False:
                                        gc.build(unit.id, other.id)
                                        print('built a factory!')
                                        # move onto the next unit
                                        continue
                                    elif other.structure_is_built() == False:
                                        d = unit.location.map_location().direction_to(other.location.map_location())
                                        if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
                                            gc.move_robot(unit.id, d)
                                            continue                                   
                        else: 
                            try_to_harvest(unit.location, unit)
                            #move_random(unit, 0)
                            move_and_expand(unit, expansion + 1)

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

            elif gc.round() <= 200:

                if unit.unit_type == bc.UnitType.Worker:
                    for d in directions:
                        if gc.karbonite() > bc.UnitType.Rocket.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Rocket, d):
                            gc.blueprint(unit.id, bc.UnitType.Rocket, d)
                        # and if that fails, try to move
                        elif location.is_on_map():
                                nearby = gc.sense_nearby_units_by_type(location.map_location(), unit.vision_range, bc.UnitType.Rocket)
                                for other in nearby:
                                    if gc.can_build(unit.id, other.id) and other.structure_is_built() == False:
                                        gc.build(unit.id, other.id)
                                        print('built a rocket!')
                                        # move onto the next unit
                                        continue
                                    elif other.structure_is_built() == False:
                                        d = unit.location.map_location().direction_to(other.location.map_location())
                                        if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
                                            gc.move_robot(unit.id, d)
                                            continue                                   
                        else: 
                            try_to_harvest(unit.location, unit)
                            #move_random(unit, 0)
                            move_and_expand(unit, expansion + 2)

                if unit.unit_type == bc.UnitType.Factory:
                    garrison = unit.structure_garrison()
                    if len(garrison) > 0:
                        d = random.choice(directions)
                        if gc.can_unload(unit.id, d):
                            print('unloaded a unit!')
                            gc.unload(unit.id, d)
                            guardList.append(unit.id)
                            continue
                    elif gc.can_produce_robot(unit.id, bc.UnitType.Ranger):
                        gc.produce_robot(unit.id, bc.UnitType.Ranger)
                        print('produced a Ranger!')
                        continue
            else: 
                if unit.unit_type == bc.UnitType.Worker:
                    for d in directions:
                        try_to_harvest(unit.location, unit)
                        move_and_expand(unit, expansion + 5)
                        #this was random move
                
                if unit.unit_type == bc.UnitType.Factory:
                    garrison = unit.structure_garrison()
                    if len(garrison) > 0:
                        d = random.choice(directions)
                        if gc.can_unload(unit.id, d):
                            print('unloaded a unit!')
                            gc.unload(unit.id, d)
                            guardList.append(unit.id)
                            continue
                    elif gc.can_produce_robot(unit.id, bc.UnitType.Ranger):
                        gc.produce_robot(unit.id, bc.UnitType.Ranger)
                        print('produced a Ranger!')
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
	

	
