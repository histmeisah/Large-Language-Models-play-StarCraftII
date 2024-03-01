"""
Bot name: CreepyBot
Bot author: BuRny (or BurnySc2)
Bot version: v1.0
Bot date (YYYY-MM-DD): 2018-06-17
This bot was made by BuRny for the "KOTN: Probots" tournament
https://eschamp.challonge.com/Probot1
Homepage: https://github.com/BurnySc2
"""

# pylint: disable=E0602
"""ylint: disable=E0001
ylint: disable=C, E0602, W0612, W0702, W0621, R0912, R0915, W0603
add a "p"
"""

import random, json, time
from collections import OrderedDict

# download maps from https://github.com/Blizzard/s2client-proto#map-packs

# import os # load text file
import math  # distance calculation
# import re # parsing build orders from text file
from sc2.unit import Unit
from sc2.units import Units
from sc2.data import race_gas, race_worker, race_townhalls, ActionResult, Attribute, Race

import sc2  # pip install sc2
from sc2.data import Race, Difficulty
from sc2.constants import *  # for autocomplete
from sc2.ids.unit_typeid import *
from sc2.ids.ability_id import *
from sc2.position import Point2, Point3

from sc2.player import Bot, Computer, Human


# from zerg.zerg_rush import ZergRushBot
# from protoss.cannon_rush import CannonRushBot

class ManageThreats(object):
    def __init__(self, client, game_data):
        # usage:
        # self.defenseGroup = ManageThreats(self._client, self._game_data)

        # class data:
        self._client = client
        self._game_data = game_data
        self.threats = {}
        self.assignedUnitsTags = set()
        self.unassignedUnitsTags = set()

        # customizable parameters upon instance creation
        self.retreatLocations = None  # retreat to the nearest location if hp percentage reached below "self.retreatWhenHp"
        self.retreatWhenHp = 0  # make a unit micro and retreat when this HP percentage is reached

        self.attackLocations = None  # attack any of these locations if there are no threats

        self.treatThreatsAsAllies = False  # if True, will mark threats as allies and tries to protect them instead
        # self.defendRange = 5 # if a unit is in range within 5 of any of the threats, attack them

        self.clumpUpEnabled = False
        self.clumpDistance = 7  # not yet tested - sums up the distance to the center of the unit-ball, if too far away and not engaged with enemy: will make them clump up before engaging again

        self.maxAssignedPerUnit = 10  # the maximum number of units that can be assigned per enemy unit / threat

        self.leader = None  # will be automatically assigned if "self.attackLocations" is not None

        availableModes = ["closest", "distributeEqually"]  # todo: focus fire
        self.mode = "closest"

    def addThreat(self, enemies):
        if isinstance(enemies, Units):
            for unit in enemies:
                self.addThreat(unit)
        elif isinstance(enemies, Unit):
            self.addThreat(enemies.tag)
        elif isinstance(enemies, int):
            if enemies not in self.threats:
                self.threats[enemies] = set()

    def clearThreats(self, threats=None):
        # accepts None, integer or iterable (with tags) as argument
        if threats is None:
            threats = self.threats
        elif isinstance(threats, int):
            threats = set([threats])

            # check for dead threats:
        for threat in threats:
            if threat in self.threats:
                unitsThatNowHaveNoTarget = self.threats.pop(threat)  # remove and return the set
                self.assignedUnitsTags -= unitsThatNowHaveNoTarget
                self.unassignedUnitsTags |= unitsThatNowHaveNoTarget  # append the tags to unassignedUnits

    def addDefense(self, myUnits):
        if isinstance(myUnits, Units):
            for unit in myUnits:
                self.addDefense(unit)
        elif isinstance(myUnits, Unit):
            self.addDefense(myUnits.tag)
        elif isinstance(myUnits, int):
            if myUnits not in self.assignedUnitsTags:
                self.unassignedUnitsTags.add(myUnits)

    def removeDefense(self, myUnits):
        if isinstance(myUnits, Units):
            for unit in myUnits:
                self.removeDefense(unit)
        elif isinstance(myUnits, Unit):
            self.removeDefense(myUnits.tag)
        elif isinstance(myUnits, int):
            self.assignedUnitsTags.discard(myUnits)
            self.unassignedUnitsTags.discard(myUnits)
            for key in self.threats.keys():
                self.threats[key].discard(myUnits)

    def setRetreatLocations(self, locations, removePreviousLocations=False):
        if self.retreatLocations is None or removePreviousLocations:
            self.retreatLocations = []
        if isinstance(locations, list):
            # we assume this is a list of points or units
            for location in locations:
                self.retreatLocations.append(location.position.to2)
        else:
            self.retreatLocations.append(location.position.to2)

    def unassignUnit(self, myUnit):
        for key, value in self.threats.items():
            # if myUnit.tag in value:
            value.discard(myUnit.tag)
            # break
        self.unassignedUnitsTags.add(myUnit.tag)
        self.assignedUnitsTags.discard(myUnit.tag)

    def getThreatTags(self):
        """Returns a set of unit tags that are considered as threats

        Returns:
            set -- set of enemy unit tags
        """
        return set(self.threats.keys())

    def getMyUnitTags(self):
        """Returns a set of tags that are in this group

        Returns:
            set -- set of my unit tags
        """
        return self.assignedUnitsTags | self.unassignedUnitsTags

    def centerOfUnits(self, units):
        if isinstance(units, list):
            units = Units(units, self._game_data)
        assert isinstance(units, Units)
        assert units.exists
        if len(units) == 1:
            return units[0].position.to2
        coordX = sum([unit.position.x for unit in units]) / len(units)
        coordY = sum([unit.position.y for unit in units]) / len(units)
        return Point2((coordX, coordY))

    async def update(self, myUnitsFromState, enemyUnitsFromState, enemyStartLocations, iteration):
        # example usage: attackgroup1.update(self.units, self.known_enemy_units, self.enemy_start_locations, iteration)
        assignedUnits = myUnitsFromState.filter(lambda x: x.tag in self.assignedUnitsTags)
        unassignedUnits = myUnitsFromState.filter(lambda x: x.tag in self.unassignedUnitsTags)
        if not self.treatThreatsAsAllies:
            threats = enemyUnitsFromState.filter(lambda x: x.tag in self.threats)
        else:
            threats = myUnitsFromState.filter(lambda x: x.tag in self.threats)
        aliveThreatTags = {x.tag for x in threats}
        deadThreatTags = {k for k in self.threats.keys() if k not in aliveThreatTags}

        # check for dead threats:
        self.clearThreats(threats=deadThreatTags)

        # check for dead units:
        self.assignedUnitsTags = {x.tag for x in assignedUnits}
        self.unassignedUnitsTags = {x.tag for x in unassignedUnits}
        # update dead assigned units inside the dicts
        for key in self.threats.keys():
            values = self.threats[key]
            self.threats[key] = {x for x in values if x in self.assignedUnitsTags}

        # if self.treatThreatsAsAllies:
        #     print("supportgroup threat tags:", self.getThreatTags())
        #     print("supportgroup existing threats:", threats)
        #     for k,v in self.threats.items():
        #         print(k,v)
        #     print("supportgroup units unassigned:", unassignedUnits)
        #     print("supportgroup units assigned:", assignedUnits)

        canAttackAir = [QUEEN, CORRUPTOR]
        canAttackGround = [ROACH, BROODLORD, QUEEN, ZERGLING]

        recentlyAssigned = set()
        # assign unassigned units a threat # TODO: attackmove on the position or attack the unit?
        for unassignedUnit in unassignedUnits.filter(lambda x: x.health / x.health_max > self.retreatWhenHp):
            # if self.retreatLocations is not None and unassignedUnit.health / unassignedUnit.health_max < self.retreatWhenHp:
            #     continue
            # if len(unassignedUnit.orders) == 1 and unassignedUnit.orders[0].ability.id in [AbilityId.ATTACK]:
            #     continue
            if not threats.exists:
                if self.attackLocations is not None and unassignedUnit.is_idle:
                    await self.do(unassignedUnit.move(random.choice(self.attackLocations)))
            else:
                # filters threats if current looped unit can attack air (and enemy is flying) or can attack ground (and enemy is ground unit)
                # also checks if current unit is in threats at all and if the maxAssigned is not overstepped
                filteredThreats = threats.filter(
                    lambda x: x.tag in self.threats and len(self.threats[x.tag]) < self.maxAssignedPerUnit and (
                                (x.is_flying and unassignedUnit.type_id in canAttackAir) or (
                                    not x.is_flying and unassignedUnit.type_id in canAttackGround)))

                chosenTarget = None
                if not filteredThreats.exists and threats.exists:
                    chosenTarget = threats.random  # for units like viper which cant attack, they will just amove there
                elif self.mode == "closest":
                    # TODO: only attack units that this unit can actually attack, like dont assign air if it cant shoot up
                    if filteredThreats.exists:
                        # only assign targets if there are any threats left
                        chosenTarget = filteredThreats.closest_to(unassignedUnit)
                elif self.mode == "distributeEqually":
                    threatTagWithLeastAssigned = min([[x, len(y)] for x, y in self.threats.items()], key=lambda q: q[1])
                    # if self.treatThreatsAsAllies:
                    #     print("supportgroup least assigned", threatTagWithLeastAssigned)
                    # if self.treatThreatsAsAllies:
                    #     print("supportgroup filtered threats", filteredThreats)
                    if filteredThreats.exists:
                        # only assign target if there are any threats remaining that have no assigned allied units
                        chosenTarget = filteredThreats.find_by_tag(threatTagWithLeastAssigned[0])
                        # if self.treatThreatsAsAllies:
                        #     print("supportgroup chosen target", chosenTarget)
                else:
                    chosenTarget = random.choice(threats)

                if chosenTarget is not None:
                    # add unit to assigned target
                    self.unassignedUnitsTags.discard(unassignedUnit.tag)
                    self.assignedUnitsTags.add(unassignedUnit.tag)
                    self.threats[chosenTarget.tag].add(unassignedUnit.tag)
                    recentlyAssigned.add(unassignedUnit.tag)
                    # threats.remove(chosenTarget)
                    unassignedUnits.remove(unassignedUnit)
                    assignedUnits.append(unassignedUnit)
                    if unassignedUnit.distance_to(chosenTarget) > 3:
                        # amove towards target when we want to help allied units
                        await self.do(unassignedUnit.attack(chosenTarget.position))
                    break  # iterating over changing list

        # if self.treatThreatsAsAllies and len(recentlyAssigned) > 0:
        #     print("supportgroup recently assigned", recentlyAssigned)

        clumpedUnits = False
        if assignedUnits.exists and self.clumpUpEnabled:
            amountUnitsInDanger = [threats.closer_than(10, x).exists for x in assignedUnits].count(True)
            # print("wanting to clump up")
            if amountUnitsInDanger < assignedUnits.amount / 5:  # if only 10% are in danger, then its worth the risk to clump up again
                # make all units clump up more until trying to push / attack again
                center = self.centerOfUnits(assignedUnits)
                distanceSum = 0
                for u in assignedUnits:
                    distanceSum += u.distance_to(center)
                distanceSum /= assignedUnits.amount

                if distanceSum > self.clumpDistance:
                    clumpedUnits = True
                    for unit in assignedUnits:
                        await self.do(unit.attack(center))

        if not clumpedUnits:
            for unit in assignedUnits:
                if unit.tag in recentlyAssigned:
                    continue
                    # # move close to leader if he exists and if unit is far from leader
                # if self.attackLocations is not None \
                #     and leader is not None \
                #     and unit.tag != leader.tag \
                #     and (unit.is_idle or len(unit.orders) == 1 and unit.orders[0].ability.id in [AbilityId.MOVE]) \
                #     and unit.distance_to(leader) > self.clumpDistance:
                #     await self.do(unit.attack(leader.position))

                # if unit is idle or move commanding, move directly to target, if close to target, amove
                if unit.is_idle or len(unit.orders) == 1 and unit.orders[0].ability.id in [AbilityId.MOVE]:
                    assignedTargetTag = next((k for k, v in self.threats.items() if unit.tag in v), None)
                    if assignedTargetTag is not None:
                        assignedTarget = threats.find_by_tag(assignedTargetTag)
                        if assignedTarget is None:
                            self.unassignUnit(unit)
                        elif assignedTarget.distance_to(unit) <= 13 or threats.filter(
                                lambda x: x.distance_to(unit) < 13).exists:
                            await self.do(unit.attack(assignedTarget.position))
                        elif assignedTarget.distance_to(unit) > 13 and unit.is_idle and unit.tag != assignedTarget.tag:
                            await self.do(unit.attack(
                                unit.position.to2.towards(assignedTarget.position.to2, 20)))  # move follow command
                    else:
                        self.unassignUnit(unit)
            # # if unit.is_idle:
            # #     self.unassignUnit(unit)
            # elif len(unit.orders) == 1 and unit.orders[0].ability.id in [AbilityId.MOVE]:
            #     # make it amove again
            #     for key, value in self.threats.items():
            #         if unit.tag in value:
            #             assignedTargetTag = key
            #             assignedTarget = threats.find_by_tag(assignedTargetTag)
            #             if assignedTarget is None:
            #                 continue
            #                 # self.unassignUnit(unit)
            #             elif assignedTarget.distance_to(unit) <= 13:
            #                 await self.do(unit.attack(assignedTarget.position))
            #                 break
            #             # elif assignedTarget.distance_to(unit) > 13:
            #             #     await self.do(unit.move(assignedTarget))

        # move to retreatLocation when there are no threats or when a unit is low hp
        if self.retreatLocations is not None and not threats.exists and iteration % 20 == 0:
            for unit in unassignedUnits.idle:
                closestRetreatLocation = unit.position.to2.closest(self.retreatLocations)
                if unit.distance_to(closestRetreatLocation) > 10:
                    await self.do(unit.move(closestRetreatLocation))

        # move when low hp
        elif self.retreatLocations is not None and self.retreatWhenHp != 0:
            for unit in (assignedUnits | unassignedUnits).filter(
                    lambda x: x.health / x.health_max < self.retreatWhenHp):
                closestRetreatLocation = unit.position.to2.closest(self.retreatLocations)
                if unit.distance_to(closestRetreatLocation) > 6:
                    await self.do(unit.move(closestRetreatLocation))

    async def do(self, action):
        r = await self._client.actions(action, game_data=self._game_data)
        return r


class CreepyBot(sc2.BotAI):
    def __init__(self):
        self.reservedWorkers = []
        self.queensAssignedHatcheries = {}  # contains a list of queen: hatchery assignments (for injects)
        self.workerProductionEnabled = []
        self.armyProductionEnabled = []
        self.queenProductionEnabled = []
        self.haltRedistributeWorkers = False

        # following are default TRUE:
        self.enableCreepSpread = True
        self.enableInjects = True

        self.getLingSpeed = False

        self.enableMakingRoaches = True
        self.getRoachBurrowAndBurrow = True  # researches burrow and roach burrow move
        self.waitForRoachBurrowBeforeAttacking = True  # if this is True, set the above to True also

        self.enableLateGame = True
        self.waitForBroodlordsBeforeAttacking = False  # if this is True, set the above to True also
        self.allowedToResupplyAttackGroups = False

        # the bot will try to make corruptor in this ratio now
        self.corruptorRatioFactor = 3
        self.broodlordRatioFactor = 3
        self.viperRatioFactor = 1

        # required for overlord production
        self.larvaPerHatch = 1 / 11  # 1 larva every 11 secs
        self.larvaPerInject = 3 / 40  # 1 larva every 40 secs

        self.nextExpansionInfo = {
            # "workerTag": workerId,
            # "location": nextExpansionLocation,
        }

        self.opponentInfo = {
            "spawnLocation": None,  # for 4player maps
            "expansions": [],  # stores a list of Point2 objects of expansions
            "expansionsTags": set(),  # stores the expansions above as tags so we dont count them double
            "furthestAwayExpansion": None,
            # stores the expansion furthest away - important for spine crawler and pool placement
            "race": None,
            "armyTagsScouted": [],  # list of dicts with entries: {"tag": 123, "scoutTime": 15.6, "supply": 2}
            "armySupplyScouted": 0,
            "armySupplyScoutedClose": 0,
            "armySupplyVisible": 0,
            "scoutingUnitsNeeded": 0,
        }
        self.myDefendGroup = None
        self.myAttackGroup = None
        self.mySupportGroup = None

        self.droneLimit = 80  # how many drones to have at late game

        self.defendRangeToTownhalls = 30  # how close the enemy has to be before defenses are alerted

        self.priotizeFirstNQueens = 4
        self.totalQueenLimit = 6  # dont have to change it, instead change the two lines below to set the queen limit before/after GREATERSPIRE tech
        self.totalEarlyGameQueenLimit = 8
        self.totalLateGameQueenLimit = 25
        self.injectQueenLimit = 4  # how many queens will be injecting until we have a greater spire?
        self.stopMakingNewTumorsWhenAtCoverage = 0.3  # stops queens from putting down new tumors and save up transfuse energy
        self.creepTargetDistance = 15  # was 10
        self.creepTargetCountsAsReachedDistance = 10  # was 25

        self.creepSpreadInterval = 10
        self.injectInterval = 100
        self.workerTransferInterval = 10
        self.buildStuffInverval = 2  # was 4
        self.microInterval = 1  # was 3

        self.prepareStart2Ran = False

    async def _prepare_start2(self):
        # print("distance to closest mineral field:", self.state.mineral_field.closest_to(self.townhalls.random).distance_to(self.townhalls.random))
        # is about 6.0

        self.prepareStart2Ran = True
        # find start locations so creep tumors dont block it
        if self.enableCreepSpread:
            await self.findExactExpansionLocations()

        # split workers to closest mineral field
        if self.townhalls.exists:
            mfs = self.state.mineral_field.closer_than(10, self.townhalls.random)
            for drone in self.units(DRONE):
                await self.do(drone.gather(mfs.closest_to(drone)))

        # set amount of spawn locations
        self.opponentInfo["scoutingUnitsNeeded"] = len(self.enemy_start_locations)

        if self.townhalls.exists:
            self.opponentInfo["furthestAwayExpansion"] = self.townhalls.random.position.to2.closest(
                self.enemy_start_locations)

        # a = self.state.units.filter(lambda x: x.name == "DestructibleRockEx16x6")
        # print(a)
        # print(a.random)
        # print(vars(a.random))
        # print(a.random._type_data)
        # print(vars(a.random._type_data))
        # print(a.random._game_data)
        # print(vars(a.random._game_data))

    def getTimeInSeconds(self):
        # returns real time if game is played on "faster"
        return self.state.game_loop * 0.725 * (1 / 16)

    def getUnitInfo(self, unit, field="food_required"):
        # get various unit data, see list below
        # usage: getUnitInfo(ROACH, "mineral_cost")
        assert isinstance(unit, (Unit, UnitTypeId))
        if isinstance(unit, Unit):
            # unit = unit.type_id
            unit = unit._type_data._proto
        else:
            unit = self._game_data.units[unit.value]._proto
        # unit = self._game_data.units[unit.value]
        # print(vars(unit)) # uncomment to get the list below
        if hasattr(unit, field):
            return getattr(unit, field)
        else:
            return None
        """
        name: "Drone"
        available: true
        cargo_size: 1
        attributes: Light
        attributes: Biological
        movement_speed: 2.8125
        armor: 0.0
        weapons {
            type: Ground
            damage: 5.0
            attacks: 1
            range: 0.10009765625
            speed: 1.5
        }
        mineral_cost: 50
        vespene_cost: 0
        food_required: 1.0
        ability_id: 1342
        race: Zerg
        build_time: 272.0
        sight_range: 8.0
        """

    def convertWeaponInfo(self, info):
        types = {1: "ground", 2: "air", 3: "any"}
        if info is None:
            return None
        returnDict = {
            "type": types[info.type],
            "damage": info.damage,
            "attacks": info.attacks,
            "range": info.range,
            "speed": info.speed,
            "dps": info.damage * info.attacks / info.speed
        }
        if hasattr(info, "damage_bonus"):
            bonus = info.damage_bonus
            try:
                # TODO: try to get rid of try / except and change attribute to "light" or "armored" etc
                returnDict["bonusAttribute"] = bonus[0].attribute
                returnDict["bonusDamage"] = bonus[0].bonus
            except:
                pass
        return returnDict

    def getSpecificUnitInfo(self, unit, query="dps"):
        # usage: print(self.getSpecificUnitInfo(self.units(DRONE).random)[0]["dps"])
        if query == "dps":
            unitInfo = self.getUnitInfo(unit, "weapons")
            if unitInfo is None:
                return None, None
            weaponInfos = []
            for weapon in unitInfo:
                weaponInfos.append(self.convertWeaponInfo(weapon))
            if len(weaponInfos) == 0:
                return [{"dps": 0}]
            return weaponInfos

    def centerOfUnits(self, units):
        if isinstance(units, list):
            units = Units(units, self._game_data)
        assert isinstance(units, Units)
        assert units.exists
        if len(units) == 1:
            return units[0].position.to2
        coordX = sum([unit.position.x for unit in units]) / len(units)
        coordY = sum([unit.position.y for unit in units]) / len(units)
        return Point2((coordX, coordY))

    # def findUnitGroup(self, unit, unitsCloseTo, maxDistanceToOtherUnits=30, minSupply=0, excludeUnits=None):
    #     # group clustering https://mubaris.com/2017/10/01/kmeans-clustering-in-python/
    #     # actually this function is not really related to that algorithm

    #     # this function takes two required arguments
    #     # unit - a unit spotted, e.g. enemy unit closest to a friendly building
    #     # unitsCloseTo - a group of units, e.g. self.units(ROACH) | self.units(HYDRA)
    #     # or self.state.units.enemy.not_structure

    #     assert isinstance(unitsCloseTo, Units)
    #     if unitsCloseTo.amount == 0:
    #         return []

    #     unitGroup = unitsCloseTo.closer_than(maxDistanceToOtherUnits, unit.position)
    #     if excludeUnits != None:
    #         assert isinstance(excludeUnits, Units)
    #         unitGroup - excludeUnits
    #     if minSupply > 0:
    #         supply = sum([self.getUnitInfo(x, "food_required") for x in unitGroup])
    #         if minSupply > supply:
    #             return self.units(QUEEN).not_ready # empty units list, idk how to create an empty one :(
    #     return unitGroup

    # def unitsFromList(self, lst):
    #     assert isinstance(lst, list)
    #     if len(lst) == 0:
    #         # return self.units(QUEEN).not_ready
    #         return Units([], self._game_data)
    #     # elif len(lst) == 1:
    #     #     return lst[0]
    #     else:
    #         # returnUnits = self.units(QUEEN).not_ready
    #         returnUnits = Units([], self._game_data)
    #         for entry in lst:
    #             returnUnits = returnUnits | entry
    #         return returnUnits

    async def findExactExpansionLocations(self):
        # execute this on start, finds all expansions where creep tumors should not be build near
        self.exactExpansionLocations = []
        for loc in self.expansion_locations.keys():
            self.exactExpansionLocations.append(await self.find_placement(HATCHERY, loc, minDistanceToResources=5.5,
                                                                          placement_step=1))  # TODO: change mindistancetoresource so that a hatch still has room to be built

    async def assignWorkerRallyPoint(self):
        if hasattr(self, "hatcheryRallyPointsSet"):
            for hatch in self.townhalls:
                if hatch.tag not in self.hatcheryRallyPointsSet:
                    # abilities = await self.get_available_abilities(hatch)
                    # if RALLY_HATCHERY_WORKERS in abilities:
                    # rally workers to nearest mineral field
                    mf = self.state.mineral_field.closest_to(hatch.position.to2.offset(Point2((0, -3))))
                    err = await self.do(hatch(RALLY_WORKERS, mf))
                    if not err:
                        mfs = self.state.mineral_field.closer_than(10, hatch.position.to2)
                        if mfs.exists:
                            loc = self.centerOfUnits(mfs)
                            err = await self.do(hatch(RALLY_UNITS, loc))
                            if not err:
                                self.hatcheryRallyPointsSet[hatch.tag] = loc
        else:
            self.hatcheryRallyPointsSet = {}

    def assignQueen(self, maxAmountInjectQueens=5):
        # # list of all alive queens and bases, will be used for injecting
        if not hasattr(self, "queensAssignedHatcheries"):
            self.queensAssignedHatcheries = {}

        if maxAmountInjectQueens == 0:
            self.queensAssignedHatcheries = {}

        # if queen is done, move it to the closest hatch/lair/hive that doesnt have a queen assigned
        queensNoInjectPartner = self.units(QUEEN).filter(lambda q: q.tag not in self.queensAssignedHatcheries.keys())
        basesNoInjectPartner = self.townhalls.filter(
            lambda h: h.tag not in self.queensAssignedHatcheries.values() and h.build_progress > 0.8)

        for queen in queensNoInjectPartner:
            if basesNoInjectPartner.amount == 0:
                break
            closestBase = basesNoInjectPartner.closest_to(queen)
            self.queensAssignedHatcheries[queen.tag] = closestBase.tag
            basesNoInjectPartner = basesNoInjectPartner - [closestBase]
            break  # else one hatch gets assigned twice

    async def doQueenInjects(self, iteration):
        # list of all alive queens and bases, will be used for injecting
        aliveQueenTags = [queen.tag for queen in self.units(QUEEN)]  # list of numbers (tags / unit IDs)
        aliveBasesTags = [base.tag for base in self.townhalls]

        # make queens inject if they have 25 or more energy
        toRemoveTags = []

        if hasattr(self, "queensAssignedHatcheries"):
            for queenTag, hatchTag in self.queensAssignedHatcheries.items():
                # queen is no longer alive
                if queenTag not in aliveQueenTags:
                    toRemoveTags.append(queenTag)
                    continue
                # hatchery / lair / hive is no longer alive
                if hatchTag not in aliveBasesTags:
                    toRemoveTags.append(queenTag)
                    continue
                # queen and base are alive, try to inject if queen has 25+ energy
                queen = self.units(QUEEN).find_by_tag(queenTag)
                hatch = self.townhalls.find_by_tag(hatchTag)
                if hatch.is_ready:
                    if queen.energy >= 25 and queen.is_idle and not hatch.has_buff(QUEENSPAWNLARVATIMER):
                        await self.do(queen(EFFECT_INJECTLARVA, hatch))
                else:
                    if iteration % self.injectInterval == 0 and queen.is_idle and queen.position.distance_to(
                            hatch.position) > 10:
                        await self.do(queen(AbilityId.MOVE, hatch.position.to2))

            # clear queen tags (in case queen died or hatch got destroyed) from the dictionary outside the iteration loop
            for tag in toRemoveTags:
                self.queensAssignedHatcheries.pop(tag)

    async def findCreepPlantLocation(self, targetPositions, castingUnit, minRange=None, maxRange=None, stepSize=1,
                                     onlyAttemptPositionsAroundUnit=False, locationAmount=32,
                                     dontPlaceTumorsOnExpansions=True):
        """function that figures out which positions are valid for a queen or tumor to put a new tumor

        Arguments:
            targetPositions {set of Point2} -- For me this parameter is a set of Point2 objects where creep should go towards
            castingUnit {Unit} -- The casting unit (queen or tumor)

        Keyword Arguments:
            minRange {int} -- Minimum range from the casting unit's location (default: {None})
            maxRange {int} -- Maximum range from the casting unit's location (default: {None})
            onlyAttemptPositionsAroundUnit {bool} -- if True, it will only attempt positions around the unit (ideal for tumor), if False, it will attempt a lot of positions closest from hatcheries (ideal for queens) (default: {False})
            locationAmount {int} -- a factor for the amount of positions that will be attempted (default: {50})
            dontPlaceTumorsOnExpansions {bool} -- if True it will sort out locations that would block expanding there (default: {True})

        Returns:
            list of Point2 -- a list of valid positions to put a tumor on
        """

        assert isinstance(castingUnit, Unit)
        positions = []
        ability = self._game_data.abilities[ZERGBUILD_CREEPTUMOR.value]
        if minRange is None: minRange = 0
        if maxRange is None: maxRange = 500

        # get positions around the casting unit
        positions = self.getPositionsAroundUnit(castingUnit, minRange=minRange, maxRange=maxRange, stepSize=stepSize,
                                                locationAmount=locationAmount)

        # stop when map is full with creep
        if len(self.positionsWithoutCreep) == 0:
            return None

        # filter positions that would block expansions
        if dontPlaceTumorsOnExpansions and hasattr(self, "exactExpansionLocations"):
            positions = [x for x in positions if
                         self.getHighestDistance(x.closest(self.exactExpansionLocations), x) > 3]
            # TODO: need to check if this doesnt have to be 6 actually
            # this number cant also be too big or else creep tumors wont be placed near mineral fields where they can actually be placed

        # check if any of the positions are valid
        validPlacements = await self._client.query_building_placement(ability, positions)

        # filter valid results
        validPlacements = [p for index, p in enumerate(positions) if validPlacements[index] == ActionResult.Success]

        allTumors = self.units(CREEPTUMOR) | self.units(CREEPTUMORBURROWED) | self.units(CREEPTUMORQUEEN)
        # usedTumors = allTumors.filter(lambda x:x.tag in self.usedCreepTumors)
        unusedTumors = allTumors.filter(lambda x: x.tag not in self.usedCreepTumors)
        if castingUnit is not None and castingUnit in allTumors:
            unusedTumors = unusedTumors.filter(lambda x: x.tag != castingUnit.tag)

        # filter placements that are close to other unused tumors
        if len(unusedTumors) > 0:
            validPlacements = [x for x in validPlacements if x.distance_to(unusedTumors.closest_to(x)) >= 10]

        validPlacements.sort(key=lambda x: x.distance_to(x.closest(self.positionsWithoutCreep)), reverse=False)

        if len(validPlacements) > 0:
            return validPlacements
        return None

    def getManhattanDistance(self, unit1, unit2):
        assert isinstance(unit1, (Unit, Point2, Point3))
        assert isinstance(unit2, (Unit, Point2, Point3))
        if isinstance(unit1, Unit):
            unit1 = unit1.position.to2
        if isinstance(unit2, Unit):
            unit2 = unit2.position.to2
        return abs(unit1.x - unit2.x) + abs(unit1.y - unit2.y)

    def getHighestDistance(self, unit1, unit2):
        # returns just the highest distance difference, return max(abs(x2-x1), abs(y2-y1))
        # required for creep tumor placement
        assert isinstance(unit1, (Unit, Point2, Point3))
        assert isinstance(unit2, (Unit, Point2, Point3))
        if isinstance(unit1, Unit):
            unit1 = unit1.position.to2
        if isinstance(unit2, Unit):
            unit2 = unit2.position.to2
        return max(abs(unit1.x - unit2.x), abs(unit1.y - unit2.y))

    def getPositionsAroundUnit(self, unit, minRange=0, maxRange=500, stepSize=1, locationAmount=32):
        # e.g. locationAmount=4 would only consider 4 points: north, west, east, south
        assert isinstance(unit, (Unit, Point2, Point3))
        if isinstance(unit, Unit):
            loc = unit.position.to2
        else:
            loc = unit
        positions = [Point2(( \
            loc.x + distance * math.cos(math.pi * 2 * alpha / locationAmount), \
            loc.y + distance * math.sin(math.pi * 2 * alpha / locationAmount))) \
            for alpha in range(locationAmount)
            # alpha is the angle here, locationAmount is the variable on how accurate the attempts look like a circle (= how many points on a circle)
            for distance in range(minRange, maxRange + 1)]  # distance depending on minrange and maxrange
        return positions

    async def updateCreepCoverage(self, stepSize=None):
        if stepSize is None:
            stepSize = self.creepTargetDistance
        ability = self._game_data.abilities[ZERGBUILD_CREEPTUMOR.value]

        positions = [Point2((x, y)) \
                     for x in range(self._game_info.playable_area[0] + stepSize,
                                    self._game_info.playable_area[0] + self._game_info.playable_area[2] - stepSize,
                                    stepSize) \
                     for y in range(self._game_info.playable_area[1] + stepSize,
                                    self._game_info.playable_area[1] + self._game_info.playable_area[3] - stepSize,
                                    stepSize)]

        validPlacements = await self._client.query_building_placement(ability, positions)
        successResults = [
            ActionResult.Success,  # tumor can be placed there, so there must be creep
            ActionResult.CantBuildLocationInvalid,  # location is used up by another building or doodad,
            ActionResult.CantBuildTooFarFromCreepSource,  # - just outside of range of creep
            # ActionResult.CantSeeBuildLocation - no vision here
        ]
        # self.positionsWithCreep = [p for index, p in enumerate(positions) if validPlacements[index] in successResults]
        self.positionsWithCreep = [p for valid, p in zip(validPlacements, positions) if valid in successResults]
        self.positionsWithoutCreep = [p for index, p in enumerate(positions) if
                                      validPlacements[index] not in successResults]
        self.positionsWithoutCreep = [p for valid, p in zip(validPlacements, positions) if valid not in successResults]
        return self.positionsWithCreep, self.positionsWithoutCreep

    async def doCreepSpread(self):
        # only use queens that are not assigned to do larva injects
        allTumors = self.units(CREEPTUMOR) | self.units(CREEPTUMORBURROWED) | self.units(CREEPTUMORQUEEN)

        if not hasattr(self, "usedCreepTumors"):
            self.usedCreepTumors = set()

        # gather all queens that are not assigned for injecting and have 25+ energy
        if hasattr(self, "queensAssignedHatcheries"):
            unassignedQueens = self.units(QUEEN).filter(
                lambda q: (q.tag not in self.queensAssignedHatcheries and q.energy >= 25 or q.energy >= 50) and (
                            q.is_idle or len(q.orders) == 1 and q.orders[0].ability.id in [AbilityId.MOVE]))
        else:
            unassignedQueens = self.units(QUEEN).filter(lambda q: q.energy >= 25 and (
                        q.is_idle or len(q.orders) == 1 and q.orders[0].ability.id in [AbilityId.MOVE]))

        # update creep coverage data and points where creep still needs to go
        if not hasattr(self, "positionsWithCreep") or self.iteration % self.creepSpreadInterval * 10 == 0:
            posWithCreep, posWithoutCreep = await self.updateCreepCoverage()
            totalPositions = len(posWithCreep) + len(posWithoutCreep)
            self.creepCoverage = len(posWithCreep) / totalPositions
            # print(self.getTimeInSeconds(), "creep coverage:", creepCoverage)

        # filter out points that have already tumors / bases near them
        if hasattr(self, "positionsWithoutCreep"):
            self.positionsWithoutCreep = [x for x in self.positionsWithoutCreep if
                                          (allTumors | self.townhalls).closer_than(
                                              self.creepTargetCountsAsReachedDistance, x).amount < 1 or (
                                                      allTumors | self.townhalls).closer_than(
                                              self.creepTargetCountsAsReachedDistance + 10,
                                              x).amount < 5]  # have to set this to some values or creep tumors will clump up in corners trying to get to a point they cant reach

        # make all available queens spread creep until creep coverage is reached 50%
        if hasattr(self, "creepCoverage") and (
                self.creepCoverage < self.stopMakingNewTumorsWhenAtCoverage or allTumors.amount - len(
                self.usedCreepTumors) < 25):
            for queen in unassignedQueens:
                # locations = await self.findCreepPlantLocation(self.positionsWithoutCreep, castingUnit=queen, minRange=3, maxRange=30, stepSize=2, locationAmount=16)
                if self.townhalls.ready.exists:
                    locations = await self.findCreepPlantLocation(self.positionsWithoutCreep, castingUnit=queen,
                                                                  minRange=3, maxRange=30, stepSize=2,
                                                                  locationAmount=16)
                    # locations = await self.findCreepPlantLocation(self.positionsWithoutCreep, castingUnit=self.townhalls.ready.random, minRange=3, maxRange=30, stepSize=2, locationAmount=16)
                    if locations is not None:
                        for loc in locations:
                            err = await self.do(queen(BUILD_CREEPTUMOR_QUEEN, loc))
                            if not err:
                                break

        unusedTumors = allTumors.filter(lambda x: x.tag not in self.usedCreepTumors)
        tumorsMadeTumorPositions = set()
        for tumor in unusedTumors:
            tumorsCloseToTumor = [x for x in tumorsMadeTumorPositions if tumor.distance_to(Point2(x)) < 8]
            if len(tumorsCloseToTumor) > 0:
                continue
            abilities = await self.get_available_abilities(tumor)
            if AbilityId.BUILD_CREEPTUMOR_TUMOR in abilities:
                locations = await self.findCreepPlantLocation(self.positionsWithoutCreep, castingUnit=tumor,
                                                              minRange=10,
                                                              maxRange=10)  # min range could be 9 and maxrange could be 11, but set both to 10 and performance is a little better
                if locations is not None:
                    for loc in locations:
                        err = await self.do(tumor(BUILD_CREEPTUMOR_TUMOR, loc))
                        if not err:
                            tumorsMadeTumorPositions.add((tumor.position.x, tumor.position.y))
                            self.usedCreepTumors.add(tumor.tag)
                            break

    async def getPathDistance(self, pos1, pos2):
        """gets the pathing distance between pos1 and pos2

        Arguments:
            pos1 {unit, Point2} -- position 1
            pos2 {Point2} -- position 2

        Returns:
            int -- distance (i guess the units of the distance is equivalent to the attackrange of in game units)
        """
        return await self._client.query_pathing(pos1, pos2)

    async def getClosestByPath(self, units1, unit2):
        """ Returns the unit from units1 that is closest by path to unit2  """
        # DOESNT SEEM TO WORK RELIABLY
        assert isinstance(unit2, (Unit, Point2))
        if isinstance(units1, (Units, list)):
            closest = None
            closestDist = 999999999999
            for u in units1:
                d = await self.getPathDistance(unit2.position.to2, u.position.to2)
                print("path distance result:", unit2.position.to2, u.position.to2, d)
                if d is not None and d < closestDist:
                    closest = u
                    closestDist = d
                    print("closest by path workingg")
            return closest
        return None

    ################################
    ######### IMPORTANT DEFAULT FUNCTIONS
    ################################

    async def find_placement(self, building, near, max_distance=20, random_alternative=False, placement_step=3,
                             min_distance=0, minDistanceToResources=3):
        """Finds a placement location for building."""

        assert isinstance(building, (AbilityId, UnitTypeId))
        # assert self.can_afford(building)
        assert isinstance(near, Point2)

        if isinstance(building, UnitTypeId):
            building = self._game_data.units[building.value].creation_ability
        else:  # AbilityId
            building = self._game_data.abilities[building.value]

        if await self.can_place(building, near):
            return near

        for distance in range(min_distance, max_distance, placement_step):
            possible_positions = [Point2(p).offset(near).to2 for p in (
                    [(dx, -distance) for dx in range(-distance, distance + 1, placement_step)] +
                    [(dx, distance) for dx in range(-distance, distance + 1, placement_step)] +
                    [(-distance, dy) for dy in range(-distance, distance + 1, placement_step)] +
                    [(distance, dy) for dy in range(-distance, distance + 1, placement_step)]
            )]
            if (
                    self.townhalls | self.state.mineral_field | self.state.vespene_geyser).exists and minDistanceToResources > 0:
                possible_positions = [x for x in possible_positions if
                                      (self.state.mineral_field | self.state.vespene_geyser).closest_to(x).distance_to(
                                          x) >= minDistanceToResources]  # filter out results that are too close to resources

            res = await self._client.query_building_placement(building, possible_positions)
            possible = [p for r, p in zip(res, possible_positions) if r == ActionResult.Success]
            if not possible:
                continue

            if random_alternative:
                return random.choice(possible)
            else:
                return min(possible, key=lambda p: p.distance_to(near))
        return None

    async def distribute_workers(self, performanceHeavy=False, onlySaturateGas=False):
        expansion_locations = self.expansion_locations
        owned_expansions = self.owned_expansions

        mineralTags = [x.tag for x in self.state.units.mineral_field]
        # gasTags = [x.tag for x in self.state.units.vespene_geyser]
        geyserTags = [x.tag for x in self.geysers]

        workerPool = self.units & []
        workerPoolTags = set()

        # find all geysers that have surplus or deficit
        deficitGeysers = {}
        surplusGeysers = {}
        for g in self.geysers.filter(lambda x: x.vespene_contents > 0):
            # only loop over geysers that have still gas in them
            deficit = g.ideal_harvesters - g.assigned_harvesters
            if deficit > 0:
                deficitGeysers[g.tag] = {"unit": g, "deficit": deficit}
            elif deficit < 0:
                surplusWorkers = self.workers.closer_than(10, g).filter(
                    lambda w: w not in workerPoolTags and len(w.orders) == 1 and w.orders[0].ability.id in [
                        AbilityId.HARVEST_GATHER] and w.orders[0].target in geyserTags)
                # workerPool.extend(surplusWorkers)
                for i in range(-deficit):
                    if surplusWorkers.amount > 0:
                        w = surplusWorkers.pop()
                        workerPool.append(w)
                        workerPoolTags.add(w.tag)
                surplusGeysers[g.tag] = {"unit": g, "deficit": deficit}

        if not onlySaturateGas:
            # find all townhalls that have surplus or deficit
            deficitTownhalls = {}
            surplusTownhalls = {}
            for th in self.townhalls:
                deficit = th.ideal_harvesters - th.assigned_harvesters
                if deficit > 0:
                    deficitTownhalls[th.tag] = {"unit": th, "deficit": deficit}
                elif deficit < 0:
                    surplusWorkers = self.workers.closer_than(10, th).filter(
                        lambda w: w.tag not in workerPoolTags and len(w.orders) == 1 and w.orders[0].ability.id in [
                            AbilityId.HARVEST_GATHER] and w.orders[0].target in mineralTags)
                    # workerPool.extend(surplusWorkers)
                    for i in range(-deficit):
                        if surplusWorkers.amount > 0:
                            w = surplusWorkers.pop()
                            workerPool.append(w)
                            workerPoolTags.add(w.tag)
                    surplusTownhalls[th.tag] = {"unit": th, "deficit": deficit}

            if all([len(deficitGeysers) == 0, len(surplusGeysers) == 0,
                    len(surplusTownhalls) == 0 or deficitTownhalls == 0]):
                # cancel early if there is nothing to balance
                return

        # check if deficit in gas less or equal than what we have in surplus, else grab some more workers from surplus bases
        deficitGasCount = sum(
            gasInfo["deficit"] for gasTag, gasInfo in deficitGeysers.items() if gasInfo["deficit"] > 0)
        surplusCount = sum(-gasInfo["deficit"] for gasTag, gasInfo in surplusGeysers.items() if gasInfo["deficit"] < 0)
        surplusCount += sum(-thInfo["deficit"] for thTag, thInfo in surplusTownhalls.items() if thInfo["deficit"] < 0)

        if deficitGasCount - surplusCount > 0:
            # grab workers near the gas who are mining minerals
            for gTag, gInfo in deficitGeysers.items():
                if workerPool.amount >= deficitGasCount:
                    break
                workersNearGas = self.workers.closer_than(10, gInfo["unit"]).filter(
                    lambda w: w.tag not in workerPoolTags and len(w.orders) == 1 and w.orders[0].ability.id in [
                        AbilityId.HARVEST_GATHER] and w.orders[0].target in mineralTags)
                while workersNearGas.amount > 0 and workerPool.amount < deficitGasCount:
                    w = workersNearGas.pop()
                    workerPool.append(w)
                    workerPoolTags.add(w.tag)

        # now we should have enough workers in the pool to saturate all gases, and if there are workers left over, make them mine at townhalls that have mineral workers deficit
        for gTag, gInfo in deficitGeysers.items():
            if performanceHeavy:
                # sort furthest away to closest (as the pop() function will take the last element)
                workerPool.sort(key=lambda x: x.distance_to(gInfo["unit"]), reverse=True)
            for i in range(gInfo["deficit"]):
                if workerPool.amount > 0:
                    w = workerPool.pop()
                    if len(w.orders) == 1 and w.orders[0].ability.id in [AbilityId.HARVEST_RETURN]:
                        await self.do(w.gather(gInfo["unit"], queue=True))
                    else:
                        await self.do(w.gather(gInfo["unit"]))

        if not onlySaturateGas:
            # if we now have left over workers, make them mine at bases with deficit in mineral workers
            for thTag, thInfo in deficitTownhalls.items():
                if performanceHeavy:
                    # sort furthest away to closest (as the pop() function will take the last element)
                    workerPool.sort(key=lambda x: x.distance_to(thInfo["unit"]), reverse=True)
                for i in range(thInfo["deficit"]):
                    if workerPool.amount > 0:
                        w = workerPool.pop()
                        mf = self.state.mineral_field.closer_than(10, thInfo["unit"]).closest_to(w)
                        if len(w.orders) == 1 and w.orders[0].ability.id in [AbilityId.HARVEST_RETURN]:
                            await self.do(w.gather(mf, queue=True))
                        else:
                            await self.do(w.gather(mf))

        # TODO: check if a drone is mining from a destroyed base (= if nearest townhalf from the GATHER target is >10 away) -> make it mine at another mineral patch

    def select_build_worker(self, pos, force=False, excludeTags=[]):
        workers = self.workers.closer_than(50, pos) or self.workers
        for worker in workers.prefer_close_to(pos).prefer_idle:
            if not worker.orders or len(worker.orders) == 1 and worker.orders[0].ability.id in [AbilityId.MOVE,
                                                                                                AbilityId.HARVEST_GATHER,
                                                                                                AbilityId.HARVEST_RETURN] and worker.tag not in excludeTags:
                return worker
        return workers.random if force else None

    def already_pending(self, unit_type):
        ability = self._game_data.units[unit_type.value].creation_ability
        unitAttributes = self._game_data.units[unit_type.value].attributes

        # # the following checks for construction of buildings, i think 8 in unitAttributes stands for "structure" tag
        # # i commented the following out because i think that is not what is meant with "already pending", but rather having a worker queued up to place a building, or having units in production queue
        # if self.units(unit_type).not_ready.exists and 8 in unitAttributes:
        #     return len(self.units(unit_type).not_ready)
        # the following checks for units being made from eggs and trained units in general
        if 8 not in unitAttributes and any(o.ability == ability for w in (self.units.not_structure) for o in w.orders):
            return sum([o.ability == ability for w in (self.units - self.workers) for o in w.orders])
        # following checks for unit production in a building queue, like queen, also checks if hatch is morphing to LAIR
        elif any(o.ability.id == ability.id for w in (self.units.structure) for o in w.orders):
            return sum([o.ability.id == ability.id for w in (self.units.structure) for o in w.orders])
        elif any(o.ability == ability for w in self.workers for o in w.orders):
            return sum([o.ability == ability for w in self.workers for o in w.orders])
        elif any(egg.orders[0].ability == ability for egg in self.units(EGG)):
            return sum([egg.orders[0].ability == ability for egg in self.units(EGG)])
        return 0

    async def on_step(self, iteration):
        """ this was my first goal when starting to write this bot
        ✓ create overlords based on: how much larva is produced in 18 seconds (overlord build time) - based on number of hatcheries and inject queens
        ✓ if we have 2 or more hatcheries building (pending), start making spawning pool
        ✓ once pool is building / pending, get the first gas
        ✓ when at 100 gas, get ling speed
        ✓ if we have 50 or more drones building (pending), start roach warren and take more gas
        ✓ once at 4:30 time, get lair
        ✓ at 70 or more drones, start making roaches
        ✓ make as many extractors to have a proper 4:1 or 3:1 income ratio (minerals:gas)
        ✓ once at 120+ supply, make 2 evo chambers and get range + armor upgrade
        ✓ if lair complete, get roach speed
        ✓ once at 180+ supply, attack with roaches
        ✓ when pool is done, make queens (one per hatch) and assign queens to hatcheries (inject)
        """

        self.workerProductionEnabled = [True]
        self.queenProductionEnabled = [True]
        self.armyProductionEnabled = [True]
        self.iteration = iteration
        if not self.prepareStart2Ran:
            await self._prepare_start2()
        self.currentDroneCountIncludingPending = self.units(DRONE).amount + self.already_pending(DRONE) + self.units(
            EXTRACTOR).ready.filter(lambda x: x.vespene_contents > 0).amount
        if self.units(GREATERSPIRE).exists:
            self.totalQueenLimit = self.totalLateGameQueenLimit
        else:
            self.totalQueenLimit = self.totalEarlyGameQueenLimit

        ################################
        ######### MACRO (ECONOMY)
        ################################

        if iteration % self.buildStuffInverval == 0:
            # calc larva production
            larvaPerSecond = self.townhalls.ready.amount * self.larvaPerHatch + self.units(
                QUEEN).ready.amount * self.larvaPerInject
            larvaPer18Seconds = larvaPerSecond * 18  # overlord build time is 18 secs

            # create overlords if low on supply
            # print(self.supply_left + self.already_pending(OVERLORD) * 8, larvaPer18Seconds)
            if self.supply_left + self.already_pending(
                    OVERLORD) * 8 < 2 * larvaPer18Seconds and self.supply_cap + self.already_pending(
                    OVERLORD) * 8 < 200 and self.supply_used >= 13 or self.supply_cap < 14:
                self.workerProductionEnabled.append(False)
                self.armyProductionEnabled.append(False)
                if self.can_afford(OVERLORD) and self.units(LARVA).exists:
                    await self.do(self.units(LARVA).random.train(OVERLORD))

            # take one extractor if we have 2+ hatcheries
            if self.townhalls.amount >= 2 and self.units(EXTRACTOR).amount + self.already_pending(EXTRACTOR) < 1 and (
                    self.getLingSpeed or (
                    self.currentDroneCountIncludingPending > 25 and self.units(SPAWNINGPOOL).exists)):
                vgs = self.state.vespene_geyser.closer_than(10, self.townhalls.ready.random)
                for vg in vgs:
                    worker = self.select_build_worker(vg.position)
                    if worker is None: break
                    if self.can_afford(EXTRACTOR) and await self.can_place(EXTRACTOR, vg.position):
                        err = await self.do(worker.build(EXTRACTOR, vg))
                        if not err: break

            # townhall furthest away from enemy base - that is where i will make all the tech buildings
            townhallLocationFurthestFromOpponent = None
            if self.townhalls.ready.exists and self.known_enemy_structures.exists:
                townhallLocationFurthestFromOpponent = max([x.position.to2 for x in self.townhalls.ready],
                                                           key=lambda x: x.closest(
                                                               self.known_enemy_structures).distance_to(x))
            if townhallLocationFurthestFromOpponent is None and self.townhalls.ready.exists:
                townhallLocationFurthestFromOpponent = self.townhalls.ready.random.position.to2

            # create spawning pool if we have 2+ hatches
            if self.currentDroneCountIncludingPending > 17 and not self.units(
                    SPAWNINGPOOL).exists and self.already_pending(SPAWNINGPOOL) < 1 and self.townhalls.amount >= 2:
                self.workerProductionEnabled.append(False)
                if self.can_afford(SPAWNINGPOOL):
                    pos = await self.find_placement(SPAWNINGPOOL, townhallLocationFurthestFromOpponent, min_distance=6)
                    # pos = await self.find_placement(SPAWNINGPOOL, self.townhalls.ready.random.position.to2, min_distance=6)
                    if pos is not None:
                        drone = self.workers.closest_to(pos)
                        if self.can_afford(SPAWNINGPOOL):
                            err = await self.do(drone.build(SPAWNINGPOOL, pos))

            # if pool is done, research ling speed if we have the money
            if self.getLingSpeed:  # parameter, see at __init__ function
                if self.units(SPAWNINGPOOL).ready.exists:
                    pool = self.units(SPAWNINGPOOL).ready.first
                    abilities = await self.get_available_abilities(pool)
                    if AbilityId.RESEARCH_ZERGLINGMETABOLICBOOST in abilities and self.can_afford(
                            AbilityId.RESEARCH_ZERGLINGMETABOLICBOOST):
                        error = await self.do(pool(AbilityId.RESEARCH_ZERGLINGMETABOLICBOOST))

            # if pool is done, make queens
            # this is at the end of the script

            # only assign queens once the first creep tumors are placed (those are more important than inject at the start afaik)
            if ((self.units(CREEPTUMOR) | self.units(CREEPTUMORBURROWED) | self.units(
                    CREEPTUMORQUEEN)).amount >= 2 or not self.enableCreepSpread) and self.enableInjects:
                if self.units(GREATERSPIRE).exists:
                    # unassign queens when we have enough hatcheries in late game when we only build expensive units that dont require much larva
                    self.assignQueen(0)
                else:
                    self.assignQueen(self.injectQueenLimit)
                    # perform injects (if they have enough energy)
                    await self.doQueenInjects(iteration)

            # make roach warren when at 43+ drones
            if (self.currentDroneCountIncludingPending >= 40 or self.opponentInfo[
                "armySupplyScouted"] > 5) and self.units(ROACHWARREN).amount + self.already_pending(
                    ROACHWARREN) < 1 and self.townhalls.exists and self.enableMakingRoaches:
                self.workerProductionEnabled.append(False)  # priotize
                if self.can_afford(ROACHWARREN):
                    pos = await self.find_placement(ROACHWARREN, townhallLocationFurthestFromOpponent, min_distance=6)
                    # pos = await self.find_placement(ROACHWARREN, self.townhalls.ready.random.position.to2, min_distance=6)
                    if pos is not None:
                        drone = self.workers.closest_to(pos)
                        if self.can_afford(ROACHWARREN):
                            err = await self.do(drone.build(ROACHWARREN, pos))

            # make 2 evo chambers when at 35+ drones
            if self.currentDroneCountIncludingPending >= 37 and self.units(
                    EVOLUTIONCHAMBER).amount + self.already_pending(EVOLUTIONCHAMBER) < 2 and self.townhalls.amount > 2:
                # self.workerProductionEnabled.append(False) # priotize?
                if self.can_afford(EVOLUTIONCHAMBER):
                    pos = await self.find_placement(EVOLUTIONCHAMBER, townhallLocationFurthestFromOpponent,
                                                    min_distance=6)
                    # pos = await self.find_placement(EVOLUTIONCHAMBER, self.townhalls.ready.random.position.to2, min_distance=6)
                    if pos is not None:
                        drone = self.workers.closest_to(pos)
                        if self.can_afford(EVOLUTIONCHAMBER):
                            err = await self.do(drone.build(EVOLUTIONCHAMBER, pos))

            # take more extractors if we have 66+ drones
            if self.currentDroneCountIncludingPending >= 66 and self.units(EXTRACTOR).filter(
                    lambda x: x.vespene_contents > 0).amount + self.already_pending(
                    EXTRACTOR) < 9 and self.already_pending(EXTRACTOR) < 4 and self.townhalls.amount > 2:
                self.workerProductionEnabled.append(False)
                vgs = self.state.vespene_geyser.closer_than(10, self.townhalls.filter(
                    lambda x: x.build_progress > 0.6).random)
                for vg in vgs:
                    worker = self.select_build_worker(vg.position)
                    if worker is None: break
                    if self.can_afford(EXTRACTOR) and await self.can_place(EXTRACTOR, vg.position):
                        err = await self.do(worker.build(EXTRACTOR, vg))
                        if not err: break

            # after 4:30 start lair
            if self.getTimeInSeconds() > 4.5 * 60 and self.currentDroneCountIncludingPending > 50:
                if self.already_pending(LAIR) < 1 and self.units(HATCHERY).ready.idle.exists and self.units(
                        SPAWNINGPOOL).ready.exists and not (
                        self.units(LAIR) | self.units(HIVE)).exists and self.vespene >= 100:
                    self.queenProductionEnabled.append(False)
                    self.armyProductionEnabled.append(False)
                    self.workerProductionEnabled.append(False)
                    if self.can_afford(LAIR):
                        err = await self.do(self.units(HATCHERY).ready.idle.random(UPGRADETOLAIR_LAIR))

                # make infestation pit when above 160 supply
                if (self.supply_used > 130 or not self.enableMakingRoaches) and self.units(
                        LAIR).ready.amount > 0 and self.units(INFESTATIONPIT).amount + self.already_pending(
                        INFESTATIONPIT) < 1 and self.townhalls.amount > 3:
                    self.armyProductionEnabled.append(False)
                    self.workerProductionEnabled.append(False)
                    pos = await self.find_placement(INFESTATIONPIT, townhallLocationFurthestFromOpponent,
                                                    min_distance=6)
                    # pos = await self.find_placement(INFESTATIONPIT, self.townhalls.ready.random.position.to2, min_distance=6)
                    if pos is not None:
                        drone = self.workers.closest_to(pos)
                        if self.can_afford(INFESTATIONPIT):
                            err = await self.do(drone.build(INFESTATIONPIT, pos))

                # morph to hive
                if self.supply_used > 150 and self.units(LAIR).ready.idle.exists and self.units(
                        INFESTATIONPIT).ready.exists and not self.already_pending(HIVE) and not self.units(
                        HIVE).exists and self.townhalls.amount > 3:
                    self.armyProductionEnabled.append(False)
                    self.workerProductionEnabled.append(False)
                    if self.can_afford(HIVE):
                        err = await self.do(self.units(LAIR).ready.idle.first(UPGRADETOHIVE_HIVE))

                # if lategame enabled: get spire (and then greater spire)
                if self.supply_used > 80 and (self.already_pending(HIVE) or self.units(HIVE).exists) and self.units(
                        GREATERSPIRE).amount + self.already_pending(GREATERSPIRE) < 1 and self.enableLateGame:
                    if not self.units(GREATERSPIRE).exists and self.units(
                            SPIRE).ready.idle.exists and self.already_pending(GREATERSPIRE) < 1:
                        self.armyProductionEnabled.append(False)
                        self.workerProductionEnabled.append(False)
                        # morph spire to greater spire
                        if self.can_afford(GREATERSPIRE):
                            err = await self.do(self.units(SPIRE).ready.idle.random(UPGRADETOGREATERSPIRE_GREATERSPIRE))

                    # build spire if we dont have spire or greater spire
                    elif not self.units(GREATERSPIRE).exists and not self.units(SPIRE).exists and self.already_pending(
                            SPIRE) < 1:
                        self.armyProductionEnabled.append(False)
                        self.workerProductionEnabled.append(False)
                        if self.can_afford(SPIRE):
                            pos = await self.find_placement(SPIRE, townhallLocationFurthestFromOpponent, min_distance=6,
                                                            minDistanceToResources=2)
                            # pos = await self.find_placement(SPIRE, self.townhalls.ready.random.position.to2, min_distance=6, minDistanceToResources=2)
                            if pos is not None:
                                drone = self.workers.closest_to(pos)
                                if self.can_afford(SPIRE):
                                    err = await self.do(drone.build(SPIRE, pos))

            ################################
            ######### MACRO (UPGRADES)
            ################################

            # when lair is done, get roach speed
            if self.units(ROACHWARREN).ready.amount > 0 and (
                    self.units(LAIR).ready.amount > 0 or self.units(HIVE).amount > 0) and self.enableMakingRoaches:
                if self.units(ROACHWARREN).ready.idle.amount > 0:
                    rw = self.units(ROACHWARREN).ready.idle.random
                    abilities = await self.get_available_abilities(rw)
                    if AbilityId.RESEARCH_GLIALREGENERATION in abilities and self.can_afford(
                            AbilityId.RESEARCH_GLIALREGENERATION):
                        error = await self.do(rw(AbilityId.RESEARCH_GLIALREGENERATION))

                    # research roach burrow movement
                    elif self.getRoachBurrowAndBurrow and AbilityId.RESEARCH_TUNNELINGCLAWS in abilities and self.can_afford(
                            AbilityId.RESEARCH_TUNNELINGCLAWS):
                        error = await self.do(rw(AbilityId.RESEARCH_TUNNELINGCLAWS))

                # research burrow from hatch, getting all abilities from hatch is still buggy
                rw = self.units(ROACHWARREN).ready.random
                abilities = await self.get_available_abilities(rw)
                if self.getRoachBurrowAndBurrow and AbilityId.RESEARCH_TUNNELINGCLAWS not in abilities and self.can_afford(
                        AbilityId.RESEARCH_TUNNELINGCLAWS) and self.can_afford(AbilityId.RESEARCH_BURROW):
                    if self.iteration % self.creepSpreadInterval == 0:
                        drone = self.units(DRONE).random
                        if drone is not None:
                            droneAbilities = await self.get_available_abilities(drone)
                            if AbilityId.BURROWDOWN_DRONE not in droneAbilities and self.can_afford(
                                    AbilityId.RESEARCH_BURROW):
                                if self.units(HATCHERY).ready.idle.exists:
                                    hatch = self.units(HATCHERY).ready.idle.random
                                    error = await self.do(hatch(AbilityId.RESEARCH_BURROW))

            # research overlord speed from hatchery if we have a big bank
            if self.minerals > 1000 and self.vespene > 1000 and self.can_afford(
                    AbilityId.RESEARCH_PNEUMATIZEDCARAPACE) and self.units(HATCHERY).idle.exists:
                hatch = self.units(HATCHERY).idle.random
                if self.can_afford(AbilityId.RESEARCH_PNEUMATIZEDCARAPACE):
                    await self.do(hatch(RESEARCH_PNEUMATIZEDCARAPACE))

            # get roach upgrades 1-1 2-2 3-3
            if self.units(EVOLUTIONCHAMBER).ready.idle.exists:
                for evo in self.units(EVOLUTIONCHAMBER).ready.idle:
                    abilities = await self.get_available_abilities(evo)
                    targetAbilities = [AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL1,
                                       AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL2,
                                       AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL3,
                                       AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL1,
                                       AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL2,
                                       AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL3]
                    if self.units(GREATERSPIRE).exists:
                        targetAbilities.extend([AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL1,
                                                AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL2,
                                                AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL3])
                    for ability in targetAbilities:
                        if ability in abilities:
                            if self.can_afford(ability):
                                err = await self.do(evo(ability))
                                if not err:
                                    break

            # if lategame enabled: get air upgrades if we have idle greater spire
            if self.enableLateGame and self.units(
                    GREATERSPIRE).ready.idle.exists:  # and self.can_afford(RESEARCH_ZERGFLYERATTACKLEVEL3):
                gs = self.units(GREATERSPIRE).ready.idle.random
                abilities = await self.get_available_abilities(gs)
                targetAbilities = [AbilityId.RESEARCH_ZERGFLYERATTACKLEVEL1,
                                   AbilityId.RESEARCH_ZERGFLYERATTACKLEVEL2,
                                   AbilityId.RESEARCH_ZERGFLYERATTACKLEVEL3,
                                   AbilityId.RESEARCH_ZERGFLYERARMORLEVEL1,
                                   AbilityId.RESEARCH_ZERGFLYERARMORLEVEL2,
                                   AbilityId.RESEARCH_ZERGFLYERARMORLEVEL3]
                for ability in targetAbilities:
                    if self.can_afford(ability) and ability in abilities:
                        err = await self.do(gs(ability))
                        if not err:
                            break

            ################################
            ######### MACRO (EXPANDING)
            ################################

            # boolean, expand when game time > 10 mins and we have less than 30 mineral fields
            # or if we have DRONES > (TOWNHALLS - 1) * 16
            inNeedOfExpansion = self.getTimeInSeconds() > 10 * 60 and sum(
                [self.state.mineral_field.closer_than(10, x).amount for x in
                 self.townhalls]) < 32 or self.currentDroneCountIncludingPending + 16 > (
                                    self.townhalls.amount) * 16 + self.units(EXTRACTOR).ready.filter(
                lambda x: x.vespene_contents > 0).amount * 3

            if self.townhalls.amount > 1:
                self.haltRedistributeWorkers = False
            # send worker to the first expansion to build it asap
            if self.townhalls.amount < 2 and (self.currentDroneCountIncludingPending > 17 or (
                    self.can_afford(HATCHERY) and self.units(
                    DRONE).amount > 5)) and self.nextExpansionInfo == {} and self.already_pending(HATCHERY) < 1:
                location = await self.get_next_expansion()
                w = self.select_build_worker(location, excludeTags=self.reservedWorkers)
                loc = await self.find_placement(HATCHERY, near=location, random_alternative=False, placement_step=1,
                                                minDistanceToResources=5, max_distance=20)
                if loc is not None:
                    location = loc
                self.reservedWorkers.append(w.tag)
                self.nextExpansionInfo = {
                    "workerTag": w.tag,
                    "location": location
                }
                print(self.getTimeInSeconds(), "moving worker to expand", w.tag)
                self.haltRedistributeWorkers = True
                self.workerProductionEnabled.append(False)
                await self.do(w.move(location))

            elif self.townhalls.amount < 2 and self.nextExpansionInfo != {} and self.already_pending(HATCHERY) < 1:
                self.haltRedistributeWorkers = True
                self.workerProductionEnabled.append(False)
                if self.can_afford(HATCHERY):
                    w = self.workers.find_by_tag(self.nextExpansionInfo["workerTag"])
                    if w is not None:
                        location = self.nextExpansionInfo["location"]
                        print(self.getTimeInSeconds(), "building first expansion with worker", w.tag,
                              self.nextExpansionInfo["workerTag"])
                        err = await self.do(w.build(HATCHERY, location))
                        if not err:
                            self.nextExpansionInfo = {}

            # expand if money available, only take one expansion at a time (queued by worker)
            # dont OVERexpand, only expand if we have less than X mineral fields near our base
            elif (self.currentDroneCountIncludingPending > self.townhalls.amount * 16 or (self.can_afford(
                    HATCHERY) and self.townhalls.amount < 3 or self.minerals > 2000)) and self.townhalls.amount > 1 and inNeedOfExpansion and self.already_pending(
                    HATCHERY) < 1:
                self.workerProductionEnabled.append(False)
                if self.can_afford(HATCHERY):
                    location = await self.get_next_expansion()
                    location = await self.find_placement(HATCHERY, near=location, random_alternative=False,
                                                         placement_step=1, minDistanceToResources=5)
                    if location is not None:
                        w = self.select_build_worker(location, excludeTags=self.reservedWorkers)
                        if w is not None:
                            err = await self.build(HATCHERY, location, max_distance=20, unit=w,
                                                   random_alternative=False, placement_step=1)

            # set rally point of hatcheries to nearby mineral field
            if iteration % self.injectInterval == 0:
                await self.assignWorkerRallyPoint()

            ################################
            ######### MACRO (worker distribution)
            ################################

            if not self.haltRedistributeWorkers:
                # make idle workers mine at the nearest hatchery
                for worker in self.workers.idle:
                    closestHatchery = self.townhalls.ready.closest_to(worker.position)
                    await self.do(worker.gather(self.state.mineral_field.closest_to(closestHatchery)))
                # every few frames, redistribute workers equally
                if iteration % self.workerTransferInterval * 5 == 0:
                    # redistribute workers (alternatively: set rally points)
                    await self.distribute_workers()
                elif iteration % self.workerTransferInterval == 0:
                    # redistribute workers (alternatively: set rally points)
                    await self.distribute_workers(onlySaturateGas=True)

        ################################
        ######### CREEPSPREAD
        ################################
        # manage creep spread

        if self.enableCreepSpread and iteration % self.creepSpreadInterval == 0 and (
                self.getTimeInSeconds() > 3 * 60 or self.opponentInfo["armySupplyScouted"] < 5 or (
                self.units(CREEPTUMOR) | self.units(CREEPTUMORBURROWED) | self.units(CREEPTUMORQUEEN)).amount < 2):
            await self.doCreepSpread()

        ################################
        ######### MACRO (ARMY)
        ################################

        if iteration % self.buildStuffInverval == 0:
            # make scouting units
            if not hasattr(self, "scoutingUnits"):
                self.scoutingUnits = set()
            if self.units(ZERGLING).amount + self.already_pending(ZERGLING) + len(self.scoutingUnits) < \
                    self.opponentInfo["scoutingUnitsNeeded"] and self.supply_left > 1 and self.units(
                    SPAWNINGPOOL).ready.exists and self.units(LARVA).exists and self.supply_used < 198:
                # self.workerProductionEnabled.append(False) # this doesnt seem to be very necessary
                if self.can_afford(ZERGLING):
                    await self.do(self.units(LARVA).random.train(ZERGLING))
            # add lings to scouting units
            for ling in self.units(ZERGLING).filter(lambda x: x.health >= 20):
                if len(self.scoutingUnits) < self.opponentInfo[
                    "scoutingUnitsNeeded"] and ling.tag not in self.scoutingUnits:
                    print("added ling to scouting units group")
                    self.scoutingUnits.add(ling.tag)
            # # clear dead lings from scouting units list - i dont want that hear because i have it again a few lines below

            # make 1 roach for every 2 enemy unit supply
            makeDefensiveRoaches = self.opponentInfo["armySupplyScoutedClose"] // 1 > self.units.not_structure.filter(
                lambda x: x.type_id not in [DRONE, LARVA, OVERLORD, ZERGLING]).amount + self.already_pending(
                ROACH) + self.already_pending(QUEEN) + self.units(
                SPINECRAWLER).not_ready.amount and self.getTimeInSeconds() < 6 * 60 and self.vespene > 25
            if makeDefensiveRoaches:
                # stop worker production for a while to build a defense since an attack is likely to come
                self.workerProductionEnabled.append(False)

            # if roach warren is ready, start making roaches
            if self.units(ROACHWARREN).ready.exists and \
                    all(self.armyProductionEnabled) and \
                    (not self.units(GREATERSPIRE).exists or self.minerals > self.vespene * 2 > 1000) and \
                    ((self.minerals > 400 and self.vespene > 400 or not self.units(
                        EVOLUTIONCHAMBER).idle.exists and self.currentDroneCountIncludingPending >= self.droneLimit) or makeDefensiveRoaches) and self.supply_used < 197:
                if self.supply_left > 1 and self.can_afford(ROACH):
                    roachesAffordable = min((196 - self.supply_used) // 2, self.supply_left // 2, self.minerals // 75,
                                            self.vespene // 25, self.units(LARVA).amount)
                    for count, larva in enumerate(self.units(LARVA)):
                        if count >= roachesAffordable:
                            break
                        if self.can_afford(ROACH):
                            await self.do(larva.train(ROACH))

            # if we have lair, make overseer
            if all(self.armyProductionEnabled) and (self.units(LAIR) | self.units(HIVE)).exists and (
                    self.units(OVERSEER) | self.units(OVERLORDCOCOON)).amount < 3 and hasattr(self,
                                                                                              "overlordsSendlocation") and (
                    self.minerals > 500 and self.vespene > 500 or self.supply_used > 150):
                if self.units(OVERLORD).exists and self.can_afford(OVERSEER):
                    assignedOverlordTags = set().union(*list(self.overlordsSendlocation.values()))
                    availableOverlords = self.units(OVERLORD).filter(lambda x: x.tag not in assignedOverlordTags)
                    if availableOverlords.exists and self.can_afford(OVERSEER):
                        ov = availableOverlords.random
                        await self.do(ov(MORPH_OVERSEER))

            # if greater spire is ready, make units in a ratio
            # bl - corruptor - viper
            # 2 - 3 - 1
            corruptorsTotal = self.units(CORRUPTOR).amount + self.already_pending(CORRUPTOR)
            broodlordsTotal = self.units(BROODLORD).amount + self.units(BROODLORDCOCOON).amount
            vipersTotal = self.units(VIPER).amount + self.already_pending(VIPER)
            makeCorruptors = self.units(CORRUPTOR).amount < 1 \
                             or corruptorsTotal / self.corruptorRatioFactor < broodlordsTotal / self.broodlordRatioFactor + 1 \
                             and corruptorsTotal / self.corruptorRatioFactor < vipersTotal / self.viperRatioFactor + 1  # or corruptorsTotal < 15
            makeBroodlords = corruptorsTotal / self.corruptorRatioFactor > broodlordsTotal / self.broodlordRatioFactor and self.units(
                CORRUPTOR).amount > 1
            makeVipers = corruptorsTotal / self.corruptorRatioFactor > vipersTotal / self.viperRatioFactor

            if all(self.armyProductionEnabled) and self.units(GREATERSPIRE).exists and self.can_afford(
                    CORRUPTOR) and self.supply_left > 1 and makeCorruptors:  # leave a bit supply for viper and BL morphs
                corruptorAffordable = min(self.supply_left // 2, self.minerals // 150, self.vespene // 100,
                                          self.units(LARVA).amount)
                for count, larva in enumerate(self.units(LARVA)):
                    if count >= corruptorAffordable:
                        break
                    if self.can_afford(CORRUPTOR):
                        await self.do(larva.train(CORRUPTOR))

            elif all(self.armyProductionEnabled) and self.units(GREATERSPIRE).exists and self.units(
                    CORRUPTOR).idle.exists and self.supply_left > 1 and makeBroodlords:
                if self.can_afford(BROODLORD):
                    lowestHpIdleCorruptor = min(self.units(CORRUPTOR), key=lambda x: x.health)
                    await self.do(lowestHpIdleCorruptor(MORPHTOBROODLORD_BROODLORD))

            elif all(self.armyProductionEnabled) and self.units(GREATERSPIRE).exists and self.can_afford(
                    VIPER) and self.supply_left > 5 and makeVipers:  # leave a bit supply for viper and BL morphs
                if self.can_afford(VIPER) and self.units(LARVA).exists:
                    await self.do(self.units(LARVA).random.train(VIPER))

        ################################
        ######### INTEL / INFO / SCOUTING
        ################################

        if iteration % self.workerTransferInterval == 0:
            # overlord scouting, send overlord to each expansion that isnt taken by opponent
            if not hasattr(self, "overlordsSendlocation"):
                self.overlordsSendlocation = OrderedDict(
                    {base.position.to2: set() for base in self.exactExpansionLocations})
                self.overlordsSendlocation = OrderedDict(sorted(self.overlordsSendlocation.items(),
                                                                key=lambda x: x[0].closest(
                                                                    self.enemy_start_locations).distance_to(x[0])))

            # else:
            #     # clear dead overlords and send new ones - DONT DO THAT because the overlord already got killed, why suicide another one?
            #     aliveOverlordTags = {x.tag for x in self.units(OVERLORD)}
            #     for key in self.overlordsSendlocation.keys():
            #         self.overlordsSendlocation[key] = {x for x in self.overlordsSendlocation[key] if x in aliveOverlordTags}

            # send new overlords if we dont have an overlord at the location and if the location is not taken by either player
            assignedOverlordTags = set().union(*list(self.overlordsSendlocation.values()))
            unassignedOverlords = self.units(OVERLORD).filter(lambda x: x.tag not in assignedOverlordTags)

            myBasesAndEnemyBases = [x.position.to2 for x in self.townhalls | self.known_enemy_structures.filter(
                lambda x: x.type_id in [HATCHERY, LAIR, HIVE, COMMANDCENTER, PLANETARYFORTRESS, ORBITALCOMMAND,
                                        NEXUS] and x.build_progress > 0.5)]
            if len(myBasesAndEnemyBases) > 0:
                for key, value in self.overlordsSendlocation.items():
                    closestBaseNearTargetLocation = key.closest(myBasesAndEnemyBases)
                    # move new overlord to target location to scout
                    if unassignedOverlords.exists and len(value) == 0 and closestBaseNearTargetLocation.distance_to(
                            key) > 15:
                        ov = unassignedOverlords.pop()
                        value.add(ov.tag)
                        await self.do(ov.move(key))
                    # move overlord back and unassign if base was taken by someone
                    elif len(value) > 0 and closestBaseNearTargetLocation.distance_to(
                            key) <= 15 and self.townhalls.exists:
                        # TODO: make it move away if enemy shooting units nearby
                        ovTag = value.pop()
                        ov = self.units(OVERLORD).find_by_tag(ovTag)
                        if ov is not None:
                            await self.do(ov.move(self.townhalls.random.position))

            if iteration % (self.workerTransferInterval * 10) == 0:
                # make overlords shit if they have ability (when lair is done)
                if self.units(OVERLORD).exists:
                    for ov in self.units(OVERLORD):
                        abilities = await self.get_available_abilities(ov)
                        if AbilityId.BEHAVIOR_GENERATECREEPON in abilities and self.can_afford(
                                BEHAVIOR_GENERATECREEPON):
                            await self.do(ov(BEHAVIOR_GENERATECREEPON))

            # make overseer create changeling
            for ov in self.units(OVERSEER).idle.filter(lambda x: x.energy >= 50):
                await self.do(ov(SPAWNCHANGELING_SPAWNCHANGELING))

            # make changeling move to random enemy building if idle
            for ch in self.units.filter(
                    lambda x: x.type_id in [CHANGELING, CHANGELINGZEALOT, CHANGELINGMARINESHIELD, CHANGELINGMARINE,
                                            CHANGELINGZERGLINGWINGS, CHANGELINGZERGLING]).idle:
                if self.known_enemy_structures.exists:
                    await self.do(ch.move(self.known_enemy_structures.random.position))

            ignoreUnits = [OVERSEER, OBSERVERSIEGEMODE, OVERSEERSIEGEMODE, PHOTONCANNON, MISSILETURRET, RAVEN,
                           SPORECRAWLER]

            # move overlords away from enemies
            for ov in self.units(OVERLORD).filter(lambda x: x.tag not in assignedOverlordTags):
                if ov.health < ov.health_max and (ov.is_idle or len(ov.orders) == 1 and ov.orders[0].ability.id in [
                    AbilityId.MOVE]) and self.townhalls.exists:
                    closestTownhall = self.townhalls.closest_to(ov)
                    await self.do(ov.attack(closestTownhall.position))  # this way we know the overlord is fleeing? idk

            if iteration % self.workerTransferInterval * 2 == 0 and self.getTimeInSeconds() > 6 * 60:
                # move drones away from enemies
                for drone in self.units(DRONE):
                    if self.known_enemy_units.not_structure.exists:
                        nearbyEnemies = self.known_enemy_units.not_structure.closer_than(15, drone.position).filter(
                            lambda x: x.type_id not in ignoreUnits)
                        if nearbyEnemies.exists and nearbyEnemies.amount >= 5:
                            townhallsWithoutEnemies = self.units & []
                            for th in self.townhalls.ready:
                                if not self.known_enemy_units.not_structure.closer_than(30, th.position).exists:
                                    townhallsWithoutEnemies.append(th)
                            if townhallsWithoutEnemies.exists:
                                closestTh = townhallsWithoutEnemies.closest_to(drone)
                                mf = self.state.mineral_field.closest_to(closestTh)
                                if mf is not None:
                                    await self.do(drone.gather(mf))

        # zergling scouting
        if iteration % self.microInterval == 0 and hasattr(self, "scoutingUnits"):
            if self.known_enemy_structures.exists:
                self.opponentInfo["scoutingUnitsNeeded"] = 1

            # update scouting data
            if not hasattr(self, "scoutingInfo"):
                self.scoutingInfo = []
                # add spawn locations if they are not in the list
                for base in self.enemy_start_locations:
                    isInList = next((x for x in self.scoutingInfo if x["location"].distance_to(base) < 10), None)
                    if isInList is None:
                        self.scoutingInfo.append({
                            "location": base,
                            "lastScouted": 0,
                            "assignedScoutTag": None
                        })
            else:
                # add existing enemy buildings
                if self.known_enemy_structures.exists:
                    for struct in self.known_enemy_structures:
                        isInList = next((x for x in self.scoutingInfo if x["location"] == struct.position.to2), None)
                        if isInList is None:
                            self.scoutingInfo.append({
                                "location": struct.position.to2,
                                "lastScouted": 0,  # only start scouting hidden bases at 5 minutes
                                "assignedScoutTag": None
                            })

                # TODO: remove enemy buildings that no longer exist

            # send scouting units
            # objective: scout for hidden bases, scout for attacks, scout if opponent expanded
            for lingTag in list(self.scoutingUnits)[:]:
                ling = self.units(ZERGLING).find_by_tag(lingTag)
                lingTarget = next((x for x in self.scoutingInfo if x["assignedScoutTag"] == lingTag), None)

                if ling is None:
                    if lingTarget is not None:
                        lingTarget["assignedScoutTag"] = None
                    self.scoutingUnits.discard(lingTag)
                    continue

                # flee from enemy units
                scoutUnitInDanger = (self.known_enemy_units.not_structure.closer_than(10, ling).filter(
                    lambda x: self.getSpecificUnitInfo(x)[0]["dps"] > 5) | self.known_enemy_structures.filter(
                    lambda x: x.type_id in [BUNKER, SPINECRAWLER, PHOTONCANNON])).exists or ling.health < 20
                if scoutUnitInDanger and self.townhalls.exists:
                    if ling.health < 20:
                        self.scoutingUnits.discard(lingTag)
                    if len(ling.orders) == 1 and ling.orders[0].ability.id in [
                        AbilityId.ATTACK]:  # here: attack-move means actively scouting a target
                        await self.do(ling.move(self.townhalls.closest_to(ling).position))
                    if lingTarget is not None and lingTarget["location"].distance_to(ling.position.to2) < 15:
                        # enemy units nearby, that means this could be the enemy defending an expansion!
                        lingTarget["lastScouted"] = self.getTimeInSeconds()
                        lingTarget["assignedScoutTag"] = None

                else:
                    # assign new scouting target and move to it
                    if lingTarget is None:
                        scoutTargets = [base for base in self.scoutingInfo if base["assignedScoutTag"] is None]
                        if len(scoutTargets) > 0:
                            scoutTarget = sorted(scoutTargets, key=lambda x: x["lastScouted"])[0]
                            scoutTarget["assignedScoutTag"] = lingTag
                            await self.do(ling.attack(scoutTarget["location"]))
                    # if scouting target reached, mark current game time and unassign ling
                    elif lingTarget["location"].distance_to(ling.position.to2) < 10:
                        # TODO: add scouting info if ling runs by other base
                        lingTarget["lastScouted"] = self.getTimeInSeconds()
                        lingTarget["assignedScoutTag"] = None
                    # if ling is move commanding (which means fleeing here) it will a-move back to the scouting target
                    elif ling.is_idle or len(ling.orders) == 1 and ling.orders[0].ability.id in [AbilityId.MOVE]:
                        # print("scout-ling amoving towards scout locations, dist: {}".format(lingTarget["location"].distance_to(ling.position.to2)))
                        await self.do(ling.attack(lingTarget["location"]))

        # update scouting info depending on visible units that we can see
        # if we see buildings that are not
        # depot, rax, bunker, spine crawler, spore, nydus, pylon, cannon, gateway
        # then assume that is the enemy spawn location
        ignoreScoutingBuildings = [SUPPLYDEPOT, SUPPLYDEPOTLOWERED, BARRACKS, BUNKER, SPINECRAWLER, SPORECRAWLER,
                                   NYDUSNETWORK, NYDUSCANAL, PYLON, PHOTONCANNON, GATEWAY]
        if self.opponentInfo["spawnLocation"] is None and len(self.enemy_start_locations) > 0:
            if self.known_enemy_units.structure.exists:
                enemyUnitsFiltered = self.known_enemy_units.structure.filter(
                    lambda x: x.type_id not in ignoreScoutingBuildings)
                if enemyUnitsFiltered.exists:
                    self.opponentInfo["spawnLocation"] = enemyUnitsFiltered.random.position.closest(
                        self.enemy_start_locations)

        # figure out the race of the opponent
        if self.opponentInfo["race"] is None and self.known_enemy_units.exists:
            self.opponentInfo["race"] = self.getUnitInfo(self.known_enemy_units.random, "race")
            racesDict = {
                Race.Terran.value: "terran",
                Race.Zerg.value: "zerg",
                Race.Protoss.value: "protoss",
            }
            self.opponentInfo["race"] = racesDict[self.opponentInfo["race"]]

        # figure out how much army supply enemy has:
        visibleEnemyUnits = self.known_enemy_units.not_structure.filter(
            lambda x: x.type_id not in [DRONE, SCV, PROBE, LARVA, EGG])
        for unit in visibleEnemyUnits:
            isUnitInInfo = next((x for x in self.opponentInfo["armyTagsScouted"] if x["tag"] == unit.tag), None)
            if isUnitInInfo is not None:
                self.opponentInfo["armyTagsScouted"].remove(isUnitInInfo)
            # if unit.tag not in self.opponentInfo["armyTagsScouted"]:
            if self.townhalls.ready.exists:
                self.opponentInfo["armyTagsScouted"].append({
                    "tag": unit.tag,
                    "scoutTime": self.getTimeInSeconds(),
                    "supply": self.getUnitInfo(unit) or 0,
                    "distanceToBase": self.townhalls.ready.closest_to(unit).distance_to(unit),
                })

        # get opponent army supply (scouted / visible)
        tempTime = self.getTimeInSeconds() - 30  # TODO: set the time on how long until the scouted army supply times out
        self.opponentInfo["armySupplyScouted"] = sum(
            x["supply"] for x in self.opponentInfo["armyTagsScouted"] if x["scoutTime"] > tempTime)
        self.opponentInfo["armySupplyScoutedClose"] = sum(x["supply"] for x in self.opponentInfo["armyTagsScouted"] if
                                                          x["scoutTime"] > tempTime and x["distanceToBase"] < 60)
        self.opponentInfo["armySupplyVisible"] = sum(self.getUnitInfo(x) or 0 for x in visibleEnemyUnits)

        # get opponent expansions
        if iteration % 20 == 0:
            enemyTownhalls = self.known_enemy_units.structure.filter(
                lambda x: x.type_id in [HATCHERY, LAIR, HIVE, COMMANDCENTER, PLANETARYFORTRESS, ORBITALCOMMAND, NEXUS])
            for th in enemyTownhalls:
                if len(self.opponentInfo["expansions"]) > 0 and th.position.closest(
                        self.opponentInfo["expansions"]).distance_to(th.position.to2) < 20:
                    continue
                if th.tag not in self.opponentInfo["expansionsTags"]:
                    self.opponentInfo["expansionsTags"].add(th.tag)
                    self.opponentInfo["expansions"].append(th.position.to2)
                    print("found a new enemy base!")
                    print(self.opponentInfo["expansions"])

        ################################
        ######### BUILDINGS MICRO
        ################################

        # cancel building if hp much lower than build progress to get some money back
        if iteration % self.microInterval == 0:
            ignoreBuildings = [CREEPTUMOR, CREEPTUMORBURROWED, CREEPTUMORQUEEN]
            for building in self.units.structure.not_ready.filter(lambda x: x.type_id not in ignoreBuildings):
                if building.health / building.health_max < building.build_progress - 0.5 or building.health / building.health_max < 0.05 and building.build_progress > 0.1:
                    await self.do(building(CANCEL))

        ################################
        ######### ROACH MICRO
        ################################

        # roach burrow micro when on low hp, unburrow when at high hp again
        if iteration % self.microInterval == 0:
            for roach in self.units(ROACH):
                # burrow when low hp
                if roach.health / roach.health_max < 5 / 10:
                    abilities = await self.get_available_abilities(roach)
                    if AbilityId.BURROWDOWN_ROACH in abilities and self.can_afford(BURROWDOWN_ROACH):
                        await self.do(roach(BURROWDOWN_ROACH))

            for roach in self.units(ROACHBURROWED):
                if 9 / 10 <= roach.health / roach.health_max <= 2 and roach.is_burrowed:
                    abilities = await self.get_available_abilities(roach)
                    # print(abilities)
                    if AbilityId.BURROWUP_ROACH in abilities and self.can_afford(BURROWUP_ROACH):
                        await self.do(roach(BURROWUP_ROACH))
                else:
                    nearbyDetection = self.known_enemy_units.filter(
                        lambda x: x.type_id in [OVERSEER, OBSERVERSIEGEMODE, OVERSEERSIEGEMODE, PHOTONCANNON,
                                                MISSILETURRET, RAVEN, SPORECRAWLER])
                    if nearbyDetection.exists:
                        pass  # TODO: implement, move away from enemy, or dont and tank damage
                    elif iteration % self.microInterval * 5 == 0:
                        nearbyGroundEnemies = self.known_enemy_units.not_structure.filter(lambda x: not x.is_flying)
                        if nearbyGroundEnemies.exists:
                            closest = nearbyGroundEnemies.closest_to(roach)
                            await self.do(roach.move(closest.position))

        if iteration % self.microInterval == 0:
            ################################
            ######### SKYZERG (preparation)
            ################################

            # skyzerg and queen management preparation
            if self.units(QUEEN).exists:
                if not hasattr(self, "transfuseProcess"):  # prevent mass transfusion (like overheal)
                    self.transfuseProcess = {}
                else:
                    # clear expired transfuses
                    for key in list(self.transfuseProcess.keys())[:]:
                        value = self.transfuseProcess[key]
                        if value["expiryTime"] < self.getTimeInSeconds():
                            self.transfuseProcess.pop(key)

                queensWith50Energy = self.units(QUEEN).filter(lambda x: x.energy >= 50)
                queensWith190Energy = queensWith50Energy.filter(lambda x: x.energy > 190)
                targetsBeingTransfusedTags = {x["target"] for x in self.transfuseProcess.values()}
                transfuseTargets = self.units.filter(
                    lambda x: x.tag not in targetsBeingTransfusedTags and x.type_id in [QUEEN, BROODLORD, CORRUPTOR,
                                                                                        SPINECRAWLER, OVERSEER,
                                                                                        ROACH] and (
                                          x.health_max - x.health >= 125 or x.health / x.health_max < 1 / 4))
                transfuseTargetsBuildings = self.units.structure.filter(
                    lambda x: x.health_max - x.health > 125 and x.type_id not in [SPINECRAWLER])

                for q in queensWith50Energy:
                    if q.tag in self.transfuseProcess:  # already transfusing
                        continue
                    targetsWithoutThisQueen = transfuseTargets.filter(lambda x: x.tag != q.tag)
                    if not targetsWithoutThisQueen.exists:
                        continue
                    transfuseTarget = targetsWithoutThisQueen.closest_to(q)
                    if transfuseTarget.distance_to(q) < 7:  # replace with general queen transfuse range
                        abilities = await self.get_available_abilities(q)
                        if AbilityId.TRANSFUSION_TRANSFUSION in abilities and self.can_afford(TRANSFUSION_TRANSFUSION):
                            self.transfuseProcess[q.tag] = {"target": transfuseTarget.tag,
                                                            "expiryTime": self.getTimeInSeconds() + 1}
                            targetsBeingTransfusedTags.add(transfuseTarget.tag)
                            transfuseTargets = transfuseTargets.filter(
                                lambda x: x.tag not in targetsBeingTransfusedTags)
                            await self.do(q(TRANSFUSION_TRANSFUSION, transfuseTarget))

                # queen transfuse buildings when in range and >= 190 energy
                for q in queensWith190Energy:
                    if q.tag in self.transfuseProcess:  # already transfusing
                        continue
                    if not transfuseTargetsBuildings.exists:
                        continue
                    transfuseTarget = transfuseTargetsBuildings.closest_to(q)
                    if transfuseTarget.distance_to(q) < 7:  # replace with general queen transfuse range
                        abilities = await self.get_available_abilities(q)
                        if AbilityId.TRANSFUSION_TRANSFUSION in abilities and self.can_afford(TRANSFUSION_TRANSFUSION):
                            self.transfuseProcess[q.tag] = {"target": transfuseTarget.tag,
                                                            "expiryTime": self.getTimeInSeconds() + 1}
                            targetsBeingTransfusedTags.add(transfuseTarget.tag)
                            transfuseTargetsBuildings = transfuseTargetsBuildings.filter(
                                lambda x: x.tag not in targetsBeingTransfusedTags)
                            await self.do(q(TRANSFUSION_TRANSFUSION, transfuseTarget))

            for vp in self.units(VIPER).filter(
                    lambda x: x.is_idle or len(x.orders) == 1 and x.orders[0].ability.id in [AbilityId.MOVE,
                                                                                             AbilityId.SCAN_MOVE,
                                                                                             AbilityId.ATTACK]):
                # if self.units(VIPER).exists:
                #     if len(vp.orders) == 1:
                #         abilities = await self.get_available_abilities(self.units(VIPER).random)
                #         print(vp.orders)
                #         print(abilities)

                # abduct targets: carrier, tempest, mothership, battlecruiser, siege tank, thor, lurker
                if vp.energy < 125:
                    # get energy
                    highHpBuildings = self.units.structure.filter(lambda x: x.health > 400)
                    if highHpBuildings.exists:
                        highHpBuilding = highHpBuildings.closest_to(vp)
                        await self.do(vp(VIPERCONSUMESTRUCTURE_VIPERCONSUME, highHpBuilding))
                else:
                    viperChoices = []
                    # para bomb, priotize!
                    if vp.energy >= 125:
                        enemyAirUnits = self.known_enemy_units.not_structure.filter(
                            lambda x: x.type_id in [MUTALISK, VIKINGFIGHTER, CORRUPTOR, BANSHEE, RAVEN, VOIDRAY,
                                                    PHOENIX, ORACLE, VIPER] and not x.has_buff(
                                PARASITICBOMB) and x.is_flying).closer_than(13, vp.position)
                        if enemyAirUnits.exists:
                            for target in enemyAirUnits:
                                viperChoices.append(vp(PARASITICBOMB_PARASITICBOMB, target))
                    # blinding cloud
                    if vp.energy >= 100:
                        targets = [SIEGETANKSIEGED, THOR, HYDRALISK, ARCHON]
                        targets2 = [MARINE, QUEEN, STALKER, SIEGETANK, MARAUDER, CYCLONE]
                        blindCloudTargets = self.known_enemy_units.not_structure.filter(
                            lambda x: x.type_id in targets and not x.has_buff(BLINDINGCLOUD)).closer_than(12,
                                                                                                          vp.position)
                        if not blindCloudTargets.exists:
                            blindCloudTargets = self.known_enemy_units.not_structure.filter(
                                lambda x: x.type_id.value in targets2 and not x.has_buff(BLINDINGCLOUD)).closer_than(12,
                                                                                                                     vp.position)
                        if blindCloudTargets.exists:
                            for target in blindCloudTargets:
                                viperChoices.append(vp(BLINDINGCLOUD_BLINDINGCLOUD, target.position))
                    # abduct
                    if vp.energy >= 75:
                        targets = [SIEGETANKSIEGED, THOR, LURKER, LURKERMPBURROWED, ARCHON, MOTHERSHIP, CARRIER,
                                   TEMPEST, LIBERATOR]
                        targets2 = [QUEEN, STALKER, SIEGETANK, MARAUDER, CYCLONE]
                        abductTargets = self.known_enemy_units.not_structure.filter(
                            lambda x: x.type_id in targets).closer_than(11, vp.position)
                        if not abductTargets.exists:
                            abductTargets = self.known_enemy_units.not_structure.filter(
                                lambda x: x.type_id in targets2).closer_than(11, vp.position)
                        if abductTargets.exists:
                            for target in abductTargets:
                                viperChoices.append(vp(EFFECT_ABDUCT, target))

                    if len(viperChoices) > 0:
                        choice = random.choice(viperChoices)
                        await self.do(choice)

            # move corruptors to random position on map if we see no enemy structures
            if iteration % self.microInterval * 10 == 0:
                if (not self.known_enemy_structures.exists):
                    stepSize = 3
                    pointsOnPlayableMap = [Point2((x, y)) \
                                           for x in range(self._game_info.playable_area[0] + stepSize,
                                                          self._game_info.playable_area[0] +
                                                          self._game_info.playable_area[2], stepSize) \
                                           for y in range(self._game_info.playable_area[1] + stepSize,
                                                          self._game_info.playable_area[1] +
                                                          self._game_info.playable_area[3], stepSize)]
                    for cr in self.units(CORRUPTOR).idle:
                        await self.do(cr.attack(random.choice(pointsOnPlayableMap)))


                elif self.known_enemy_structures.filter(lambda x: x.is_flying).exists:
                    flyingBuildings = self.known_enemy_structures.filter(lambda x: x.is_flying)
                    # make idle corruptors amove to them
                    for cr in self.units(CORRUPTOR).idle:
                        await self.do(cr.attack(flyingBuildings.random.position))

        ################################
        ######### UNIT MANAGEMENT
        ################################

        unitsAssignedToGroups = set().union(
            *[group.getMyUnitTags() for group in [self.myDefendGroup, self.myAttackGroup, self.mySupportGroup] if
              group is not None])

        # clear defendgroup, attackgroup, supportgroup if they are empty, this way a new attackgroup will be formed
        if self.myDefendGroup is not None and len(self.myDefendGroup.getMyUnitTags()) < 1:
            self.myDefendGroup = None
        if self.myAttackGroup is not None and (len(self.myAttackGroup.getMyUnitTags()) < 1 or self.supply_used < 140):
            print("attackgroup disbanded because lowish on supply")
            self.myAttackGroup = None
            self.mySupportGroup = None
        # if self.mySupportGroup is not None and len(self.mySupportGroup.getMyUnitTags()) < 1:
        #     self.mySupportGroup = None

        # make queens and raoches defend stuff nearby
        if self.myDefendGroup is None:
            self.myDefendGroup = ManageThreats(self._client, self._game_data)
            self.myDefendGroup.maxAssignedPerUnit = 2
            self.myDefendGroup.retreatWhenHp = 0.25
            self.myDefendGroup.mode = "distributeEqually"

        if iteration % self.microInterval * 5 == 0:
            # add threats: all enemy units that are closer than 30 to nearby townhalls (which are completed)
            thisRoundAddedThreats = set()
            oldThreats = self.myDefendGroup.getThreatTags()
            for th in self.townhalls.ready:
                enemiesCloseToTh = self.known_enemy_units.closer_than(self.defendRangeToTownhalls, th.position)
                self.myDefendGroup.addThreat(enemiesCloseToTh)
                thisRoundAddedThreats |= {x.tag for x in enemiesCloseToTh}
            # threats that are outside the 30 range or no longer visible on map:
            notVisibleOrOutsideRangeThreats = oldThreats - thisRoundAddedThreats
            self.myDefendGroup.clearThreats(notVisibleOrOutsideRangeThreats)

            # add units to defense
            myDefendUnits = self.units & []
            myDefendUnits += self.units(ROACH)
            myDefendUnits += self.units(OVERSEER)
            myDefendUnits += self.units(ROACHBURROWED)
            myDefendUnits += self.units(BROODLORD)
            myDefendUnits += self.units(BROODLORDCOCOON)
            myDefendUnits += self.units(VIPER)
            myDefendUnits += self.units(CORRUPTOR)
            myDefendUnits += self.units(ZERGLING).filter(lambda x: x.tag not in self.scoutingUnits)
            # remove queens after 5 mins (used for early game defense):
            if self.getTimeInSeconds() < 5 * 60 and self.opponentInfo["armySupplyScoutedClose"] > 2:
                self.myDefendGroup.addDefense(self.units(QUEEN))
            elif hasattr(self, "queensAssignedHatcheries"):
                myDefendUnits += self.units(QUEEN).filter(lambda q: q.tag not in self.queensAssignedHatcheries)
                self.myDefendGroup.removeDefense(
                    self.units(QUEEN).filter(lambda q: q.tag in self.queensAssignedHatcheries))
            # self.myDefendGroup.addDefense(self.units(ROACH))
            # self.myDefendGroup.addDefense(self.units(ZERGLING).filter(lambda x:x.tag not in self.scoutingUnits))
            myDefendUnits = myDefendUnits.filter(lambda x: x.tag not in unitsAssignedToGroups)
            self.myDefendGroup.addDefense(myDefendUnits)
            self.myDefendGroup.removeDefense(self.units(ZERGLING).filter(lambda x: x.tag in self.scoutingUnits))

            # setting retreat location
            if self.units(SPINECRAWLER).ready.exists:
                self.myDefendGroup.setRetreatLocations(self.units(SPINECRAWLER), removePreviousLocations=True)
            elif self.townhalls.exists:
                self.myDefendGroup.setRetreatLocations(self.townhalls, removePreviousLocations=True)

            # attack when we have a big army
            if self.myAttackGroup is None:
                if all([
                    # check if we have: requirement to attack = roach burrow
                    not self.waitForRoachBurrowBeforeAttacking or (
                            self.units(DRONE).exists and AbilityId.BURROWDOWN_DRONE in (
                    await self.get_available_abilities(self.units(DRONE).random))),
                    # check if we have: requirement to attack = at least 1 broodlord
                    not self.waitForBroodlordsBeforeAttacking or self.units(BROODLORD).exists
                ]):
                    myArmy = self.units(ROACH) | self.units(ROACHBURROWED) | self.units(BROODLORD) | self.units(
                        BROODLORDCOCOON) | self.units(EGG).filter(lambda x: x.orders[0].ability in [ROACH])
                    mySupportUnits = self.units(VIPER) | self.units(CORRUPTOR) | self.units(OVERSEER) | self.units(
                        EGG).filter(lambda x: x.orders[0].ability in [CORRUPTOR, VIPER])
                    if hasattr(self, "queensAssignedHatcheries"):
                        mySupportUnits.extend(
                            self.units(QUEEN).filter(lambda x: x.tag not in self.queensAssignedHatcheries))

                    if self.supply_used >= 195:
                        # disband defendgroup once when creating attackgroup, reassign new units to it when they spawn
                        self.myDefendGroup = None

                        # create attackgroup, has no retreat
                        knownEnemyUnitsFiltered = self.known_enemy_units.filter(
                            lambda x: x.type_id not in [OVERLORD, OVERSEER, OVERLORDTRANSPORT, OVERSEERSIEGEMODE])
                        self.myAttackGroup = ManageThreats(self._client, self._game_data)
                        print("{} - attack started!".format(self.getTimeInSeconds()))
                        self.myAttackGroup.clumpUpEnabled = True
                        self.myAttackGroup.addThreat(knownEnemyUnitsFiltered)
                        self.myAttackGroup.maxAssignedPerUnit = 2
                        self.myAttackGroup.addDefense(myArmy)
                        self.myAttackGroup.attackLocations = self.enemy_start_locations

                        # create support group that helps the attackgroup
                        self.mySupportGroup = ManageThreats(self._client, self._game_data)
                        self.mySupportGroup.addThreat(myArmy)
                        self.mySupportGroup.addDefense(mySupportUnits)
                        self.mySupportGroup.maxAssignedPerUnit = 5
                        self.mySupportGroup.mode = "distributeEqually"
                        self.mySupportGroup.retreatWhenHp = 0.25
                        self.mySupportGroup.treatThreatsAsAllies = True
                        if self.townhalls.exists:
                            self.mySupportGroup.setRetreatLocations(self.townhalls)

            else:
                # keep adding corruptors, broodlords and vipers to the groups, because corruptors will constantly morph
                myArmy = self.units(ROACH) | self.units(ROACHBURROWED) | self.units(BROODLORD) | self.units(
                    BROODLORDCOCOON)
                mySupportUnits = self.units(VIPER) | self.units(CORRUPTOR) | self.units(OVERSEER)
                knownEnemyUnitsFilteredInRange = self.known_enemy_units.filter(
                    lambda x: x.type_id not in [OVERLORD, OVERSEER, OVERLORDTRANSPORT,
                                                OVERSEERSIEGEMODE] and myArmy.closer_than(25, x.position).exists)
                knownEnemyUnitsFilteredOutsideRange = self.known_enemy_units.filter(
                    lambda x: x.type_id not in [OVERLORD, OVERSEER, OVERLORDTRANSPORT,
                                                OVERSEERSIEGEMODE] and not myArmy.closer_than(30, x.position).exists)
                knownEnemyUnitsFilteredOutsideRangeTags = {x.tag for x in knownEnemyUnitsFilteredOutsideRange}
                if hasattr(self, "queensAssignedHatcheries"):
                    mySupportUnits.extend(
                        self.units(QUEEN).filter(lambda x: x.tag not in self.queensAssignedHatcheries))
                if self.myAttackGroup is not None:
                    # keep updating the enemy unit list
                    self.myAttackGroup.addThreat(knownEnemyUnitsFilteredInRange)
                    self.myAttackGroup.clearThreats(knownEnemyUnitsFilteredOutsideRangeTags)
                    if self.allowedToResupplyAttackGroups:
                        self.myAttackGroup.addDefense(myArmy)

                if self.mySupportGroup is not None:
                    # keep updating the support list
                    self.mySupportGroup.addThreat(myArmy)
                    self.mySupportGroup.removeDefense(myArmy)  # removes corruptors that morphed to broodlords
                    if self.allowedToResupplyAttackGroups:
                        self.mySupportGroup.addDefense(mySupportUnits)

        # micro units, assign them targets etc (from the assigned unit tags above)
        if iteration % self.microInterval == 0:
            if self.myDefendGroup is not None:
                # all units (that can shoot) except scouting units and inject queens are put in here
                await self.myDefendGroup.update(self.units, self.known_enemy_units, self.enemy_start_locations,
                                                iteration)
            if self.myAttackGroup is not None:
                # contains roaches, burrow roaches, broodlords
                # this group will not retreat
                await self.myAttackGroup.update(self.units, self.known_enemy_units, self.enemy_start_locations,
                                                iteration)
            if self.mySupportGroup is not None:
                # contains queens, corruptors, vipers
                await self.mySupportGroup.update(self.units, self.known_enemy_units, self.enemy_start_locations,
                                                 iteration)

        ################################
        ######### DEFENSIVE REACTIONS (buildings)
        ################################

        # make spines if we scouted that opponent has large army supply at <5 mins
        if iteration % self.buildStuffInverval == 0 and 120 < self.getTimeInSeconds() < 240 and self.opponentInfo[
            "armySupplyScoutedClose"] > 2 and len(
                self.opponentInfo["expansions"]) < 2 and self.townhalls.ready.amount > 1 and self.units(
                SPINECRAWLER).amount < min(3,
                                           self.opponentInfo["armySupplyScoutedClose"] // 2) and self.already_pending(
                SPINECRAWLER) < 1:
            if self.currentDroneCountIncludingPending > 10:
                self.workerProductionEnabled.append(False)
            furthestExpansion = self.opponentInfo["furthestAwayExpansion"] or random.choice(self.enemy_start_locations)

            if self.can_afford(
                    SPINECRAWLER) and self.workers.exists and self.townhalls.exists and furthestExpansion is not None:
                newestBase = max(self.townhalls.ready, key=lambda x: x.tag)

                if furthestExpansion.position.to2 == newestBase.position.to2:
                    print("ERROR in spine placement")
                else:
                    loc = newestBase.position.to2.towards(furthestExpansion.position.to2, 3)
                    loc = await self.find_placement(SPINECRAWLER, loc, placement_step=3, minDistanceToResources=4)
                    w = self.workers.closest_to(loc)
                    if self.can_afford(SPINECRAWLER) and loc is not None:
                        err = await self.do(w.build(SPINECRAWLER, loc))

        # make spores if we scouted oracle / banshee / mutas / corruptors
        if iteration % self.buildStuffInverval == 0:
            airUnits = self.known_enemy_units.filter(
                lambda x: x.type_id in [ORACLE, BANSHEE, MUTALISK, CORRUPTOR, DARKSHRINE, STARGATE, PHOENIX,
                                        DARKTEMPLAR])  # STARPORTTECHLAB
            if airUnits.exists and self.already_pending(SPORECRAWLER) < 1:
                if self.getTimeInSeconds() < 6 * 60:
                    self.workerProductionEnabled.append(False)
                if self.can_afford(SPORECRAWLER):
                    for th in self.townhalls.ready:
                        # spore already exists?
                        if self.units(SPORECRAWLER).exists and self.units(SPORECRAWLER).closest_to(th).distance_to(
                                th) < 10:
                            continue
                        mfs = self.state.mineral_field.closer_than(10, th.position.to2)
                        # if mineral fields are nearby? dont make spores at a mined out base
                        if not mfs.exists or not self.workers.exists:
                            continue
                        if self.centerOfUnits(mfs).to2 != th.position.to2:
                            loc = self.centerOfUnits(mfs).towards(th.position, 4)
                            loc = await self.find_placement(SPORECRAWLER, loc, placement_step=1,
                                                            minDistanceToResources=0)
                            w = self.workers.closest_to(loc)
                            if loc is not None and self.can_afford(SPORECRAWLER):
                                await self.do(w.build(SPORECRAWLER, loc))

        ################################
        ######### DEFENSIVE REACTION (worker rush, cannon rush)
        ################################

        # worker rush defense
        # cannon rush defense: if a probe + pylon were scouted near any of our building and gametime < 4:00: attack probe with 1 drone and each scouted cannon with 4 drones
        if self.townhalls.exists and self.getTimeInSeconds() < 5 * 60:

            cannonRushUnits = self.units & []
            for th in self.townhalls:
                cannonRushUnits |= self.known_enemy_units.closer_than(30, th.position)
            pylons = cannonRushUnits(PYLON)
            probes = cannonRushUnits.filter(lambda x: x.type_id in [PROBE, SCV, DRONE, ZERGLING])
            cannons = cannonRushUnits.filter(lambda x: x.type_id in [PHOTONCANNON, SPINECRAWLER])

            if (pylons.amount + probes.amount > 0 or cannons.amount > 0) and self.opponentInfo[
                "armySupplyVisible"] < 3 and self.units(SPINECRAWLER).ready.amount < 1 and self.units(QUEEN).amount < 4:
                if not hasattr(self, "defendCannonRushProbes"):
                    self.defendCannonRushProbes = {}
                    self.defendCannonRushCannons = {}

                assignedDroneTagsSets = [x for x in self.defendCannonRushProbes.values()] + [x for x in
                                                                                             self.defendCannonRushCannons.values()]
                assignedDroneTags = set()
                for sett in assignedDroneTagsSets:
                    assignedDroneTags |= sett
                unassignedDrones = self.units(DRONE).filter(lambda x: x.tag not in assignedDroneTags and x.health > 6)
                unassignedDroneTags = set((x.tag for x in unassignedDrones))

                # adding probe and cannons as threats
                for probe in probes:
                    if probe.tag not in self.defendCannonRushProbes:
                        self.defendCannonRushProbes[probe.tag] = set()
                for cannon in cannons:
                    if cannon.tag not in self.defendCannonRushCannons:
                        self.defendCannonRushCannons[cannon.tag] = set()

                # filter out dead units chasing probe
                for probeTag, droneTags in self.defendCannonRushProbes.items():
                    drones = self.units(DRONE).filter(lambda x: x.tag in droneTags)
                    lowHpDrones = drones.filter(lambda x: x.health < 7)
                    for drone in lowHpDrones:
                        mf = self.state.mineral_field.closest_to(self.townhalls.closest_to(drone))
                        await self.do(drone.gather(mf))
                        drones.remove(drone)
                    self.defendCannonRushProbes[probeTag] = set(x.tag for x in drones)  # clear dead drones
                    # if probe not alive anymore or outside of range, send drones to mining
                    # print(drones, unassignedDrones)
                    if probeTag not in [x.tag for x in probes]:
                        self.defendCannonRushProbes.pop(probeTag)
                        break  # iterating over a changing dictionary

                    # if probe still alive, check if it has a drone chasing it
                    elif drones.amount < 1 and unassignedDrones.amount > 0:
                        # if no drones chasing it, get a random drone and assign it to probe
                        probe = probes.find_by_tag(probeTag)
                        newDrone = unassignedDrones.closest_to(probe)
                        mf = self.state.mineral_field.closest_to(self.townhalls.closest_to(newDrone))
                        if probe is not None and newDrone is not None:
                            unassignedDroneTags.remove(newDrone.tag)
                            unassignedDrones.remove(newDrone)  # TODO: need to test if this works
                            # unassignedDrones = unassignedDrones.filter(lambda x: x.tag in unassignedDroneTags)
                            self.defendCannonRushProbes[probeTag].add(newDrone.tag)
                            await self.do(newDrone.attack(probe))
                            await self.do(newDrone.gather(mf, queue=True))

                # filter out dead units attacking a cannon
                for cannonTag, droneTags in self.defendCannonRushCannons.items():
                    drones = self.units(DRONE).filter(lambda x: x.tag in droneTags)
                    self.defendCannonRushCannons[cannonTag] = set(x.tag for x in drones)  # clear dead drones
                    # if cannon not alive anymore or outside of range, send drones to mining
                    if cannonTag not in [x.tag for x in cannons]:
                        self.defendCannonRushCannons.pop(cannonTag)
                        break  # iterating over a changing dictionary
                    # if probe still alive, check if it has a drone chasing it
                    elif drones.amount < 4 and unassignedDrones.amount > 0:
                        # if no drones chasing it, get a random drone and assign it to probe
                        for i in range(4 - drones.amount):
                            if unassignedDrones.amount <= 0:
                                break
                            cannon = cannons.find_by_tag(cannonTag)
                            newDrone = unassignedDrones.closest_to(cannon)
                            mf = self.state.mineral_field.closest_to(self.townhalls.closest_to(newDrone))
                            if cannon is not None and newDrone is not None:
                                unassignedDroneTags.remove(newDrone.tag)
                                unassignedDrones.remove(newDrone)
                                self.defendCannonRushCannons[cannonTag].add(newDrone.tag)
                                await self.do(newDrone.attack(cannon))
                                await self.do(newDrone.gather(mf, queue=True))

        ################################
        ######### DEFENSIVE REACTION (mass lings / 1base allin)
        ################################

        # TODO: implement defensive maneuvers:
        # proxy rax
        # 12 pool
        # proxy gate

        # if pool is done, make queens
        if all(self.queenProductionEnabled) and self.units(SPAWNINGPOOL).ready.exists and self.units(
                QUEEN).amount + self.already_pending(QUEEN) < self.totalQueenLimit and (
                self.units(HATCHERY) | self.units(
                HIVE)).ready.idle.exists and iteration % self.buildStuffInverval == 0 and self.supply_left > 1 and self.supply_used < 197:
            # pause worker production to squeeze out first N queens
            if len(self.units(QUEEN)) + self.already_pending(QUEEN) < self.priotizeFirstNQueens:
                self.workerProductionEnabled.append(False)
            for hatch in (self.units(HATCHERY) | self.units(HIVE)).ready.idle:
                if self.can_afford(QUEEN):
                    err = await self.do(hatch.train(QUEEN))
                    if not err:
                        break

        # make more drones
        # print(self.workerProductionEnabled)
        if all(self.workerProductionEnabled) and iteration % self.buildStuffInverval == 0:
            if self.supply_left > 0 and self.supply_used < 198 and self.can_afford(DRONE) and self.units(
                    LARVA).exists and self.currentDroneCountIncludingPending < self.droneLimit:
                dronesAffordable = min(198 - self.supply_used,
                                       self.droneLimit - self.units(DRONE).amount + self.already_pending(DRONE),
                                       self.supply_left // 1, self.minerals // 50, self.units(LARVA).amount)
                # print("current drones: {}, affordable: {}".format(self.units(DRONE).amount + self.already_pending(DRONE), dronesAffordable))
                for count, larva in enumerate(self.units(LARVA)):
                    if count >= dronesAffordable or count + self.currentDroneCountIncludingPending >= self.droneLimit:  # because drones in extractor appear as "missing" and dont get counted
                        break
                    if self.can_afford(DRONE):
                        await self.do(larva.train(DRONE))

        ################################
        ######### TESTING
        ################################

        # print(1, self.getUnitInfo(self.units(HATCHERY).first))
        # print(2, self.getUnitInfo(HATCHERY))

        # self._client.leave()


def main():
    # sc2.run_game(sc2.maps.get("(2)RedshiftLE"), [
    #     Bot(Race.Zerg, CreepyBot()),
    #     Bot(Race.Protoss, CannonRushBot())
    # ], realtime=False)

    # sc2.run_game(sc2.maps.get("(2)16-BitLE"), [
    #     Bot(Race.Zerg, CreepyBot()),
    #     Bot(Race.Protoss, CannonRushBot())
    # ], realtime=False)

    # sc2.run_game(sc2.maps.get("(2)RedshiftLE"), [
    #     Bot(Race.Zerg, CreepyBot()),
    #     Bot(Race.Protoss, ThreebaseVoidrayBot())
    # ], realtime=False)

    # sc2.run_game(sc2.maps.get("(2)16-BitLE"), [
    #     Bot(Race.Zerg, CreepyBot()),
    #     Bot(Race.Zerg, ZergRushBot())
    # ], realtime=False)

    # sc2.run_game(sc2.maps.get("(2)RedshiftLE"), [
    #     Bot(Race.Zerg, CreepyBot()),
    #     Bot(Race.Zerg, ZergRushBot())
    # ], realtime=False)

    # sc2.run_game(sc2.maps.get("(2)RedshiftLE"), [
    #     Bot(Race.Zerg, CreepyBot()),
    #     Computer(Race.Zerg, Difficulty.Easy)
    # ], realtime=False)

    # sc2.run_game(sc2.maps.get("(2)RedshiftLE"), [
    #     Bot(Race.Zerg, CreepyBot()),
    #     Computer(Race.Random, Difficulty.VeryHard)
    # ], realtime=False)

    # sc2.run_game(sc2.maps.get("(4)DarknessSanctuaryLE"), [
    #     Bot(Race.Zerg, CreepyBot()),
    #     Computer(Race.Random, Difficulty.CheatMoney)
    # ], realtime=False)

    sc2.run_game(sc2.maps.get("(2)16-BitLE"), [
        Bot(Race.Zerg, CreepyBot()),
        Computer(Race.Protoss, Difficulty.CheatInsane)
    ], realtime=False)

    # sc2.run_game(sc2.maps.get("(2)RedshiftLE"), [
    #     Human(Race.Protoss),
    #     Bot(Race.Zerg, CreepyBot())
    # ], realtime=True)


if __name__ == '__main__':
    main()