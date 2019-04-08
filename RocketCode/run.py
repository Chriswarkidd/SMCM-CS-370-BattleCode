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

#random.seed(6137)


gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Knight)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Knight)


my_team = gc.team()

guardList = []
gathererList = []
builderList = []
nearest_enemy_location_earth = None
nearest_enemy_location_mars = None
reached_mars = False

marsLocations = []
initialMars = gc.starting_map(bc.Planet.Mars)


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
def sense_opposition(location, unit, current_nearest_enemy_location):
        if location.is_on_map():
            if location.is_in_garrison() or location.is_in_space():
                return current_nearest_enemy_location
            nearby = gc.sense_nearby_units(location.map_location(), unit.vision_range)
            if gc.is_move_ready(unit.id):
                for other in nearby:
                    if other.team != my_team:
                        return other.location.map_location()
        return current_nearest_enemy_location

#This function takes in a unit and a location, it will see if there are any units around it that
# if there are, it will return the map_location of the first enemy found.
def sense_opposition_factories(location, unit, current_nearest_enemy_location):
        if location.is_on_map():
            if location.is_in_garrison() or location.is_in_space():
                return current_nearest_enemy_location
            nearby = gc.sense_nearby_units_by_type(location.map_location(), unit.vision_range, bc.UnitType.Factory)
            if gc.is_move_ready(unit.id):
                for other in nearby:
                    if other.team != my_team:
                        return other.location.map_location()
        return current_nearest_enemy_location
       

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
#Edits were(or will be) made to the code to handle walls during exploration 
def move_and_expand(unit):
	# makes the robot move to the least crowded square
    # hoping that this is expanding the crowd
    
    moves = []
    location = unit.location
    if location.is_in_garrison() or location.is_in_space():
        return
    for temp in range(9):
        dir = bc.Direction(temp)
        # center is direction 8 so it will always be last
        try:
            new_location = (location.map_location()).add(dir)
            nearby_units = gc.sense_nearby_units_by_team(new_location, 2, my_team)
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

#Finds and returns the dimentions of a planet
#Idea from https://github.com/AnPelec/Battlecode-2018/blob/master/Project%20Achilles/run.py
def mapDimensions(planet):
    minCoor = 19
    maxCoor = 49
    coorX = 19
    coorY = 19
    
    planetMap = gc.starting_map(planet)
    
    while(minCoor <= maxCoor):
        median = (minCoor + maxCoor)//2
        checkSpot = bc.MapLocation(planet, median, 0)
        if planetMap.on_map(checkSpot):
            if coorX < median:
                coorX = median
            minCoor = median + 1
        else:
            maxCoor = median - 1
    
    minCoor = 19
    maxCoor = 49
    
    while(minCoor <= maxCoor):
        median = (minCoor + maxCoor)//2
        checkSpot = bc.MapLocation(planet, 0, median)
        if planetMap.on_map(checkSpot):
            if coorY < median:
                coorY = median
            minCoor = median + 1
        else:
            maxCoor = median - 1
            
    return(coorX,coorY)

(heightMars, widthMars) = mapDimensions(bc.Planet.Mars)

#Creates a list of coordinates of Mars which are free to land with Rockets
def free_spots_on_Mars():
    for i in range(heightMars+1):
        for j in range(widthMars+1):
            if (i,j) not in marsLocations:
                checkLoc = bc.MapLocation(bc.Planet.Mars, i, j)
                try:
                    if initialMars.is_passable_terrain_at(checkLoc):
                        marsLocations.append((i,j))
                except Exception as e:
                    print(i,j)
                    print("Error:",e)
                    traceback.print_exc()

#Gets a random location's coordinates from marsLocations (spots on Mars that are free)                    
def getMarsLocation(unit):
    randLoc = random.choice(marsLocations)
    marsLocations.remove(randLoc)
    return bc.MapLocation(bc.Planet.Mars,randLoc[0],randLoc[1])

#Logic for unit movement on earth
#This method takes in the unit who's turn it currently is, and determines the best move for it at the current turn.
def unit_on_earth(unit):
    global nearest_enemy_location_earth

    location = unit.location
    
    if gc.round() <= 1:
        if unit.unit_type == bc.UnitType.Worker:
            nearest_enemy_location_earth = unit.location.map_location()

    nearest_enemy_location_earth = sense_opposition(location, unit, nearest_enemy_location_earth)
    if unit.unit_type == bc.UnitType.Knight or unit.unit_type == bc.UnitType.Mage or unit.unit_type == bc.UnitType.Ranger:
        if location.is_in_garrison() or location.is_in_space():
            return
        useAbilityIfCan(location, unit)
        attackIfCan(location, unit)
        if move_to_engage(location, unit):
            return
        if (nearest_enemy_location_earth != location.map_location()):
            move_toward_location(location, unit, nearest_enemy_location_earth)
            #move_random(unit, 0)
            move_and_expand(unit)

    if gc.round() <= 30:

        if unit.unit_type == bc.UnitType.Worker:
            for d in directions:
                    try_to_harvest(unit.location, unit)
                    if gc.can_replicate(unit.id, d):
                        gc.replicate(unit.id, d)
                        continue
            #move_random(unit, 0)
            move_and_expand(unit)


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
                    move_and_expand(unit)

        if unit.unit_type == bc.UnitType.Factory:
            garrison = unit.structure_garrison()
            if len(garrison) > 0:
                d = random.choice(directions)
                if gc.can_unload(unit.id, d):
                    print('unloaded a Knight!')
                    gc.unload(unit.id, d)
                    guardList.append(unit.id)
                    return
            elif gc.can_produce_robot(unit.id, bc.UnitType.Knight):
                gc.produce_robot(unit.id, bc.UnitType.Knight)
                print('produced a Knight!')
                return

    elif gc.round() <= 350:

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
                    move_and_expand(unit)

        if unit.unit_type == bc.UnitType.Factory:
            garrison = unit.structure_garrison()
            if len(garrison) > 0:
                d = random.choice(directions)
                if gc.can_unload(unit.id, d):
                    print('unloaded a unit!')
                    gc.unload(unit.id, d)
                    guardList.append(unit.id)
                    return
            elif gc.can_produce_robot(unit.id, bc.UnitType.Ranger):
                gc.produce_robot(unit.id, bc.UnitType.Ranger)
                print('produced a Ranger!')
                return
                        
    else: 
        if unit.unit_type == bc.UnitType.Rocket:
            nearby = gc.sense_nearby_units(unit.location.map_location(),2)
            garrison = unit.structure_garrison()
                    
            if location.is_on_planet(bc.Planet.Mars):
                if len(garrison) > 0:
                    for d in directions:
                        if gc.can_unload(unit.id,d):
                            gc.unload(unit.id,d)
                                    
            if location.is_on_planet(bc.Planet.Earth):
                if len(garrison) >= 5:
                    landLoc = getMarsLocation(unit)
                    if gc.can_launch_rocket(unit.id, landLoc):
                        gc.launch_rocket(unit.id,landLoc)
                        print("Launched rocket")

                for other in nearby:
                    garrison = unit.structure_garrison()
                    if gc.can_load(unit.id, other.id) and len(garrison) < 9:
                        gc.load(unit.id, other.id)
                        print("Unit loaded into rocket")
                    
                    
        if unit.unit_type == bc.UnitType.Worker:
            for d in directions:
                try_to_harvest(unit.location, unit)
                move_and_expand(unit)
                #this was random move
                
        if unit.unit_type == bc.UnitType.Factory:
            garrison = unit.structure_garrison()
            if len(garrison) > 0:
                d = random.choice(directions)
                if gc.can_unload(unit.id, d):
                    print('unloaded a unit!')
                    gc.unload(unit.id, d)
                    guardList.append(unit.id)
                    return
            elif gc.can_produce_robot(unit.id, bc.UnitType.Ranger):
                gc.produce_robot(unit.id, bc.UnitType.Ranger)
                print('produced a Ranger!')
                return

#Logic for unit movement on mars
#This method takes in the unit who's turn it currently is, and determines the best move for it at the current turn.
def unit_on_mars(unit):
        global reached_mars
        global nearest_enemy_location_mars

        if reached_mars == False:
            reached_mars = True
            nearest_enemy_location_mars = unit.location.map_location()

        location = unit.location
        nearest_enemy_location_mars = sense_opposition(location, unit, nearest_enemy_location_mars)

        if unit.unit_type == bc.UnitType.Knight or unit.unit_type == bc.UnitType.Mage or unit.unit_type == bc.UnitType.Ranger:
            if location.is_in_garrison() or location.is_in_space():
                return
            useAbilityIfCan(location, unit)
            attackIfCan(location, unit)
            if move_to_engage(location, unit):
                return
            if (nearest_enemy_location_mars != location.map_location()):
                move_toward_location(location, unit, nearest_enemy_location_mars)
                #move_random(unit, 0)
                move_and_expand(unit)

        if unit.unit_type == bc.UnitType.Rocket:
            nearby = gc.sense_nearby_units(unit.location.map_location(),2)
            garrison = unit.structure_garrison()
                    
            if location.is_on_planet(bc.Planet.Mars):
                if len(garrison) > 0:
                    for d in directions:
                        if gc.can_unload(unit.id,d):
                            gc.unload(unit.id,d)
                                    
            if location.is_on_planet(bc.Planet.Earth):
                if len(garrison) == 8:
                    landLoc = getMarsLocation(unit)
                    if gc.can_launch_rocket(unit.id, landLoc):
                        gc.launch_rocket(unit.id,landLoc)
                        print("Launched rocket")

                for other in nearby:
                    garrison = unit.structure_garrison()
                    if gc.can_load(unit.id, other.id) and len(garrison) < 9:
                        gc.load(unit.id, other.id)
                        print("Unit loaded into rocket")
                    
                    
        if unit.unit_type == bc.UnitType.Worker:
            if gc.karbonite() >= 60:     
                for d in directions:
                    if gc.can_replicate(unit.id, d):
                        gc.replicate(unit.id, d)
            else:
                for d in directions:
                    try_to_harvest(unit.location, unit)
                    move_and_expand(unit)
                    #this was random move
                
                    
free_spots_on_Mars()

while True:
    # We only support Python 3, which means brackets around print()
    print('pyround:', gc.round(), 'time left:', gc.get_time_left_ms(), 'ms')

    # frequent try/catches are a good idea
    try:
        for unit in gc.my_units():
            if unit.location.is_on_planet(bc.Planet.Earth):
                unit_on_earth(unit)
            elif unit.location.is_on_planet(bc.Planet.Mars):
                unit_on_mars(unit)
            else:
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
	