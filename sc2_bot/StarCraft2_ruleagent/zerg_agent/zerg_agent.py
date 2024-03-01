import random
from typing import Set, List, Tuple
from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units
import asyncio

ladder_map_pool_2022_07 = ["Data-C", "Moondance", "Stargazers", "Waterfall", "Tropical Sacrifice", "Inside and Out",
                           "Cosmic Sapphire"]
step_count = 0


class Zerg_normal_agent(BotAI):

    def __init__(self):
        self.roach_tag_list: Units = []
        self.army_units: Units = []
        self.ravager_tag_list: Units = []
        self.queen_tag_list: Units = []
        # self.barrack_tag_list = []
        # self.factory_tag_list = []
        # self.starport_tag_list = []
        self.worker_tag_list = []
        self.center_tag_list = []
        self.bunker_tag_list = []
        self.upgrade_tag_list = []
        self.flag = False
        self.add_on = False
        self.attacking = False
        self.rally_defend = True
        self.producing_roach = False
        self.auto_mode = False
        self.queen_inject_mode = False
        self.expend_mode = False
        self.reaper_attack = True
        self.vespenetrigger = False
        self.zergling_train = False
        self.roach_train = False
        self.main_base = None
        # self.trigger_extra_supply = False
        self.step_count = 0

    def select_target(self) -> Point2:
        if self.enemy_structures:
            return random.choice(self.enemy_structures).position
        return self.enemy_start_locations[0]

    async def on_step(self, iteration: int):
        if self.time_formatted == "00:00":
            self.main_base = self.townhalls.first
        if iteration == 0:
            await self.chat_send("(glhf)")
        forces: Units = self.units.of_type({UnitTypeId.ZERGLING, UnitTypeId.ROACH})
        await self.distribute_workers()
        await self.procedure()
        await self.building_supply()

        if self.units(UnitTypeId.QUEEN):
            self.queen_inject_mode = True
        if self.queen_inject_mode:
            await self.inject()
        if self.expend_mode:
            await self.expand()
        if self.vespenetrigger == True:
            await self.build_vespene()
        if self.time_formatted >= "06:00":
            await self.check_geysers()
        if self.auto_mode == True:
            await self.produce_worker()
        if self.zergling_train:
            await self.zergling_bulid()
        if self.roach_train:
            await self.roach_bulid()
        # await self.burrow_depot()
        # await self.upgrade_center()
        # await self.oc_drop_mule()
        # await self.reaper_scout()
        # await self.exchange_add_on()
        # await self.check_geysers()
        # await self.marine_movement()
        # await self.med_movement()
        # await self.tank_movement()
        # await self.expansion()
        await self.defend()
        await self.attack()
        if self.expend_mode == True:
            await self.expand()

    async def procedure(self):
        if self.time_formatted == '00:01':
            if self.start_location == Point2((160.5, 46.5)):
                self.Location = -1  # detect location
            else:
                self.Location = 1

        larvae: Units = self.larva
        await self.distribute_workers()
        if self.time_formatted < "01:00":

            if self.townhalls.amount == 1:
                hq: Unit = self.townhalls.first
            if self.supply_left < 2 and larvae and self.can_afford(UnitTypeId.OVERLORD) and self.already_pending(
                    UnitTypeId.OVERLORD) == 0:
                larvae.random.train(UnitTypeId.OVERLORD)
                return
            if self.supply_used == 12 and self.already_pending(UnitTypeId.DRONE) == 0:
                larvae.random.train(UnitTypeId.DRONE)
            if self.supply_used == 13 and self.can_afford(UnitTypeId.OVERLORD) and self.already_pending(
                    UnitTypeId.OVERLORD) == 0:
                if self.can_afford(UnitTypeId.OVERLORD):
                    larvae.random.train(UnitTypeId.OVERLORD)
            if self.supply_used == 13 and self.already_pending(UnitTypeId.OVERLORD) == 1:
                larvae.random.train(UnitTypeId.DRONE)

            if self.supply_used < 17 and larvae:
                larvae.random.train(UnitTypeId.DRONE)

            if self.supply_used == 17 and self.can_afford(UnitTypeId.HATCHERY) and \
                    self.already_pending(UnitTypeId.HATCHERY) == 0:
                await self.expand_now()
        elif "01:00" < self.time_formatted <= "02:00":
            if self.supply_used < 18 and self.already_pending(UnitTypeId.HATCHERY) \
                    and self.can_afford(UnitTypeId.DRONE) and larvae:
                larvae.random.train(UnitTypeId.DRONE)
            if self.supply_used == 18 and self.already_pending(UnitTypeId.HATCHERY) \
                    and self.can_afford(UnitTypeId.SPAWNINGPOOL) \
                    and self.already_pending(UnitTypeId.SPAWNINGPOOL) == 0 \
                    and self.structures(UnitTypeId.SPAWNINGPOOL).amount == 0:
                worker_candidates = self.workers.filter(lambda worker: (
                                                                               worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)

                place_postion = self.start_location.position + Point2((self.Location * 10, 0))
                placement_position = await self.find_placement(UnitTypeId.SPAWNINGPOOL, near=place_postion,
                                                               placement_step=6)
                if placement_position and self.already_pending(UnitTypeId.SPAWNINGPOOL) == 0:
                    build_worker = worker_candidates.closest_to(placement_position)
                    build_worker.build(UnitTypeId.SPAWNINGPOOL, placement_position)
            if self.already_pending(UnitTypeId.SPAWNINGPOOL) and self.already_pending(UnitTypeId.HATCHERY) \
                    and self.already_pending(UnitTypeId.EXTRACTOR) == 0 \
                    and self.structures(UnitTypeId.EXTRACTOR).amount == 0:
                hq = self.townhalls.first
                vespenes = self.vespene_geyser.closer_than(8, hq)
                for vespene in vespenes:
                    if self.can_afford(UnitTypeId.EXTRACTOR):
                        await self.build(UnitTypeId.EXTRACTOR, vespenes[0])
        elif "02:00" < self.time_formatted <= "03:00":
            if self.supply_used < 20 and self.already_pending(UnitTypeId.HATCHERY) == 1 and self.already_pending(
                    UnitTypeId.SPAWNINGPOOL) == 1 and self.already_pending(UnitTypeId.EXTRACTOR) == 1:
                if larvae and self.can_afford(UnitTypeId.DRONE):
                    larvae.random.train(UnitTypeId.DRONE)
            if self.units(UnitTypeId.QUEEN).amount + self.already_pending(UnitTypeId.QUEEN) < 2 and self.structures(
                    UnitTypeId.SPAWNINGPOOL) and self.already_pending(UnitTypeId.QUEEN) < 2:
                for hq in self.townhalls:
                    if hq.is_idle and self.can_afford(UnitTypeId.QUEEN):
                        hq.train(UnitTypeId.QUEEN)
            if self.structures(UnitTypeId.SPAWNINGPOOL) and self.structures(UnitTypeId.HATCHERY).amount == 2:
                if self.units(UnitTypeId.ZERGLING).amount + self.already_pending(UnitTypeId.ZERGLING) * 2 <= 4:
                    if self.can_afford(UnitTypeId.ZERGLING) and larvae:
                        larvae.random.train(UnitTypeId.ZERGLING)
            if self.supply_left <= 4 and self.already_pending(UnitTypeId.OVERLORD) == 0:
                if self.can_afford(UnitTypeId.OVERLORD) and larvae:
                    larvae.random.train(UnitTypeId.OVERLORD)
            if self.supply_left <= 2 and larvae:
                if self.can_afford(UnitTypeId.DRONE):
                    larvae.random.train(UnitTypeId.DRONE)
            if self.can_afford(UnitTypeId.HATCHERY) and self.townhalls.amount + self.already_pending(
                    UnitTypeId.HATCHERY) < 3:
                if self.can_afford(UnitTypeId.HATCHERY):
                    await self.expand_now()
            if self.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED
                                            ) == 0 and self.can_afford(UpgradeId.ZERGLINGMOVEMENTSPEED):
                spawning_pools_ready: Units = self.structures(UnitTypeId.SPAWNINGPOOL).ready
                if spawning_pools_ready:
                    self.research(UpgradeId.ZERGLINGMOVEMENTSPEED)
            if self.already_pending(UnitTypeId.HATCHERY) + self.structures(UnitTypeId.HATCHERY).amount < 3:
                if self.can_afford(UnitTypeId.HATCHERY):
                    await self.expand_now()
        elif "03:00" < self.time_formatted <= "04:00":
            if self.units(UnitTypeId.QUEEN).amount <= self.townhalls.amount and self.already_pending(
                    UnitTypeId.QUEEN) <= 2:
                for hq in self.townhalls:
                    if hq.is_idle and self.can_afford(UnitTypeId.QUEEN):
                        hq.train(UnitTypeId.QUEEN)
            self.auto_mode = True

        elif "04:00" < self.time_formatted <= "05:00":

            hq = self.main_base
            if self.structures(UnitTypeId.HATCHERY).amount + self.already_pending(UnitTypeId.HATCHERY) <= 4 \
                    and self.can_afford(UnitTypeId.ROACHWARREN) \
                    and self.already_pending(UnitTypeId.ROACHWARREN) == 0 \
                    and self.structures(UnitTypeId.ROACHWARREN).amount == 0:
                await self.build(UnitTypeId.ROACHWARREN, near=hq.position.towards(self.game_info.map_center, 5))
            if self.structures(UnitTypeId.HATCHERY).amount + self.already_pending(UnitTypeId.HATCHERY) <= 4 \
                    and self.can_afford(UnitTypeId.ROACHWARREN) \
                    and self.already_pending(UnitTypeId.ROACHWARREN) == 0 \
                    and self.structures(UnitTypeId.ROACHWARREN).amount == 0:
                await self.build(UnitTypeId.ROACHWARREN, near=hq.position.towards(self.game_info.map_center, 5))
            if self.structures(UnitTypeId.LAIR).amount + self.already_pending(UnitTypeId.LAIR) == 0 and self.can_afford(
                    UnitTypeId.LAIR):
                if hq.is_idle:
                    hq.build(UnitTypeId.LAIR)
            self.expend_mode = True


        elif "05:00" < self.time_formatted <= "06:00":
            hq = self.townhalls.first
            if self.structures(UnitTypeId.EVOLUTIONCHAMBER).amount + self.already_pending(
                    UnitTypeId.EVOLUTIONCHAMBER) < 2 and self.can_afford(UnitTypeId.EVOLUTIONCHAMBER):
                if self.can_afford(UnitTypeId.EVOLUTIONCHAMBER):
                    await self.build(UnitTypeId.EVOLUTIONCHAMBER,
                                     near=hq.position.towards(self.game_info.map_center, 3))
            if self.time_formatted == "05:30":
                self.vespenetrigger = True
            if self.minerals>=500:
                self.zergling_train=True
            if self.minerals>=600 and self.vespene>=300:
                self.roach_train=True
        elif "06:00" < self.time_formatted:
            if self.structures(UnitTypeId.EVOLUTIONCHAMBER) == 2 and len(self.upgrade_tag_list) < 2:
                for ec in self.structures(UnitTypeId.EVOLUTIONCHAMBER):
                    self.upgrade_tag_list.append(ec)
            for ec in self.upgrade_tag_list:
                if ec.is_idel and self.can_afford(UpgradeId.ZERGMISSILEWEAPONSLEVEL1) and self.already_pending(
                        UpgradeId.ZERGMISSILEWEAPONSLEVEL1) == 0:
                    ec.research(UpgradeId.ZERGMISSILEWEAPONSLEVEL1)
                if ec.is_idel and self.can_afford(UpgradeId.ZERGGROUNDARMORSLEVEL1) and self.already_pending(
                        UpgradeId.ZERGGROUNDARMORSLEVEL1):
                    ec.research(UpgradeId.ZERGGROUNDARMORSLEVEL1)
            if self.structures(UnitTypeId.LAIR).ready and self.can_afford(
                    UpgradeId.GLIALRECONSTITUTION) and self.already_pending(UpgradeId.GLIALRECONSTITUTION) == 0:
                roachwarren = self.structures(UnitTypeId.ROACHWARREN)
                if roachwarren.idle:
                    self.research(UpgradeId.GLIALRECONSTITUTION)



        else:

            forces: Units = self.units.of_type({UnitTypeId.ZERGLING, UnitTypeId.ROACH})
            if self.units(UnitTypeId.ROACH).amount >= 20:
                for unit in forces.idle:
                    unit.attack(self.select_target())

    async def build_vespene(self):
        if self.townhalls.exists and self.workers.exists:
            base = []
            for hc in self.structures(UnitTypeId.HATCHERY) | self.structures(
                    UnitTypeId.LAIR).ready:
                base.append(hc)
                # gases = self.state.vespene_geyser.closer_than(9.0, cc)
            for i in range(self.townhalls.amount-1):
                base_ = base[i]
                gases = self.vespene_geyser.closer_than(9, base_)
                for gas in gases:
                    if not self.can_afford(UnitTypeId.EXTRACTOR):
                        break
                    if not self.units(UnitTypeId.EXTRACTOR).closer_than(1.0, gas).exists:
                        await self.build(UnitTypeId.EXTRACTOR, gas)

    async def produce_worker(self):
        larvae: Units = self.larva
        if self.supply_workers + self.already_pending(UnitTypeId.DRONE) <= 60 and larvae and self.supply_left >= 2:
            if larvae and self.can_afford(UnitTypeId.DRONE):
                larvae.random.train(UnitTypeId.DRONE)

    async def building_supply(self):
        larvae: Units = self.larva
        if "04:00" <= self.time_formatted < "06:00":
            if self.supply_left <= 4 and self.already_pending(UnitTypeId.OVERLORD) <= 2 and not self.supply_cap == 200:
                if larvae and self.can_afford(UnitTypeId.OVERLORD):
                    larvae.random.train(UnitTypeId.OVERLORD)
        if "08:00" <= self.time_formatted:
            if self.supply_left <= 4 and self.already_pending(UnitTypeId.OVERLORD) <= 3 and not self.supply_cap == 200:
                if larvae and self.can_afford(UnitTypeId.OVERLORD):
                    larvae.random.train(UnitTypeId.OVERLORD)

    async def inject(self):
        hq = self.townhalls.random
        # Send idle queens with >=25 energy to inject
        for queen in self.units(UnitTypeId.QUEEN).idle:

            # The following checks if the inject ability is in the queen abilitys - basically it checks if we have enough energy and if the ability is off-cooldown
            # abilities = await self.get_available_abilities(queen)
            # if AbilityId.EFFECT_INJECTLARVA in abilities:
            if queen.energy >= 25:
                hq = self.townhalls.closest_to(queen)
                queen(AbilityId.EFFECT_INJECTLARVA, hq)

    async def expand(self):
        if self.time_formatted <= "06:00":
            if self.townhalls.amount + self.already_pending(UnitTypeId.HATCHERY) <= 3 and self.can_afford(
                    UnitTypeId.HATCHERY):
                await self.expand_now()
        if self.time_formatted > "08:00":
            if self.townhalls.amount + self.already_pending(UnitTypeId.HATCHERY) <= 4 and self.can_afford(
                    UnitTypeId.HATCHERY):
                await self.expand_now()

    async def roach_bulid(self):
        larvae: Units = self.larva
        if self.can_afford(UnitTypeId.ROACH) and self.structures(UnitTypeId.ROACHWARREN).ready:
            if larvae and self.can_afford(UnitTypeId.ROACH) and self.supply_left >= 2:
                larvae.random.train(UnitTypeId.ROACH)

    async def zergling_bulid(self):
        larvae: Units = self.larva
        if self.units(UnitTypeId.ZERGLING).amount <= 30:
            if larvae and self.can_afford(UnitTypeId.ZERGLING):
                larvae.random.train(UnitTypeId.ZERGLING)

    async def check_geysers(self):
        if self.structures(UnitTypeId.EXTRACTOR).ready.exists and self.workers.exists:
            extractor = self.structures(UnitTypeId.EXTRACTOR).ready.random
            if extractor.assigned_harvesters != 3:
                worker_choice = self.workers.filter(lambda worker: (
                                                                           worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action).random
                worker_choice.gather(extractor)

    async def defend(self):
        print("Defend:", self.rally_defend)
        print("Attack:", self.attacking)
        for base in self.structures(UnitTypeId.HATCHERY) | self.structures(UnitTypeId.LAIR):
            if self.enemy_units.amount >= 2 and self.enemy_units.closest_distance_to(base) < 30:
                self.rally_defend = True
                for unit in self.units.of_type({UnitTypeId.ZERGLING, UnitTypeId.QUEEN, UnitTypeId.ROACH}):
                    closed_enemy = self.enemy_units.sorted(lambda x: x.distance_to(unit))
                    unit.attack(closed_enemy[0])
            else:
                self.rally_defend = False

        if self.rally_defend == True:
            map_center = self.game_info.map_center
            rally_point = self.townhalls.random.position.towards(map_center, distance=5)
            for unit in self.units.of_type({UnitTypeId.ZERGLING, UnitTypeId.ROACH, UnitTypeId.QUEEN}):
                if unit.distance_to(self.start_location) > 100 and unit not in self.unit_tags_received_action:
                    unit.move(rally_point)

    async def attack(self):

        if self.supply_army > 70 and self.rally_defend == False:
            target, target_is_enemy_unit = self.select_target()
            for unit in self.units.of_type({UnitTypeId.ROACH, UnitTypeId.ZERGLING}):
                self.army_units.append(unit)
                unit.attack(target)
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
    run_game(
        maps.get(ladder_map_pool_2022_07[random.randint(0, 6)]),
        [Bot(Race.Zerg, Zerg_normal_agent()), Computer(Race.Protoss, Difficulty.Hard)],
        realtime=False,

    )


if __name__ == "__main__":
    main()
