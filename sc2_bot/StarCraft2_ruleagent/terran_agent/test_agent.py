import random

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
map_pool = ladder_map_pool_2022_07


class Terran_normal_agent(BotAI):
    def __init__(self):
        self.step_count = 0


    def select_target(self) -> Point2:
        if self.enemy_structures:
            return random.choice(self.enemy_structures).position
        return self.enemy_start_locations[0]



    async def on_step(self, iteration):
        CCs: Units = self.townhalls
        fcc: Unit = CCs.first
        bases = self.townhalls.random
        if iteration == 0:
            await self.chat_send("(glhf)")
        await self.distribute_workers()
        if self.step_count == 0:
            if self.supply_used == 12:
                fcc.train(UnitTypeId.SCV)
            if self.supply_used == 13 and self.already_pending(UnitTypeId.SUPPLYDEPOT) == 0:
                await self.build(UnitTypeId.SUPPLYDEPOT, near=fcc.position.towards(self.game_info.map_center, 8))
                fcc.train(UnitTypeId.SCV)
            if self.workers.amount <= 19 and not self.structures(UnitTypeId.BARRACKS):
                fcc.train(UnitTypeId.SCV)
            if self.structures(UnitTypeId.SUPPLYDEPOT):
                if not self.structures(UnitTypeId.BARRACKS) and self.already_pending(UnitTypeId.BARRACKS) == 0:
                    if self.can_afford(UnitTypeId.BARRACKS):
                        await self.build(UnitTypeId.BARRACKS, near=fcc.position.towards(self.game_info.map_center, 4))

            if self.supply_left < 2 and self.can_afford(UnitTypeId.SUPPLYDEPOT) and self.already_pending(
                    UnitTypeId.SUPPLYDEPOT) <= 3:
                await self.build(UnitTypeId.SUPPLYDEPOT, near=fcc.position.towards(self.game_info.map_center, 8))

            if self.structures(UnitTypeId.SUPPLYDEPOT) and self.gas_buildings.amount == 0 and self.already_pending(
                    UnitTypeId.REFINERY) == 0:
                if self.can_afford(UnitTypeId.REFINERY):
                    # All the vespene geysirs nearby, including ones with a refinery on top of it
                    vgs = self.vespene_geyser.closer_than(10, fcc)
                    for vg in vgs:
                        if self.gas_buildings.filter(lambda unit: unit.distance_to(vg) < 1):
                            continue
                        # Select a worker closest to the vespene geysir
                        worker: Unit = self.select_build_worker(vg)
                        # Worker can be none in cases where all workers are dead
                        # or 'select_build_worker' function only selects from workers which carry no minerals
                        if worker is None:
                            continue
                        # Issue the build command to the worker, important: vg has to be a Unit, not a position
                        worker.build_gas(vg)
                        # Only issue one build geysir command per frame
                        break
            if self.can_afford(UnitTypeId.REACTOR) and self.structures(UnitTypeId.BARRACKS):
                for bb in self.structures(UnitTypeId.BARRACKS).ready.idle:
                    bb(AbilityId.BUILD_REACTOR_BARRACKS)

            if self.townhalls.ready.amount + self.already_pending(UnitTypeId.COMMANDCENTER) < 2:

                if self.can_afford(UnitTypeId.COMMANDCENTER):
                    await self.expand_now()
            if self.supply_workers + self.already_pending(
                    UnitTypeId.SCV) < self.townhalls.amount * 18 and bases.is_idle:
                if self.can_afford(UnitTypeId.SCV):
                    bases.train(UnitTypeId.SCV)

            for ccs in self.townhalls(UnitTypeId.COMMANDCENTER).idle:
                # Check if we have 150 minerals; this used to be an issue when the API returned 550 (value) of the orbital, but we only wanted the 150 minerals morph cost
                if self.can_afford(UnitTypeId.ORBITALCOMMAND):
                    ccs(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND)
            for oc in self.townhalls(UnitTypeId.ORBITALCOMMAND).filter(lambda x: x.energy >= 50):
                mfs: Units = self.mineral_field.closer_than(10, oc)
                if mfs:
                    mf: Unit = max(mfs, key=lambda x: x.mineral_contents)
                    oc(AbilityId.CALLDOWNMULE_CALLDOWNMULE, mf)
            barracks_tech_requirement: float = self.tech_requirement_progress(UnitTypeId.BARRACKS)
            if (
                    barracks_tech_requirement == 1
                    # self.structures.of_type(
                    #     [UnitTypeId.SUPPLYDEPOT, UnitTypeId.SUPPLYDEPOTLOWERED, UnitTypeId.SUPPLYDEPOTDROP]
                    # ).ready
                    and self.structures(UnitTypeId.BARRACKS).ready.amount + self.already_pending(
                UnitTypeId.BARRACKS) < 4 and
                    self.can_afford(UnitTypeId.BARRACKS)
            ):
                workers: Units = self.workers.gathering
                if (
                        workers and self.townhalls
                ):  # need to check if townhalls.amount > 0 because placement is based on townhall location
                    worker: Unit = workers.furthest_to(workers.center)
                    # I chose placement_step 4 here so there will be gaps between barracks hopefully
                    location: Point2 = await self.find_placement(
                        UnitTypeId.BARRACKS, self.townhalls.random.position, placement_step=4
                    )
                    if location:
                        worker.build(UnitTypeId.BARRACKS, location)
            if self.supply_left > 0 and self.structures(UnitTypeId.BARRACKS).ready:
                for rax in self.structures(UnitTypeId.BARRACKS).idle:
                    if self.can_afford(UnitTypeId.MARINE):
                        rax.train(UnitTypeId.MARINE)



def main():
    run_game(
        maps.get(ladder_map_pool_2022_07[1]),
        [Bot(Race.Terran, Terran_normal_agent()), Computer(Race.Terran, Difficulty.Hard)],
        realtime=False,

    )




if __name__ == "__main__":
    main()
