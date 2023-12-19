import os
import random
import copy
import time
from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Race
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from config.config import map_race, map_difficulty
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.position import Point2
from sc2.units import Units
from utils.action_info import ActionDescriptions

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
import nest_asyncio

nest_asyncio.apply()


class Zerg_Bot(BotAI):
    def __init__(self, transaction, lock, isReadyForNextStep):

        self.lock = lock
        self.transaction = transaction
        self.worker_supply = 12  # 农民数量
        self.army_supply = 0  # 部队人口
        self.base_count = 1  # 基地数量
        self.base_pending = 0
        self.enemy_units_count = 0
        # self.army_units_list=[]  # 我方部队列表

        # self.enemy_list = []

        self.overlord_count = 1
        self.overlord_planning_count = 0
        self.queen_count = 0

        # building_count
        self.Evolution_chamber_count = 0
        self.Spire_count = 0
        self.Roach_warren_count = 0
        self.Baneling_nest_count = 0
        self.Nydus_Network_count = 0
        self.Nydus_Worm_count = 0
        self.Greater_spire_count = 0
        self.Hydralisk_den_count = 0
        self.Lurker_Den_count = 0
        self.Lair_count = 0
        self.Hive_count = 0
        self.Ultralisk_Cavern_count = 0
        self.gas_buildings_count = 0
        self.gas_buildings_planning_count = 0
        self.overseer_count = 0
        self.rally_defend = False
        self.isReadyForNextStep = isReadyForNextStep
        self.action_dict = self.get_action_dict()
        self.temp_failure_list = []

    def get_enemy_unity(self):
        if self.enemy_units:
            unit_type_amount = dict()
            for unit in self.enemy_units:
                unit_type = 'enemy_' + str(unit.type_id)  # 将键值加上前缀 'enemy_'
                if unit_type not in unit_type_amount:
                    unit_type_amount[unit_type] = 1
                    print(unit_type_amount)
                else:
                    unit_type_amount[unit_type] += 1
            return unit_type_amount
        else:
            return {}

    def get_action_dict(self):
        action_description = ActionDescriptions('Zerg')
        action_dict = action_description.action_descriptions
        flat_dict = {}
        for key, value in action_dict.items():
            for inner_key, inner_value in value.items():
                flat_dict[inner_key] = inner_value
        return flat_dict

    def get_enemy_structure(self):
        if self.enemy_structures:
            structure_type_amount = dict()
            for structure in self.enemy_structures:
                structure_type = 'enemy_' + str(structure.type_id)  # 将键值加上前缀 'enemy_'
                if structure_type not in structure_type_amount:
                    structure_type_amount[structure_type] = 1
                    print(structure_type_amount)
                else:
                    structure_type_amount[structure_type] += 1
            return structure_type_amount
        else:
            return {}

    def get_information(self):
        self.worker_supply = self.workers.amount  # 农民数量
        self.army_supply = self.supply_army  # 部队人口
        self.base_count = self.structures(UnitTypeId.HATCHERY).amount + self.structures(
            UnitTypeId.LAIR).amount + self.structures(UnitTypeId.HIVE).amount  # 基地数量
        self.base_pending = self.already_pending(UnitTypeId.HATCHERY)  # 正在建造的基地数量
        self.overlord_count = self.units(UnitTypeId.OVERLORD).amount  # 当前的房子数量
        self.overlord_planning_count = self.already_pending(UnitTypeId.OVERLORD)  # 正在建造的房子数量

        self.queen_count = self.units(UnitTypeId.QUEEN).amount  # 当前的女王数量
        self.Evolution_chamber_count = self.structures(UnitTypeId.EVOLUTIONCHAMBER).amount  # bv数量
        self.Spire_count = self.structures(UnitTypeId.SPIRE).amount  # vs数量
        self.Roach_warren_count = self.structures(UnitTypeId.ROACHWARREN).amount  # 蟑螂巢数量
        self.Baneling_nest_count = self.structures(UnitTypeId.BANELINGNEST).amount  # 爆虫巢数量
        self.Nydus_Network_count = self.structures(UnitTypeId.NYDUSNETWORK).amount  # 虫洞网络数量
        self.Nydus_Worm_count = self.structures(UnitTypeId.NYDUSWORMLAVADEATH).amount  # 虫洞数量
        self.Greater_spire_count = self.structures(UnitTypeId.GREATERSPIRE).amount  # 大龙塔数量
        self.Hydralisk_den_count = self.structures(UnitTypeId.HYDRALISKDEN).amount  # 刺蛇巢数量
        self.Lurker_Den_count = self.structures(UnitTypeId.LURKERDENMP).amount  # 潜伏者巢穴数量
        self.Lair_count = self.structures(UnitTypeId.LAIR).amount  # 巢穴数量
        self.Hive_count = self.structures(UnitTypeId.HIVE).amount  # 主巢数量
        self.Ultralisk_Cavern_count = self.structures(UnitTypeId.ULTRALISKCAVERN).amount  # 雷兽窟数量
        self.gas_buildings_count = self.gas_buildings.amount  # 气矿建筑数量
        self.gas_buildings_planning_count = self.already_pending(UnitTypeId.EXTRACTOR)  # 正在建造的气矿建筑数量
        self.overseer_count = self.units(UnitTypeId.OVERSEER).amount  # 当前的监察王虫数量
        self.enemy_unit_type_amount = self.get_enemy_unity()
        self.enemy_structure_type_amount = self.get_enemy_structure()
        information = {
            # 资源相关
            'game_time': self.time_formatted,
            'worker_supply': self.worker_supply,
            'mineral': self.minerals,
            'gas': self.vespene,
            'supply_left': self.supply_left,
            'supply_cap': self.supply_cap,
            'supply_used': self.supply_used,
            'army_supply': self.army_supply,
            'enemy_units_count': self.enemy_units_count,

            # 建筑相关
            'base_count': self.base_count,
            'lair_count': self.Lair_count,
            'hive_count': self.Hive_count,
            'evolution_chamber_count': self.Evolution_chamber_count,
            'spire_count': self.Spire_count,
            'roach_warren_count': self.Roach_warren_count,
            'baneling_nest_count': self.Baneling_nest_count,
            'greater_spire_count': self.Greater_spire_count,
            'hydralisk_den_count': self.Hydralisk_den_count,
            'lurker_den_count': self.Lurker_Den_count,
            'ultralisk_cavern_count': self.Ultralisk_Cavern_count,
            'gas_buildings_count': self.gas_buildings_count,
            'spore_crawler_count': self.structures(UnitTypeId.SPORECRAWLER).amount,
            'spine_crawler_count': self.structures(UnitTypeId.SPINECRAWLER).amount,
            'nydus_network_count': self.structures(UnitTypeId.NYDUSNETWORK).amount,
            'nydus_worm_count': self.Nydus_Worm_count,

            # 单位相关
            'queen_count': self.queen_count,
            'overlord_count': self.overlord_count,
            'overseer_count': self.overseer_count,
            'larva_count': self.larva.amount,
            'drone_count': self.units(UnitTypeId.DRONE).amount,
            'zergling_count': self.units(UnitTypeId.ZERGLING).amount,
            'baneling_count': self.units(UnitTypeId.BANELING).amount,
            'roach_count': self.units(UnitTypeId.ROACH).amount,
            'ravager_count': self.units(UnitTypeId.RAVAGER).amount,
            'hydralisk_count': self.units(UnitTypeId.HYDRALISK).amount,
            'lurker_count': self.units(UnitTypeId.LURKERMP).amount,
            'mutalisk_count': self.units(UnitTypeId.MUTALISK).amount,
            'corruptor_count': self.units(UnitTypeId.CORRUPTOR).amount,
            'broodlord_count': self.units(UnitTypeId.BROODLORD).amount,
            'ultralisk_count': self.units(UnitTypeId.ULTRALISK).amount,
            'infestor_count': self.units(UnitTypeId.INFESTOR).amount,
            'viper_count': self.units(UnitTypeId.VIPER).amount,
            'swarmhost_count': self.units(UnitTypeId.SWARMHOSTMP).amount,

            # 计划中的事项
            'planning_base_count': self.base_pending,
            'planning_lair_count': self.already_pending(UnitTypeId.LAIR),
            'planning_hive_count': self.already_pending(UnitTypeId.HIVE),
            'planning_gas_building_count': self.gas_buildings_planning_count,
            'planning_spawning_pool_count': self.already_pending(UnitTypeId.SPAWNINGPOOL),
            'planning_evolution_chamber_count': self.already_pending(UnitTypeId.EVOLUTIONCHAMBER),
            'planning_baneling_nest_count': self.already_pending(UnitTypeId.BANELINGNEST),
            'planning_roach_warren_count': self.already_pending(UnitTypeId.ROACHWARREN),
            'planning_infestation_pit_count': self.already_pending(UnitTypeId.INFESTATIONPIT),
            'planning_hydralisk_den_count': self.already_pending(UnitTypeId.HYDRALISKDEN),
            'planning_spire_count': self.already_pending(UnitTypeId.SPIRE),
            'planning_ultralisk_cavern_count': self.already_pending(UnitTypeId.ULTRALISKCAVERN),
            'planning_lurker_den_count': self.already_pending(UnitTypeId.LURKERDENMP),
            'planning_greater_spire_count': self.already_pending(UnitTypeId.GREATERSPIRE),
            'planning_spore_crawler_count': self.already_pending(UnitTypeId.SPORECRAWLER),
            'planning_spine_crawler_count': self.already_pending(UnitTypeId.SPINECRAWLER),
            'planning_nydus_network_count': self.already_pending(UnitTypeId.NYDUSNETWORK),

            # 计划中的单位
            'planning_queen_count': self.already_pending(UnitTypeId.QUEEN),
            'planning_drone_count': self.already_pending(UnitTypeId.DRONE),
            'planning_overlord_count': self.overlord_planning_count,
            'planning_overseer_count': self.already_pending(UnitTypeId.OVERSEER),
            'planning_zergling_count': self.already_pending(UnitTypeId.ZERGLING),
            'planning_baneling_count': self.already_pending(UnitTypeId.BANELING),
            'planning_roach_count': self.already_pending(UnitTypeId.ROACH),
            'planning_ravager_count': self.already_pending(UnitTypeId.RAVAGER),
            'planning_hydralisk_count': self.already_pending(UnitTypeId.HYDRALISK),
            'planning_lurker_count': self.already_pending(UnitTypeId.LURKERMP),
            'planning_mutalisk_count': self.already_pending(UnitTypeId.MUTALISK),
            'planning_corruptor_count': self.already_pending(UnitTypeId.CORRUPTOR),
            'planning_broodlord_count': self.already_pending(UnitTypeId.BROODLORD),
            'planning_ultralisk_count': self.already_pending(UnitTypeId.ULTRALISK),
            'planning_infestor_count': self.already_pending(UnitTypeId.INFESTOR),
            'planning_viper_count': self.already_pending(UnitTypeId.VIPER),
            'planning_swarmhost_count': self.already_pending(UnitTypeId.SWARMHOSTMP),
            # 研究状态: 1 表示已完成，0 表示未完成，0-1 之间的数值表示研究进度
            'zergling_movement_speed_research_status': self.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED),
            'zergling_attack_speed_research_status': self.already_pending_upgrade(UpgradeId.ZERGLINGATTACKSPEED),
            'zerg_ground_armor_level_1_research_status': self.already_pending_upgrade(UpgradeId.ZERGGROUNDARMORSLEVEL1),
            'zerg_ground_armor_level_2_research_status': self.already_pending_upgrade(UpgradeId.ZERGGROUNDARMORSLEVEL2),
            'zerg_ground_armor_level_3_research_status': self.already_pending_upgrade(UpgradeId.ZERGGROUNDARMORSLEVEL3),
            'zerg_melee_weapons_level_1_research_status': self.already_pending_upgrade(
                UpgradeId.ZERGMELEEWEAPONSLEVEL1),
            'zerg_melee_weapons_level_2_research_status': self.already_pending_upgrade(
                UpgradeId.ZERGMELEEWEAPONSLEVEL2),
            'zerg_melee_weapons_level_3_research_status': self.already_pending_upgrade(
                UpgradeId.ZERGMELEEWEAPONSLEVEL3),
            'zerg_missile_weapons_level_1_research_status': self.already_pending_upgrade(
                UpgradeId.ZERGMISSILEWEAPONSLEVEL1),
            'zerg_missile_weapons_level_2_research_status': self.already_pending_upgrade(
                UpgradeId.ZERGMISSILEWEAPONSLEVEL2),
            'zerg_missile_weapons_level_3_research_status': self.already_pending_upgrade(
                UpgradeId.ZERGMISSILEWEAPONSLEVEL3),
            'glial_reconstitution_research_status': self.already_pending_upgrade(UpgradeId.GLIALRECONSTITUTION),
            'tunneling_claws_research_status': self.already_pending_upgrade(UpgradeId.TUNNELINGCLAWS),
            'digging_claws_research_status': self.already_pending_upgrade(UpgradeId.DIGGINGCLAWS),
            'lurker_range_research_status': self.already_pending_upgrade(UpgradeId.LURKERRANGE),
            'burrow_research_status': self.already_pending_upgrade(UpgradeId.BURROW),
            'overlord_speed_research_status': self.already_pending_upgrade(UpgradeId.OVERLORDSPEED),
            'infestor_energy_upgrade_research_status': self.already_pending_upgrade(UpgradeId.INFESTORENERGYUPGRADE),
            'neural_parasite_research_status': self.already_pending_upgrade(UpgradeId.NEURALPARASITE),
            'evolve_grooved_spines_research_status': self.already_pending_upgrade(UpgradeId.EVOLVEGROOVEDSPINES),
            'evolve_muscular_augments_research_status': self.already_pending_upgrade(UpgradeId.EVOLVEMUSCULARAUGMENTS),
            'centrifical_hooks_research_status': self.already_pending_upgrade(UpgradeId.CENTRIFICALHOOKS),
            'chitinous_plating_research_status': self.already_pending_upgrade(UpgradeId.CHITINOUSPLATING),
            'anabolic_synthesis_research_status': self.already_pending_upgrade(UpgradeId.ANABOLICSYNTHESIS),
            'zerg_flyer_armor_level_1_research_status': self.already_pending_upgrade(UpgradeId.ZERGFLYERARMORSLEVEL1),
            'zerg_flyer_armor_level_2_research_status': self.already_pending_upgrade(UpgradeId.ZERGFLYERARMORSLEVEL2),
            'zerg_flyer_armor_level_3_research_status': self.already_pending_upgrade(UpgradeId.ZERGFLYERARMORSLEVEL3),
            'zerg_flyer_weapons_level_1_research_status': self.already_pending_upgrade(
                UpgradeId.ZERGFLYERWEAPONSLEVEL1),
            'zerg_flyer_weapons_level_2_research_status': self.already_pending_upgrade(
                UpgradeId.ZERGFLYERWEAPONSLEVEL2),
            'zerg_flyer_weapons_level_3_research_status': self.already_pending_upgrade(
                UpgradeId.ZERGFLYERWEAPONSLEVEL3),
        }
        if self.enemy_unit_type_amount is not None:
            information.update(self.enemy_unit_type_amount)
        if self.enemy_structure_type_amount is not None:
            information.update(self.enemy_structure_type_amount)
        return information

    async def defend(self):
        print("Defend:", self.rally_defend)
        if self.structures(UnitTypeId.HATCHERY).exists or self.structures(UnitTypeId.LAIR).exists or self.structures(
                UnitTypeId.HIVE).exists and self.supply_army >= 2:
            for base in self.townhalls:
                if self.enemy_units.amount >= 2 and self.enemy_units.closest_distance_to(base) < 30:
                    self.rally_defend = True
                    for unit in self.units.of_type(
                            {UnitTypeId.ZERGLING, UnitTypeId.BANELING, UnitTypeId.QUEEN, UnitTypeId.ROACH,
                             UnitTypeId.OVERSEER,
                             UnitTypeId.ULTRALISK, UnitTypeId.MUTALISK, UnitTypeId.INFESTOR, UnitTypeId.CORRUPTOR,
                             UnitTypeId.BROODLORD,
                             UnitTypeId.OVERSEER, UnitTypeId.RAVAGER, UnitTypeId.VIPER, UnitTypeId.SWARMHOSTMP,
                             UnitTypeId.LURKERMP}):
                        closed_enemy = self.enemy_units.sorted(lambda x: x.distance_to(unit))
                        unit.attack(closed_enemy[0])
                else:
                    self.rally_defend = False

            if self.rally_defend == True:
                map_center = self.game_info.map_center
                rally_point = self.townhalls.random.position.towards(map_center, distance=5)
                for unit in self.units.of_type(
                        {UnitTypeId.ZEALOT, UnitTypeId.ARCHON, UnitTypeId.STALKER, UnitTypeId.SENTRY,
                         UnitTypeId.ADEPT, UnitTypeId.HIGHTEMPLAR, UnitTypeId.DARKTEMPLAR,
                         UnitTypeId.OBSERVER, UnitTypeId.PHOENIX, UnitTypeId.CARRIER, UnitTypeId.VOIDRAY,
                         UnitTypeId.TEMPEST, UnitTypeId.ORACLE, UnitTypeId.COLOSSUS,
                         UnitTypeId.DISRUPTOR, UnitTypeId.WARPPRISM, UnitTypeId.IMMORTAL,
                         UnitTypeId.CHANGELINGZEALOT}):
                    if unit.distance_to(self.start_location) > 100 and unit not in self.unit_tags_received_action:
                        unit.move(rally_point)

    def record_failure(self, action, reason):
        self.temp_failure_list.append(f'Action failed: {self.action_dict[action]}, Reason: {reason}')

    def handle_attack(self, unit, target_units, target_structures, reward_value):
        try:
            if target_units.closer_than(30, unit):
                unit.attack(random.choice(target_units.closer_than(30, unit)))
            elif target_structures.closer_than(30, unit):
                unit.attack(random.choice(target_structures.closer_than(30, unit)))
            else:
                unit.attack(self.enemy_start_locations[0])
            print('attack')
            return reward_value
        except Exception as e:
            print(e)
            return 0

    async def handle_scouting(self, unit_type, action_id):
        # print(f'action={action_id}')

        # Check if the iteration delay has passed
        if not self.units(unit_type).exists:
            return self.record_failure(action_id, f'No {unit_type} available for scouting')
        scout_unit = random.choice(self.units(unit_type).idle) if self.units(
            unit_type).idle.exists else random.choice(self.units(unit_type))
        scout_unit.attack(self.enemy_start_locations[0])
        # print(f'{unit_type} scouting')

    async def handle_action_0(self):
        action_id = 0
        action = self.action_dict[action_id]
        print(f'action={action}')

        if not self.townhalls.exists:
            return self.record_failure(action_id, 'No bases available')

        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No drones available')

        if self.supply_cap + self.already_pending(UnitTypeId.OVERLORD) * 6 > 200:
            return self.record_failure(action_id, 'Supply cap exceeded')

        larvae: Units = self.larva
        if not larvae:
            return self.record_failure(action_id, 'Not enough larvae')

        if not self.can_afford(UnitTypeId.OVERLORD):
            return self.record_failure(action_id, 'Cannot afford to train overlord')

        larvae.random.train(UnitTypeId.OVERLORD)
        print('train overlord')

    async def handle_action_1(self):
        action_id = 1
        action = self.action_dict[action_id]
        print(f'action={action}')

        if not self.townhalls.exists:
            return self.record_failure(action_id, 'No bases available')

        if self.supply_left < 1:
            return self.record_failure(action_id, 'Not enough supply')

        larvae: Units = self.larva
        if not larvae:
            return self.record_failure(action_id, 'Not enough larvae')

        if not self.can_afford(UnitTypeId.DRONE):
            return self.record_failure(action_id, 'Cannot afford to train drone')

        larvae.random.train(UnitTypeId.DRONE)
        print('train drones')

    async def handle_action_2(self):
        action_id = 2
        action = self.action_dict[action_id]
        print(f'action={action}')

        bases = self.townhalls
        if not bases.exists:
            return self.record_failure(action_id, 'No bases available')

        if not self.structures(UnitTypeId.SPAWNINGPOOL).exists:
            return self.record_failure(action_id, 'Spawning pool not available')

        if self.supply_left < 2:
            return self.record_failure(action_id, 'Not enough supply')

        if not self.can_afford(UnitTypeId.QUEEN):
            return self.record_failure(action_id, 'Cannot afford to train queen')

        for base in bases:
            if base.is_idle:
                base.train(UnitTypeId.QUEEN)
                print('train queen')
                break

    async def handle_action_3(self):
        action_id = 3
        action = self.action_dict[action_id]
        print(f'action={action}')

        bases = self.townhalls
        if not bases.exists:
            return self.record_failure(action_id, 'No bases available')

        if not self.structures(UnitTypeId.SPAWNINGPOOL).exists:
            return self.record_failure(action_id, 'Spawning pool not available')

        if self.supply_left < 1:
            return self.record_failure(action_id, 'Not enough supply')

        larvae: Units = self.larva
        if not larvae:
            return self.record_failure(action_id, 'Not enough larvae')

        if not self.can_afford(UnitTypeId.ZERGLING):
            return self.record_failure(action_id, 'Cannot afford to train zergling')

        larvae.random.train(UnitTypeId.ZERGLING)
        print('train zergling')

    async def handle_action_4(self):
        action_id = 4
        action = self.action_dict[action_id]
        print(f'action={action}')

        bases = self.townhalls
        if not bases.exists:
            return self.record_failure(action_id, 'No bases available')

        if not self.structures(UnitTypeId.ROACHWARREN).exists:
            return self.record_failure(action_id, 'Roach warren not available')

        if self.supply_left < 2:
            return self.record_failure(action_id, 'Not enough supply')

        larvae: Units = self.larva
        if not larvae:
            return self.record_failure(action_id, 'Not enough larvae')

        if not self.can_afford(UnitTypeId.ROACH):
            return self.record_failure(action_id, 'Cannot afford to train roach')

        larvae.random.train(UnitTypeId.ROACH)
        print('train roach')

    async def handle_action_5(self):
        action_id = 5
        action = self.action_dict[action_id]
        print(f'action={action}')

        bases = self.townhalls
        if not bases.exists:
            return self.record_failure(action_id, 'No bases available')

        if not self.structures(UnitTypeId.HYDRALISKDEN).exists:
            return self.record_failure(action_id, 'Hydralisk den not available')

        if self.supply_left < 2:
            return self.record_failure(action_id, 'Not enough supply')

        larvae: Units = self.larva
        if not larvae:
            return self.record_failure(action_id, 'Not enough larvae')

        if not self.can_afford(UnitTypeId.HYDRALISK):
            return self.record_failure(action_id, 'Cannot afford to train hydralisk')

        larvae.random.train(UnitTypeId.HYDRALISK)
        print('train hydralisk')

    async def handle_action_6(self):
        action_id = 6
        action = self.action_dict[action_id]
        print(f'action={action}')
        bases = self.townhalls
        if not bases.exists:
            return self.record_failure(action_id, 'No bases available')

        if not self.structures(UnitTypeId.SPIRE).exists:
            return self.record_failure(action_id, 'Spire not available')

        if self.supply_left < 2:
            return self.record_failure(action_id, 'Not enough supply')

        larvae: Units = self.larva
        if not larvae:
            return self.record_failure(action_id, 'Not enough larvae')

        if not self.can_afford(UnitTypeId.MUTALISK):
            return self.record_failure(action_id, 'Cannot afford to train mutalisk')

        larvae.random.train(UnitTypeId.MUTALISK)
        print('train mutalisk')

    async def handle_action_7(self):
        action_id = 7
        action = self.action_dict[action_id]
        print(f'action={action}')
        bases = self.townhalls
        if not bases.exists:
            return self.record_failure(action_id, 'No bases available')

        if not self.structures(UnitTypeId.SPIRE).exists:
            return self.record_failure(action_id, 'Spire not available')

        if self.supply_left < 2:
            return self.record_failure(action_id, 'Not enough supply')

        larvae: Units = self.larva
        if not larvae:
            return self.record_failure(action_id, 'Not enough larvae')

        if not self.can_afford(UnitTypeId.CORRUPTOR):
            return self.record_failure(action_id, 'Cannot afford to train corruptor')

        larvae.random.train(UnitTypeId.CORRUPTOR)
        print('train corruptor')

    async def handle_action_8(self):
        action_id = 8
        action = self.action_dict[action_id]
        print(f'action={action}')
        bases = self.townhalls
        if not bases.exists:
            return self.record_failure(action_id, 'No bases available')

        if not self.structures(UnitTypeId.SPIRE).exists:
            return self.record_failure(action_id, 'Spire not available')

        if self.supply_left < 2:
            return self.record_failure(action_id, 'Not enough supply')

        larvae: Units = self.larva
        if not larvae:
            return self.record_failure(action_id, 'Not enough larvae')

        if not self.can_afford(UnitTypeId.INFESTOR):
            return self.record_failure(action_id, 'Cannot afford to train infestor')

        larvae.random.train(UnitTypeId.INFESTOR)
        print('train infestor')

    async def handle_action_9(self):
        action_id = 9
        action = self.action_dict[action_id]
        print(f'action={action}')

        bases = self.townhalls
        if not bases.exists:
            return self.record_failure(action_id, 'No bases available')

        if not self.structures(UnitTypeId.INFESTATIONPIT).exists:
            return self.record_failure(action_id, 'Infestation Pit not available')

        if self.supply_left < 4:
            return self.record_failure(action_id, 'Not enough supply')

        larvae: Units = self.larva
        if not larvae:
            return self.record_failure(action_id, 'Not enough larvae')

        if not self.can_afford(UnitTypeId.SWARMHOSTMP):
            return self.record_failure(action_id, 'Cannot afford to train swarm host')

        larvae.random.train(UnitTypeId.SWARMHOSTMP)
        print('train swarm host')

    async def handle_action_10(self):
        action_id = 10
        action = self.action_dict[action_id]
        print(f'action={action}')

        bases = self.townhalls
        if not bases.exists:
            return self.record_failure(action_id, 'No bases available')

        if not self.structures(UnitTypeId.ULTRALISKCAVERN).exists:
            return self.record_failure(action_id, 'Ultralisk Cavern not available')

        if self.supply_left < 6:
            return self.record_failure(action_id, 'Not enough supply')

        larvae: Units = self.larva
        if not larvae:
            return self.record_failure(action_id, 'Not enough larvae')

        if not self.can_afford(UnitTypeId.ULTRALISK):
            return self.record_failure(action_id, 'Cannot afford to train ultralisk')

        larvae.random.train(UnitTypeId.ULTRALISK)
        print('train ultralisk')

    async def handle_action_11(self):
        action_id = 11
        action = self.action_dict[action_id]
        print(f'action={action}')

        bases = self.townhalls
        if not bases.exists:
            return self.record_failure(action_id, 'No bases available')

        if not self.structures(UnitTypeId.HIVE).exists:
            return self.record_failure(action_id, 'Hive not available')

        if self.supply_left < 3:
            return self.record_failure(action_id, 'Not enough supply')

        larvae: Units = self.larva
        if not larvae:
            return self.record_failure(action_id, 'Not enough larvae')

        if not self.can_afford(UnitTypeId.VIPER):
            return self.record_failure(action_id, 'Cannot afford to train viper')

        larvae.random.train(UnitTypeId.VIPER)
        print('train viper')

    async def handle_action_12(self):
        action_id = 12
        action = self.action_dict[action_id]
        print(f'action={action}')
        bases = self.townhalls
        if not bases.exists:
            return self.record_failure(action_id, 'No bases available')
        if not self.structures(UnitTypeId.BANELINGNEST).exists:
            return self.record_failure(action_id, 'Baneling Nest not available')
        if not self.can_afford(UnitTypeId.BANELING):
            return self.record_failure(action_id, 'Cannot afford Baneling')
        if not self.units(UnitTypeId.ZERGLING).exists:
            return self.record_failure(action_id, 'No Zerglings available to morph')

        zerglings = self.units(UnitTypeId.ZERGLING)
        for ling in zerglings:
            if ling.is_idle:
                ling.build(UnitTypeId.BANELING)
                print('morph baneling')
                break

    async def handle_action_13(self):
        action_id = 13
        action = self.action_dict[action_id]
        print(f'action={action}')

        bases = self.townhalls
        if not bases.exists:
            return self.record_failure(action_id, 'No bases available')
        if not self.structures(UnitTypeId.ROACHWARREN).exists:
            return self.record_failure(action_id, 'Roach Warren not available')
        if self.supply_left < 1:
            return self.record_failure(action_id, 'Not enough supply')
        if not self.can_afford(UnitTypeId.RAVAGER):
            return self.record_failure(action_id, 'Cannot afford Ravager')
        if not self.units(UnitTypeId.ROACH).exists:
            return self.record_failure(action_id, 'No Roaches available to morph')

        roaches = self.units(UnitTypeId.ROACH)
        for roach in roaches:
            if roach.is_idle:
                roach.build(UnitTypeId.RAVAGER)
                print('morph Ravager')
                break

    async def handle_action_14(self):
        action_id = 14
        action = self.action_dict[action_id]
        print(f'action={action}')

        bases = self.townhalls
        if not bases.exists:
            return self.record_failure(action_id, 'No bases available')
        if not self.structures(UnitTypeId.LURKERDENMP).exists:
            return self.record_failure(action_id, 'LurkerDen not available')
        if self.supply_left < 1:
            return self.record_failure(action_id, 'Not enough supply')
        if not self.can_afford(UnitTypeId.LURKERMP):
            return self.record_failure(action_id, 'Cannot afford lurker')
        if not self.units(UnitTypeId.HYDRALISK).exists:
            return self.record_failure(action_id, 'No hydra available to morph')

        hydras = self.units(UnitTypeId.HYDRALISK)
        for hydra in hydras:
            if hydra.is_idle:
                hydra.build(UnitTypeId.LURKERMP)
                print('morph Lurker')
                break

    async def handle_action_15(self):
        action_id = 15
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check if we have bases and overlords
        if not self.townhalls.exists:
            return self.record_failure(action_id, 'No bases available')

        # Check if Greater Spire exists
        if not self.structures(UnitTypeId.GREATERSPIRE).exists:
            return self.record_failure(action_id, 'Greater Spire not available')

        # Check supply left
        if self.supply_left < 2:
            return self.record_failure(action_id, 'Not enough supply')

        # Check if we can afford a broodlord
        if not self.can_afford(UnitTypeId.BROODLORD):
            return self.record_failure(action_id, 'Cannot afford broodlord')

        # Check if we have corruptors available for morphing
        corruptors = self.units(UnitTypeId.CORRUPTOR)
        if not corruptors.exists:
            return self.record_failure(action_id, 'No corruptor available to morph')

        # Find an idle corruptor and morph it into a broodlord
        for corruptor in corruptors:
            if corruptor.is_idle:
                corruptor.build(UnitTypeId.BROODLORD)
                print('morph broodlord')
                return  # Exit after morphing one corruptor

    async def handle_action_16(self):
        action_id = 16
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check if we have bases and overlords
        if not self.townhalls.exists:
            return self.record_failure(action_id, 'No bases available')
        if not self.units(UnitTypeId.OVERLORD).exists:
            return self.record_failure(action_id, 'No overlords available')

        # Check if LAIR or HIVE exists
        if not (self.structures(UnitTypeId.LAIR).exists or self.structures(UnitTypeId.HIVE).exists):
            return self.record_failure(action_id, 'LAIR or HIVE not available')

        # Check if we can afford an overseer
        if not self.can_afford(UnitTypeId.OVERSEER):
            return self.record_failure(action_id, 'Cannot afford overseer')

        # Find an idle overlord and morph it into an overseer
        overlords = self.units(UnitTypeId.OVERLORD).idle
        for overlord in overlords:
            if self.can_afford(UnitTypeId.OVERSEER):
                overlord.build(UnitTypeId.OVERSEER)
                print('morph overseer')
                return  # Exit after morphing one overlord

    async def handle_action_17(self):
        action_id = 17
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check if we have drones
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No drones available')

        # Check if we have townhalls
        if not self.townhalls.exists:
            return self.record_failure(action_id, 'No townhalls available')

        # Check if we can afford an extractor
        if not self.can_afford(UnitTypeId.EXTRACTOR):
            return self.record_failure(action_id, 'Cannot afford extractor')

        # Try to build extractors near each townhall
        for base in self.townhalls:
            for vespene in self.vespene_geyser.closer_than(10, base):
                if not self.structures(UnitTypeId.EXTRACTOR).closer_than(2, vespene):
                    await self.build(UnitTypeId.EXTRACTOR, vespene)
                    print('build extractor')
                    return  # Exit after building one extractor

    async def handle_action_18(self):
        action_id = 18
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check if we have drones
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No drones available')

        # Check if we have townhalls
        if not self.townhalls.amount:
            return self.record_failure(action_id, 'No townhalls available')

        # Check if we can afford a hatchery
        if not self.can_afford(UnitTypeId.HATCHERY):
            return self.record_failure(action_id, 'Cannot afford hatchery')

        # Try to expand
        await self.expand_now()
        print('build hatchery')

    async def handle_action_19(self):
        action_id = 19
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check if we have drones
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No drones available')

        # Check if we have townhalls
        if not self.townhalls.exists:
            return self.record_failure(action_id, 'No townhalls available')

        # Check if SPAWNINGPOOL does not exist and is not pending
        if self.structures(UnitTypeId.SPAWNINGPOOL).exists or self.already_pending(UnitTypeId.SPAWNINGPOOL):
            return self.record_failure(action_id, 'Spawning pool already exists or is pending')

        # Try to build SPAWNINGPOOL
        worker_candidates = self.workers.filter(lambda worker: (
                                                                       worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
        place_postion = self.start_location.position + Point2((self.Location * 10, 0))
        placement_position = await self.find_placement(UnitTypeId.SPAWNINGPOOL, near=place_postion, placement_step=6)

        if not placement_position:
            return self.record_failure(action_id, 'Cannot find placement for spawning pool')

        if not self.can_afford(UnitTypeId.SPAWNINGPOOL) or self.already_pending(UnitTypeId.SPAWNINGPOOL) != 0:
            return self.record_failure(action_id, 'Cannot afford spawning pool or spawning pool is already pending')

        build_worker = worker_candidates.closest_to(placement_position)
        build_worker.build(UnitTypeId.SPAWNINGPOOL, placement_position)
        print('build spawningpool')

    async def handle_action_20(self):
        action_id = 20
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check if we have drones
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No drones available')

        # Check if we have townhalls
        if not self.townhalls.exists:
            return self.record_failure(action_id, 'No townhalls available')

        # Check if SPAWNINGPOOL exists
        if not self.structures(UnitTypeId.SPAWNINGPOOL).exists:
            return self.record_failure(action_id, 'No spawning pool available')

        # Check if BANELINGNEST does not exist and is not pending
        if self.structures(UnitTypeId.BANELINGNEST).exists or self.already_pending(UnitTypeId.BANELINGNEST):
            return self.record_failure(action_id, 'Baneling nest already exists or is pending')

        # Try to build BANELINGNEST
        worker_candidates = self.workers.filter(lambda worker: (
                                                                       worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
        place_postion = self.start_location.position + Point2((self.Location * 10, 0))
        placement_position = await self.find_placement(UnitTypeId.BANELINGNEST, near=place_postion, placement_step=6)

        if not placement_position:
            return self.record_failure(action_id, 'Cannot find placement for baneling nest')

        if not self.can_afford(UnitTypeId.BANELINGNEST) or self.already_pending(UnitTypeId.BANELINGNEST) != 0:
            return self.record_failure(action_id, 'Cannot afford baneling nest or baneling nest is already pending')

        build_worker = worker_candidates.closest_to(placement_position)
        build_worker.build(UnitTypeId.BANELINGNEST, placement_position)
        print('build banelingnest')

    async def handle_action_21(self):
        action_id = 21
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check if we have drones
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No drones available')

        # Check if we have townhalls
        if not self.townhalls.exists:
            return self.record_failure(action_id, 'No townhalls available')

        # Check if SPAWNINGPOOL exists
        if not self.structures(UnitTypeId.SPAWNINGPOOL).exists:
            return self.record_failure(action_id, 'No spawning pool available')

        # Check if ROACHWARREN does not exist and is not pending
        if self.structures(UnitTypeId.ROACHWARREN).exists or self.already_pending(UnitTypeId.ROACHWARREN):
            return self.record_failure(action_id, 'Roach warren already exists or is pending')

        # Try to build ROACHWARREN
        worker_candidates = self.workers.filter(lambda worker: (
                                                                       worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
        place_postion = self.start_location.position + Point2((self.Location * 10, 0))
        placement_position = await self.find_placement(UnitTypeId.ROACHWARREN, near=place_postion, placement_step=6)

        if not placement_position:
            return self.record_failure(action_id, 'Cannot find placement for roach warren')

        if not self.can_afford(UnitTypeId.ROACHWARREN) or self.structures(
                UnitTypeId.ROACHWARREN).amount + self.already_pending(UnitTypeId.ROACHWARREN) != 0:
            return self.record_failure(action_id,
                                       'Cannot afford roach warren or roach warren is already existing/pending')

        build_worker = worker_candidates.closest_to(placement_position)
        build_worker.build(UnitTypeId.ROACHWARREN, placement_position)
        print('build roachwarren')

    async def handle_action_22(self):
        action_id = 22
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check if we have drones
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No drones available')

        # Check if we have townhalls
        if not self.townhalls.exists:
            return self.record_failure(action_id, 'No townhalls available')

        # Check if LAIR or HIVE exists
        if not self.structures(UnitTypeId.LAIR).exists and not self.structures(UnitTypeId.HIVE).exists:
            return self.record_failure(action_id, 'Neither Lair nor Hive available')

        # Check if HYDRALISKDEN does not exist and is not pending
        if self.structures(UnitTypeId.HYDRALISKDEN).exists or self.already_pending(UnitTypeId.HYDRALISKDEN):
            return self.record_failure(action_id, 'Hydralisk Den already exists or is pending')

        # Try to build HYDRALISKDEN
        worker_candidates = self.workers.filter(lambda worker: (
                                                                       worker.is_collecting or worker.is_idle) and worker.tag not in self.unit_tags_received_action)
        place_postion = self.start_location.position + Point2((self.Location * 10, 0))
        placement_position = await self.find_placement(UnitTypeId.HYDRALISKDEN, near=place_postion, placement_step=6)

        if not placement_position:
            return self.record_failure(action_id, 'Cannot find placement for hydralisk den')

        if not self.can_afford(UnitTypeId.HYDRALISKDEN) or self.structures(
                UnitTypeId.HYDRALISKDEN).amount + self.already_pending(UnitTypeId.HYDRALISKDEN) != 0:
            return self.record_failure(action_id,
                                       'Cannot afford hydralisk den or hydralisk den is already existing/pending')

        build_worker = worker_candidates.closest_to(placement_position)
        build_worker.build(UnitTypeId.HYDRALISKDEN, placement_position)
        print('build hydra den')

    async def handle_action_23(self):
        action_id = 23
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check if we have HATCHERY
        if not self.structures(UnitTypeId.HATCHERY).exists:
            return self.record_failure(action_id, 'No hatcheries available')

        # Check if we have drones
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No drones available')

        # Check if SPAWNINGPOOL exists
        if not self.structures(UnitTypeId.SPAWNINGPOOL).exists:
            return self.record_failure(action_id, 'No spawning pool available')

        # Check if neither LAIR nor HIVE are in production or exist
        if self.already_pending(UnitTypeId.LAIR) + self.structures(UnitTypeId.LAIR).amount > 0 \
                or self.structures(UnitTypeId.HIVE).amount + self.already_pending(UnitTypeId.HIVE) > 0:
            return self.record_failure(action_id, 'Lair or Hive already exists or is in production')

        # Check if we can afford a LAIR
        if not self.can_afford(UnitTypeId.LAIR):
            return self.record_failure(action_id, 'Cannot afford lair')

        # Try to build LAIR
        bases = self.townhalls
        for base in bases:
            if base.is_idle:
                base.build(UnitTypeId.LAIR)
                print('build lair')
                break

    async def handle_action_24(self):
        action_id = 24
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check if we have LAIR
        if not self.structures(UnitTypeId.LAIR).exists:
            return self.record_failure(action_id, 'No lairs available')

        # Check if we have drones
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No drones available')

        # Check if INFESTATIONPIT exists
        if not self.structures(UnitTypeId.INFESTATIONPIT).exists:
            return self.record_failure(action_id, 'No infestation pit available')

        # Check if we can afford a HIVE
        if not self.can_afford(UnitTypeId.HIVE):
            return self.record_failure(action_id, 'Cannot afford hive')

        # Check if INFESTATIONPIT is ready
        if not self.structures(UnitTypeId.INFESTATIONPIT).ready.exists:
            return self.record_failure(action_id, 'Infestation pit is not ready')

        # Check if there's no HIVE being built or existing
        if self.already_pending(UnitTypeId.HIVE) + self.structures(UnitTypeId.HIVE).amount > 0:
            return self.record_failure(action_id, 'Hive already exists or is in production')

        # Try to build HIVE
        lairs = self.structures(UnitTypeId.LAIR).ready
        for lair in lairs:
            if lair.is_idle:
                lair.build(UnitTypeId.HIVE)
                print('build hive')
                break

    async def handle_action_25(self):
        action_id = 25
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check if we have SPAWNINGPOOL
        if not self.structures(UnitTypeId.SPAWNINGPOOL).exists:
            return self.record_failure(action_id, 'No spawning pools available')

        # Check if we have bases
        if not self.townhalls.exists:
            return self.record_failure(action_id, 'No townhalls available')

        # Check the count of existing and pending EVOLUTIONCHAMBER
        if self.already_pending(UnitTypeId.EVOLUTIONCHAMBER) + self.structures(UnitTypeId.EVOLUTIONCHAMBER).amount > 3:
            return self.record_failure(action_id, 'More than 3 Evolution Chambers existing or pending')

        # Check if we can afford a EVOLUTIONCHAMBER
        if not self.can_afford(UnitTypeId.EVOLUTIONCHAMBER):
            return self.record_failure(action_id, 'Cannot afford evolution chamber')

        # Check the count of pending EVOLUTIONCHAMBER
        if self.already_pending(UnitTypeId.EVOLUTIONCHAMBER) > 2:
            return self.record_failure(action_id, 'More than 2 Evolution Chambers are pending')

        # Try to build EVOLUTIONCHAMBER
        building_place = self.townhalls.random.position
        placement_position = await self.find_placement(UnitTypeId.EVOLUTIONCHAMBER, near=building_place,
                                                       placement_step=4)

        if placement_position is None:
            return self.record_failure(action_id, 'Cannot find placement for evolution chamber')

        await self.build(UnitTypeId.EVOLUTIONCHAMBER, near=placement_position)
        print('build evolutionchamber')

    async def handle_action_26(self):
        action_id = 26
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check if we have LAIR or HIVE
        if not self.structures(UnitTypeId.LAIR).exists and not self.structures(UnitTypeId.HIVE).exists:
            return self.record_failure(action_id, 'Neither Lair nor Hive available')

        # Check if we have drones
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No drones available')

        # Check if we have townhalls
        if not self.townhalls.exists:
            return self.record_failure(action_id, 'No townhalls available')

        # Check if we have at least 2 townhalls
        if self.townhalls.amount < 2:
            return self.record_failure(action_id, 'Less than 2 townhalls')

        # Check if supply used is at least 40
        if self.supply_used < 40:
            return self.record_failure(action_id, 'Supply used is less than 40')

        # Check the count of existing and pending INFESTATIONPIT
        if self.already_pending(UnitTypeId.INFESTATIONPIT) + self.structures(UnitTypeId.INFESTATIONPIT).amount > 0:
            return self.record_failure(action_id, 'Infestation Pit already exists or is in production')

        # Check if we can afford an INFESTATIONPIT
        if not self.can_afford(UnitTypeId.INFESTATIONPIT):
            return self.record_failure(action_id, 'Cannot afford infestation pit')

        # Check the count of pending INFESTATIONPIT
        if self.already_pending(UnitTypeId.INFESTATIONPIT) > 0:
            return self.record_failure(action_id, 'Infestation Pit is already in production')

        # Try to build INFESTATIONPIT
        building_place = self.townhalls.random.position
        placement_position = await self.find_placement(UnitTypeId.INFESTATIONPIT, near=building_place, placement_step=4)

        if placement_position is None:
            return self.record_failure(action_id, 'Cannot find placement for infestation pit')

        await self.build(UnitTypeId.INFESTATIONPIT, near=placement_position)
        print('build infestation pit')

    async def handle_action_27(self):
        action_id = 27
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check if we have townhalls
        if not self.townhalls.exists:
            return self.record_failure(action_id, 'No townhalls available')

        # Check if we have drones
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No drones available')

        # Check if we have LAIR or HIVE
        if not (self.structures(UnitTypeId.LAIR).exists or self.structures(UnitTypeId.HIVE).exists):
            return self.record_failure(action_id, 'Neither Lair nor Hive available')

        # Check the count of existing and pending SPIRE
        if self.already_pending(UnitTypeId.SPIRE) + self.structures(UnitTypeId.SPIRE).amount >= 2:
            return self.record_failure(action_id, '2 or more Spires existing or pending')

        # Check if we can afford a SPIRE
        if not self.can_afford(UnitTypeId.SPIRE):
            return self.record_failure(action_id, 'Cannot afford spire')

        # Check the count of pending SPIRE
        if self.already_pending(UnitTypeId.SPIRE) > 1:
            return self.record_failure(action_id, 'More than 1 Spire is already in production')

        # Try to build SPIRE
        building_place = self.townhalls.random.position
        placement_position = await self.find_placement(UnitTypeId.SPIRE, near=building_place, placement_step=4)

        if placement_position is None:
            return self.record_failure(action_id, 'Cannot find placement for spire')

        await self.build(UnitTypeId.SPIRE, near=placement_position)
        print('build spire')

    async def handle_action_28(self):
        action_id = 28
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check if we have SPIRE
        if not self.structures(UnitTypeId.SPIRE).exists:
            return self.record_failure(action_id, 'No spires available')

        # Check if we have drones
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No drones available')

        # Check if we have HIVE
        if not self.structures(UnitTypeId.HIVE).exists:
            return self.record_failure(action_id, 'No hive available')

        # Check the count of existing and pending GREATERSPIRE
        if self.already_pending(UnitTypeId.GREATERSPIRE) + self.structures(UnitTypeId.GREATERSPIRE).amount > 0:
            return self.record_failure(action_id, 'Greater Spire already exists or is in production')

        # Check if we have ready SPIRE
        if not self.structures(UnitTypeId.SPIRE).ready:
            return self.record_failure(action_id, 'No spire is ready for upgrade')

        # Try to upgrade SPIRE
        spires = self.structures(UnitTypeId.SPIRE).ready
        abilities = await self.get_available_abilities(spires)

        for spire in spires:
            if spire.is_idle:
                if not self.can_afford(UnitTypeId.GREATERSPIRE):
                    return self.record_failure(action_id, 'Cannot afford greater spire')
                if AbilityId.UPGRADETOGREATERSPIRE_GREATERSPIRE not in abilities:
                    return self.record_failure(action_id, 'Upgrade to Greater Spire ability is not available')
                spire.build(UnitTypeId.GREATERSPIRE)
                print('build greater spire')

    async def handle_action_29(self):
        action_id = 29
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check if we have drones
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No drones available')
        # Check if we have townhalls
        if not self.townhalls.exists:
            return self.record_failure(action_id, 'No townhalls available')
        # Check if we have HIVE
        if not self.structures(UnitTypeId.HIVE).exists:
            return self.record_failure(action_id, 'No hive available')

        # Check the count of existing and pending ULTRALISKCAVERN
        if self.already_pending(UnitTypeId.ULTRALISKCAVERN) + self.structures(UnitTypeId.ULTRALISKCAVERN).amount > 0:
            return self.record_failure(action_id, 'Ultralisk Cavern already exists or is in production')

        # Try to build ULTRALISKCAVERN
        building_place = self.townhalls.random.position
        placement_position = await self.find_placement(UnitTypeId.ULTRALISKCAVERN, near=building_place,
                                                       placement_step=4)

        if placement_position is None:
            return self.record_failure(action_id, 'Cannot find placement for ultralisk cavern')

        await self.build(UnitTypeId.ULTRALISKCAVERN, near=placement_position)
        print('build ultralisk cavern')

    async def handle_action_30(self):
        action_id = 30
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check if we have drones
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No drones available')
        # Check if we have townhalls
        if not self.townhalls.exists:
            return self.record_failure(action_id, 'No townhalls available')

        # Check if we have HIVE or LAIR
        if not (self.structures(UnitTypeId.HIVE).exists or self.structures(UnitTypeId.LAIR).exists):
            return self.record_failure(action_id, 'Neither Hive nor Lair available')

        # Check if we have HYDRALISKDEN
        if not self.structures(UnitTypeId.HYDRALISKDEN).exists:
            return self.record_failure(action_id, 'No Hydralisk Den available')

        # Check the count of existing and pending LURKERDENMP
        if self.already_pending(UnitTypeId.LURKERDENMP) + self.structures(UnitTypeId.LURKERDENMP).amount > 0:
            return self.record_failure(action_id, 'Lurker Den already exists or is in production')

        # Try to build LURKERDENMP
        building_place = self.townhalls.random.position
        placement_position = await self.find_placement(UnitTypeId.LURKERDENMP, near=building_place, placement_step=4)

        if placement_position is None:
            return self.record_failure(action_id, 'Cannot find placement for Lurker Den')

        await self.build(UnitTypeId.LURKERDENMP, near=placement_position)
        print('build LURKERDENMP')

    async def handle_action_31(self):
        action_id = 31
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check if we have SPAWNINGPOOL
        if not self.structures(UnitTypeId.SPAWNINGPOOL).exists:
            return self.record_failure(action_id, 'No Spawning Pool available')

        # Check if we have at least one townhall
        if not self.townhalls.exists:
            return self.record_failure(action_id, 'No townhalls available')

        # Check if we can afford SPORECRAWLER
        if not self.can_afford(UnitTypeId.SPORECRAWLER):
            return self.record_failure(action_id, 'Cannot afford Spore Crawler')

        # Try to build SPORECRAWLER
        nexus = self.townhalls.random
        placement_position = await self.find_placement(UnitTypeId.SPORECRAWLER, near=nexus.position, placement_step=3)

        if placement_position is None:
            return self.record_failure(action_id, 'Cannot find placement for Spore Crawler')

        await self.build(UnitTypeId.SPORECRAWLER, near=placement_position)
        print('build spore crawler')

    async def handle_action_32(self):
        action_id = 32
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check if we have SPAWNINGPOOL
        if not self.structures(UnitTypeId.SPAWNINGPOOL).exists:
            return self.record_failure(action_id, 'No Spawning Pool available')

        # Check if we have at least one townhall
        if not self.townhalls.exists:
            return self.record_failure(action_id, 'No townhalls available')

        max_spine_crawler = 0
        if 3 <= self.townhalls.amount <= 4:
            max_spine_crawler = 1
        elif 5 <= self.townhalls.amount:
            max_spine_crawler = 3
        else:
            return self.record_failure(action_id, 'Invalid number of townhalls for this action')

        # Check existing and pending SPINECRAWLER count
        existing_spine_crawler_count = self.structures(UnitTypeId.SPINECRAWLER).amount + self.already_pending(
            UnitTypeId.SPINECRAWLER)
        if existing_spine_crawler_count >= max_spine_crawler:
            return self.record_failure(action_id, f'Already have {existing_spine_crawler_count} Spine Crawlers')

        # Check if we can afford SPINECRAWLER
        if not self.can_afford(UnitTypeId.SPINECRAWLER):
            return self.record_failure(action_id, 'Cannot afford Spine Crawler')

        # Try to build SPINECRAWLER
        base = self.townhalls.random
        placement_position = await self.find_placement(UnitTypeId.SPINECRAWLER, near=base.position, placement_step=3)

        if placement_position is None:
            return self.record_failure(action_id, 'Cannot find placement for Spine Crawler')

        await self.build(UnitTypeId.SPINECRAWLER, near=placement_position)
        print('build spine crawler')

    async def handle_action_33(self):
        action_id = 33
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check for OVERLORD, DRONE, and townhalls existence
        if not (self.units(UnitTypeId.OVERLORD).exists and self.units(
                UnitTypeId.DRONE).exists and self.townhalls.exists):
            return self.record_failure(action_id, 'No Overlords, Drones, or townhalls available')

        # Check for SPAWNINGPOOL existence
        if not self.structures(UnitTypeId.SPAWNINGPOOL).exists:
            return self.record_failure(action_id, 'No Spawning Pool available')

        spawningpool = self.structures(UnitTypeId.SPAWNINGPOOL).random
        abilities = await self.get_available_abilities(spawningpool)

        # Check if SPAWNINGPOOL is ready
        if not self.structures(UnitTypeId.SPAWNINGPOOL).ready:
            return self.record_failure(action_id, 'Spawning Pool not ready')

        # Check if the upgrade is already pending or completed
        if self.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED) > 0:
            return self.record_failure(action_id, 'Zergling Speed upgrade already in progress or completed')

        # Check if we can afford the upgrade and if it's available
        if not self.can_afford(UpgradeId.ZERGLINGMOVEMENTSPEED):
            return self.record_failure(action_id, 'Cannot afford Zergling Speed upgrade')

        if AbilityId.RESEARCH_ZERGLINGMETABOLICBOOST not in abilities:
            return self.record_failure(action_id, 'Zergling Speed upgrade not available')

        # Start the upgrade
        self.research(UpgradeId.ZERGLINGMOVEMENTSPEED)
        print('research zergling speed')

    async def handle_action_34(self):
        action_id = 34
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check for OVERLORD, DRONE, and townhalls existence
        if not self.townhalls.exists:
            return self.record_failure(action_id, 'No townhalls available')

        # Check for SPAWNINGPOOL existence
        if not self.structures(UnitTypeId.SPAWNINGPOOL).exists:
            return self.record_failure(action_id, 'No Spawning Pool available')

        spawningpool = self.structures(UnitTypeId.SPAWNINGPOOL).random
        abilities = await self.get_available_abilities(spawningpool)

        # Check if SPAWNINGPOOL is ready
        if not self.structures(UnitTypeId.SPAWNINGPOOL).ready:
            return self.record_failure(action_id, 'Spawning Pool not ready')

        # Check if the upgrade is already pending or completed
        if self.already_pending_upgrade(UpgradeId.ZERGLINGATTACKSPEED) > 0:
            return self.record_failure(action_id, 'Zergling Attack Speed upgrade already in progress or completed')

        # Check if we can afford the upgrade and if it's available
        if not self.can_afford(UpgradeId.ZERGLINGATTACKSPEED):
            return self.record_failure(action_id, 'Cannot afford Zergling Attack Speed upgrade')

        if AbilityId.RESEARCH_ZERGLINGADRENALGLANDS not in abilities:
            return self.record_failure(action_id, 'Zergling Attack Speed upgrade not available')

        # Start the upgrade
        self.research(UpgradeId.ZERGLINGATTACKSPEED)
        print('research zergling attack speed')

    async def handle_action_35(self):
        action_id = 35
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check for BANELINGNEST existence
        if not self.structures(UnitTypeId.BANELINGNEST).exists:
            return self.record_failure(action_id, 'No Baneling Nest available')

        # Check for LAIR existence
        if not self.structures(UnitTypeId.LAIR).exists:
            return self.record_failure(action_id, 'No Lair available')

        # Check for HIVE existence
        if not self.structures(UnitTypeId.HIVE).exists:
            return self.record_failure(action_id, 'No Hive available')

        banelingnest = self.structures(UnitTypeId.BANELINGNEST).random
        abilities = await self.get_available_abilities(banelingnest)

        # Check if BANELINGNEST is ready
        if not self.structures(UnitTypeId.BANELINGNEST).ready:
            return self.record_failure(action_id, 'Baneling Nest not ready')

        # Check if the upgrade is already pending or completed
        if self.already_pending_upgrade(UpgradeId.CENTRIFICALHOOKS) > 0:
            return self.record_failure(action_id, 'Centrifical Hooks upgrade already in progress or completed')

        # Check if we can afford the upgrade and if it's available
        if not self.can_afford(UpgradeId.CENTRIFICALHOOKS):
            return self.record_failure(action_id, 'Cannot afford Centrifical Hooks upgrade')

        if AbilityId.RESEARCH_CENTRIFUGALHOOKS not in abilities:
            return self.record_failure(action_id, 'Centrifical Hooks upgrade not available')

        # Start the upgrade
        self.research(UpgradeId.CENTRIFICALHOOKS)
        print('research baneling speed')

    async def handle_action_36(self):
        action_id = 36
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check for ROACHWARREN existence
        if not self.structures(UnitTypeId.ROACHWARREN).exists:
            return self.record_failure(action_id, 'No Roach Warren available')

        # Check for LAIR or HIVE existence
        if not self.structures(UnitTypeId.LAIR).exists and not self.structures(UnitTypeId.HIVE).exists:
            return self.record_failure(action_id, 'No Lair or Hive available')

        # Check if LAIR is ready
        if not self.structures(UnitTypeId.LAIR).ready:
            return self.record_failure(action_id, 'Lair not ready')

        # Check if the upgrade is already pending or completed
        if self.already_pending_upgrade(UpgradeId.GLIALRECONSTITUTION) > 0:
            return self.record_failure(action_id, 'Glial Reconstitution upgrade already in progress or completed')

        roachwarren = self.structures(UnitTypeId.ROACHWARREN).random
        abilities = await self.get_available_abilities(roachwarren)

        # Check if we can afford the upgrade and if it's available
        if not self.can_afford(UpgradeId.GLIALRECONSTITUTION):
            return self.record_failure(action_id, 'Cannot afford Glial Reconstitution upgrade')

        if AbilityId.RESEARCH_GLIALREGENERATION not in abilities:
            return self.record_failure(action_id, 'Glial Reconstitution upgrade not available')

        # Check if ROACHWARREN is idle
        if not roachwarren.is_idle:
            return self.record_failure(action_id, 'Roach Warren is not idle')

        # Start the upgrade
        self.research(UpgradeId.GLIALRECONSTITUTION)
        print('research roach speed')

    async def handle_action_37(self):
        action_id = 37
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check for ROACHWARREN existence
        if not self.structures(UnitTypeId.ROACHWARREN).exists:
            return self.record_failure(action_id, 'No Roach Warren available')

        # Check for LAIR or HIVE existence
        if not self.structures(UnitTypeId.LAIR).exists and not self.structures(UnitTypeId.HIVE).exists:
            return self.record_failure(action_id, 'No Lair or Hive available')

        # Check if LAIR is ready
        if not self.structures(UnitTypeId.LAIR).ready:
            return self.record_failure(action_id, 'Lair not ready')

        # Check if the Roach speed upgrade is already pending
        if not self.already_pending_upgrade(UpgradeId.GLIALRECONSTITUTION) == 1:
            return self.record_failure(action_id, 'Roach speed upgrade not in progress or completed')

        # Check if the Tunneling Claws upgrade hasn't started yet
        if self.already_pending_upgrade(UpgradeId.TUNNELINGCLAWS) > 0:
            return self.record_failure(action_id, 'Tunneling Claws upgrade already in progress or completed')

        roachwarren = self.structures(UnitTypeId.ROACHWARREN).random
        abilities = await self.get_available_abilities(roachwarren)

        # Check if we can afford the Tunneling Claws upgrade and if it's available
        if not self.can_afford(UpgradeId.TUNNELINGCLAWS):
            return self.record_failure(action_id, 'Cannot afford Tunneling Claws upgrade')

        if AbilityId.RESEARCH_TUNNELINGCLAWS not in abilities:
            return self.record_failure(action_id, 'Tunneling Claws upgrade not available')

        # Check if ROACHWARREN is idle
        if not roachwarren.is_idle:
            return self.record_failure(action_id, 'Roach Warren is not idle')

        # Start the upgrade
        self.research(UpgradeId.TUNNELINGCLAWS)
        print('research tunnelingclaws')

    async def handle_action_38(self):
        action_id = 38
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check if a Hatchery exists
        if not self.townhalls.exists:
            return self.record_failure(action_id, 'No Hatchery available')

        # Check if any Hatchery is ready
        if not self.townhalls.ready:
            return self.record_failure(action_id, 'No Hatchery is ready')

        # Check if the Overlord speed upgrade has already been started
        if self.already_pending_upgrade(UpgradeId.OVERLORDSPEED) > 0:
            return self.record_failure(action_id, 'Overlord speed upgrade already in progress or completed')

        # Check if we can afford the Overlord speed upgrade
        if not self.can_afford(UpgradeId.OVERLORDSPEED):
            return self.record_failure(action_id, 'Cannot afford Overlord speed upgrade')

        # Check if Overlord speed upgrade is available
        base = self.townhalls.random
        abilities = await self.get_available_abilities(base)
        if AbilityId.RESEARCH_PNEUMATIZEDCARAPACE not in abilities:
            return self.record_failure(action_id, 'Overlord speed upgrade not available')

        # Check if any Hatchery is idle and start the upgrade
        for hatchery in self.townhalls:
            if hatchery.is_idle:
                self.research(UpgradeId.OVERLORDSPEED)
                print('research overlord speed')
                return
        return self.record_failure(action_id, 'All Hatcheries are busy')

    async def handle_action_39(self):
        action_id = 39
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check if a Hatchery exists
        if not self.townhalls.exists:
            return self.record_failure(action_id, 'No Hatchery available')

        # Check if either Lair or Hive exists
        if not (self.structures(UnitTypeId.LAIR).exists or self.structures(UnitTypeId.HIVE).exists):
            return self.record_failure(action_id, 'Neither Lair nor Hive exists')

        # Check if any Lair is ready
        if not self.structures(UnitTypeId.LAIR).ready:
            return self.record_failure(action_id, 'No Lair is ready')

        # Check if the Burrow upgrade has already been started
        if self.already_pending_upgrade(UpgradeId.BURROW) > 0:
            return self.record_failure(action_id, 'Burrow upgrade already in progress or completed')

        # Check if we can afford the Burrow upgrade
        if not self.can_afford(UpgradeId.BURROW):
            return self.record_failure(action_id, 'Cannot afford Burrow upgrade')

        # Check if Burrow upgrade is available
        base = self.townhalls.random
        abilities = await self.get_available_abilities(base)
        if AbilityId.RESEARCH_BURROW not in abilities:
            return self.record_failure(action_id, 'Burrow upgrade not available')

        # Check if any Hatchery is idle and start the upgrade
        for hatchery in self.townhalls:
            if hatchery.is_idle:
                self.research(UpgradeId.BURROW)
                print('research burrow')
                return
        return self.record_failure(action_id, 'All Hatcheries are busy')

    async def handle_action_40(self):
        action_id = 40
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check if a Hydralisk Den exists
        if not self.structures(UnitTypeId.HYDRALISKDEN).exists:
            return self.record_failure(action_id, 'No Hydralisk Den available')

        # Check if either Lair or Hive exists
        if not (self.structures(UnitTypeId.LAIR).exists or self.structures(UnitTypeId.HIVE).exists):
            return self.record_failure(action_id, 'Neither Lair nor Hive exists')

        # Check if any Lair is ready
        if not self.structures(UnitTypeId.LAIR).ready:
            return self.record_failure(action_id, 'No Lair is ready')

        # Check if the Hydralisk Speed upgrade has already been started
        if self.already_pending_upgrade(UpgradeId.EVOLVEMUSCULARAUGMENTS) > 0:
            return self.record_failure(action_id, 'Hydralisk Speed upgrade already in progress or completed')

        # Check if we can afford the Hydralisk Speed upgrade
        if not self.can_afford(UpgradeId.EVOLVEMUSCULARAUGMENTS):
            return self.record_failure(action_id, 'Cannot afford Hydralisk Speed upgrade')

        # Check if Hydralisk Speed upgrade is available
        hydraden = self.structures(UnitTypeId.HYDRALISKDEN).random
        abilities = await self.get_available_abilities(hydraden)
        if AbilityId.RESEARCH_MUSCULARAUGMENTS not in abilities:
            return self.record_failure(action_id, 'Hydralisk Speed upgrade not available')

        # Check if Hydralisk Den is idle and start the upgrade
        if hydraden.is_idle:
            self.research(UpgradeId.EVOLVEMUSCULARAUGMENTS)
            print('research hydra speed')
            return
        return self.record_failure(action_id, 'Hydralisk Den is busy')

    async def handle_action_41(self):
        action_id = 41
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check for the presence of a Hydralisk Den
        if not self.structures(UnitTypeId.HYDRALISKDEN).exists:
            return self.record_failure(action_id, 'No Hydralisk Den available')

        # Check if either Lair or Hive exists
        if not (self.structures(UnitTypeId.LAIR).exists or self.structures(UnitTypeId.HIVE).exists):
            return self.record_failure(action_id, 'Neither Lair nor Hive exists')

        # Check if any Lair is ready
        if not self.structures(UnitTypeId.LAIR).ready:
            return self.record_failure(action_id, 'No Lair is ready')

        # Check for Hydra Range upgrade state
        if self.already_pending_upgrade(UpgradeId.EVOLVEGROOVEDSPINES) > 0:
            return self.record_failure(action_id, 'Hydra Range upgrade already in progress or completed')

        hydraden = self.structures(UnitTypeId.HYDRALISKDEN).random
        abilities = await self.get_available_abilities(hydraden)

        # Check if Hydra Range upgrade is available and start it
        if AbilityId.RESEARCH_GROOVEDSPINES in abilities and hydraden.is_idle:
            if self.can_afford(UpgradeId.EVOLVEGROOVEDSPINES):
                self.research(UpgradeId.EVOLVEGROOVEDSPINES)
                print('research hydra range')
                return
            return self.record_failure(action_id, 'Cannot afford Hydra Range upgrade')

        return self.record_failure(action_id, 'Hydra Range upgrade not available or Hydralisk Den is busy')

    async def handle_action_42(self):
        action_id = 42
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check if there's at least one ready Evolution Chamber
        if not self.structures(UnitTypeId.EVOLUTIONCHAMBER).ready:
            return self.record_failure(action_id, 'No ready Evolution Chamber available')

        # Check if drones exist
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No Drones available')

        bvs = self.structures(UnitTypeId.EVOLUTIONCHAMBER)
        abilities = await self.get_available_abilities(bvs)

        # Check if Zerg Ground Melee +1 upgrade is available and start it
        for bv in bvs:
            if bv.is_idle and AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL1 in abilities:
                if self.can_afford(UpgradeId.ZERGMELEEWEAPONSLEVEL1) and self.already_pending_upgrade(
                        UpgradeId.ZERGMELEEWEAPONSLEVEL1) == 0:
                    self.research(UpgradeId.ZERGMELEEWEAPONSLEVEL1)
                    print('research zerg ground melee plus 1')
                    return
                return self.record_failure(action_id,
                                           'Cannot afford Zerg Ground Melee +1 upgrade or upgrade already in progress')

        return self.record_failure(action_id,
                                   'No idle Evolution Chamber available or Zerg Ground Melee +1 upgrade not available')

    async def handle_action_43(self):
        action_id = 43
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check for the presence of a ready Evolution Chamber
        if not self.structures(UnitTypeId.EVOLUTIONCHAMBER).ready:
            return self.record_failure(action_id, 'No ready Evolution Chamber available')

        # Check if drones exist
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No Drones available')

        # Check if either Lair or Hive exists
        if not (self.structures(UnitTypeId.LAIR).exists or self.structures(UnitTypeId.HIVE).exists):
            return self.record_failure(action_id, 'Neither Lair nor Hive exists')

        bvs = self.structures(UnitTypeId.EVOLUTIONCHAMBER)
        abilities = await self.get_available_abilities(bvs)

        # Check if Zerg Ground Melee +2 upgrade is available and start it
        for bv in bvs:
            if bv.is_idle and AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL2 in abilities:
                if self.can_afford(UpgradeId.ZERGMELEEWEAPONSLEVEL2) and self.already_pending_upgrade(
                        UpgradeId.ZERGMELEEWEAPONSLEVEL2) == 0:
                    self.research(UpgradeId.ZERGMELEEWEAPONSLEVEL2)
                    print('research zerg ground melee plus 2')
                    return
                return self.record_failure(action_id,
                                           'Cannot afford Zerg Ground Melee +2 upgrade or upgrade already in progress')

        return self.record_failure(action_id,
                                   'No idle Evolution Chamber available or Zerg Ground Melee +2 upgrade not available')

    async def handle_action_44(self):
        action_id = 44
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check for the presence of a ready Evolution Chamber
        if not self.structures(UnitTypeId.EVOLUTIONCHAMBER).ready:
            return self.record_failure(action_id, 'No ready Evolution Chamber available')

        # Check if there are at least 2 Hatcheries
        if self.townhalls.amount < 2:
            return self.record_failure(action_id, 'Less than 2 Hatcheries available')

        # Check if drones exist
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No Drones available')

        # Check if Hive exists
        if not self.structures(UnitTypeId.HIVE).exists:
            return self.record_failure(action_id, "Hive doesn't exist")

        bvs = self.structures(UnitTypeId.EVOLUTIONCHAMBER)
        abilities = await self.get_available_abilities(bvs)

        # Check if Zerg Ground Melee +3 upgrade is available and start it
        for bv in bvs:
            if bv.is_idle and AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL3 in abilities:
                if self.can_afford(UpgradeId.ZERGMELEEWEAPONSLEVEL3) and self.already_pending_upgrade(
                        UpgradeId.ZERGMELEEWEAPONSLEVEL3) == 0:
                    self.research(UpgradeId.ZERGMELEEWEAPONSLEVEL3)
                    print('research zerg ground melee plus 3')
                    return
                return self.record_failure(action_id,
                                           'Cannot afford Zerg Ground Melee +3 upgrade or upgrade already in progress')

        return self.record_failure(action_id,
                                   'No idle Evolution Chamber available or Zerg Ground Melee +3 upgrade not available')

    async def handle_action_45(self):
        action_id = 45
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check for the presence of a ready Evolution Chamber
        if not self.structures(UnitTypeId.EVOLUTIONCHAMBER).ready:
            return self.record_failure(action_id, 'No ready Evolution Chamber available')

        # Check if drones exist
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No Drones available')

        bvs = self.structures(UnitTypeId.EVOLUTIONCHAMBER)
        abilities = await self.get_available_abilities(bvs)

        # Check if Zerg Ground Missile +1 upgrade is available and start it
        for bv in bvs:
            if bv.is_idle and AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL1 in abilities:
                if self.can_afford(UpgradeId.ZERGMISSILEWEAPONSLEVEL1) and self.already_pending_upgrade(
                        UpgradeId.ZERGMISSILEWEAPONSLEVEL1) == 0:
                    self.research(UpgradeId.ZERGMISSILEWEAPONSLEVEL1)
                    print('research zerg ground missile plus 1')
                    return
                return self.record_failure(action_id,
                                           'Cannot afford Zerg Ground Missile +1 upgrade or upgrade already in progress')

        return self.record_failure(action_id,
                                   'No idle Evolution Chamber available or Zerg Ground Missile +1 upgrade not available')

    async def handle_action_46(self):
        action_id = 46
        action = self.action_dict[action_id]
        print(f'action={action}')

        # Check for the presence of a ready Evolution Chamber
        if not self.structures(UnitTypeId.EVOLUTIONCHAMBER).ready:
            return self.record_failure(action_id, 'No ready Evolution Chamber available')

        # Check if drones exist
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No Drones available')

        # Check if Hive or Lair exists
        if not (self.structures(UnitTypeId.LAIR).exists or self.structures(UnitTypeId.HIVE).exists):
            return self.record_failure(action_id, 'Neither Lair nor Hive exists')

        bvs = self.structures(UnitTypeId.EVOLUTIONCHAMBER)
        abilities = await self.get_available_abilities(bvs)

        # Check if Zerg Ground Missile +2 upgrade is available and start it
        for bv in bvs:
            if bv.is_idle and AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL2 in abilities:
                if self.can_afford(UpgradeId.ZERGMISSILEWEAPONSLEVEL2) and self.already_pending_upgrade(
                        UpgradeId.ZERGMISSILEWEAPONSLEVEL2) == 0:
                    self.research(UpgradeId.ZERGMISSILEWEAPONSLEVEL2)
                    print('research zerg ground missile plus 2')
                    return
                return self.record_failure(action_id,
                                           'Cannot afford Zerg Ground Missile +2 upgrade or upgrade already in progress')

        return self.record_failure(action_id,
                                   'No idle Evolution Chamber available or Zerg Ground Missile +2 upgrade not available')

    async def handle_action_47(self):
        action_id = 47
        print(f'action={action_id}')

        if not self.structures(UnitTypeId.EVOLUTIONCHAMBER).ready:
            return self.record_failure(action_id, 'No ready Evolution Chamber available')
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No Drones available')
        if not self.structures(UnitTypeId.HIVE).exists:
            return self.record_failure(action_id, 'Hive is not available')

        bvs = self.structures(UnitTypeId.EVOLUTIONCHAMBER)
        abilities = await self.get_available_abilities(bvs)
        for bv in bvs:
            if bv.is_idle and AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL3 in abilities:
                if self.can_afford(UpgradeId.ZERGMISSILEWEAPONSLEVEL3) and self.already_pending_upgrade(
                        UpgradeId.ZERGMISSILEWEAPONSLEVEL3) == 0:
                    self.research(UpgradeId.ZERGMISSILEWEAPONSLEVEL3)
                    print('research zerg ground missile plus 3')
                    return
                else:
                    return self.record_failure(action_id,
                                               'Cannot afford Zerg Ground Missile +3 upgrade or upgrade already in progress')

        return self.record_failure(action_id,
                                   'No idle Evolution Chamber available or Zerg Ground Missile +3 upgrade not available')

    async def handle_action_48(self):
        action_id = 48
        print(f'action={action_id}')

        if not self.structures(UnitTypeId.EVOLUTIONCHAMBER).ready:
            return self.record_failure(action_id, 'No ready Evolution Chamber available')
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No Drones available')

        bvs = self.structures(UnitTypeId.EVOLUTIONCHAMBER)
        abilities = await self.get_available_abilities(bvs)
        for bv in bvs:
            if bv.is_idle and AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL1 in abilities:
                if self.can_afford(UpgradeId.ZERGGROUNDARMORSLEVEL1) and self.already_pending_upgrade(
                        UpgradeId.ZERGGROUNDARMORSLEVEL1) == 0:
                    self.research(UpgradeId.ZERGGROUNDARMORSLEVEL1)
                    print('research zerg ground armor plus 1')
                    return
                else:
                    return self.record_failure(action_id,
                                               'Cannot afford Zerg Ground Armor +1 upgrade or upgrade already in progress')

        return self.record_failure(action_id,
                                   'No idle Evolution Chamber available or Zerg Ground Armor +1 upgrade not available')

    async def handle_action_49(self):
        action_id = 49
        print(f'action={action_id}')

        if not self.structures(UnitTypeId.EVOLUTIONCHAMBER).ready:
            return self.record_failure(action_id, 'No ready Evolution Chamber available')

        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No Drones available')
        if not (self.structures(UnitTypeId.LAIR).exists or self.structures(UnitTypeId.HIVE).exists):
            return self.record_failure(action_id, 'Neither Lair nor Hive is available')

        bvs = self.structures(UnitTypeId.EVOLUTIONCHAMBER)
        abilities = await self.get_available_abilities(bvs)
        for bv in bvs:
            if bv.is_idle and AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL2 in abilities:
                if self.can_afford(UpgradeId.ZERGGROUNDARMORSLEVEL2) and self.already_pending_upgrade(
                        UpgradeId.ZERGGROUNDARMORSLEVEL2) == 0:
                    self.research(UpgradeId.ZERGGROUNDARMORSLEVEL2)
                    print('research zerg ground armor plus 2')
                    return
                else:
                    return self.record_failure(action_id,
                                               'Cannot afford Zerg Ground Armor +2 upgrade or upgrade already in progress')

        return self.record_failure(action_id,
                                   'No idle Evolution Chamber available or Zerg Ground Armor +2 upgrade not available')

    async def handle_action_50(self):
        action_id = 50
        print(f'action={action_id}')

        if not self.structures(UnitTypeId.EVOLUTIONCHAMBER).ready:
            return self.record_failure(action_id, 'No ready Evolution Chamber available')

        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No Drones available')
        if not self.structures(UnitTypeId.HIVE).exists:
            return self.record_failure(action_id, 'Hive is not available')

        bvs = self.structures(UnitTypeId.EVOLUTIONCHAMBER)
        abilities = await self.get_available_abilities(bvs)
        for bv in bvs:
            if bv.is_idle and AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL3 in abilities:
                if self.can_afford(UpgradeId.ZERGGROUNDARMORSLEVEL3) and self.already_pending_upgrade(
                        UpgradeId.ZERGGROUNDARMORSLEVEL3) == 0:
                    self.research(UpgradeId.ZERGGROUNDARMORSLEVEL3)
                    print('research zerg ground armor plus 3')
                    return
                else:
                    return self.record_failure(action_id,
                                               'Cannot afford Zerg Ground Armor +3 upgrade or upgrade already in progress')

        return self.record_failure(action_id,
                                   'No idle Evolution Chamber available or Zerg Ground Armor +3 upgrade not available')

    async def handle_action_51(self):
        action_id = 51
        print(f'action={action_id}')

        if not self.structures(UnitTypeId.INFESTATIONPIT).exists:
            return self.record_failure(action_id, 'No Infestation Pit available')

        if not (self.structures(UnitTypeId.LAIR).exists or self.structures(UnitTypeId.HIVE).exists):
            return self.record_failure(action_id, 'Neither Lair nor Hive is available')

        vis = self.structures(UnitTypeId.INFESTATIONPIT)
        abilities = await self.get_available_abilities(vis)
        for vi in vis:
            if vi.is_idle and AbilityId.RESEARCH_PATHOGENGLANDS in abilities:
                if self.can_afford(UpgradeId.INFESTORENERGYUPGRADE) and self.already_pending_upgrade(
                        UpgradeId.INFESTORENERGYUPGRADE) == 0:
                    vi.research(UpgradeId.INFESTORENERGYUPGRADE)
                    print('research infestor energy upgrade')
                    return
                else:
                    return self.record_failure(action_id,
                                               'Cannot afford Infestor Energy upgrade or upgrade already in progress')

        return self.record_failure(action_id,
                                   'No idle Infestation Pit available or Infestor Energy upgrade not available')

    async def handle_action_52(self):
        action_id = 52
        print(f'action={action_id}')

        if not self.structures(UnitTypeId.INFESTATIONPIT).exists:
            return self.record_failure(action_id, 'No Infestation Pit available')

        if not (self.structures(UnitTypeId.LAIR).exists or self.structures(UnitTypeId.HIVE).exists):
            return self.record_failure(action_id, 'Neither Lair nor Hive is available')

        vis = self.structures(UnitTypeId.INFESTATIONPIT)
        abilities = await self.get_available_abilities(vis)
        for vi in vis:
            if vi.is_idle and AbilityId.RESEARCH_NEURALPARASITE in abilities:
                if self.can_afford(UpgradeId.NEURALPARASITE) and self.already_pending_upgrade(
                        UpgradeId.NEURALPARASITE) == 0:
                    vi.research(UpgradeId.NEURALPARASITE)
                    print('research neural parasite')
                    return
                else:
                    return self.record_failure(action_id,
                                               'Cannot afford Neural Parasite upgrade or upgrade already in progress')

        return self.record_failure(action_id,
                                   'No idle Infestation Pit available or Neural Parasite upgrade not available')

    async def handle_action_53(self):
        action_id = 53
        print(f'action={action_id}')

        if not self.structures(UnitTypeId.SPIRE).exists:
            return self.record_failure(action_id, 'No Spire available')
        if not (self.structures(UnitTypeId.LAIR).exists or self.structures(UnitTypeId.HIVE).exists):
            return self.record_failure(action_id, 'Neither Lair nor Hive is available')
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No Drones available')

        spires = self.structures(UnitTypeId.SPIRE)
        abilities = await self.get_available_abilities(spires)
        for spire in spires:
            if spire.is_idle and AbilityId.RESEARCH_ZERGFLYERATTACKLEVEL1 in abilities:
                if self.can_afford(UpgradeId.ZERGFLYERWEAPONSLEVEL1) and self.already_pending_upgrade(
                        UpgradeId.ZERGFLYERWEAPONSLEVEL1) == 0:
                    spire.research(UpgradeId.ZERGFLYERWEAPONSLEVEL1)
                    print('research zerg fly attack plus 1')
                    return
                else:
                    return self.record_failure(action_id,
                                               'Cannot afford Zerg Fly Attack +1 upgrade or upgrade already in progress')

        return self.record_failure(action_id, 'No idle Spire available or Zerg Fly Attack +1 upgrade not available')

    async def handle_action_54(self):
        action_id = 54
        print(f'action={action_id}')

        if not self.structures(UnitTypeId.SPIRE).exists:
            return self.record_failure(action_id, 'No Spire available')
        if not (self.structures(UnitTypeId.LAIR).exists or self.structures(UnitTypeId.HIVE).exists):
            return self.record_failure(action_id, 'Neither Lair nor Hive is available')
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No Drones available')

        spires = self.structures(UnitTypeId.SPIRE)
        abilities = await self.get_available_abilities(spires)
        for spire in spires:
            if spire.is_idle and AbilityId.RESEARCH_ZERGFLYERATTACKLEVEL2 in abilities:
                if self.can_afford(UpgradeId.ZERGFLYERWEAPONSLEVEL2) and self.already_pending_upgrade(
                        UpgradeId.ZERGFLYERWEAPONSLEVEL2) == 0:
                    spire.research(UpgradeId.ZERGFLYERWEAPONSLEVEL2)
                    print('research zerg fly attack plus 2')
                    return
                else:
                    return self.record_failure(action_id,
                                               'Cannot afford Zerg Fly Attack +2 upgrade or upgrade already in progress')

        return self.record_failure(action_id, 'No idle Spire available or Zerg Fly Attack +2 upgrade not available')

    async def handle_action_55(self):
        action_id = 55
        print(f'action={action_id}')

        if not self.structures(UnitTypeId.SPIRE).exists:
            return self.record_failure(action_id, 'No Spire available')
        if not self.structures(UnitTypeId.HIVE).exists:
            return self.record_failure(action_id, 'No Hive available')
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No Drones available')

        spires = self.structures(UnitTypeId.SPIRE)
        abilities = await self.get_available_abilities(spires)
        for spire in spires:
            if spire.is_idle and AbilityId.RESEARCH_ZERGFLYERATTACKLEVEL3 in abilities:
                if self.can_afford(UpgradeId.ZERGFLYERWEAPONSLEVEL3) and self.already_pending_upgrade(
                        UpgradeId.ZERGFLYERWEAPONSLEVEL3) == 0:
                    spire.research(UpgradeId.ZERGFLYERWEAPONSLEVEL3)
                    print('research zerg fly attack plus 3')
                    return
                else:
                    return self.record_failure(action_id,
                                               'Cannot afford Zerg Fly Attack +3 upgrade or upgrade already in progress')

        return self.record_failure(action_id, 'No idle Spire available or Zerg Fly Attack +3 upgrade not available')

    async def handle_action_56(self):
        action_id = 56
        print(f'action={action_id}')

        if not (self.structures(UnitTypeId.SPIRE).exists or self.structures(UnitTypeId.GREATERSPIRE).exists):
            return self.record_failure(action_id, 'Neither Spire nor Greater Spire available')
        if not (self.structures(UnitTypeId.LAIR).exists or self.structures(UnitTypeId.HIVE).exists):
            return self.record_failure(action_id, 'Neither Lair nor Hive is available')
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No Drones available')

        spires = self.structures(UnitTypeId.SPIRE) + self.structures(UnitTypeId.GREATERSPIRE)
        abilities = await self.get_available_abilities(spires)
        for spire in spires:
            if spire.is_idle and AbilityId.RESEARCH_ZERGFLYERARMORLEVEL1 in abilities:
                if self.can_afford(UpgradeId.ZERGFLYERARMORSLEVEL1) and self.already_pending_upgrade(
                        UpgradeId.ZERGFLYERARMORSLEVEL1) == 0:
                    spire.research(UpgradeId.ZERGFLYERARMORSLEVEL1)
                    print('research zerg fly armor plus 1')
                    return
                else:
                    return self.record_failure(action_id,
                                               'Cannot afford Zerg Fly Armor +1 upgrade or upgrade already in progress')

        return self.record_failure(action_id,
                                   'No idle Spire or Greater Spire available or Zerg Fly Armor +1 upgrade not available')

    async def handle_action_57(self):
        action_id = 57
        print(f'action={action_id}')

        if not (self.structures(UnitTypeId.SPIRE).exists or self.structures(UnitTypeId.GREATERSPIRE).exists):
            return self.record_failure(action_id, 'Neither Spire nor Greater Spire available')
        if not (self.structures(UnitTypeId.LAIR).exists or self.structures(UnitTypeId.HIVE).exists):
            return self.record_failure(action_id, 'Neither Lair nor Hive is available')
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No Drones available')
        spires = self.structures(UnitTypeId.SPIRE) + self.structures(UnitTypeId.GREATERSPIRE)
        abilities = await self.get_available_abilities(spires)
        for spire in spires:
            if spire.is_idle and AbilityId.RESEARCH_ZERGFLYERARMORLEVEL2 in abilities:
                if self.can_afford(UpgradeId.ZERGFLYERARMORSLEVEL2) and self.already_pending_upgrade(
                        UpgradeId.ZERGFLYERARMORSLEVEL2) == 0:
                    spire.research(UpgradeId.ZERGFLYERARMORSLEVEL2)
                    print('research zerg fly armor plus 2')
                    return
                else:
                    return self.record_failure(action_id,
                                               'Cannot afford Zerg Fly Armor +2 upgrade or upgrade already in progress')

        return self.record_failure(action_id,
                                   'No idle Spire or Greater Spire available or Zerg Fly Armor +2 upgrade not available')

    async def handle_action_58(self):
        action_id = 58
        print(f'action={action_id}')

        if not (self.structures(UnitTypeId.SPIRE).exists or self.structures(UnitTypeId.GREATERSPIRE).exists):
            return self.record_failure(action_id, 'Neither Spire nor Greater Spire available')
        if not self.structures(UnitTypeId.HIVE).exists:
            return self.record_failure(action_id, 'No Hive available')
        if not self.units(UnitTypeId.DRONE).exists:
            return self.record_failure(action_id, 'No Drones available')

        spires = self.structures(UnitTypeId.SPIRE) + self.structures(UnitTypeId.GREATERSPIRE)
        abilities = await self.get_available_abilities(spires)
        for spire in spires:
            if spire.is_idle and AbilityId.RESEARCH_ZERGFLYERARMORLEVEL3 in abilities:
                if self.can_afford(UpgradeId.ZERGFLYERARMORSLEVEL3) and self.already_pending_upgrade(
                        UpgradeId.ZERGFLYERARMORSLEVEL3) == 0:
                    spire.research(UpgradeId.ZERGFLYERARMORSLEVEL3)
                    print('research zerg fly armor plus 3')
                    return
                else:
                    return self.record_failure(action_id,
                                               'Cannot afford Zerg Fly Armor +3 upgrade or upgrade already in progress')

        return self.record_failure(action_id,
                                   'No idle Spire or Greater Spire available or Zerg Fly Armor +3 upgrade not available')

    async def handle_action_59(self):
        action_id = 59
        print(f'action={action_id}')

        if not self.structures(UnitTypeId.ULTRALISKCAVERN).exists:
            return self.record_failure(action_id, 'No Ultralisk Cavern available')
        if not self.structures(UnitTypeId.HIVE).exists:
            return self.record_failure(action_id, 'No Hive available')

        ultraliskcaverns = self.structures(UnitTypeId.ULTRALISKCAVERN)
        abilities = await self.get_available_abilities(ultraliskcaverns)
        for ultraliskcavern in ultraliskcaverns:
            if ultraliskcavern.is_idle and AbilityId.RESEARCH_CHITINOUSPLATING in abilities:
                if self.can_afford(UpgradeId.CHITINOUSPLATING) and self.already_pending_upgrade(
                        UpgradeId.CHITINOUSPLATING) == 0:
                    ultraliskcavern.research(UpgradeId.CHITINOUSPLATING)
                    print('research chitionous splating')
                    return
                else:
                    return self.record_failure(action_id,
                                               'Cannot afford Chitonous Splating upgrade or upgrade already in progress')

        return self.record_failure(action_id,
                                   'No idle Ultralisk Cavern available or Chitonous Splating upgrade not available')

    async def handle_action_60(self):
        action_id = 60
        print(f'action={action_id}')

        if not self.structures(UnitTypeId.ULTRALISKCAVERN).exists:
            return self.record_failure(action_id, 'No Ultralisk Cavern available')
        if not self.structures(UnitTypeId.HIVE).exists:
            return self.record_failure(action_id, 'No Hive available')

        ultraliskcaverns = self.structures(UnitTypeId.ULTRALISKCAVERN)
        abilities = await self.get_available_abilities(ultraliskcaverns)
        for ultraliskcavern in ultraliskcaverns:
            if ultraliskcavern.is_idle and AbilityId.RESEARCH_ANABOLICSYNTHESIS in abilities:
                if self.can_afford(UpgradeId.ANABOLICSYNTHESIS) and self.already_pending_upgrade(
                        UpgradeId.ANABOLICSYNTHESIS) == 0:
                    ultraliskcavern.research(UpgradeId.ANABOLICSYNTHESIS)
                    print('research anabolic synthesis')
                    return
                else:
                    return self.record_failure(action_id,
                                               'Cannot afford Anabolic Synthesis upgrade or upgrade already in progress')

        return self.record_failure(action_id,
                                   'No idle Ultralisk Cavern available or Anabolic Synthesis upgrade not available')

    async def handle_action_61(self):
        action_id = 61
        print(f'action={action_id}')

        if not self.structures(UnitTypeId.LURKERDENMP).exists:
            return self.record_failure(action_id, 'No Lurker Den available')
        if not self.workers.exists:
            return self.record_failure(action_id, 'No workers available')
        if not self.structures(UnitTypeId.HIVE).exists:
            return self.record_failure(action_id, 'No Hive available')
        lurkerdens = self.structures(UnitTypeId.LURKERDENMP)
        abilities = await self.get_available_abilities(lurkerdens)
        for lurkerden in lurkerdens:
            if lurkerden.is_idle and AbilityId.LURKERDENRESEARCH_RESEARCHLURKERRANGE in abilities:
                if self.can_afford(UpgradeId.LURKERRANGE) and self.already_pending_upgrade(UpgradeId.LURKERRANGE) == 0:
                    lurkerden.research(UpgradeId.LURKERRANGE)
                    print('research lurker range')
                    return
                else:
                    return self.record_failure(action_id,
                                               'Cannot afford Lurker Range upgrade or upgrade already in progress')

        return self.record_failure(action_id, 'No idle Lurker Den available or Lurker Range upgrade not available')

    async def handle_action_62(self):
        action_id = 62
        print(f'action={action_id}')

        # The conditions for existence of structures and units are the same as for action 61.
        # We can reuse those checks here.

        if not self.structures(UnitTypeId.LURKERDENMP).exists:
            return self.record_failure(action_id, 'No Lurker Den available')
        if not self.workers.exists:
            return self.record_failure(action_id, 'No workers available')
        if not self.structures(UnitTypeId.HIVE).exists:
            return self.record_failure(action_id, 'No Hive available')

        lurkerdens = self.structures(UnitTypeId.LURKERDENMP)
        abilities = await self.get_available_abilities(lurkerdens)
        for lurkerden in lurkerdens:
            if lurkerden.is_idle and AbilityId.RESEARCH_ADAPTIVETALONS in abilities:
                if self.can_afford(UpgradeId.DIGGINGCLAWS) and self.already_pending_upgrade(
                        UpgradeId.DIGGINGCLAWS) == 0:
                    lurkerden.research(UpgradeId.DIGGINGCLAWS)
                    print('research diggingclaws')
                    return
                else:
                    return self.record_failure(action_id,
                                               'Cannot afford Digging Claws upgrade or upgrade already in progress')

        return self.record_failure(action_id, 'No idle Lurker Den available or Digging Claws upgrade not available')

    async def handle_action_63(self):
        return await self.handle_scouting(UnitTypeId.ZERGLING, 63)

    async def handle_action_64(self):
        return await self.handle_scouting(UnitTypeId.OVERLORD, 64)

    async def handle_action_65(self):
        return await self.handle_scouting(UnitTypeId.OVERSEER, 64)

    async def handle_action_66(self):
        action_id = 66
        print(f'action={action_id}')

        if self.supply_army <= 0:
            return self.record_failure(action_id, 'No army available for attack')
        if not self.enemy_units:
            return self.record_failure(action_id, 'No enemy units to attack')
        if not self.enemy_structures:
            return self.record_failure(action_id, 'No enemy structures to attack')

        reward = 0
        attack_units = {UnitTypeId.ZERGLING, UnitTypeId.BANELING, UnitTypeId.QUEEN, UnitTypeId.ROACH,
                        UnitTypeId.OVERSEER,
                        UnitTypeId.ULTRALISK, UnitTypeId.MUTALISK, UnitTypeId.INFESTOR, UnitTypeId.CORRUPTOR,
                        UnitTypeId.BROODLORD,
                        UnitTypeId.OVERSEER, UnitTypeId.RAVAGER, UnitTypeId.VIPER, UnitTypeId.SWARMHOSTMP,
                        UnitTypeId.LURKERMP}  # list all unit types

        for unit in self.units.of_type(attack_units):
            reward += self.handle_attack(unit, self.enemy_units, self.enemy_structures, 0.015)

    async def handle_action_67(self):
        action_id = 67
        print(f'action={action_id}')

        if self.supply_army <= 0:
            return self.record_failure(action_id, 'No army available for retreat')
        if not self.townhalls:
            return self.record_failure(action_id, 'No townhalls for retreat')
        retreat_units = {UnitTypeId.ZERGLING, UnitTypeId.BANELING, UnitTypeId.QUEEN, UnitTypeId.ROACH,
                         UnitTypeId.OVERSEER,
                         UnitTypeId.ULTRALISK, UnitTypeId.MUTALISK, UnitTypeId.INFESTOR, UnitTypeId.CORRUPTOR,
                         UnitTypeId.BROODLORD,
                         UnitTypeId.OVERSEER, UnitTypeId.RAVAGER, UnitTypeId.VIPER, UnitTypeId.SWARMHOSTMP,
                         UnitTypeId.LURKERMP}  # list all unit types

        for unit in self.units.of_type(retreat_units):
            where2retreat = random.choice(self.townhalls)
            unit.move(where2retreat)
            print('retreat')

    async def handle_action_68(self):
        action_id = 68
        print(f'action={action_id}')

        if not self.townhalls.exists:
            return self.record_failure(action_id, 'No townhalls available')

        if not self.units(UnitTypeId.QUEEN).exists:
            return self.record_failure(action_id, 'No Queen available for inject')

        queens = self.units(UnitTypeId.QUEEN)
        abilities = await self.get_available_abilities(queens)

        for queen in queens.idle:
            if AbilityId.EFFECT_INJECTLARVA in abilities and queen.energy >= 25:
                hq = self.townhalls.closest_to(queen)
                queen(AbilityId.EFFECT_INJECTLARVA, hq)
                print('queen inject')
                return

    async def handle_action_69(self):
        action_id = 0
        print(f'action={action_id}')
        pass

    async def on_step(self, iteration: int):
        if self.time_formatted == '00:00':
            if self.start_location == Point2((160.5, 46.5)):
                self.Location = -1  # detect location
            else:
                self.Location = 1

        # 获取信息
        information = self.get_information()
        await self.defend()

        # 锁定并读取动作
        with self.lock:
            self.transaction['information'] = information
        while self.transaction['action'] is None:
            time.sleep(0.001)
        action = self.transaction['action']

        # 处理聊天命令
        # 处理聊天命令
        if self.transaction['output_command_flag'] == True:
            command = self.transaction['command']
            if command is None:
                message = "Welcome to StarCraft II"
            # elif isinstance(command, list):  # 判断command是否为列表
            #     message = "\n".join(command)  # 将列表元素连接起来，并使用换行符分隔
            # else:
            #     message = command
            else:
                message = self.action_dict[action]
            await self.chat_send(message)

        # 调用相应的动作处理函数
        method_name = f'handle_action_{action}'
        method = getattr(self, method_name, None)
        if method and callable(method):
            await method()
        else:
            print(f'Error: Method {method_name} does not exist!')

        # 进行常规操作
        await self.distribute_workers()

        # 更新transaction字典
        with self.lock:
            self.transaction['action'] = None
            self.transaction['reward'] = 0  # 你可能需要在此计算真正的reward
            self.transaction['iter'] = iteration
            self.transaction['action_failures'] = copy.deepcopy(self.temp_failure_list)
            self.transaction['action_executed'] = copy.deepcopy(self.action_dict[action])
            #
            print("self.temp_failure_list", self.temp_failure_list)
            print("self.transaction['action_failures']", self.transaction['action_failures'])
            print("self.transaction['action_executed']",self.transaction['action_executed'])
            self.temp_failure_list.clear()  # 清空临时列表

        self.isReadyForNextStep.set()






def zerg_agent_vs_build_in(transaction, lock, map_name, isReadyForNextStep, game_end_event, done_event, opposite_race,
                           difficulty, replay_folder, process_id, args):
    if not os.path.exists(replay_folder):
        try:
            os.makedirs(replay_folder)
        except OSError:
            print(f"create dictionary {replay_folder} failure,please check and run program again.")
            return

    map = map_name

    result = run_game(maps.get(map),
                      [Bot(Race.Zerg, Zerg_Bot(transaction, lock, isReadyForNextStep)),
                       Computer(map_race(opposite_race), map_difficulty(difficulty))],
                      realtime=False,
                      save_replay_as=f'{replay_folder}/{args.current_time}_{map}Player_race_ZERG_VS_BUILD_IN_AI_{difficulty}_{opposite_race}_process_{process_id}.SC2Replay')

    with lock:
        # print("_________")
        # print("last lock")
        # print("_________")
        transaction['done'] = True
        transaction['result'] = result
    # print("transaction done:", transaction['done'])
    done_event.set()  # Set done_event when the game is over

    # print("game end")
    game_end_event.set()  # Set game_end_event when the game is over


def zerg_agent_vs_rule(transaction, lock, map_name, isReadyForNextStep, game_end_event, done_event, opposite_race,
                       opposite_bot, replay_folder, process_id, args):
    map = map_name

    # 检查文件夹是否存在，如果不存在则创建
    if not os.path.exists(replay_folder):
        try:
            os.makedirs(replay_folder)
        except OSError:
            print(f"create dictionary {replay_folder} failure,please check and run program again.")
            return

    result = run_game(maps.get(map),
                      [Bot(Race.Zerg, Zerg_Bot(transaction, lock, isReadyForNextStep)),
                       Bot(map_race(opposite_race), map_rule_bot(opposite_bot))],
                      realtime=True,
                      save_replay_as=f'{replay_folder}/{args.current_time}_{map}Player_race_ZERG_VS_RULE_AI_{opposite_bot}_{opposite_race}_process_{process_id}.SC2Replay')

    with lock:
        # print("_________")
        # print("last lock")
        # print("_________")
        transaction['done'] = True
        transaction['result'] = result
    # print("transaction done:", transaction['done'])
    done_event.set()  # Set done_event when the game is over

    # print("game end")
    game_end_event.set()  # Set game_end_event when the game is over
