import random
from typing import Set, List, Tuple
from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.main import run_game
from sc2.player import Bot, Computer, Human
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units
import asyncio

ladder_map_pool_2022_07 = ["Data-C", "Moondance", "Stargazers", "Waterfall", "Tropical Sacrifice", "Inside and Out",
                           "Cosmic Sapphire"]
step_count = 0


class roach_ling_baneling_bot(BotAI):

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
        self.ultra_train = False
        self.baneling_train = False
        self.hydra_train = False
        # self.trigger_extra_supply = False
        self.step_count = 0

    async def on_step(self, iteration: int):
        if self.time_formatted == "00:00":
            self.main_base = self.townhalls.first
        if iteration == 0:
            await self.chat_send("(glhf)")
        forces: Units = self.units.of_type({UnitTypeId.ZERGLING, UnitTypeId.ROACH})
        await self.distribute_workers()
        await self.procedure()
        if self.time_formatted >= "04:00":
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
            await self.queen_build()
        if self.roach_train:
            await self.roach_bulid()
        if self.time_formatted >= "07:00":
            await self.oversee_build()
        if self.ultra_train == True:
            await self.ultra_build()
        if self.baneling_train == True:
            await self.bailing_bulid()
        if self.hydra_train == True:
            await self.hydra_bulid()
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
        if self.time_formatted == '00:00':
            if self.start_location == Point2((160.5, 46.5)):
                self.Location = -1  # detect location
            else:
                self.Location = 1

        larvae: Units = self.larva
        await self.distribute_workers()
        if self.time_formatted < "01:00":
            if self.time_formatted == "00:00" and self.supply_used == 12 and self.already_pending(
                    UnitTypeId.DRONE) == 0:
                if self.can_afford(UnitTypeId.DRONE):
                    larvae.random.train(UnitTypeId.DRONE)
            elif "00:13"<=self.time_formatted <= "00:15" and self.supply_used == 13 and self.already_pending(
                    UnitTypeId.OVERLORD) == 0:
                if self.can_afford(UnitTypeId.OVERLORD):
                    larvae.random.train(UnitTypeId.OVERLORD)
            elif "00:17"<=self.time_formatted == "00:19" and self.supply_used == 13 and self.already_pending(
                    UnitTypeId.OVERLORD) == 1 \
                    and self.already_pending(UnitTypeId.DRONE) == 0:
                if self.can_afford(UnitTypeId.DRONE):
                    larvae.random.train(UnitTypeId.DRONE)
            elif "00:29" < self.time_formatted <= "00:36":
                if self.supply_used < 17 and self.already_pending(UnitTypeId.OVERLORD) == 0 and self.already_pending(
                        UnitTypeId.DRONE) <= 3:
                    if larvae and self.can_afford(UnitTypeId.DRONE):
                        larvae.random.train(UnitTypeId.DRONE)
            elif "00:37" <= self.time_formatted <= "00:59":
                if self.supply_used == 17 and self.can_afford(UnitTypeId.HATCHERY) and \
                        self.already_pending(UnitTypeId.HATCHERY) == 0:
                    await self.expand_now()
                if self.already_pending(UnitTypeId.HATCHERY) == 1 and self.supply_used < 18 and self.can_afford(
                        UnitTypeId.DRONE):
                    if larvae:
                        larvae.random.train(UnitTypeId.DRONE)
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
                vespenes = self.vespene_geyser.closer_than(8, self.main_base)
                for vespene in vespenes:
                    if self.can_afford(UnitTypeId.EXTRACTOR):
                        await self.build(UnitTypeId.EXTRACTOR, vespenes[0])
            if self.supply_left >= 2 and self.already_pending(UnitTypeId.HATCHERY) == 1 and self.already_pending(
                    UnitTypeId.SPAWNINGPOOL) == 1:
                if larvae and self.can_afford(UnitTypeId.DRONE):
                    larvae.random.train(UnitTypeId.DRONE)
        elif "02:00" < self.time_formatted <= "03:00":
            if self.supply_left < 20 and self.already_pending(UnitTypeId.HATCHERY) == 1 and self.already_pending(
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
            if self.supply_left <= 4 and self.already_pending(UnitTypeId.OVERLORD) <= 0:
                if self.can_afford(UnitTypeId.OVERLORD) and larvae:
                    larvae.random.train(UnitTypeId.OVERLORD)
            if self.supply_left >= 2 and larvae:
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
            if self.supply_left <= 4 and self.already_pending(UnitTypeId.OVERLORD) <= 0:
                if self.can_afford(UnitTypeId.OVERLORD) and larvae:
                    larvae.random.train(UnitTypeId.OVERLORD)
            if self.supply_left >= 2 and larvae:
                if self.can_afford(UnitTypeId.DRONE):
                    larvae.random.train(UnitTypeId.DRONE)
            if self.units(UnitTypeId.QUEEN).amount <= self.townhalls.amount and self.already_pending(
                    UnitTypeId.QUEEN) <= 3:
                for hq in self.townhalls:
                    if hq.is_idle and self.can_afford(UnitTypeId.QUEEN):
                        hq.train(UnitTypeId.QUEEN)
            self.auto_mode = True

        elif "04:00" < self.time_formatted <= "05:00":
            if self.supply_left >= 2 and larvae:
                if self.can_afford(UnitTypeId.DRONE):
                    larvae.random.train(UnitTypeId.DRONE)
            hq = self.main_base
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
            if self.time_formatted >= "05:30" and self.structures(UnitTypeId.EXTRACTOR).amount + self.already_pending(
                    UnitTypeId.EXTRACTOR) <= 3:
                self.vespenetrigger = True
            else:
                self.vespenetrigger = False
            larvae: Units = self.larva
            if self.units(UnitTypeId.ZERGLING).amount + self.already_pending(UnitTypeId.ZERGLING) <= 30:
                if larvae and self.can_afford(UnitTypeId.ZERGLING):
                    larvae.random.train(UnitTypeId.ZERGLING)

        elif "06:00" < self.time_formatted <= "07:00":
            if self.structures(UnitTypeId.BANELINGNEST).amount + self.already_pending(UnitTypeId.BANELINGNEST) == 0:
                if self.can_afford(UnitTypeId.BANELINGNEST) and self.workers.amount >= 50:
                    if self.structures(UnitTypeId.SPAWNINGPOOL).ready and self.structures(UnitTypeId.ROACHWARREN).ready:

                        worker_candidates = self.workers.filter(lambda worker: (
                                                                                       worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)

                        place_postion = self.start_location.position + Point2((self.Location * 10, 0))
                        placement_position = await self.find_placement(UnitTypeId.BANELINGNEST, near=place_postion,
                                                                       placement_step=6)
                        if placement_position and self.already_pending(UnitTypeId.BANELINGNEST) == 0:
                            build_worker = worker_candidates.closest_to(placement_position)
                            build_worker.build(UnitTypeId.BANELINGNEST, placement_position)
            bvs = self.structures(UnitTypeId.EVOLUTIONCHAMBER)
            for bv in bvs.ready.idle:
                if bv.is_idle:
                    if self.already_pending_upgrade(UpgradeId.ZERGMELEEWEAPONSLEVEL1) == 0 and self.can_afford(
                            UpgradeId.ZERGMELEEWEAPONSLEVEL1):
                        bv.research(UpgradeId.ZERGMELEEWEAPONSLEVEL1)
                if bv.is_idle:
                    if self.already_pending_upgrade(UpgradeId.ZERGGROUNDARMORSLEVEL1) == 0 and self.can_afford(
                            UpgradeId.ZERGGROUNDARMORSLEVEL1):
                        bv.research(UpgradeId.ZERGGROUNDARMORSLEVEL1)

            if self.structures(UnitTypeId.LAIR).ready and self.can_afford(
                    UpgradeId.GLIALRECONSTITUTION) and self.already_pending_upgrade(UpgradeId.GLIALRECONSTITUTION) == 0:
                roachwarren = self.structures(UnitTypeId.ROACHWARREN)
                for warren in roachwarren.ready.idle:
                    warren.research(UpgradeId.GLIALRECONSTITUTION)
            if self.structures(UnitTypeId.EXTRACTOR).amount + self.already_pending(UnitTypeId.EXTRACTOR) <= 3:
                self.vespenetrigger = True
            else:
                self.vespenetrigger = False
            if self.minerals >= 400 and self.workers.amount >= 60:
                self.zergling_train = True
                self.baneling_train = True

            if self.minerals >= 400 and self.vespene >= 200 and self.workers.amount >= 60:
                self.roach_train = True
        elif "09:00" >= self.time_formatted > "07:00":
            if self.structures(UnitTypeId.BANELINGNEST).ready and self.structures(UnitTypeId.LAIR).ready and self.can_afford(UpgradeId.CENTRIFICALHOOKS):
                banelingnet = self.structures(UnitTypeId.BANELINGNEST).first
                if banelingnet.is_idle and self.can_afford(UpgradeId.CENTRIFICALHOOKS):
                        self.research(UpgradeId.CENTRIFICALHOOKS)
            bvs = self.structures(UnitTypeId.EVOLUTIONCHAMBER)
            for bv in bvs.ready.idle:
                if self.already_pending_upgrade(UpgradeId.ZERGMISSILEWEAPONSLEVEL1) == 0 and self.can_afford(
                        UpgradeId.ZERGMISSILEWEAPONSLEVEL1):
                    bv.research(UpgradeId.ZERGMISSILEWEAPONSLEVEL1)
                if self.already_pending_upgrade(UpgradeId.ZERGGROUNDARMORSLEVEL2) == 0 and self.can_afford(
                        UpgradeId.ZERGGROUNDARMORSLEVEL2):
                    bv.research(UpgradeId.ZERGGROUNDARMORSLEVEL2)
            if self.vespene > 300 and self.supply_used > 130:
                if self.already_pending(UnitTypeId.INFESTATIONPIT) + self.structures(
                        UnitTypeId.INFESTATIONPIT).amount == 0 and self.can_afford(UnitTypeId.INFESTATIONPIT):
                    worker_candidates = self.workers.filter(lambda worker: (
                                                                                   worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)

                    place_postion = self.start_location.position + Point2((self.Location * 10, 0))
                    placement_position = await self.find_placement(UnitTypeId.INFESTATIONPIT, near=place_postion,
                                                                   placement_step=6)
                    if placement_position and self.already_pending(UnitTypeId.INFESTATIONPIT) == 0:
                        build_worker = worker_candidates.closest_to(placement_position)
                        build_worker.build(UnitTypeId.INFESTATIONPIT, placement_position)

        elif "13:00" > self.time_formatted > "09:00":
            if self.structures(UnitTypeId.LAIR).ready and self.can_afford(UpgradeId.OVERLORDSPEED) and self.workers.amount>=66:
                bases = self.townhalls
                for base in self.townhalls:
                    if base == self.main_base:
                        pass
                    else:
                        if base.is_idle and self.can_afford(UpgradeId.OVERLORDSPEED):
                            base.research(UpgradeId.OVERLORDSPEED)


            if self.structures(UnitTypeId.INFESTATIONPIT).ready and self.can_afford(
                    UnitTypeId.HIVE) and self.already_pending(UnitTypeId.HIVE) == 0:
                lair = self.main_base
                if lair and lair.is_idle:
                    lair.build(UnitTypeId.HIVE)
            if self.structures(UnitTypeId.HIVE):
                pool = self.structures(UnitTypeId.SPAWNINGPOOL).first
                if pool and pool.is_idle:
                    pool.research(UpgradeId.ZERGLINGATTACKSPEED)
            bvs = self.structures(UnitTypeId.EVOLUTIONCHAMBER)
            for bv in bvs.ready.idle:
                if self.already_pending_upgrade(UpgradeId.ZERGMELEEWEAPONSLEVEL2) == 0 and self.can_afford(
                        UpgradeId.ZERGMELEEWEAPONSLEVEL2):
                    bv.research(UpgradeId.ZERGMELEEWEAPONSLEVEL2)
                if self.already_pending_upgrade(UpgradeId.ZERGMISSILEWEAPONSLEVEL2) == 0 and self.can_afford(
                        UpgradeId.ZERGMISSILEWEAPONSLEVEL2):
                    bv.research(UpgradeId.ZERGMISSILEWEAPONSLEVEL2)
        elif "15:00" >= self.time_formatted >= "13:00":
            if self.structures(UnitTypeId.HIVE).ready and self.can_afford(
                    UnitTypeId.ULTRALISKCAVERN) and self.structures(UnitTypeId.ULTRALISKCAVERN).amount == 0:
                if self.already_pending(UnitTypeId.ULTRALISKCAVERN) == 0 and self.can_afford(
                        UnitTypeId.ULTRALISKCAVERN):
                    worker_candidates = self.workers.filter(lambda worker: (
                                                                                   worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)

                    place_postion = self.start_location.position + Point2((self.Location * 10, 0))
                    placement_position = await self.find_placement(UnitTypeId.ULTRALISKCAVERN, near=place_postion,
                                                                   placement_step=6)
                    if placement_position and self.already_pending(UnitTypeId.ULTRALISKCAVERN) == 0:
                        build_worker = worker_candidates.closest_to(placement_position)
                        build_worker.build(UnitTypeId.ULTRALISKCAVERN, placement_position)
            if self.structures(UnitTypeId.ULTRALISKCAVERN).ready:
                ucavern = self.structures(UnitTypeId.ULTRALISKCAVERN).first
                if ucavern.is_idle:
                    if self.can_afford(UpgradeId.CHITINOUSPLATING):
                        ucavern.research(UpgradeId.CHITINOUSPLATING)
                    if self.can_afford(UpgradeId.ANABOLICSYNTHESIS):
                        ucavern.research(UpgradeId.ANABOLICSYNTHESIS)
            bvs = self.structures(UnitTypeId.EVOLUTIONCHAMBER)
            for bv in bvs.ready.idle:
                if self.already_pending_upgrade(UpgradeId.ZERGMELEEWEAPONSLEVEL3) == 0 and self.can_afford(
                        UpgradeId.ZERGMELEEWEAPONSLEVEL3):
                    bv.research(UpgradeId.ZERGMELEEWEAPONSLEVEL3)
                if self.already_pending_upgrade(UpgradeId.ZERGGROUNDARMORSLEVEL3) == 0 and self.can_afford(
                        UpgradeId.ZERGGROUNDARMORSLEVEL3):
                    bv.research(UpgradeId.ZERGGROUNDARMORSLEVEL3)
            if self.structures(UnitTypeId.ULTRALISKCAVERN).ready:
                self.ultra_train = True

        else:
            pass

    async def build_vespene(self):
        if self.townhalls.exists and self.workers.exists:
            base = []
            for hc in self.townhalls:
                base.append(hc)
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
        if "08:00" >= self.time_formatted >= "06:00":
            if self.supply_workers + self.already_pending(UnitTypeId.DRONE) <= 66 and larvae and self.supply_left >= 2:
                if larvae and self.can_afford(UnitTypeId.DRONE):
                    larvae.random.train(UnitTypeId.DRONE)
        if self.time_formatted >= "08:01":
            if self.supply_workers + self.already_pending(UnitTypeId.DRONE) <= 76 and larvae and self.supply_left >= 2:
                if larvae and self.can_afford(UnitTypeId.DRONE):
                    larvae.random.train(UnitTypeId.DRONE)

    async def building_supply(self):
        larvae: Units = self.larva

        if "04:00" <= self.time_formatted < "06:00":
            if self.supply_left <= 4 and self.already_pending(UnitTypeId.OVERLORD) < 2 and not self.supply_cap == 200 \
                    and self.minerals >= 200:
                if larvae and self.can_afford(UnitTypeId.OVERLORD):
                    larvae.random.train(UnitTypeId.OVERLORD)
        elif "09:00" >= self.time_formatted >= "06:00":
            if self.supply_left <= 6 and self.already_pending(UnitTypeId.OVERLORD) < 3 and not self.supply_cap == 200 \
                    and self.minerals >= 250:
                if larvae and self.can_afford(UnitTypeId.OVERLORD):
                    larvae.random.train(UnitTypeId.OVERLORD)
        elif "09:00" <= self.time_formatted:
            if self.supply_left <= 6 and self.already_pending(
                    UnitTypeId.OVERLORD) < 4 and not self.supply_cap + self.already_pending(
                    UnitTypeId.OVERLORD) * 8 == 200 \
                    and self.minerals >= 250:
                if larvae and self.can_afford(UnitTypeId.OVERLORD):
                    larvae.random.train(UnitTypeId.OVERLORD)
        else:
            pass

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

    async def ultra_build(self):
        larvae: Units = self.larva
        if self.units(UnitTypeId.ULTRALISK).amount + self.already_pending(UnitTypeId.ULTRALISK) < 3 and self.can_afford(
                UnitTypeId.ULTRALISK):
            if self.supply_used >= 100 and larvae:
                larvae.random.train(UnitTypeId.ULTRALISK)

    async def expand(self):
        if self.time_formatted <= "07:00":
            if self.townhalls.amount + self.already_pending(UnitTypeId.HATCHERY) <= 3 and self.can_afford(
                    UnitTypeId.HATCHERY):
                await self.expand_now()
        elif "09:00" >= self.time_formatted > "07:00":
            if self.townhalls.amount + self.already_pending(UnitTypeId.HATCHERY) <= 5 and self.can_afford(
                    UnitTypeId.HATCHERY):
                await self.expand_now()
        elif "11:00" >= self.time_formatted > "09:00":
            if self.townhalls.amount + self.already_pending(UnitTypeId.HATCHERY) <= 6 and self.can_afford(
                    UnitTypeId.HATCHERY):
                await self.expand_now()
        elif self.time_formatted > "11:00":
            if self.townhalls.amount + self.already_pending(UnitTypeId.HATCHERY) <= 8 and self.can_afford(
                    UnitTypeId.HATCHERY):
                await self.expand_now()
        else:
            pass

    async def roach_bulid(self):
        larvae: Units = self.larva
        if 60 <= self.workers.amount + self.already_pending(UnitTypeId.DRONE) <= 70:
            if self.can_afford(UnitTypeId.ROACH) and self.structures(UnitTypeId.ROACHWARREN).ready:
                if larvae and self.can_afford(UnitTypeId.ROACH) and self.supply_left >= 4 and self.units(
                        UnitTypeId.ROACH).amount + self.already_pending(UnitTypeId.ROACH) < 10:
                    larvae.random.train(UnitTypeId.ROACH)
        elif 70 <= self.workers.amount + self.already_pending(UnitTypeId.DRONE):
            if self.can_afford(UnitTypeId.ROACH) and self.structures(UnitTypeId.ROACHWARREN).ready:
                if larvae and self.can_afford(UnitTypeId.ROACH) and self.supply_left >= 4 and self.units(
                        UnitTypeId.ROACH).amount + self.already_pending(UnitTypeId.ROACH) < 20:
                    larvae.random.train(UnitTypeId.ROACH)
        else:
            pass

    async def hydra_bulid(self):
        larvae: Units = self.larva
        if self.can_afford(UnitTypeId.HYDRALISK) and self.structures(UnitTypeId.HYDRALISKDEN).ready:
            if larvae and self.can_afford(UnitTypeId.HYDRALISK) and self.supply_left >= 4 and self.already_pending(
                    UnitTypeId.HYDRALISK) + self.units(UnitTypeId.HYDRALISK).amount < 20:
                larvae.random.train(UnitTypeId.ROACH)

    async def bailing_bulid(self):
        larvae: Units = self.larva
        zerglings = self.units(UnitTypeId.ZERGLING)
        if 60 <= self.workers.amount + self.already_pending(UnitTypeId.DRONE) <= 70:
            if self.can_afford(UnitTypeId.BANELING) and self.structures(UnitTypeId.BANELINGNEST).ready:
                if zerglings and self.can_afford(UnitTypeId.BANELING) and self.already_pending(
                        UnitTypeId.BANELING) + self.units(UnitTypeId.BANELING).amount < 10:
                    for ling in zerglings:
                        if ling.is_idle and self.can_afford(UnitTypeId.BANELING):
                            ling.build(UnitTypeId.BANELING)
        elif 70 <= self.workers.amount + self.already_pending(UnitTypeId.DRONE):
            if self.can_afford(UnitTypeId.BANELING) and self.structures(UnitTypeId.BANELINGNEST).ready:
                if zerglings and self.can_afford(UnitTypeId.BANELING) and self.already_pending(
                        UnitTypeId.BANELING) + self.units(UnitTypeId.BANELING).amount < 30:
                    for ling in zerglings:
                        if ling.is_idle and self.can_afford(UnitTypeId.BANELING):
                            ling.build(UnitTypeId.BANELING)
        else:
            pass

    async def zergling_bulid(self):

        larvae: Units = self.larva
        if 60 <= self.workers.amount + self.already_pending(UnitTypeId.DRONE) <= 70:
            if self.units(UnitTypeId.ZERGLING).amount + self.already_pending(UnitTypeId.ZERGLING) <= 40:
                if larvae and self.can_afford(UnitTypeId.ZERGLING):
                    larvae.random.train(UnitTypeId.ZERGLING)
        elif 70 <= self.workers.amount + self.already_pending(UnitTypeId.DRONE) <= 80:
            if self.units(UnitTypeId.ZERGLING).amount + self.already_pending(UnitTypeId.ZERGLING) <= 80:
                if larvae and self.can_afford(UnitTypeId.ZERGLING):
                    larvae.random.train(UnitTypeId.ZERGLING)

    async def queen_build(self):
        for base in self.townhalls:
            if base.is_idle and self.can_afford(UnitTypeId.QUEEN) and self.units(UnitTypeId.QUEEN).amount < 10:
                base.train(UnitTypeId.QUEEN)

    async def check_geysers(self):
        if self.structures(UnitTypeId.EXTRACTOR).ready.exists:
            extractor = self.structures(UnitTypeId.EXTRACTOR).ready.random
            if extractor.assigned_harvesters != 3:
                worker_choice = self.workers.filter(lambda worker: (
                                                                           worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action).random
                worker_choice.gather(extractor)

    async def oversee_build(self):
        if self.units(UnitTypeId.OVERSEER).amount + self.already_pending(UnitTypeId.OVERSEER) < 2 and self.can_afford(
                UnitTypeId.OVERSEER):
            self.units(UnitTypeId.OVERLORD).random.train(UnitTypeId.OVERSEER)

    async def defend(self):
        print("Defend:", self.rally_defend)
        print("Attack:", self.attacking)
        for base in self.structures(UnitTypeId.HATCHERY) | self.structures(UnitTypeId.LAIR):
            if self.enemy_units.amount >= 2 and self.enemy_units.closest_distance_to(base) < 30:
                self.rally_defend = True
                for unit in self.units.of_type(
                        {UnitTypeId.ZERGLING, UnitTypeId.QUEEN, UnitTypeId.ROACH, UnitTypeId.OVERSEER,
                         UnitTypeId.ULTRALISK}):
                    closed_enemy = self.enemy_units.sorted(lambda x: x.distance_to(unit))
                    unit.attack(closed_enemy[0])
            else:
                self.rally_defend = False

        if self.rally_defend == True:
            map_center = self.game_info.map_center
            rally_point = self.townhalls.random.position.towards(map_center, distance=5)
            for unit in self.units.of_type(
                    {UnitTypeId.ZERGLING, UnitTypeId.ROACH, UnitTypeId.QUEEN, UnitTypeId.ULTRALISK}):
                if unit.distance_to(self.start_location) > 100 and unit not in self.unit_tags_received_action:
                    unit.move(rally_point)

    async def attack(self):

        if self.supply_army > 80 and self.rally_defend == False:
            target = self.select_target()
            for unit in self.units.of_type(
                    {UnitTypeId.ROACH, UnitTypeId.ZERGLING, UnitTypeId.OVERSEER, UnitTypeId.ULTRALISK,UnitTypeId.BANELING}):
                self.army_units.append(unit)
                unit.attack(target)

    def select_target(self) -> Point2:
        if self.enemy_structures:
            return random.choice(self.enemy_structures).position
        return self.enemy_start_locations[0]

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
        # [Human(Race.Protoss), Bot(Race.Zerg, Zerg_normal_agent())],
        [Bot(Race.Zerg, roach_ling_baneling_bot()), Computer(Race.Terran, Difficulty.Hard)],
        realtime=True,
        save_replay_as='massive_lings.SC2Replay',

    )


if __name__ == "__main__":
    main()
