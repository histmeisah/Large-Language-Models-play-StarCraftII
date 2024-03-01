import random
from typing import Set, List, Tuple

from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty
from sc2.data import Race
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.main import run_game
from sc2.player import Bot, Computer, Human
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units

ladder_map_pool_2022_07 = ["Data-C", "Moondance", "Stargazers", "Waterfall", "Tropical Sacrifice", "Inside and Out",
                           "Cosmic Sapphire"]
play_map = ladder_map_pool_2022_07[random.randint(0,6)]

class marine_tank_Bot(BotAI):
    # (55.5, 157.5)左上
    # (160.5, 46.5)右下
    def __init__(self):
        self.marine_tag_list: Units = []
        self.army_units: Units = []
        self.tank_tag_list: Units = []
        self.medic_tag_list: Units = []
        self.barrack_tag_list = []
        self.factory_tag_list = []
        self.starport_tag_list = []
        self.worker_tag_list = []
        self.center_tag_list = []
        self.bunker_tag_list = []
        self.upgrade_tag_list = []
        self.flag = True
        self.add_on = False
        self.attacking = False
        self.rally_defend = True
        self.producing_marine = False
        self.producing_tank = False
        self.producing_medic = False
        self.auto_mode = False
        self.producing_marauder = False

        self.reaper_attack = True
        self.vespenetrigger = False
        self.trigger_extra_supply = False

    async def on_step(self, iteration: int):
        await self.distribute_workers()
        if self.flag == True:
            await self.produce_worker()
        await self.procedure()
        await self.building_supply()
        await self.burrow_depot()
        await self.upgrade_center()
        await self.oc_drop_mule()
        await self.reaper_scout()
        await self.exchange_add_on()
        await self.check_geysers()
        await self.marine_movement()
        await self.med_movement()
        await self.tank_movement()
        await self.expansion()
        await self.defend()
        await self.attack()
        if self.auto_mode == True:
            await self.add_on_after_exp()
        # if self.rally_defend == True:
        #     await self.back_to_rally()

        if self.reaper_attack == True:
            await self.reaper_scout()

        await self.rally_units(iteration)
        await self.fill_bunker()

        if self.vespenetrigger == True:
            await self.build_vespene()

        if self.producing_tank == True:
            await self.train_tank()

        if self.producing_marine == True:
            await self.train_marine()

        if self.producing_medic == True:
            await self.train_medic()

    async def produce_worker(self):
        # if used commander_center , when upgrade to the orbital , the commander_center item will return null
        if self.townhalls and self.supply_workers <= 70:
            commander_center = self.townhalls.random
            if commander_center.is_idle and self.can_afford(UnitTypeId.SCV):
                commander_center.train(UnitTypeId.SCV)

    async def procedure(self):
        print(self.time_formatted, self.minerals, self.vespene, self.enemy_units, self.enemy_start_locations)
        if self.time_formatted == '00:01':
            if self.start_location == Point2((160.5, 46.5)):
                self.Location = -1  # detect location
            else:
                self.Location = 1
        if self.time_formatted == '00:43' and not self.already_pending(UnitTypeId.BARRACKS):
            print(self.minerals)
            worker_candidates = self.workers.filter(lambda worker: (
                                                                           worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)

            place_postion = self.start_location.position + Point2((self.Location * 10, 0))
            placement_position = await self.find_placement(UnitTypeId.BARRACKS, near=place_postion, placement_step=4)
            if placement_position:
                build_worker = worker_candidates.closest_to(placement_position)
                build_worker.build(UnitTypeId.BARRACKS, placement_position)

        elif (self.time_formatted == '00:47' and not self.already_pending(UnitTypeId.REFINERY)) or self.structures(
                UnitTypeId.REFINERY) == 0:
            for center in self.structures(UnitTypeId.COMMANDCENTER):
                vespenes = self.vespene_geyser.closer_than(15, center)
                for vespene in vespenes:
                    if self.can_afford(UnitTypeId.REFINERY):
                        await self.build(UnitTypeId.REFINERY, vespenes[0])

        elif self.time_formatted == '01:35':
            self.flag = False
            ready = self.structures(UnitTypeId.BARRACKS).random
            ready.train(UnitTypeId.REAPER)
            await self.upgrade_center()

        elif self.time_formatted == '01:55':
            print(self.already_pending(UnitTypeId.COMMANDCENTER))
            print(self.can_afford(UnitTypeId.COMMANDCENTER))
            if not self.already_pending(UnitTypeId.COMMANDCENTER) and self.can_afford(UnitTypeId.COMMANDCENTER):
                location = await self.get_next_expansion()
                print(location)
                if location:
                    worker = self.select_build_worker(location)
                    if worker and self.can_afford(UnitTypeId.COMMANDCENTER):
                        worker.build(UnitTypeId.COMMANDCENTER, location)

        elif self.time_formatted == '02:20':
            print(self.minerals)
            print(self.vespene)
            worker_candidates = self.workers.filter(lambda worker: (
                                                                           worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
            place_postion = self.start_location.position + Point2((0, -self.Location * 7))
            placement_position = await self.find_placement(UnitTypeId.BARRACKS, near=place_postion, placement_step=2)
            if placement_position:
                build_worker = worker_candidates.closest_to(placement_position)
                build_worker.build(UnitTypeId.FACTORY, placement_position)

        elif self.time_formatted == '02:35':
            if self.can_afford(UnitTypeId.BARRACKSREACTOR):
                bar = self.structures(UnitTypeId.BARRACKS).random
                bar(AbilityId.BUILD_TECHLAB_BARRACKS)
                if bar not in self.barrack_tag_list:
                    self.barrack_tag_list.append(bar)




        elif self.time_formatted == '02:45':
            if self.can_afford(UnitTypeId.COMMANDCENTER):
                location = await self.get_next_expansion()
                if location:
                    worker = self.select_build_worker(location)
                    if worker and self.can_afford(UnitTypeId.COMMANDCENTER):
                        worker.build(UnitTypeId.COMMANDCENTER, location)




        elif self.time_formatted == '03:10':
            if self.can_afford(UnitTypeId.BARRACKS) and not self.already_pending(UnitTypeId.BARRACKS):
                building_place = self.structures(UnitTypeId.BARRACKS).random.position + Point2((0, -self.Location * 3))
                placement_position = await self.find_placement(UnitTypeId.BARRACKS, near=building_place,
                                                               placement_step=2)
                worker_candidates = self.workers.filter(lambda worker: (
                                                                               worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
                if placement_position:
                    build_worker = worker_candidates.closest_to(placement_position)
                    build_worker.build(UnitTypeId.BARRACKS, placement_position)


        elif self.time_formatted == '03:25':
            fac = self.structures(UnitTypeId.FACTORY).random
            fac(AbilityId.BUILD_TECHLAB_FACTORY)
            if fac not in self.factory_tag_list:
                self.factory_tag_list.append(fac)

        elif self.time_formatted == "03:40":
            for tech in self.structures(UnitTypeId.BARRACKSTECHLAB):
                if self.can_afford(UpgradeId.STIMPACK):
                    tech.research(UpgradeId.STIMPACK)

            # if len(self.building_tag_list) == 0:
            #     Barrack = self.structures(UnitTypeId.BARRACKS).random
            #     Factory = self.structures(UnitTypeId.FACTORY).random
            #     self.building_tag_list.append(Barrack.tag)
            #     self.building_tag_list.append(Factory.tag)
            #     print(self.building_tag_list)
            #     print(Barrack,Factory)
            #     self.position_barrack = Barrack.position
            #     self.position_factory = Factory.position
            # else:
            #     print(self.structures.find_by_tag(self.building_tag_list[0]).is_ready)
            #     self.structures.find_by_tag(self.building_tag_list[0])(AbilityId.LIFT)
            #     print(self.structures.find_by_tag(self.building_tag_list[1]).is_ready)
            #     self.structures.find_by_tag(self.building_tag_list[1])(AbilityId.LIFT_FACTORY)


        elif self.time_formatted == '03:50':
            self.vespenetrigger = True


        elif self.time_formatted == '04:10':
            for bar in self.structures(UnitTypeId.BARRACKS):
                if not bar.has_add_on:
                    bar(AbilityId.BUILD_REACTOR_BARRACKS)
                    if bar not in self.barrack_tag_list:
                        self.barrack_tag_list.append(bar)

        elif self.time_formatted == '04:26':
            if self.can_afford(UnitTypeId.STARPORT) and not self.already_pending(UnitTypeId.STARPORT):
                building_place = self.start_location + Point2((-self.Location * 6, -self.Location * 6))
                placement_position = await self.find_placement(UnitTypeId.STARPORT, near=building_place,
                                                               placement_step=2)
                worker_candidates = self.workers.filter(lambda worker: (
                                                                               worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
                if placement_position:
                    build_worker = worker_candidates.closest_to(placement_position)
                    build_worker.build(UnitTypeId.STARPORT, placement_position)

            self.producing_marine = True




        elif self.time_formatted == '04:45':
            worker_candidate2 = self.workers.filter(lambda worker: (
                                                                           worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action).random
            location2 = self.structures(UnitTypeId.ORBITALCOMMAND).find_by_tag(
                self.center_tag_list[1]).position + Point2((self.Location * 8, -self.Location * 1))
            placement_position = await self.find_placement(UnitTypeId.ENGINEERINGBAY, near=location2,
                                                           placement_step=1)
            if self.can_afford(UnitTypeId.ENGINEERINGBAY) and self.already_pending(UnitTypeId.ENGINEERINGBAY) < 2:
                worker_candidate2.build(UnitTypeId.ENGINEERINGBAY, placement_position)

            if self.can_afford(UnitTypeId.BUNKER) and self.already_pending(UnitTypeId.BUNKER) < 1:
                place_postion = self.structures(UnitTypeId.ORBITALCOMMAND).find_by_tag(
                    self.center_tag_list[1]).position + Point2((self.Location * 9, -self.Location * 9))
                placement_position2 = await self.find_placement(UnitTypeId.BUNKER, near=place_postion,
                                                                placement_step=2)

                worker = self.workers.filter(lambda worker: (
                                                                    worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action).random
                worker.build(UnitTypeId.BUNKER, placement_position2)





        elif self.time_formatted == '05:10':
            for star in self.structures(UnitTypeId.STARPORT):
                star(AbilityId.BUILD_REACTOR_STARPORT)
                if star.tag not in self.starport_tag_list:
                    self.starport_tag_list.append(star)
            self.producing_tank = True

            for eb in self.structures(UnitTypeId.ENGINEERINGBAY):
                if eb not in self.upgrade_tag_list:
                    self.upgrade_tag_list.append(eb)

        elif self.time_formatted == '05:30':
            for tech in self.structures(UnitTypeId.BARRACKSTECHLAB):
                if self.can_afford(UpgradeId.SHIELDWALL):
                    tech.research(UpgradeId.SHIELDWALL)


        elif self.time_formatted == '05:40':
            self.producing_medic = True
            if self.can_afford(UnitTypeId.BARRACKS) and not self.already_pending(UnitTypeId.BARRACKS):
                building_place = self.barrack_tag_list[-1].position + Point2((0, -self.Location * 3))
                placement_position = await self.find_placement(UnitTypeId.BARRACKS, near=building_place,
                                                               placement_step=2)
                worker_candidates = self.workers.filter(lambda worker: (
                                                                               worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
                if placement_position:
                    build_worker = worker_candidates.closest_to(placement_position)
                    build_worker.build(UnitTypeId.BARRACKS, placement_position)

            self.trigger_extra_supply = True

        elif self.time_formatted == '06:00':
            if self.can_afford(UpgradeId.TERRANINFANTRYARMORSLEVEL1):
                self.upgrade_tag_list[0].research(UpgradeId.TERRANINFANTRYARMORSLEVEL1)
            if self.can_afford(UpgradeId.TERRANINFANTRYARMORSLEVEL1):
                self.upgrade_tag_list[1].research(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1)

            if self.can_afford(UnitTypeId.ARMORY) and not self.already_pending(UnitTypeId.ARMORY):
                building_place = self.start_location.position + Point2((-self.Location * 10, -self.Location * 0))
                placement_position = await self.find_placement(UnitTypeId.ARMORY, near=building_place,
                                                               placement_step=2)
                worker_candidates = self.workers.filter(lambda worker: (
                                                                               worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
                if placement_position:
                    build_worker = worker_candidates.closest_to(placement_position)
                    build_worker.build(UnitTypeId.ARMORY, placement_position)


        elif self.time_formatted == '06:15':
            if self.can_afford(UnitTypeId.ARMORY) and self.already_pending(UnitTypeId.ARMORY) < 2:
                building_place = self.start_location.position + Point2((-self.Location * 12, -self.Location * 0))
                placement_position = await self.find_placement(UnitTypeId.ARMORY, near=building_place,
                                                               placement_step=2)
                worker_candidates = self.workers.filter(lambda worker: (
                                                                               worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
                if placement_position:
                    build_worker = worker_candidates.closest_to(placement_position)
                    build_worker.build(UnitTypeId.ARMORY, placement_position)




        elif self.time_formatted == '06:30':
            for bar in self.structures(UnitTypeId.BARRACKS):
                if not bar.has_add_on:
                    bar(AbilityId.BUILD_REACTOR_BARRACKS)
                    self.barrack_tag_list.append(bar)

        elif self.time_formatted == '07:00':
            self.auto_mode = True
            for ar in self.structures(UnitTypeId.ARMORY):
                if ar not in self.upgrade_tag_list:
                    self.upgrade_tag_list.append(ar)


        elif self.time_formatted == '07:30':
            if self.can_afford(UpgradeId.TERRANINFANTRYARMORSLEVEL2):
                self.upgrade_tag_list[0].research(UpgradeId.TERRANINFANTRYARMORSLEVEL2)
            if self.can_afford(UpgradeId.TERRANINFANTRYARMORSLEVEL2):
                self.upgrade_tag_list[1].research(UpgradeId.TERRANINFANTRYWEAPONSLEVEL2)

            if self.can_afford(UpgradeId.TERRANVEHICLEWEAPONSLEVEL1):
                self.upgrade_tag_list[2].research(UpgradeId.TERRANVEHICLEWEAPONSLEVEL1)
            if self.can_afford(UpgradeId.TERRANVEHICLEARMORSLEVEL1):
                self.upgrade_tag_list[3].research(UpgradeId.TERRANVEHICLEWEAPONSLEVEL1)

            # if len(self.building_tag_list) == 2:
            #     for Barrack in self.structures(UnitTypeId.BARRACKS):
            #         if Barrack.has_add_on == False:
            #             self.position_barrack = Barrack.position
            #             self.building_tag_list.append(Barrack.tag)
            #             print(self.building_tag_list)
            #             break
            #
            #     self.position_barrack = Barrack.position
            #     self.position_factory = self.structures(UnitTypeId.FACTORY).find_by_tag(self.building_tag_list[1]).position
            #
            # else:
            #     print(self.structures.find_by_tag(self.building_tag_list[2]).is_ready)
            #     self.structures.find_by_tag(self.building_tag_list[2])(AbilityId.LIFT)
            #     print(self.structures.find_by_tag(self.building_tag_list[1]).is_ready)
            #     self.structures.find_by_tag(self.building_tag_list[1])(AbilityId.LIFT_FACTORY)

    async def build_vespene(self):
        for cc in self.structures(UnitTypeId.COMMANDCENTER) | self.structures(UnitTypeId.ORBITALCOMMAND).ready:
            # gases = self.state.vespene_geyser.closer_than(9.0, cc)
            gases = self.vespene_geyser.closer_than(10, cc)
            for gas in gases:
                if not self.can_afford(UnitTypeId.REFINERY):
                    break
                worker = self.select_build_worker(gas.position)
                if worker is None:
                    break
                if not self.units(UnitTypeId.REFINERY).closer_than(1.0, gas).exists:
                    worker.build(UnitTypeId.REFINERY, gas)

    async def building_supply(self):
        commander_center = self.townhalls.random
        if self.supply_left <= 4 and not self.already_pending(UnitTypeId.SUPPLYDEPOT) and not self.supply_cap == 200:
            if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                place_postion = self.start_location.position + Point2((0, self.Location * 8))
                await self.build(UnitTypeId.SUPPLYDEPOT, near=place_postion, placement_step=2)

            if self.trigger_extra_supply == True:
                place_postion2 = self.structures.find_by_tag(self.center_tag_list[1]).position + Point2(
                    (0, self.Location * 8))
                await self.build(UnitTypeId.SUPPLYDEPOT, near=place_postion2, placement_step=2)

    async def burrow_depot(self):
        for depot in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
            depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER)

    async def check_geysers(self):
        if self.structures(UnitTypeId.REFINERY).ready.exists:
            refinery = self.structures(UnitTypeId.REFINERY).ready.random
            if refinery.assigned_harvesters != 3:
                worker_choice = self.workers.filter(lambda worker: (
                                                                           worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action).random
                worker_choice.gather(refinery)

    async def upgrade_center(self):
        if self.structures(UnitTypeId.COMMANDCENTER).exists and self.can_afford(UnitTypeId.ORBITALCOMMAND):
            center = self.structures(UnitTypeId.COMMANDCENTER).random
            center(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND)
            if center.tag not in self.center_tag_list:
                self.center_tag_list.append(center.tag)
        if self.structures(UnitTypeId.ORBITALCOMMAND).ready:
            self.flag = True

    async def expansion(self):
        if self.minerals > 1000:
            if not self.already_pending(UnitTypeId.COMMANDCENTER) and self.can_afford(UnitTypeId.COMMANDCENTER):
                location = await self.get_next_expansion()
                if location:
                    worker = self.select_build_worker(location)
                    if worker and self.can_afford(UnitTypeId.COMMANDCENTER):
                        worker.build(UnitTypeId.COMMANDCENTER, location)
            if self.structures(UnitTypeId.BARRACKS).amount < 6 and not self.already_pending(
                    UnitTypeId.BARRACKS) and self.can_afford(UnitTypeId.BARRACKS):
                if self.can_afford(UnitTypeId.BARRACKS) and not self.already_pending(UnitTypeId.BARRACKS):
                    building_place = self.barrack_tag_list[-1].position + Point2((0, -self.Location * 3))
                    placement_position = await self.find_placement(UnitTypeId.BARRACKS, near=building_place,
                                                                   placement_step=2)
                    worker_candidates = self.workers.filter(lambda worker: (
                                                                                   worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
                    if placement_position:
                        build_worker = worker_candidates.closest_to(placement_position)
                        build_worker.build(UnitTypeId.BARRACKS, placement_position)

            if self.structures(UnitTypeId.FACTORY).amount < 4 and not self.already_pending(
                    UnitTypeId.FACTORY) and self.can_afford(UnitTypeId.FACTORY):
                if self.can_afford(UnitTypeId.FACTORY) and not self.already_pending(UnitTypeId.FACTORY):
                    building_place = self.factory_tag_list[-1].position + Point2((0, -self.Location * 3))
                    placement_position = await self.find_placement(UnitTypeId.BARRACKS, near=building_place,
                                                                   placement_step=2)
                    worker_candidates = self.workers.filter(lambda worker: (
                                                                                   worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
                    if placement_position:
                        build_worker = worker_candidates.closest_to(placement_position)
                        build_worker.build(UnitTypeId.FACTORY, placement_position)

            if self.structures(UnitTypeId.STARPORT).amount < 3 and not self.already_pending(
                    UnitTypeId.STARPORT) and self.can_afford(UnitTypeId.STARPORT):
                if self.can_afford(UnitTypeId.STARPORT) and not self.already_pending(UnitTypeId.STARPORT):
                    building_place = self.starport_tag_list[-1].position + Point2((0, -self.Location * 3))
                    placement_position = await self.find_placement(UnitTypeId.STARPORT, near=building_place,
                                                                   placement_step=2)
                    worker_candidates = self.workers.filter(lambda worker: (
                                                                                   worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
                    if placement_position:
                        build_worker = worker_candidates.closest_to(placement_position)
                        build_worker.build(UnitTypeId.STARPORT, placement_position)

    async def add_on_after_exp(self):
        for bar in self.structures(UnitTypeId.BARRACKS):
            if not bar.has_add_on:
                bar(AbilityId.BUILD_REACTOR_BARRACKS)
                self.barrack_tag_list.append(bar)

        for fac in self.structures(UnitTypeId.FACTORY):
            if not fac.has_add_on:
                fac(AbilityId.BUILD_TECHLAB_FACTORY)
                self.factory_tag_list.append(fac)

        for star in self.structures(UnitTypeId.STARPORT):
            if not star.has_add_on:
                star(AbilityId.BUILD_REACTOR_STARPORT)
                self.starport_tag_list.append(star)

    async def oc_drop_mule(self):
        if self.structures(UnitTypeId.ORBITALCOMMAND).exists:
            for oc in self.structures(UnitTypeId.ORBITALCOMMAND).filter(lambda x: x.energy >= 50):
                mfs = self.mineral_field.closer_than(10, oc)
                if mfs:
                    mf = max(mfs, key=lambda x: x.mineral_contents)
                    oc(AbilityId.CALLDOWNMULE_CALLDOWNMULE, mf)

    async def tank_movement(self):
        if self.units(UnitTypeId.SIEGETANK).exists:
            enemies = self.enemy_units | self.enemy_structures
            for tank in self.units(UnitTypeId.SIEGETANK):
                enemy_threats_close: Units = enemies.filter(
                    lambda unit: unit.distance_to(tank) < 13
                )

                if enemy_threats_close.amount > 2:
                    tank(AbilityId.SIEGEMODE_SIEGEMODE)

        if self.units(UnitTypeId.SIEGETANKSIEGED).exists:
            enemies = self.enemy_units | self.enemy_structures
            for tank in self.units(UnitTypeId.SIEGETANKSIEGED):
                enemy_threats_close: Units = enemies.filter(
                    lambda unit: unit.distance_to(tank) < 15
                )
                if enemy_threats_close.amount < 2:
                    tank(AbilityId.UNSIEGE_UNSIEGE)

    async def med_movement(self):
        if self.units(UnitTypeId.MEDIVAC).exists:
            enemies = self.enemy_units
            for med in self.units(UnitTypeId.MEDIVAC):
                enemy_threats_close: Units = enemies.filter(
                    lambda unit: unit.distance_to(med) < 7
                )
                if enemy_threats_close:
                    retreat_points: Set[Point2] = self.neighbors8(med.position,
                                                                  distance=1) | self.neighbors8(med.position,
                                                                                                distance=2)

                    retreat_points: Set[Point2] = {x for x in retreat_points if self.in_pathing_grid(x)}
                    if retreat_points:
                        closest_enemy: Unit = enemy_threats_close.closest_to(med)
                        retreat_point: Unit = closest_enemy.position.furthest(retreat_points)
                        med.move(retreat_point)
                        continue

    async def marine_movement(self):
        if self.units(UnitTypeId.MARINE).exists:
            enemies = self.enemy_units | self.enemy_structures
            for r in self.units(UnitTypeId.MARINE):
                enemy_threats_close: Units = enemies.filter(
                    lambda unit: unit.distance_to(r) < 20
                )

                if r.health_percentage < 2 / 5 and enemy_threats_close:
                    retreat_points: Set[Point2] = self.neighbors8(r.position,
                                                                  distance=1) | self.neighbors8(r.position, distance=2)

                    retreat_points: Set[Point2] = {x for x in retreat_points if self.in_pathing_grid(x)}
                    if retreat_points:
                        closest_enemy: Unit = enemy_threats_close.closest_to(r)
                        retreat_point: Unit = closest_enemy.position.furthest(retreat_points)
                        r.move(retreat_point)

                if r.is_moving and enemy_threats_close:
                    r.attack(enemies.closest_to(r.position))

                enemy_units: Units = enemies.filter(
                    lambda unit: unit.distance_to(r) < 7)
                if r.health_percentage > 2 / 5 and enemy_units and not r.has_buff(
                        BuffId.STIMPACK) and enemy_units.amount >= 10:
                    r(AbilityId.EFFECT_STIM_MARINE)

                if r.weapon_cooldown == 0 and enemy_units:
                    enemy_units_list: Units = enemy_units.sorted(lambda x: x.distance_to(r))
                    closest_enemy: Unit = enemy_units_list[0]
                    r.attack(closest_enemy)
                    continue

    async def reaper_scout(self):
        if self.units(UnitTypeId.REAPER).exists:
            enemies: Units = self.enemy_units | self.enemy_structures
            print(enemies)
            enemies_can_attack: Units = enemies.filter(lambda unit: unit.can_attack_ground)
            for r in self.units(UnitTypeId.REAPER):
                enemy_threats_close: Units = enemies_can_attack.filter(
                    lambda unit: unit.distance_to(r) < 15
                )

                if r.health_percentage < 4 / 5 and enemy_threats_close:
                    retreat_points: Set[Point2] = self.neighbors8(r.position,
                                                                  distance=2) | self.neighbors8(r.position, distance=4)
                    # Filter points that are pathable
                    retreat_points: Set[Point2] = {x for x in retreat_points if self.in_pathing_grid(x)}
                    if retreat_points:
                        closest_enemy: Unit = enemy_threats_close.closest_to(r)
                        retreat_point: Unit = closest_enemy.position.furthest(retreat_points)
                        r.move(retreat_point)
                        continue  # Continue for loop, dont execute any of the following

                    # Reaper is ready to attack, shoot nearest ground unit
                enemy_ground_units: Units = enemies.filter(
                    lambda unit: unit.distance_to(r) < 5 and not unit.is_flying
                )  # Hardcoded attackrange of 5
                if r.weapon_cooldown == 0 and enemy_ground_units:
                    enemy_ground_units: Units = enemy_ground_units.sorted(lambda x: x.distance_to(r))
                    closest_enemy: Unit = enemy_ground_units[0]
                    r.attack(closest_enemy)
                    continue  # Continue for loop, dont execute any of the following

                # Attack is on cooldown, check if grenade is on cooldown, if not then throw it to furthest enemy in range 5
                # pylint: disable=W0212
                reaper_grenade_range: float = (
                    self.game_data.abilities[AbilityId.KD8CHARGE_KD8CHARGE.value]._proto.cast_range
                )
                enemy_ground_units_in_grenade_range: Units = enemies_can_attack.filter(
                    lambda unit: not unit.is_structure and not unit.is_flying and unit.type_id not in
                                 {UnitTypeId.LARVA, UnitTypeId.EGG} and unit.distance_to(r) < reaper_grenade_range
                )
                if enemy_ground_units_in_grenade_range and (r.is_attacking or r.is_moving):
                    # If AbilityId.KD8CHARGE_KD8CHARGE in abilities, we check that to see if the reaper grenade is off cooldown
                    abilities = await self.get_available_abilities(r)
                    enemy_ground_units_in_grenade_range = enemy_ground_units_in_grenade_range.sorted(
                        lambda x: x.distance_to(r), reverse=True
                    )
                    furthest_enemy: Unit = None
                    for enemy in enemy_ground_units_in_grenade_range:
                        if await self.can_cast(r, AbilityId.KD8CHARGE_KD8CHARGE, enemy,
                                               cached_abilities_of_unit=abilities):
                            furthest_enemy: Unit = enemy
                            break
                    if furthest_enemy:
                        r(AbilityId.KD8CHARGE_KD8CHARGE, furthest_enemy)
                        continue  # Continue for loop, don't execute any of the following

                # Move to max unit range if enemy is closer than 4
                enemy_threats_very_close: Units = enemies.filter(
                    lambda unit: unit.can_attack_ground and unit.distance_to(r) < 4.5
                )  # Hardcoded attackrange minus 0.5
                # Threats that can attack the reaper
                if r.weapon_cooldown != 0 and enemy_threats_very_close:
                    retreat_points: Set[Point2] = self.neighbors8(r.position,
                                                                  distance=2) | self.neighbors8(r.position, distance=4)
                    # Filter points that are pathable by a reaper
                    retreat_points: Set[Point2] = {x for x in retreat_points if self.in_pathing_grid(x)}
                    if retreat_points:
                        closest_enemy: Unit = enemy_threats_very_close.closest_to(r)
                        retreat_point: Point2 = max(
                            retreat_points, key=lambda x: x.distance_to(closest_enemy) - x.distance_to(r)
                        )
                        if r.health_percentage < 2 / 5:
                            r.move(self.townhalls.closest_distance_to(r.position))
                            self.reaper_attack = False
                            return
                        else:
                            r.move(retreat_point)
                        continue  # Continue for loop, don't execute any of the following

                # Move to nearest enemy ground unit/building because no enemy unit is closer than 5
                all_enemy_ground_units: Units = self.enemy_units.not_flying
                if all_enemy_ground_units:
                    closest_enemy: Unit = all_enemy_ground_units.closest_to(r)
                    r.move(closest_enemy)
                    continue  # Continue for loop, don't execute any of the following

                # Move to random enemy start location if no enemy buildings have been seen
                r.move(random.choice(self.enemy_start_locations))

    async def hellion_scout(self):
        units = 0
        if self.units(UnitTypeId.HELLION).exists and self.units(UnitTypeId.HELLION).amount >= 2:
            enemies: Units = self.enemy_units | self.enemy_structures
            enemies_can_attack: Units = enemies.filter(lambda unit: unit.is_collecting)
            for r in self.units(UnitTypeId.HELLION):
                enemy_threats_close: Units = enemies_can_attack.filter(
                    lambda unit: unit.distance_to(r) < 15
                )
                if r.health_percentage < 4 / 5 and enemy_threats_close:
                    retreat_points: Set[Point2] = self.neighbors8(r.position,
                                                                  distance=2) | self.neighbors8(r.position, distance=4)
                    # Filter points that are pathable
                    retreat_points: Set[Point2] = {x for x in retreat_points if self.in_pathing_grid(x)}
                    if retreat_points:
                        closest_enemy: Unit = enemy_threats_close.closest_to(r)
                        retreat_point: Unit = closest_enemy.position.furthest(retreat_points)
                        r.move(retreat_point)
                        continue  # Continue for loop, dont execute any of the following

                    # Reaper is ready to attack, shoot nearest ground unit
                enemy_ground_units: Units = enemies.filter(
                    lambda unit: unit.distance_to(r) < 5 and not unit.is_flying
                )  # Hardcoded attackrange of 5
                if r.weapon_cooldown == 0 and enemy_ground_units:
                    enemy_ground_units: Units = enemy_ground_units.sorted(lambda x: x.distance_to(r))
                    closest_enemy: Unit = enemy_ground_units[0]
                    r.attack(closest_enemy)
                    continue  # Continue for loop, dont execute any of the following

                # Move to max unit range if enemy is closer than 4
                enemy_threats_very_close: Units = enemies.filter(
                    lambda unit: unit.can_attack_ground and unit.distance_to(r) < 4.5
                )  # Hardcoded attackrange minus 0.5
                # Threats that can attack the reaper
                if r.weapon_cooldown != 0 and enemy_threats_very_close:
                    retreat_points: Set[Point2] = self.neighbors8(r.position,
                                                                  distance=2) | self.neighbors8(r.position, distance=4)
                    # Filter points that are pathable by a reaper
                    retreat_points: Set[Point2] = {x for x in retreat_points if self.in_pathing_grid(x)}
                    if retreat_points:
                        closest_enemy: Unit = enemy_threats_very_close.closest_to(r)
                        retreat_point: Point2 = max(
                            retreat_points, key=lambda x: x.distance_to(closest_enemy) - x.distance_to(r)
                        )
                        r.move(retreat_point)
                        continue  # Continue for loop, don't execute any of the following

                # Move to nearest enemy ground unit/building because no enemy unit is closer than 5
                all_enemy_ground_units: Units = self.enemy_units.not_flying
                if all_enemy_ground_units:
                    closest_enemy: Unit = all_enemy_ground_units.closest_to(r)
                    r.move(closest_enemy)
                    continue  # Continue for loop, don't execute any of the following

                # Move to random enemy start location if no enemy buildings have been seen
                r.move(random.choice(self.enemy_start_locations))

    async def Barrack_add_on_reactor(self):
        for Bar in self.structures(UnitTypeId.BARRACKS).ready.idle:
            if not Bar.has_add_on and self.can_afford(UnitTypeId.BARRACKSREACTOR):
                addon_points = self.add_on_position_check(Bar.position)
                if all(
                        self.in_map_bounds(addon_point) and self.in_placement_grid(addon_point)
                        and self.in_pathing_grid(addon_point) for addon_point in addon_points
                ):
                    Bar.build(UnitTypeId.BARRACKSREACTOR)
                else:
                    Bar(AbilityId.LIFT)

    async def Barrack_add_on_tech(self):
        for Bar in self.structures(UnitTypeId.BARRACKS).ready.idle:
            if not Bar.has_add_on and self.can_afford(UnitTypeId.BARRACKSTECHLAB):
                addon_points = self.add_on_position_check(Bar.position)
                if all(
                        self.in_map_bounds(addon_point) and self.in_placement_grid(addon_point)
                        and self.in_pathing_grid(addon_point) for addon_point in addon_points
                ):
                    Bar.build(UnitTypeId.BARRACKSTECHLAB)
                else:
                    Bar(AbilityId.LIFT)

    async def Factory_add_on_tech(self):
        for fac in self.structures(UnitTypeId.FACTORY).ready.idle:
            if not fac.has_add_on and self.can_afford(UnitTypeId.FACTORYTECHLAB):
                addon_points = self.add_on_position_check(fac.position)
                if all(
                        self.in_map_bounds(addon_point) and self.in_placement_grid(addon_point)
                        and self.in_pathing_grid(addon_point) for addon_point in addon_points
                ):
                    fac.build(UnitTypeId.FACTORYTECHLAB)
                else:
                    fac(AbilityId.LIFT_FACTORY)
    async def Facotry_add_on_reactor(self):
        for fac in self.structures(UnitTypeId.FACTORY).ready.idle:
            if not fac.has_add_on and self.can_afford(UnitTypeId.REACTOR):
                addon_points = self.add_on_position_check(fac.position)
                if all(
                        self.in_map_bounds(addon_point) and self.in_placement_grid(addon_point)
                        and self.in_pathing_grid(addon_point) for addon_point in addon_points
                ):
                    fac.build(UnitTypeId.FACTORYREACTOR)
                else:
                    fac(AbilityId.LIFT_FACTORY)


    async def Starport_add_on_tech(self):
        for star in self.structures(UnitTypeId.STARPORT).ready.idle:
            if not star.has_add_on and self.can_afford(UnitTypeId.STARPORTTECHLAB):
                addon_points = self.add_on_position_check(star.position)
                if all(
                        self.in_map_bounds(addon_point) and self.in_placement_grid(addon_point)
                        and self.in_pathing_grid(addon_point) for addon_point in addon_points
                ):
                    star(AbilityId.BUILD_TECHLAB_STARPORT)
                else:
                    star(AbilityId.LIFT_STARPORT)

    async def Starport_add_on_reactor(self):
        for star in self.structures(UnitTypeId.STARPORT).ready.idle:
            if not star.has_add_on and self.can_afford(UnitTypeId.STARPORTREACTOR):
                addon_points = self.add_on_position_check(star.position)
                if all(
                        self.in_map_bounds(addon_point) and self.in_placement_grid(addon_point)
                        and self.in_pathing_grid(addon_point) for addon_point in addon_points
                ):
                    star(AbilityId.BUILD_REACTOR_STARPORT)
                else:
                    star(AbilityId.LIFT_STARPORT)

    async def Land_Barrack(self):
        for Bar in self.structures(UnitTypeId.BARRACKSFLYING).ready.idle:
            possible_land_positions_offset = sorted(
                (Point2((x, y)) for x in range(-10, 10) for y in range(-10, 10)),
                key=lambda point: point.x ** 2 + point.y ** 2,
            )
            offset_point: Point2 = Point2((-0.5, -0.5))
            possible_land_positions = (Bar.position.rounded + offset_point + p for p in possible_land_positions_offset)
            for target_land_position in possible_land_positions:
                land_and_addon_points: List[Point2] = self.land_positions(target_land_position)
                if all(
                        self.in_map_bounds(land_pos) and self.in_placement_grid(land_pos)
                        and self.in_pathing_grid(land_pos) for land_pos in land_and_addon_points
                ):
                    Bar(AbilityId.LAND, target_land_position)
                    break

    async def Land_Factory(self):
        for fac in self.structures(UnitTypeId.FACTORYFLYING).ready.idle:
            possible_land_positions_offset = sorted(
                (Point2((x, y)) for x in range(-10, 10) for y in range(-10, 10)),
                key=lambda point: point.x ** 2 + point.y ** 2,
            )
            offset_point: Point2 = Point2((-0.5, -0.5))
            possible_land_positions = (fac.position.rounded + offset_point + p for p in possible_land_positions_offset)
            for target_land_position in possible_land_positions:
                land_and_addon_points: List[Point2] = self.land_positions(target_land_position)
                if all(
                        self.in_map_bounds(land_pos) and self.in_placement_grid(land_pos)
                        and self.in_pathing_grid(land_pos) for land_pos in land_and_addon_points
                ):
                    fac(AbilityId.LAND, target_land_position)
                    break

    async def Land_Starport(self):
        for star in self.structures(UnitTypeId.STARPORTFLYING).ready.idle:
            possible_land_positions_offset = sorted(
                (Point2((x, y)) for x in range(-10, 10) for y in range(-10, 10)),
                key=lambda point: point.x ** 2 + point.y ** 2,
            )
            offset_point: Point2 = Point2((-0.5, -0.5))
            possible_land_positions = (star.position.rounded + offset_point + p for p in possible_land_positions_offset)
            for target_land_position in possible_land_positions:
                land_and_addon_points: List[Point2] = self.land_positions(target_land_position)
                if all(
                        self.in_map_bounds(land_pos) and self.in_placement_grid(land_pos)
                        and self.in_pathing_grid(land_pos) for land_pos in land_and_addon_points
                ):
                    star(AbilityId.LAND, target_land_position)
                    break

    async def train_tank(self):
        if self.structures(UnitTypeId.FACTORY).exists:
            for fac in self.structures(UnitTypeId.FACTORY):
                if fac.has_techlab and len(fac.orders) < 1:
                    fac.train(UnitTypeId.SIEGETANK)

    async def train_marine(self):
        if self.structures(UnitTypeId.BARRACKS).exists:
            for bar in self.structures(UnitTypeId.BARRACKS):
                if bar.has_reactor and len(bar.orders) < 2:
                    bar.train(UnitTypeId.MARINE)
                elif bar.has_techlab and len(bar.orders)  < 1 and self.producing_marauder==False:
                    bar.train(UnitTypeId.MARINE)
    async def train_marauder(self):
        if self.structures(UnitTypeId.BARRACKS).exists:
            for bar in self.structures(UnitTypeId.BARRACKS):
                if bar.has_techlab and len(bar.orders)<2 and self.supply_left>=2:
                    bar.train(UnitTypeId.MARAUDER)

    async def train_medic(self):
        if self.structures(UnitTypeId.STARPORT).exists:
            for star in self.structures(UnitTypeId.STARPORT):
                if self.units(UnitTypeId.MEDIVAC).amount < 7 and star.has_reactor and len(star.orders) < 2:
                    star.train(UnitTypeId.MEDIVAC)

    def add_on_position_check(self, position: Point2) -> List[Point2]:
        addon_offset: Point2 = Point2((2.5, -0.5))
        addon_position: Point2 = position + addon_offset
        add_points = [(addon_position + Point2((x - 0.5, y - 0.5))).rounded for x in range(0, 2) for y in range(0, 2)]
        return add_points

    def land_positions(self, position: Point2) -> List[Point2]:
        land_positions = [(position + Point2((x, y))).rounded for x in range(-1, 2) for y in range(-1, 2)]
        return land_positions + self.add_on_position_check(position)

    async def exchange_add_on(self):
        if self.structures(UnitTypeId.BARRACKSFLYING).idle and self.structures(UnitTypeId.FACTORYFLYING).idle:
            for bar in self.structures(UnitTypeId.BARRACKSFLYING).idle:
                bar(AbilityId.LAND_BARRACKS, self.position_factory)

            for fac in self.structures(UnitTypeId.FACTORYFLYING).idle:
                fac(AbilityId.LAND_FACTORY, self.position_barrack)

    async def rally_units(self, iteration):
        map_center = self.game_info.map_center
        if iteration % 3 == 0:
            building = self.structures.of_type(UnitTypeId.BARRACKS)
            for biu in building:
                biu(AbilityId.RALLY_BUILDING, self.start_location + Point2((self.Location * 60, -self.Location * 30)))

        if iteration % 3 == 1:
            building = self.structures.of_type(UnitTypeId.FACTORY)
            for biu in building:
                biu(AbilityId.RALLY_BUILDING, self.start_location + Point2((self.Location * 60, -self.Location * 30)))

        if iteration % 3 == 2:
            building = self.structures.of_type(UnitTypeId.STARPORT)
            for biu in building:
                biu(AbilityId.RALLY_BUILDING, self.start_location + Point2((self.Location * 60, -self.Location * 30)))

        # building = self.structures.of_type({UnitTypeId.BARRACKS, UnitTypeId.FACTORY, UnitTypeId.STARPORT})
        # for biu in building:
        #     biu(AbilityId.RALLY_BUILDING, self.start_location + Point2((self.Location * 35 , -self.Location * 10)))

    async def fill_bunker(self):
        for bunk in self.structures(UnitTypeId.BUNKER).ready:
            if bunk.cargo_left > 0:
                if self.units(UnitTypeId.MARINE).amount >= 4:
                    bunk(AbilityId.LOAD_BUNKER, self.units(UnitTypeId.MARINE).random)

    async def attack(self):

        if self.supply_army > 100 and self.rally_defend == False:
            target, target_is_enemy_unit = self.select_target()
            for unit in self.units.of_type({UnitTypeId.MARINE, UnitTypeId.SIEGETANK}):
                self.army_units.append(unit)
                unit.attack(target)
            for med in self.units.of_type({UnitTypeId.MEDIVAC}):
                tank = self.units(UnitTypeId.MARINE).closest_to(self.enemy_start_locations[0])
                med.move(tank.position)

        # tank : Unit
        # if self.units(UnitTypeId.SIEGETANK).exists:
        #     tank = self.units(UnitTypeId.SIEGETANK).closest_to(random.choice(self.enemy_start_locations))
        #
        # for unit in self.marine_tag_list:
        #     unit.move(random.choice(self.enemy_start_locations))
        # for unit in self.tank_tag_list:
        #     unit.attack(random.choice(self.enemy_start_locations))
        # for unit in self.medic_tag_list:
        #     unit.move(tank.position)

    # async def back_to_rally(self):
    #     force = self.units.of_type({UnitTypeId.MARINE,UnitTypeId.SIEGETANK,UnitTypeId.MEDIVAC})
    #     if force.exists:
    #         map_center = self.game_info.map_center
    #         rally_point = self.structures.find_by_tag(self.center_tag_list[-1]).position.towards(map_center,distance=5)
    #         for unit in force:
    #             if unit not in self.unit_tags_received_action and unit.distance_to(rally_point) > 10:
    #                 unit.move(rally_point)

    async def defend(self):
        print("Defend:", self.rally_defend)
        print("Attack:", self.attacking)
        for OC in self.structures(UnitTypeId.ORBITALCOMMAND) | self.structures(UnitTypeId.COMMANDCENTER):
            if self.enemy_units.amount >= 2 and self.enemy_units.closest_distance_to(OC) < 30:
                self.rally_defend = True
                for unit in self.units.of_type({UnitTypeId.MARINE, UnitTypeId.SIEGETANK, UnitTypeId.MEDIVAC}):
                    closed_enemy = self.enemy_units.sorted(lambda x: x.distance_to(unit))
                    unit.attack(closed_enemy[0])
            else:
                self.rally_defend = False

        if self.rally_defend == True:
            map_center = self.game_info.map_center
            rally_point = self.townhalls.random.position.towards(map_center, distance=5)
            for unit in self.units.of_type({UnitTypeId.MARINE, UnitTypeId.MEDIVAC, UnitTypeId.SIEGETANK}):
                if unit.distance_to(self.start_location) > 100 and unit not in self.unit_tags_received_action:
                    unit.move(rally_point)

    def select_target(self) -> Tuple[Point2, bool]:
        """ Select an enemy target the units should attack. """
        targets: Units = self.enemy_structures
        if targets:
            return targets.random.position, True

        targets: Units = self.enemy_units
        if targets:
            return targets.random.position, True

        if self.units and min((u.position.distance_to(self.enemy_start_locations[0]) for u in self.units)) < 5:
            return self.enemy_start_locations[0].position, False

        return self.mineral_field.random.position, False

    @staticmethod
    def neighbors4(position, distance=1) -> Set[Point2]:
        p = position
        d = distance
        return {Point2((p.x - d, p.y)), Point2((p.x + d, p.y)), Point2((p.x, p.y - d)), Point2((p.x, p.y + d))}

    # Stolen and modified from position.py
    def neighbors8(self, position, distance=1) -> Set[Point2]:
        p = position
        d = distance
        return self.neighbors4(position, distance) | {
            Point2((p.x - d, p.y - d)),
            Point2((p.x - d, p.y + d)),
            Point2((p.x + d, p.y - d)),
            Point2((p.x + d, p.y + d)),
        }


def main():
    run_game(  # run_game is a function that runs the game.
        maps.get(play_map),  # the map we are playing on
        [Human(Race.Protoss),
        Bot(Race.Terran, marine_tank_Bot())],  # runs a pre-made computer bot, zerg race, with a hard difficulty.
        realtime=True,  # When set to True, the bot is limited in how long each step can take to process.
    )


if __name__ == "__main__":
    main()
