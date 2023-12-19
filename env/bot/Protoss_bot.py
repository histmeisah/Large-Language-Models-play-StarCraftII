import os
import random
import time
import copy
from typing import Set, List
import math
from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Race
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.position import Point2
from utils.action_info import ActionDescriptions
from config.config import map_difficulty, map_race
from collections import Counter

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
import nest_asyncio

nest_asyncio.apply()

ATTACK_START_THRESHOLD = 70
ATTACK_STOP_THRESHOLD = 40
SOME_DELAY = 100
WAIT_ITER_FOR_KILL_VISIBLE = 200
WAIT_ITER_FOR_CLUSTER_ASSIGN = 400
CRITICAL_BUILDING_DISTANCE = 3  # 或者其他适合的值
# 定义常量
DEFEND_UNIT_COUNT = 5  # 防守单位的数量
DEFEND_UNIT_ASSIGN_INTERVAL = 200  # 重新划分防守单位的间隔步数
MIN_DISTANCE = 3  # 这个值可以根据实际情况调整
BUILDING_DISTANCE = 7
EXCLUDED_UNITS = {UnitTypeId.LARVA, UnitTypeId.CHANGELING, UnitTypeId.EGG}
SCOUTING_INTERVAL = 300


# import torch
#
# device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


class Protoss_Bot(BotAI):
    def __init__(self, transaction, lock, isReadyForNextStep):
        self.iteration = 0
        self.lock = lock
        self.transaction = transaction
        self.worker_supply = 12  # 农民数量
        self.army_supply = 0  # 部队人口
        self.base_pending = 0
        self.enemy_units_count = 0  # 敌方单位数量
        # self.army_units_list=[]  # 我方部队列表
        # self.enemy_list = []
        self.base_count = 1  # 基地数量
        self.pylon_count = 0
        self.gas_buildings_count = 0
        self.gateway_count = 0
        self.forge_count = 0
        self.photon_cannon_count = 0
        self.shield_battery_count = 0
        self.warp_gate_count = 0
        self.cybernetics_core_count = 0
        self.twilight_council_count = 0
        self.robotics_facility_count = 0
        self.stargate_count = 0
        self.templar_archives_count = 0
        self.dark_shrine_count = 0
        self.robotics_bay_count = 0
        self.fleet_beacon_count = 0

        self.base_pending = 0
        self.action_dict = self.get_action_dict()

        self.rally_defend = False
        self.isReadyForNextStep = isReadyForNextStep
        self.is_attacking = False  # 判断是否在进攻
        self.assigned_to_clusters = False  # 判断是否分配了进攻单位
        self.temp1 = False  # 用于判断是否发起进攻
        self.temp2 = False  # 用于判断是否摧毁敌方基地
        self.last_cluster_assignment_iter = 0
        self.clear_base_check_count = 0
        self.wait_iter_start = 0
        self.wait_iter_start_for_cluster = 0
        self.last_attack_visible_iter = 0
        self.last_cluster_assignment_iter = 0
        self.defend_units = []  # 防守单位列表
        self.last_defend_units_assign_iter = 0  # 上次划分防守单位的iteration
        self.temp_failure_list = []
        self.last_scouting_iteration = 0

        self.military_unit_types = {
            UnitTypeId.ZEALOT, UnitTypeId.ARCHON, UnitTypeId.VOIDRAY, UnitTypeId.STALKER,
            UnitTypeId.ADEPT, UnitTypeId.HIGHTEMPLAR, UnitTypeId.DARKTEMPLAR, UnitTypeId.OBSERVER,
            UnitTypeId.PHOENIX, UnitTypeId.CARRIER, UnitTypeId.VOIDRAY, UnitTypeId.TEMPEST,
            UnitTypeId.ORACLE, UnitTypeId.COLOSSUS, UnitTypeId.DISRUPTOR, UnitTypeId.WARPPRISM,
            UnitTypeId.IMMORTAL, UnitTypeId.CHANGELINGZEALOT
        }

    def is_position_valid_for_building(self, position: Point2) -> bool:
        """
        检查给定的位置是否适合建造建筑。
        :param position: 要检查的位置。
        :return: 如果位置适合建造建筑，则返回True，否则返回False。
        """

        # 检查与其他建筑的距离
        # 迭代遍历当前存在的所有建筑
        for structure in self.structures:
            # 如果给定位置与某个建筑的距离小于预设的最小距离 + 建筑的半径，说明太近了，可能会导致建筑重叠。
            if position.distance_to(structure.position) < BUILDING_DISTANCE + structure.radius:
                return False

        # 检查与资源的距离
        # 迭代遍历当前存在的所有资源（矿石和气体）
        for resource in self.resources:
            # 如果给定位置与某个资源的距离小于预设的最小距离 + 资源的半径，说明太近了，可能会妨碍单位的采集。
            if position.distance_to(resource.position) < MIN_DISTANCE + 2:  # 这里加3是为了确保水晶塔离资源有一定的距离
                return False

        # 检查与关键建筑的距离
        # 迭代遍历当前存在的关键建筑，例如瓦斯采集器和主基地
        critical_structures = self.structures({UnitTypeId.ASSIMILATOR, UnitTypeId.NEXUS})
        for critical_structure in critical_structures:
            # 如果给定位置与某个关键建筑的距离小于预设的关键建筑最小距离 + 关键建筑的半径，说明太近了。
            # 这可能会阻碍单位的移动，特别是在基地和瓦斯采集器之间。
            if position.distance_to(
                    critical_structure.position) < CRITICAL_BUILDING_DISTANCE + critical_structure.radius:
                return False

        # 检查与同类型建筑的距离
        # 迭代遍历当前存在的某些特定类型的建筑（如星门、机器人工厂等）
        for building in self.structures(
                {UnitTypeId.STARGATE, UnitTypeId.ROBOTICSFACILITY, UnitTypeId.GATEWAY, ...}):
            # 如果给定位置与某个特定类型的建筑的距离小于预设的最小距离 + 建筑的半径，说明太近了。
            # 这可能会导致建筑重叠或其他不期望的行为。
            if position.distance_to(building.position) < BUILDING_DISTANCE + building.radius:
                return False

        # 如果上述所有条件都满足，说明给定位置是适合建造建筑的。
        return True

    def find_optimal_building_position_for_base(self, base_position: Point2, building_type: UnitTypeId,
                                                max_distance=15) -> Point2:
        """
        查找靠近基地的最佳建筑位置。

        Args:
        - base_position (Point2): 我们想要在其周围建造的基地的位置。
        - building_type (UnitTypeId): 我们想要建造的建筑的类型。
        - max_distance (int): 在基地周围搜索建筑位置的最大半径。

        Returns:
        - Point2 or None: 新建筑的最佳位置，如果找不到合适的位置，则为None。
        """

        # 获取所有的水晶塔
        pylons = self.structures(UnitTypeId.PYLON)

        # 如果没有水晶塔，我们使用原始的方法在Nexus附近寻找建筑位置
        if not pylons.exists:
            return self.original_building_position_search(base_position, building_type, max_distance)

        # 为每个水晶塔计算得分，基于其距离Nexus的远近和其附近的建筑数量
        pylon_scores = {}
        for pylon in pylons:
            distance_to_base = pylon.distance_to(base_position)
            nearby_buildings = sum(1 for building in self.structures if building.distance_to(pylon) < 12)
            # 评分函数：距离Nexus的远近权重为1，附近建筑数量的权重为-2
            score = 1 * distance_to_base - 2 * nearby_buildings
            pylon_scores[pylon] = score

        # 选择得分最高的水晶塔
        best_pylon = max(pylon_scores, key=pylon_scores.get)

        # 在最佳水晶塔附近使用原始方法寻找建筑位置
        best_position = self.original_building_position_search(best_pylon.position, building_type, max_distance)

        return best_position

    def original_building_position_search(self, base_position: Point2, building_type: UnitTypeId,
                                          max_distance=15) -> Point2:
        """
        原始的寻找建筑位置的方法。
        """
        enemy_base_position = self.enemy_start_locations[0]
        weight_own_base = 1.0  # Positive weight: prefer positions farther from our base
        weight_enemy_base = -2.0  # Negative weight: avoid positions too close to the enemy base

        # Define a scoring function for each position
        def compute_score(pos):
            distance_to_own_base = pos.distance_to(base_position)
            distance_to_enemy_base = pos.distance_to(enemy_base_position)

            # Calculate score based on weighted distances
            score = weight_own_base * distance_to_own_base + weight_enemy_base / (distance_to_enemy_base + 1)
            return score

        for distance in range(1, max_distance + 1):
            candidate_positions = list(self.neighbors8(base_position, distance))
            valid_positions = [pos for pos in candidate_positions if self.is_position_valid_for_building(pos)]

            if valid_positions:
                best_position = max(valid_positions, key=compute_score)
                return best_position

        return None

    def find_best_base_for_building(self, building_type: UnitTypeId):
        base_positions = [base.position for base in self.townhalls]
        building_positions = [building.position for building in self.structures(building_type)]
        base_building_counts = {}
        for base_pos in base_positions:
            count = sum(1 for building_pos in building_positions if base_pos.distance_to(building_pos) <= 12)
            base_building_counts[base_pos] = count
        sorted_bases = sorted(base_building_counts.keys(), key=lambda base: base_building_counts[base])
        return sorted_bases[0] if sorted_bases else None

    async def handle_action_build_building(self, building_type: UnitTypeId, building_limits=None):
        """
        building_limits是一个字典，键是时间范围，值是该时间范围内允许建造的建筑数量。
        例如，{"00:00-02:00": 1}表示在0:00到2:00之间只允许建造1个建筑。

        """
        # 如果无法负担费用，则直接返回
        if not self.can_afford(building_type):
            print(f"Cannot afford {building_type}")
            return

        current_time = self.time_formatted  # 获取当前游戏时间

        # 如果提供了建筑限制，并且当前时间在限制的范围内
        if building_limits:
            for time_range, limit in building_limits.items():
                start_time, end_time = time_range.split('-')
                if start_time <= current_time <= end_time:
                    # 计算当前已有的相同类型建筑的数量（包括正在建造的）
                    current_building_count = self.structures(building_type).amount + self.already_pending(building_type)

                    # 如果当前建筑数量已达到或超过此时间段的限制，则不建造
                    if current_building_count >= limit:
                        print(f"Building limit reached for {building_type} for the time range {time_range}.")
                        return

        # --- 以下是寻找建筑位置和发起建造的代码，与原先保持一致 ---

        if building_type in {UnitTypeId.PHOTONCANNON, UnitTypeId.SHIELDBATTERY}:
            # 确定外侧基地
            enemy_start = self.enemy_start_locations[0]
            outermost_base = min(self.townhalls, key=lambda base: base.distance_to(enemy_start))

            # 找到附近的建筑位置
            best_position = self.find_optimal_building_position_for_base(outermost_base.position, max_distance=8,
                                                                         building_type=building_type)

        else:
            best_base = self.find_best_base_for_building(building_type)
            if not best_base:
                print(f"No suitable base found for {building_type}")
                return

            # 优先找到最佳位置
            best_position = self.find_optimal_building_position_for_base(best_base, building_type=building_type)

            # 如果在这个最佳基地找不到合适的位置，则尝试在其他基地找到合适的位置
            if not best_position:
                print(f"No suitable position found near best base for {building_type}. Trying alternative bases.")

                for base in self.townhalls:
                    if base.position != best_base.position:
                        best_position = self.find_optimal_building_position_for_base(base.position,
                                                                                     building_type=building_type)
                        if best_position:
                            break

            # 如果在所有基地都找不到理想位置，尝试寻找次佳位置
            if not best_position:
                print("Trying suboptimal positions...")

                adjusted_building_distance = 10  # 可以根据需要进行调整
                best_position = self.find_optimal_building_position_for_base(best_base.position,
                                                                             max_distance=adjusted_building_distance,
                                                                             building_type=building_type)

                # 如果还是找不到，尝试扩展搜索范围
                if not best_position:
                    print("Expanding search range...")
                    expanded_search_range = 30  # 可以根据需要进行调整
                    best_position = self.find_optimal_building_position_for_base(best_base.position,
                                                                                 max_distance=expanded_search_range,
                                                                                 building_type=building_type)

        if not best_position:
            print(f"Still no suitable position found for {building_type}. Aborting.")
            return

        await self.build(building_type, near=best_position)
        print(f"Building {building_type}")

    def is_position_blocking_resources(self, position: Point2) -> bool:
        """
        检查指定位置是否会妨碍资源采集。
        """
        for resource in self.resources:
            if position.distance_to(resource.position) < MIN_DISTANCE:
                return True
        return False

    def is_position_valid_for_pylon(self, position: Point2) -> bool:
        """
        检查指定位置是否适合建造水晶塔。
        """
        # 检查与其他建筑的距离，包括其他的水晶塔
        for structure in self.structures:
            if position.distance_to(structure.position) < MIN_DISTANCE:
                return False

        # 特别检查与ASSIMILATOR的距离
        for assimilator in self.structures(UnitTypeId.ASSIMILATOR):
            if position.distance_to(assimilator.position) < MIN_DISTANCE * 1.5:
                return False

        # 检查与资源的距离
        for resource in self.resources:
            if position.distance_to(resource.position) < MIN_DISTANCE:
                return False

        return True

    def find_optimal_pylon_position_for_base(self, base_position: Point2) -> Point2:
        """
        查找最佳的水晶塔位置。
        """
        # 为基地生成候选位置
        candidate_positions = [base_position] + [pos for i in range(1, 15) for pos in
                                                 self.neighbors8(base_position, distance=i)]

        # 从候选位置中筛选出不会阻挡资源采集的位置
        valid_positions = [pos for pos in candidate_positions if
                           not self.is_position_blocking_resources(pos) and self.is_position_valid_for_pylon(pos)]

        # 如果没有合适的位置，直接返回基地位置
        if not valid_positions:
            return base_position

        pylons = self.structures(UnitTypeId.PYLON)
        pylon_positions = [pylon.position for pylon in pylons]

        # 使用sigmoid函数为每个位置评分
        def score_position(pos):
            total_score = 0
            for pylon_pos in pylon_positions:
                distance = pos.distance_to(pylon_pos)
                # 这个sigmoid函数会使得距离为5的位置得到0.5的分数
                score = 1 / (1 + math.exp(-distance + 5))
                total_score += score
            return total_score

        # 选择得分最高的位置
        best_position = max(valid_positions, key=score_position)
        return best_position

    def find_best_base_for_pylon(self):
        """
        寻找建造水晶塔的最佳基地位置。
        """
        pylons = self.structures(UnitTypeId.PYLON)
        base_positions = [base.position for base in self.townhalls]
        pylon_positions = [pylon.position for pylon in pylons]
        base_pylon_counts = {}

        # 计算每个基地附近的水晶塔数量
        for base_pos in base_positions:
            count = sum(1 for pylon_pos in pylon_positions if base_pos.distance_to(pylon_pos) <= 10)
            base_pylon_counts[base_pos] = count

        # 返回附近水晶塔数量最少的基地
        sorted_bases = sorted(base_pylon_counts.keys(), key=lambda base: base_pylon_counts[base])
        return sorted_bases[0]

    def assign_defend_units(self, iteration):
        MILITARY_UNITS = self.get_military_units()

        # 如果还没有开始进攻，不重新指定防守部队
        if not self.temp1:
            return

        # 判断是否需要重新划分防守单位
        if not self.defend_units or iteration - self.last_defend_units_assign_iter >= DEFEND_UNIT_ASSIGN_INTERVAL:
            self.defend_units = random.sample(MILITARY_UNITS, DEFEND_UNIT_COUNT)
            self.last_defend_units_assign_iter = iteration

    def get_military_units(self):
        return self.units.of_type(self.military_unit_types)

    def get_enemy_unity(self):
        # 判断是否有敌方单位
        if self.enemy_units:
            # 使用列表推导来获取每个敌方单位的名称，名称格式为 "enemy_" + 单位的类型ID
            unit_names = ['enemy_' + str(unit.type_id) for unit in self.enemy_units]

            # 使用Counter统计每种单位的数量
            unit_type_amount = Counter(unit_names)

            # 打印当前的单位数量统计
            print(unit_type_amount)

            # 返回单位数量统计的字典
            return unit_type_amount
        else:
            # 如果没有敌方单位，返回空字典
            return {}

    def get_action_dict(self):
        action_description = ActionDescriptions('Protoss')
        action_dict = action_description.action_descriptions
        flat_dict = {}
        for key, value in action_dict.items():
            for inner_key, inner_value in value.items():
                flat_dict[inner_key] = inner_value
        return flat_dict

    def get_enemy_structure(self):
        # 判断是否有敌方建筑
        if self.enemy_structures:
            # 使用列表推导来获取每个敌方建筑的名称，名称格式为 "enemy_" + 建筑的类型ID
            structure_names = ['enemy_' + str(structure.type_id) for structure in self.enemy_structures]

            # 使用Counter统计每种建筑的数量
            structure_type_amount = Counter(structure_names)

            # 打印当前的建筑数量统计
            print(structure_type_amount)

            # 返回建筑数量统计的字典
        else:
            # 如果没有敌方建筑，返回空字典
            return {}

    def get_information(self):
        """Retrieve game-related information and structure it."""
        information = {
            "resource": self._get_resource_information(),
            "building": self._get_building_information(),
            "unit": self._get_unit_information(),
            "planning": self._get_planning_information(),
            "research": self._get_research_information(),
        }

        information = self._update_enemy_information(information)
        return information

    def _get_resource_information(self):
        """Retrieve resource-related information."""
        self.worker_supply = self.workers.amount
        self.army_supply = self.supply_army
        return {
            'game_time': self.time_formatted,
            'worker_supply': self.worker_supply,
            'mineral': self.minerals,
            'gas': self.vespene,
            'supply_left': self.supply_left,
            'supply_cap': self.supply_cap,
            'supply_used': self.supply_used,
            'army_supply': self.army_supply,
        }

    def _get_building_information(self):
        """Retrieve building-related information."""
        self.base_count = self.structures(UnitTypeId.NEXUS).amount
        self.base_pending = self.already_pending(UnitTypeId.NEXUS)
        self.pylon_count = self.structures(UnitTypeId.PYLON).amount
        self.gas_buildings_count = self.structures(UnitTypeId.ASSIMILATOR).amount
        self.gateway_count = self.structures(UnitTypeId.GATEWAY).amount
        self.forge_count = self.structures(UnitTypeId.FORGE).amount
        self.photon_cannon_count = self.structures(UnitTypeId.PHOTONCANNON).amount
        self.shield_battery_count = self.structures(UnitTypeId.SHIELDBATTERY).amount
        self.warp_gate_count = self.structures(UnitTypeId.WARPGATE).amount
        self.cybernetics_core_count = self.structures(UnitTypeId.CYBERNETICSCORE).amount
        self.twilight_council_count = self.structures(UnitTypeId.TWILIGHTCOUNCIL).amount
        self.robotics_facility_count = self.structures(UnitTypeId.ROBOTICSFACILITY).amount
        self.stargate_count = self.structures(UnitTypeId.STARGATE).amount
        self.templar_archives_count = self.structures(UnitTypeId.TEMPLARARCHIVE).amount
        self.dark_shrine_count = self.structures(UnitTypeId.DARKSHRINE).amount
        self.robotics_bay_count = self.structures(UnitTypeId.ROBOTICSBAY).amount
        self.fleet_beacon_count = self.structures(UnitTypeId.FLEETBEACON).amount
        return {
            'nexus_count': self.base_count,
            'pylon_count': self.pylon_count,
            'gas_buildings_count': self.gas_buildings_count,
            'gateway_count': self.gateway_count,
            'forge_count': self.forge_count,
            'photon_cannon_count': self.photon_cannon_count,
            'shield_battery_count': self.shield_battery_count,
            'warp_gate_count': self.warp_gate_count,
            'cybernetics_core_count': self.cybernetics_core_count,
            'twilight_council_count': self.twilight_council_count,
            'robotics_facility_count': self.robotics_facility_count,
            'statgate_count': self.stargate_count,
            'templar_archives_count': self.templar_archives_count,
            'dark_shrine_count': self.dark_shrine_count,
            'robotics_bay_count': self.robotics_bay_count,
            'fleet_beacon_count': self.fleet_beacon_count,
        }

    def _get_unit_information(self):
        """Retrieve unit-related information."""
        return {
            "probe_count": self.units(UnitTypeId.PROBE).amount,
            'Zealot_count': self.units(UnitTypeId.ZEALOT).amount,
            'stalker_count': self.units(UnitTypeId.STALKER).amount,
            'sentry_count': self.units(UnitTypeId.SENTRY).amount,
            'adept_count': self.units(UnitTypeId.ADEPT).amount,
            'high_templar_count': self.units(UnitTypeId.HIGHTEMPLAR).amount,
            'dark_templar_count': self.units(UnitTypeId.DARKTEMPLAR).amount,
            'immortal_count': self.units(UnitTypeId.IMMORTAL).amount,
            'colossus_count': self.units(UnitTypeId.COLOSSUS).amount,
            'disruptor_count': self.units(UnitTypeId.DISRUPTOR).amount,
            'archon_count': self.units(UnitTypeId.ARCHON).amount,
            'observer_count': self.units(UnitTypeId.OBSERVER).amount,
            'warp_prism_count': self.units(UnitTypeId.WARPPRISM).amount,
            'phoenix_count': self.units(UnitTypeId.PHOENIX).amount,
            'voidray_count': self.units(UnitTypeId.VOIDRAY).amount,
            'Oracle_count': self.units(UnitTypeId.ORACLE).amount,
            'Carrier_count': self.units(UnitTypeId.CARRIER).amount,
            'tempest_count': self.units(UnitTypeId.TEMPEST).amount,
            'mothership_count': self.units(UnitTypeId.MOTHERSHIP).amount,
        }

    def _get_planning_information(self):
        """Retrieve planning-related information."""
        return {
            # 建筑相关
            "planning_structure": {
                'planning_nexus_count': self.already_pending(UnitTypeId.NEXUS),
                'planning_pylon_count': self.already_pending(UnitTypeId.PYLON),
                'planning_gas_buildings_count': self.already_pending(UnitTypeId.ASSIMILATOR),
                'planning_gateway_count': self.already_pending(UnitTypeId.GATEWAY),
                'planning_forge_count': self.already_pending(UnitTypeId.FORGE),
                'planning_photon_cannon_count': self.already_pending(UnitTypeId.PHOTONCANNON),
                'planning_shield_battery_count': self.already_pending(UnitTypeId.SHIELDBATTERY),
                'planning_warp_gate_count': self.already_pending(UnitTypeId.WARPGATE),
                'planning_cybernetics_core_count': self.already_pending(UnitTypeId.CYBERNETICSCORE),
                'planning_twilight_council_count': self.already_pending(UnitTypeId.TWILIGHTCOUNCIL),
                'planning_robotics_facility_count': self.already_pending(UnitTypeId.ROBOTICSFACILITY),
                'planning_stargate_count': self.already_pending(UnitTypeId.STARGATE),
                'planning_templar_archives_count': self.already_pending(UnitTypeId.TEMPLARARCHIVE),
                'planning_dark_shrine_count': self.already_pending(UnitTypeId.DARKSHRINE),
                'planning_robotics_bay_count': self.already_pending(UnitTypeId.ROBOTICSBAY),
                'planning_fleet_beacon_count': self.already_pending(UnitTypeId.FLEETBEACON),
            },
            # 单位相关
            "planning_unit": {
                'planning_probe_count': self.already_pending(UnitTypeId.PROBE),
                'planning_Zealot_count': self.already_pending(UnitTypeId.ZEALOT),
                'planning_stalker_count': self.already_pending(UnitTypeId.STALKER),
                'planning_sentry_count': self.already_pending(UnitTypeId.SENTRY),
                'planning_adept_count': self.already_pending(UnitTypeId.ADEPT),
                'planning_high_templar_count': self.already_pending(UnitTypeId.HIGHTEMPLAR),
                'planning_dark_templar_count': self.already_pending(UnitTypeId.DARKTEMPLAR),
                'planning_immortal_count': self.already_pending(UnitTypeId.IMMORTAL),
                'planning_colossus_count': self.already_pending(UnitTypeId.COLOSSUS),
                'planning_disruptor_count': self.already_pending(UnitTypeId.DISRUPTOR),
                'planning_archon_count': self.already_pending(UnitTypeId.ARCHON),
                'planning_observer_count': self.already_pending(UnitTypeId.OBSERVER),
                'planning_warp_prism_count': self.already_pending(UnitTypeId.WARPPRISM),
                'planning_phoenix_count': self.already_pending(UnitTypeId.PHOENIX),
                'planning_voidray_count': self.already_pending(UnitTypeId.VOIDRAY),
                'planning_Oracle_count': self.already_pending(UnitTypeId.ORACLE),
                'planning_Carrier_count': self.already_pending(UnitTypeId.CARRIER),
                'planning_tempest_count': self.already_pending(UnitTypeId.TEMPEST),
                'planning_mothership_count': self.already_pending(UnitTypeId.MOTHERSHIP),
            }
        }

    def _get_research_information(self):
        return {
            # warpgate
            "cybernetics_core": {
                'warpgate_research_status': self.already_pending_upgrade(UpgradeId.WARPGATERESEARCH),

                # protoss air weapons

                'protoss_air_armor_level_1_research_status': self.already_pending_upgrade(
                    UpgradeId.PROTOSSAIRARMORSLEVEL1),
                'protoss_air_armor_level_2_research_status': self.already_pending_upgrade(
                    UpgradeId.PROTOSSAIRARMORSLEVEL2),
                'protoss_air_armor_level_3_research_status': self.already_pending_upgrade(
                    UpgradeId.PROTOSSAIRARMORSLEVEL3),

                # protoss air weapons
                "protoss_air_weapon_level_1_research_status": self.already_pending_upgrade(
                    UpgradeId.PROTOSSAIRWEAPONSLEVEL1),
                "protoss_air_weapon_level_2_research_status": self.already_pending_upgrade(
                    UpgradeId.PROTOSSAIRWEAPONSLEVEL2),
                "protoss_air_weapon_level_3_research_status": self.already_pending_upgrade(
                    UpgradeId.PROTOSSAIRWEAPONSLEVEL3),
            },

            "forge": {
                # protoss ground armor

                'protoss_ground_armor_level_1_research_status': self.already_pending_upgrade(
                    UpgradeId.PROTOSSGROUNDARMORSLEVEL1),
                'protoss_ground_armor_level_2_research_status': self.already_pending_upgrade(
                    UpgradeId.PROTOSSGROUNDARMORSLEVEL2),
                'protoss_ground_armor_level_3_research_status': self.already_pending_upgrade(
                    UpgradeId.PROTOSSGROUNDARMORSLEVEL3),

                # protoss ground weapons

                'protoss_ground_weapon_level_1_research_status': self.already_pending_upgrade(
                    UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1),
                'protoss_ground_weapon_level_2_research_status': self.already_pending_upgrade(
                    UpgradeId.PROTOSSGROUNDWEAPONSLEVEL2),
                'protoss_ground_weapon_level_3_research_status': self.already_pending_upgrade(
                    UpgradeId.PROTOSSGROUNDWEAPONSLEVEL3),

                # protoss_shield

                'protoss_shield_level_1_research_status': self.already_pending_upgrade(
                    UpgradeId.PROTOSSSHIELDSLEVEL1),
                'protoss_shield_level_2_research_status': self.already_pending_upgrade(
                    UpgradeId.PROTOSSSHIELDSLEVEL2),
                'protoss_shield_level_3_research_status': self.already_pending_upgrade(
                    UpgradeId.PROTOSSSHIELDSLEVEL3),
            },

            # twilight council upgrades
            "twilight_council": {
                'blink_research_status': self.already_pending_upgrade(UpgradeId.BLINKTECH),
                'charge_research_status': self.already_pending_upgrade(UpgradeId.CHARGE),
                'resonating_glaives_research_status': self.already_pending_upgrade(UpgradeId.ADEPTPIERCINGATTACK),
                # adept attack speed
            },

            # robotics bay upgrades
            "robotics_bay": {
                'extended_thermal_lance_research_status': self.already_pending_upgrade(UpgradeId.EXTENDEDTHERMALLANCE),
                "GRAVITICDRIVE_research_status": self.already_pending_upgrade(UpgradeId.GRAVITICDRIVE),
                "OBSERVERGRAVITICBOOSTER_research_status": self.already_pending_upgrade(
                    UpgradeId.OBSERVERGRAVITICBOOSTER),
            },
            # fleet beacon upgrades
            "fleet_beacon": {
                "PHOENIXRANGEUPGRADE_research_status": self.already_pending_upgrade(UpgradeId.PHOENIXRANGEUPGRADE),
                # "TEMPESTGROUNDATTACKUPGRADE_research_status": self.already_pending_upgrade(
                #     UpgradeId.TEMPESTGROUNDATTACKUPGRADE),
                "VOIDRAYSPEEDUPGRADE_research_status": self.already_pending_upgrade(UpgradeId.VOIDRAYSPEEDUPGRADE),
            },
            # templar archives upgrades
            "templar_archives": {
                "PSISTORMTECH_research_status": self.already_pending_upgrade(UpgradeId.PSISTORMTECH),
            },
            # dark shrine upgrades
            "dark_shrine": {
                "SHADOWSTRIKE_research_status": self.already_pending_upgrade(UpgradeId.DARKTEMPLARBLINKUPGRADE), },
        }

    def _update_enemy_information(self, information):
        self.enemy_unit_type_amount = self.get_enemy_unity()
        self.enemy_structure_type_amount = self.get_enemy_structure()
        """
        Update the given information dictionary with enemy data.

        Args:
        - information (dict): Original information dictionary.

        Returns:
        - dict: Updated information dictionary.
        """
        # Initialize enemy information part if it doesn't exist.
        if 'enemy' not in information:
            information['enemy'] = {
                'unit': {},
                'structure': {}
            }

        # Try to add enemy unit types and amounts if they exist.
        try:
            if hasattr(self, 'enemy_unit_type_amount') and self.enemy_unit_type_amount:
                information['enemy']['unit'].update(self.enemy_unit_type_amount)
        except Exception as e:
            print(f"Error updating enemy unit information: {e}")

        # Try to add enemy structure types and amounts if they exist.
        try:
            if hasattr(self, 'enemy_structure_type_amount') and self.enemy_structure_type_amount:
                information['enemy']['structure'].update(self.enemy_structure_type_amount)
        except Exception as e:
            print(f"Error updating enemy structure information: {e}")

        return information

    async def defend(self):
        print("Defend:", self.rally_defend)
        if self.structures(UnitTypeId.NEXUS).exists and self.supply_army >= 2:
            for nexus in self.townhalls:
                if self.enemy_units.amount >= 2 and self.enemy_units.closest_distance_to(nexus) < 30:
                    self.rally_defend = True
                    for unit in self.units.of_type(
                            {UnitTypeId.ZEALOT, UnitTypeId.ARCHON, UnitTypeId.STALKER, UnitTypeId.SENTRY,
                             UnitTypeId.ADEPT, UnitTypeId.HIGHTEMPLAR, UnitTypeId.DARKTEMPLAR,
                             UnitTypeId.OBSERVER, UnitTypeId.PHOENIX, UnitTypeId.CARRIER, UnitTypeId.VOIDRAY,
                             UnitTypeId.CARRIER,
                             UnitTypeId.TEMPEST, UnitTypeId.ORACLE, UnitTypeId.COLOSSUS,
                             UnitTypeId.DISRUPTOR, UnitTypeId.WARPPRISM, UnitTypeId.IMMORTAL,
                             UnitTypeId.CHANGELINGZEALOT}):
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
                         UnitTypeId.CARRIER,
                         UnitTypeId.TEMPEST, UnitTypeId.ORACLE, UnitTypeId.COLOSSUS,
                         UnitTypeId.DISRUPTOR, UnitTypeId.WARPPRISM, UnitTypeId.IMMORTAL,
                         UnitTypeId.CHANGELINGZEALOT}):
                    if unit.distance_to(self.start_location) > 100 and unit not in self.unit_tags_received_action:
                        unit.move(rally_point)

    def record_failure(self, action, reason):
        self.temp_failure_list.append(f'Action failed: {self.action_dict[action]}, Reason: {reason}')

    async def handle_scouting(self, unit_type, action_id):
        """
        使用指定的单位进行侦查。

        :param unit_type: 用于侦查的单位类型。
        :param action_id: 动作ID，用于记录失败原因。
        """
        # 检查从上次侦查开始是否已经过了指定的间隔
        if self.iteration - self.last_scouting_iteration < SCOUTING_INTERVAL:
            return

        # 如果没有可用的侦查单位，则记录失败并返回
        if not self.units(unit_type).exists:
            return self.record_failure(action_id, f'No {unit_type} available for scouting')

        # 优先选择空闲的侦查单位，如果没有，则随机选择一个
        if self.units(unit_type).idle.exists:
            scout_unit = random.choice(self.units(unit_type).idle)
        else:
            scout_unit = random.choice(self.units(unit_type))

        # 定位侦查位置，这里简单地选择敌方的起始位置
        target_location = self.enemy_start_locations[0]

        # 发出侦查命令
        scout_unit.attack(target_location)

        # 更新上次侦查的迭代次数
        self.last_scouting_iteration = self.iteration

        print(f'{unit_type} scouting towards {target_location}')

    async def produce_bg_unit(self, action_id: int, unit_type: UnitTypeId, required_buildings: List[UnitTypeId] = None):
        print(f'action={action_id}')

        # 检查Warp Gate的研究状态
        warp_gate_research_status = self.already_pending_upgrade(UpgradeId.WARPGATERESEARCH)

        if warp_gate_research_status == 1:
            # 检查是否有水晶塔存在
            if not self.structures(UnitTypeId.PYLON).ready.exists:
                return self.record_failure(action_id, 'No pylons available')

            # 获取最接近敌方起始位置的水晶塔作为参考点
            proxy = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0]).position

            # 尝试从折跃门折跃单位
            await self.warp_unit(action_id, unit_type, proxy, required_buildings=required_buildings)
            print(f'折跃{unit_type.name}')
        else:
            # 尝试从传送门生产单位
            success = await self.train_from_gateway(action_id, unit_type, required_buildings)
            if success:
                print(f'训练{unit_type.name}')

    async def research_air_upgrade(self, action_id, upgrade_id, ability_id, description):
        print(f'action={action_id}')

        # 前置条件检查
        if not self.structures(UnitTypeId.PYLON).exists:
            return self.record_failure(action_id, 'Pylon does not exist')

        if not self.structures(UnitTypeId.NEXUS).exists:
            return self.record_failure(action_id, 'Nexus does not exist')

        if not self.structures(UnitTypeId.CYBERNETICSCORE).exists:
            return self.record_failure(action_id, 'Cybernetics Core does not exist')

        # 获取随机的CYBERNETICSCORE实例
        by = self.structures(UnitTypeId.CYBERNETICSCORE).random
        abilities = await self.get_available_abilities(by)

        # 检查是否可以研究指定的升级
        if self.structures(UnitTypeId.CYBERNETICSCORE).ready and self.already_pending(upgrade_id) == 0:
            if self.can_afford(upgrade_id) and self.structures(
                    UnitTypeId.CYBERNETICSCORE).idle.exists and ability_id in abilities:
                by = self.structures(UnitTypeId.CYBERNETICSCORE).idle.random
                by.research(upgrade_id)
                print(description)

        return self.record_failure(action_id, f'Cannot afford {description} or Cybernetics Core is not idle')

    async def build_pylon_time_period(self, action_id, supply_threshold, pending_threshold, location_multiplier):
        if self.supply_left <= supply_threshold and self.already_pending(
                UnitTypeId.PYLON) <= pending_threshold and not self.supply_cap == 200:
            if self.can_afford(UnitTypeId.PYLON):
                base = self.townhalls.random
                place_position = base.position + Point2((0, self.Location * location_multiplier))
                await self.build(UnitTypeId.PYLON, near=place_position, placement_step=2)
                print('建设水晶塔')
            else:
                return self.record_failure(action_id, 'Cannot afford Pylon')
        return self.record_failure(action_id, 'Not enough supply or too many pending Pylons')

    async def research_upgrade(self, action_id, upgrade_id, ability_id, description):
        print(f'action={action_id}')

        # 前置条件检查
        if not self.structures(UnitTypeId.PYLON).exists:
            return self.record_failure(action_id, 'Pylon does not exist')

        if not self.structures(UnitTypeId.NEXUS).exists:
            return self.record_failure(action_id, 'Nexus does not exist')

        if not self.structures(UnitTypeId.CYBERNETICSCORE).exists:
            return self.record_failure(action_id, 'Cybernetics Core does not exist')

        # 获取随机的CYBERNETICSCORE实例
        by = self.structures(UnitTypeId.CYBERNETICSCORE).random
        abilities = await self.get_available_abilities(by)

        # 检查是否可以研究指定的升级
        if self.structures(UnitTypeId.CYBERNETICSCORE).ready and self.already_pending(upgrade_id) == 0:
            if self.can_afford(upgrade_id) and by.is_idle and ability_id in abilities:
                by.research(upgrade_id)
                print(description)

        return self.record_failure(action_id, f'Cannot afford {description} or Cybernetics Core is not idle')

    async def research_twilight_upgrade(self, action_id, upgrade_id, ability_id, description):
        print(f'action={action_id}')

        # 前置条件检查
        if not self.structures(UnitTypeId.TWILIGHTCOUNCIL).exists:
            return self.record_failure(action_id, 'Twilight Council does not exist')

        # 获取随机的TWILIGHTCOUNCIL实例
        vc = self.structures(UnitTypeId.TWILIGHTCOUNCIL).random
        abilities = await self.get_available_abilities(vc)

        # 检查是否可以研究指定的升级
        if self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready and self.already_pending(upgrade_id) == 0:
            if self.can_afford(upgrade_id) and self.structures(
                    UnitTypeId.TWILIGHTCOUNCIL).idle.exists and ability_id in abilities:
                vc = self.structures(UnitTypeId.TWILIGHTCOUNCIL).idle.random
                vc.research(upgrade_id)
                print(description)

        return self.record_failure(action_id, f'Cannot afford {description} or Twilight Council is not idle')

    async def research_fleetbeacon_upgrade(self, action_id, upgrade_id, ability_id, description):
        print(f'action={action_id}')

        # 前置条件检查
        if not self.structures(UnitTypeId.PYLON).exists:
            return self.record_failure(action_id, 'Pylon does not exist')

        if not self.units(UnitTypeId.PROBE).exists:
            return self.record_failure(action_id, 'Probe does not exist')

        if not self.structures(UnitTypeId.NEXUS).exists:
            return self.record_failure(action_id, 'Nexus does not exist')

        if not self.structures(UnitTypeId.STARGATE).exists:
            return self.record_failure(action_id, 'Stargate does not exist')

        if not self.structures(UnitTypeId.FLEETBEACON).exists:
            return self.record_failure(action_id, 'FleetBeacon does not exist')

        # 获取随机的FLEETBEACON实例
        vf = self.structures(UnitTypeId.FLEETBEACON).random
        abilities = await self.get_available_abilities(vf)

        # 检查是否可以研究指定的升级
        if not self.structures(UnitTypeId.FLEETBEACON).ready:
            return self.record_failure(action_id, 'FleetBeacon is not ready')

        if self.already_pending(upgrade_id) != 0:
            return self.record_failure(action_id, f'Upgrade {description} is already pending')

        if not self.can_afford(upgrade_id):
            return self.record_failure(action_id, f'Cannot afford {description}')

        if not self.structures(UnitTypeId.FLEETBEACON).idle.exists:
            return self.record_failure(action_id, 'FleetBeacon is not idle')

        if ability_id not in abilities:
            return self.record_failure(action_id, f'Ability {description} is not available')
        vf = self.structures(UnitTypeId.FLEETBEACON).idle.random
        vf.research(upgrade_id)
        print(description)

    async def research_forge_upgrade(self, action_id, upgrade_id, ability_id, description):
        print(f'action={action_id}')

        # 前置条件检查
        if not (self.structures(UnitTypeId.PYLON).exists
                and self.units(UnitTypeId.PROBE).exists
                and self.structures(UnitTypeId.NEXUS).exists
                and self.structures(UnitTypeId.FORGE).exists):
            return self.record_failure(action_id, 'Required structures or units do not exist')

        # 获取随机的FORGE实例
        bf = self.structures(UnitTypeId.FORGE).random
        abilities = await self.get_available_abilities(bf)

        # 检查是否可以研究指定的升级
        if self.structures(UnitTypeId.FORGE).ready and self.already_pending(upgrade_id) == 0:
            if self.can_afford(upgrade_id) and self.structures(
                    UnitTypeId.FORGE).idle.exists and ability_id in abilities:
                bf = self.structures(UnitTypeId.FORGE).idle.random
                bf.research(upgrade_id)
                print(description)

        return self.record_failure(action_id, f'Cannot afford {description} or Forge is not idle')

    async def research_roboticsbay_upgrade(self, action_id, upgrade_id, ability_id, description):
        print(f'action={action_id}')

        # 前置条件检查
        if not (self.structures(UnitTypeId.PYLON).exists
                and self.units(UnitTypeId.PROBE).exists
                and self.structures(UnitTypeId.NEXUS).exists
                and self.structures(UnitTypeId.ROBOTICSFACILITY).exists
                and self.structures(UnitTypeId.ROBOTICSBAY).exists):
            return self.record_failure(action_id, 'Required structures or units do not exist')

        # 获取随机的ROBOTICSBAY实例
        vb = self.structures(UnitTypeId.ROBOTICSBAY).random
        abilities = await self.get_available_abilities(vb)

        # 检查是否可以研究指定的升级
        if self.structures(UnitTypeId.ROBOTICSBAY).ready and self.already_pending(upgrade_id) == 0:
            if self.can_afford(upgrade_id) and self.structures(
                    UnitTypeId.ROBOTICSBAY).idle.exists and ability_id in abilities:
                vb = self.structures(UnitTypeId.ROBOTICSBAY).idle.random
                vb.research(upgrade_id)
                print(description)

        return self.record_failure(action_id, f'Cannot afford {description} or RoboticsBay is not idle')

    async def apply_chronoboost(self, action_id, target_type, supply_requirement, description):
        print(f'action={action_id}')

        # 前置条件检查
        if not self.structures(target_type).exists:
            return self.record_failure(action_id, f'{target_type} does not exist')

        if not self.structures(UnitTypeId.NEXUS).exists:
            return self.record_failure(action_id, 'Nexus does not exist')

        target = self.structures(target_type).random

        # 检查目标建筑是否空闲或已经被加速
        if target.is_idle or target.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
            return self.record_failure(action_id, f'{description} is idle or already chronoboosted')

        # 检查供应情况
        if self.supply_left < supply_requirement:
            return self.record_failure(action_id, f'Not enough supply for {description}')

        # 尝试应用星空加速
        nexuses = self.structures(UnitTypeId.NEXUS)
        abilities = await self.get_available_abilities(nexuses)
        for loop_nexus, abilities_nexus in zip(nexuses, abilities):
            if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities_nexus:
                loop_nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, target)
                print(f'Chronoboost applied to {description}')

        return self.record_failure(action_id, f'No available Nexus to chronoboost {description}')

    async def warp_unit(self, action_id: int, unit_type: UnitTypeId, initial_reference_point: Point2,
                        required_buildings: List[UnitTypeId] = None,
                        max_attempts=5) -> None:
        """
        尝试在参考点附近折跃指定的单位。
        :param action_id: 动作的ID，用于记录失败原因。
        :param unit_type: 想要折跃的单位类型。
        :param initial_reference_point: 参考点，通常是最接近敌方基地的水晶塔。
        :param max_attempts: 尝试折跃的最大次数。
        :param required_buildings: 需要的科技建筑列表。
        """

        # 如果需要额外的科技建筑，则进行检查
        if required_buildings:
            for building in required_buildings:
                if not self.structures(building).exists:
                    return self.record_failure(action_id, f'{building.name} not available')

        # 检查是否是允许折跃的单位类型
        if unit_type not in {UnitTypeId.ZEALOT, UnitTypeId.STALKER, UnitTypeId.DARKTEMPLAR}:
            return self.record_failure(action_id, f"Unit type {unit_type.name} not warpable")

        # 检查是否有Warp Gate存在
        if not self.structures(UnitTypeId.WARPGATE).exists:
            return self.record_failure(action_id, 'No Warp Gate available')

        # 选择一个空闲的Warp Gate
        idle_warpgates = self.structures(UnitTypeId.WARPGATE).ready.idle
        if not idle_warpgates:
            return self.record_failure(action_id, 'No idle Warp Gate available')
        warpgate = idle_warpgates.first
        warp_ability = getattr(AbilityId, f"WARPGATETRAIN_{unit_type.name}")

        # 获取Warp Gate的可用能力
        abilities = await self.get_available_abilities(warpgate)

        # 检查是否可以从Warp Gate中折跃指定的单位
        if warp_ability not in abilities:
            return self.record_failure(action_id, f'Cannot train {unit_type.name} from Warp Gate')
        elif not self.can_afford(unit_type):
            return self.record_failure(action_id, f'Cannot afford {unit_type.name}')
        elif self.supply_left < self.calculate_supply_cost(unit_type):
            return self.record_failure(action_id, 'Not enough supply left')

        # 查找最接近参考点的有能量的水晶塔
        pylons = [p for p in self.structures(UnitTypeId.PYLON) if p.is_ready]
        pylons.sort(key=lambda p: p.distance_to(initial_reference_point))
        if not pylons:
            return self.record_failure(action_id, 'No powered pylons available')
        pylon = pylons[0]

        # 尝试在水晶塔附近找到一个合适的位置进行折跃
        for distance in range(1, 6):
            pos = pylon.position.random_on_distance(distance)
            placement = await self.find_placement(warp_ability, pos, placement_step=1)
            if placement and placement.distance_to(pylon.position) <= 5:
                warpgate.warp_in(unit_type, placement)
                print(f'Warped in {unit_type.name}')

        # 如果所有尝试都失败，记录失败原因
        return self.record_failure(action_id, f"Couldn't find a placement near pylon for {unit_type.name}")

    async def train_from_gateway(self, action_id: int, unit_type: UnitTypeId,
                                 required_buildings: List[UnitTypeId] = None):
        """
        从传送门训练指定的单位。

        :param action_id: 动作ID，用于记录失败原因。
        :param unit_type: 想要训练的单位类型。
        :param required_buildings: 训练该单位所需的额外建筑列表。
        :return: 如果成功返回True，否则返回False。
        """
        print(f'action={action_id}')

        # 检查是否存在传送门
        if not self.structures(UnitTypeId.GATEWAY).exists:
            return self.record_failure(action_id, 'No Gateway available')

        # 使用calculate_supply_cost函数获取单位所需的供给
        required_supply = self.calculate_supply_cost(unit_type)
        # 检查是否有足够的供给空间
        if self.supply_left < required_supply:
            return self.record_failure(action_id, 'Not enough supply left')

        # 如果需要额外的科技建筑，则进行检查
        if required_buildings:
            for building in required_buildings:
                if not self.structures(building).exists:
                    return self.record_failure(action_id, f'{building.name} not available')

        # 选择空闲的传送门进行单位训练
        idle_gates = [gate for gate in self.structures(UnitTypeId.GATEWAY) if gate.is_idle]
        if not idle_gates:
            # 如果没有空闲的Gateway，选择一个即将完成任务的Gateway
            gates_sorted_by_build_progress = sorted(self.structures(UnitTypeId.GATEWAY), key=lambda g: g.build_progress,
                                                    reverse=True)
            gate = gates_sorted_by_build_progress[0]
        else:
            gate = idle_gates[0]

        # 检查是否有足够的资源
        if not self.can_afford(unit_type):
            return self.record_failure(action_id, f'Cannot afford {unit_type.name}')

        # 训练单位
        gate.train(unit_type)
        print(f'训练{unit_type.name}')
        return True

    async def train_from_robotics(self, action_id: int, unit_type: UnitTypeId,
                                  required_buildings: List[UnitTypeId] = None,
                                  unit_limit: int = None) -> None:
        """
        从Robotics Facility训练指定的单位，但一次只训练一个单位。
        """

        # 如果需要额外的科技建筑，则进行检查
        if required_buildings:
            for building in required_buildings:
                if not self.structures(building).exists:
                    return self.record_failure(action_id, f'{building.name} not available')

        # 检查Robotics Facility是否存在且是否空闲
        robotics_facilities = self.structures(UnitTypeId.ROBOTICSFACILITY)
        if robotics_facilities.empty:
            return self.record_failure(action_id, 'No Robotics Facility available')

        # 检查是否有正在生产的单位
        if robotics_facilities.filter(lambda facility: facility.is_idle).empty:
            # 如果所有的 Robotics Facility 都在忙，那么不进行新的生产任务。
            print('Robotics Facility is busy')
            return  # 不记录失败，因为这是正常的生产状态

        # 如果存在单位限制，则检查是否已经达到
        if unit_limit is not None and (self.units(unit_type).amount + self.already_pending(unit_type)) >= unit_limit:
            return self.record_failure(action_id, f'{unit_type.name} limit reached')

        # 检查资源和供应是否充足
        if self.supply_left < self.calculate_supply_cost(unit_type):
            return self.record_failure(action_id, 'Not enough supply left')
        if not self.can_afford(unit_type):
            return self.record_failure(action_id, f'Cannot afford {unit_type.name}')

        # 找到一个空闲的Robotics Facility并开始训练
        idle_facility = robotics_facilities.idle.first
        if idle_facility:
            idle_facility.train(unit_type)
            print(f'训练{unit_type.name}')
            return  # 生产任务已经开始，所以正常返回

        # 在一些极端情况下，如果没有找到空闲的设施，记录失败
        return self.record_failure(action_id, 'No idle Robotics Facility available')

    async def train_from_stargate(self, action_id: int, unit_type: UnitTypeId,
                                  required_buildings: List[UnitTypeId] = None,
                                  unit_limit: int = None) -> None:
        """
        从Stargate训练指定的单位，但一次只训练一个单位。
        """

        # 如果需要额外的科技建筑，则进行检查
        if required_buildings:
            for building in required_buildings:
                if not self.structures(building).exists:
                    return self.record_failure(action_id, f'{building.name} not available')

        # 检查Stargate是否存在且是否空闲
        stargates = self.structures(UnitTypeId.STARGATE)
        if stargates.empty:
            return self.record_failure(action_id, 'No Stargate available')

        # 检查是否有正在生产的单位
        if stargates.filter(lambda facility: facility.is_idle).empty:
            # 如果所有的 Stargate 都在忙，那么不进行新的生产任务。
            print('Stargate is busy')
            return  # 不记录失败，因为这是正常的生产状态

        # 如果存在单位限制，则检查是否已经达到
        if unit_limit is not None and (self.units(unit_type).amount + self.already_pending(unit_type)) >= unit_limit:
            return self.record_failure(action_id, f'{unit_type.name} limit reached')

        # 检查资源和供应是否充足
        if self.supply_left < self.calculate_supply_cost(unit_type):
            return self.record_failure(action_id, 'Not enough supply left')
        if not self.can_afford(unit_type):
            return self.record_failure(action_id, f'Cannot afford {unit_type.name}')

        # 找到一个空闲的Stargate并开始训练
        idle_stargate = stargates.idle.first
        if idle_stargate:
            idle_stargate.train(unit_type)
            print(f'训练{unit_type.name}')
            return  # 生产任务已经开始，所以正常返回

        # 在一些极端情况下，如果没有找到空闲的设施，记录失败
        return self.record_failure(action_id, 'No idle Stargate available')

    async def handle_action_attack(self, action_id, iteration):
        print(f'action={action_id}')
        await self.attack()

    async def handle_action_0(self):
        action_id = 0
        print(f'action={action_id}')

        if not self.structures(UnitTypeId.NEXUS).exists:
            return self.record_failure(action_id, 'No Nexus available')

        for nexus in self.townhalls:
            if self.workers.amount + self.already_pending(UnitTypeId.PROBE) > 75:
                return self.record_failure(action_id, 'Too many probes (more than 75)')
            if self.supply_left <= 0:
                return self.record_failure(action_id, 'No supply left')
            if not self.can_afford(UnitTypeId.PROBE):
                return self.record_failure(action_id, 'Cannot afford Probe')
            if nexus.is_idle:
                nexus.train(UnitTypeId.PROBE)
                print('训练探机')
                return

        return self.record_failure(action_id, 'All Nexus are busy')

    async def handle_action_1(self):
        action_id = 1
        print(f'action={action_id}')

        success = await self.produce_bg_unit(action_id, UnitTypeId.ZEALOT)
        if success:
            print('训练zealot')

    async def handle_action_2(self):
        action_id = 2
        print(f'action={action_id}')

        # 列出训练Adept所需的建筑
        required_buildings = [UnitTypeId.CYBERNETICSCORE]

        success = await self.produce_bg_unit(action_id, UnitTypeId.ADEPT, required_buildings)
        if success:
            print('训练使徒')

    async def handle_action_3(self):
        action_id = 3
        print(f'action={action_id}')

        # 列出训练Stalker所需的建筑
        required_buildings = [UnitTypeId.CYBERNETICSCORE]

        success = await self.produce_bg_unit(action_id, UnitTypeId.STALKER, required_buildings)
        if success:
            print('训练追猎者')

    async def handle_action_4(self):
        action_id = 4
        print(f'action={action_id}')

        # 列出训练Sentry所需的建筑
        required_buildings = [UnitTypeId.CYBERNETICSCORE]

        success = await self.produce_bg_unit(action_id, UnitTypeId.SENTRY, required_buildings)
        if success:
            print('训练机械哨兵')

    async def handle_action_5(self):
        action_id = 5
        print(f'action={action_id}')

        # 列出训练High Templar所需的建筑
        required_buildings = [UnitTypeId.TEMPLARARCHIVE]

        success = await self.produce_bg_unit(action_id, UnitTypeId.HIGHTEMPLAR, required_buildings)
        if success:
            print('训练高阶圣堂武士')

    async def handle_action_6(self):
        action_id = 6
        print(f'action={action_id}')

        # 列出训练Dark Templar所需的建筑
        required_buildings = [UnitTypeId.DARKSHRINE]

        success = await self.produce_bg_unit(action_id, UnitTypeId.DARKTEMPLAR, required_buildings)
        if success:
            print('训练黑暗圣堂武士')

    async def handle_action_7(self):
        action_id = 7
        print(f'action={action_id}')
        await self.train_from_stargate(action_id, UnitTypeId.VOIDRAY)

    async def handle_action_8(self):
        action_id = 8
        print(f'action={action_id}')
        await self.train_from_stargate(action_id, UnitTypeId.CARRIER)

    async def handle_action_9(self):
        action_id = 9
        print(f'action={action_id}')
        await self.train_from_stargate(action_id, UnitTypeId.TEMPEST)

    async def handle_action_10(self):
        action_id = 10
        print(f'action={action_id}')
        await self.train_from_stargate(action_id, UnitTypeId.ORACLE, unit_limit=1)

    async def handle_action_11(self):
        action_id = 11
        print(f'action={action_id}')
        await self.train_from_stargate(action_id, UnitTypeId.PHOENIX, unit_limit=4)

    async def handle_action_12(self):
        action_id = 12
        print(f'action={action_id}')

        if not self.structures(UnitTypeId.NEXUS).exists:
            return self.record_failure(action_id, 'No Nexus available')

        if not self.structures(UnitTypeId.STARGATE).exists:
            return self.record_failure(action_id, 'No Stargate available')

        if not self.structures(UnitTypeId.FLEETBEACON).exists:
            return self.record_failure(action_id, 'Fleet Beacon not available')

        if self.supply_left < 10:
            return self.record_failure(action_id, 'Not enough supply left')

        nexuses = self.structures(UnitTypeId.NEXUS)
        abilities = await self.get_available_abilities(nexuses)

        if AbilityId.NEXUSTRAINMOTHERSHIP_MOTHERSHIP not in abilities:
            return self.record_failure(action_id, 'Cannot train Mothership')

        if not self.can_afford(UnitTypeId.MOTHERSHIP):
            return self.record_failure(action_id, 'Cannot afford Mothership')

        for base in self.townhalls:
            if base.is_idle:
                base.train(UnitTypeId.MOTHERSHIP)
                reward = 0.010
                print('训练母舰')
                return reward

        return self.record_failure(action_id, 'No idle Nexus available')

    async def handle_action_13(self):
        action_id = 13
        print(f'action={action_id}')
        await self.train_from_robotics(action_id, UnitTypeId.OBSERVER, unit_limit=2)
        print('训练侦察者')
        return

    async def handle_action_14(self):
        action_id = 14
        print(f'action={action_id}')

        await self.train_from_robotics(action_id, UnitTypeId.IMMORTAL)
        print('训练不朽者')
        return

    async def handle_action_15(self):
        action_id = 15
        print(f'action={action_id}')
        await self.train_from_robotics(action_id, UnitTypeId.WARPPRISM, unit_limit=1)
        print('训练折跃棱镜')
        return

    async def handle_action_16(self):
        action_id = 16
        print(f'action={action_id}')
        required_buildings = [UnitTypeId.ROBOTICSBAY]
        await self.train_from_robotics(action_id, UnitTypeId.COLOSSUS, required_buildings=required_buildings)
        print('训练巨像')
        return

    async def handle_action_17(self):
        action_id = 17
        print(f'action={action_id}')
        required_buildings = [UnitTypeId.DISRUPTOR]
        await self.train_from_robotics(action_id, UnitTypeId.DISRUPTOR, required_buildings=required_buildings,
                                       unit_limit=1)
        print('训练干扰者')
        return

    async def handle_action_18(self):
        action_id = 18
        print(f'action={action_id}')

        if self.units(UnitTypeId.HIGHTEMPLAR).exists:
            hts = self.units(UnitTypeId.HIGHTEMPLAR)
            for ht in hts:
                ht(AbilityId.MORPH_ARCHON)
            return 0.005

        elif self.units(UnitTypeId.DARKTEMPLAR).exists:
            dts = self.units(UnitTypeId.DARKTEMPLAR)
            for dt in dts:
                dt(AbilityId.MORPH_ARCHON)
            print('合成执政官')
            return 0.005

        return self.record_failure(action_id, 'No High Templar or Dark Templar available for Archon morph')

    async def handle_action_19(self):
        action_id = 19
        print(f'action={action_id}')

        # 如果没有 Nexus 或 Probe，不进行下一步
        if not (self.structures(UnitTypeId.NEXUS).exists and self.units(UnitTypeId.PROBE).exists):
            return self.record_failure(action_id, 'No Nexus or Probe available')

        # 根据当前时间设置供应量阈值和已挂起的Pylon数量
        supply_left_threshold, pending_pylon_threshold = 3, 2
        current_time = self.time_formatted

        if '06:00' <= current_time <= '07:00':
            supply_left_threshold, pending_pylon_threshold = 5, 4
        elif '06:00' <= current_time <= '08:00':
            supply_left_threshold, pending_pylon_threshold = 5, 3
        elif '08:00' <= current_time <= '10:00':
            supply_left_threshold, pending_pylon_threshold = 7, 4
        elif '10:00' <= current_time:
            supply_left_threshold, pending_pylon_threshold = 7, 4

        # 如果满足建造Pylon的条件，则执行建造
        if (
                self.supply_left <= supply_left_threshold and
                self.already_pending(UnitTypeId.PYLON) <= pending_pylon_threshold and
                not self.supply_cap == 200  # 确保供应上限不是200
        ):
            if not self.can_afford(UnitTypeId.PYLON):
                return self.record_failure(action_id, 'Cannot afford Pylon')

            # 找到最佳的基地和位置来建造Pylon
            best_base = self.find_best_base_for_pylon()
            best_position = self.find_optimal_pylon_position_for_base(best_base)

            # 尝试建造Pylon
            construction_result = await self.build(UnitTypeId.PYLON, near=best_position, placement_step=2)
            if not construction_result:  # 如果建造失败
                return self.record_failure(action_id, 'Could not build Pylon for unknown reasons')

        else:
            # 如果不满足建造条件
            return self.record_failure(action_id, 'Not the right conditions to build a Pylon')

    async def handle_action_20(self):
        action_id = 20
        print(f'action={action_id}')

        if not self.structures(UnitTypeId.NEXUS).exists:
            return self.record_failure(action_id, 'No Nexus available')
        if not self.units(UnitTypeId.PROBE).exists:
            return self.record_failure(action_id, 'No Probe available')
        if not self.can_afford(UnitTypeId.ASSIMILATOR):
            return self.record_failure(action_id, 'Cannot afford Assimilator')
        if not self.vespene_geyser.exists:
            return self.record_failure(action_id, 'No Vespene Geyser available')
        if not self.structures(UnitTypeId.PYLON).exists:
            return self.record_failure(action_id, 'No Pylon available')

        # 获取正在建造中的气矿数量
        building_assimilators_num = self.already_pending(UnitTypeId.ASSIMILATOR)

        # 如果正在建造的气矿数量少于2个，我们可以尝试建造新的气矿
        if building_assimilators_num < 2:
            for nexus in self.townhalls:
                for vespene in self.vespene_geyser.closer_than(10, nexus):
                    # 检查气矿周围是否已有工人正在前往建造
                    moving_workers = [worker for worker in self.workers.closer_than(5, vespene) if worker.is_moving]
                    if moving_workers:
                        continue  # 如果已有工人在移动去建造，我们跳过这个气矿

                    # 如果附近没有其他Assimilator，则尝试在这个气矿上建造一个新的Assimilator
                    if self.can_afford(UnitTypeId.ASSIMILATOR) and not self.structures(
                            UnitTypeId.ASSIMILATOR).closer_than(2, vespene):
                        await self.build(UnitTypeId.ASSIMILATOR, vespene)
                        print('建设气矿')
                        return  # 在开始建造后立即退出函数，确保一次只建造一个Assimilator
        else:
            print('Already building 2 Assimilators, waiting...')  # 如果已经有2个在建造中，则等待


    async def handle_action_21(self):
        action_id = 21
        print(f'action={action_id}')

        if not self.units(UnitTypeId.PROBE).exists:
            return self.record_failure(action_id, 'No Probe available')
        if not self.can_afford(UnitTypeId.NEXUS):
            return self.record_failure(action_id, 'Cannot afford Nexus')
        if self.can_afford(UnitTypeId.NEXUS) and self.already_pending(UnitTypeId.NEXUS) <= 1 and self.structures(
                UnitTypeId.NEXUS).amount <= 8:
            await self.expand_now()
            print('扩建基地')

    async def handle_action_22(self):
        action_id = 22
        print(f'action={action_id}')
        building_limits = {
            '00:00-03:00': 1,  # 从游戏开始到5分钟内，只能有一个Robotics Facility
            '03:00-05:00': 3,  # 从5分钟到10分钟内，只能有两个Robotics Facility
            '05:00-07:00': 6,  # 从10分钟到15分钟内，只能有三个Robotics Facility
            '07:00-10:00': 8,  # 从15分钟到20分钟内，只能有四个Robotics Facility
        }
        if not self.structures(UnitTypeId.PYLON).exists:
            return self.record_failure(action_id, 'No Pylon available')
        if not self.structures(UnitTypeId.NEXUS).exists:
            return self.record_failure(action_id, 'No Nexus available')
        if not self.units(UnitTypeId.PROBE).exists:
            return self.record_failure(action_id, 'No Probe available')
        if not self.can_afford(UnitTypeId.GATEWAY):
            return self.record_failure(action_id, 'Cannot afford Gateway')
        await self.handle_action_build_building(UnitTypeId.GATEWAY,building_limits=building_limits)
        print('建设BG')

    async def handle_action_23(self):
        action_id = 23
        print(f'action={action_id}')
        building_limits = {
            '00:00-05:00': 1,
            '05:00-20:00': 2,
        }
        if not self.structures(UnitTypeId.PYLON).exists:
            return self.record_failure(action_id, 'No Pylon available')
        if not self.structures(UnitTypeId.NEXUS).exists:
            return self.record_failure(action_id, 'No Nexus available')
        if not self.units(UnitTypeId.PROBE).exists:
            return self.record_failure(action_id, 'No Probe available')
        if not self.structures(UnitTypeId.GATEWAY).exists:
            return self.record_failure(action_id, 'No Gateway available')
        if not self.can_afford(UnitTypeId.CYBERNETICSCORE):
            return self.record_failure(action_id, 'Cannot afford Cybernetics Core')
        await self.handle_action_build_building(UnitTypeId.CYBERNETICSCORE,building_limits=building_limits)
        print('建设BY')

    async def handle_action_24(self):
        action_id = 24
        print(f'action={action_id}')
        building_limits = {
            '00:00-05:00': 1,
            '05:00-10:00': 2,
        }
        if not self.structures(UnitTypeId.PYLON).exists:
            return self.record_failure(action_id, 'No Pylon available')
        if not self.structures(UnitTypeId.NEXUS).exists:
            return self.record_failure(action_id, 'No Nexus available')
        if not self.units(UnitTypeId.PROBE).exists:
            return self.record_failure(action_id, 'No Probe available')
        if not self.can_afford(UnitTypeId.FORGE):
            return self.record_failure(action_id, 'Cannot afford Forge')
        await self.handle_action_build_building(UnitTypeId.FORGE,building_limits=building_limits)
        print('建设BF')

    async def handle_action_25(self):
        action_id = 25
        print(f'action={action_id}')

        if not self.structures(UnitTypeId.PYLON).exists:
            return self.record_failure(action_id, 'No Pylon available')
        if not self.structures(UnitTypeId.NEXUS).exists:
            return self.record_failure(action_id, 'No Nexus available')
        if not self.units(UnitTypeId.PROBE).exists:
            return self.record_failure(action_id, 'No Probe available')
        if not self.structures(UnitTypeId.CYBERNETICSCORE).exists:
            return self.record_failure(action_id, 'No Cybernetics Core available')
        if not self.can_afford(UnitTypeId.TWILIGHTCOUNCIL):
            return self.record_failure(action_id, 'Cannot afford Twilight Council')
        await self.handle_action_build_building(UnitTypeId.TWILIGHTCOUNCIL)
        print('建设VC')

    async def handle_action_26(self):
        action_id = 26
        print(f'action={action_id}')
        building_limits = {
            '00:00-05:00': 1,  # 从游戏开始到5分钟内，只能有一个Robotics Facility
            '05:00-10:00': 2,  # 从5分钟到10分钟内，只能有两个Robotics Facility
            '10:00-15:00': 3,  # 从10分钟到15分钟内，只能有三个Robotics Facility
        }
        if not self.structures(UnitTypeId.PYLON).exists:
            return self.record_failure(action_id, 'No Pylon available')
        if not self.structures(UnitTypeId.NEXUS).exists:
            return self.record_failure(action_id, 'No Nexus available')
        if not self.units(UnitTypeId.PROBE).exists:
            return self.record_failure(action_id, 'No Probe available')
        if not self.structures(UnitTypeId.CYBERNETICSCORE).exists:
            return self.record_failure(action_id, 'No Cybernetics Core available')
        if not self.can_afford(UnitTypeId.ROBOTICSFACILITY):
            return self.record_failure(action_id, 'Cannot afford Robotics Facility')
        await self.handle_action_build_building(UnitTypeId.ROBOTICSFACILITY, building_limits=building_limits)
        print('建设VR')

    async def handle_action_27(self):
        action_id = 27
        print(f'action={action_id}')
        buildind_limits = {
            '00:00-05:00': 1,  # 从游戏开始到5分钟内，只能有一个Stargate
            '05:00-10:00': 3,  # 从5分钟到10分钟内，只能有两个Stargate
            '10:00-15:00': 4,  # 从10分钟到15分钟内，只能有三个Stargate
        }
        if not self.structures(UnitTypeId.PYLON).exists:
            return self.record_failure(action_id, 'No Pylon available')
        if not self.structures(UnitTypeId.NEXUS).exists:
            return self.record_failure(action_id, 'No Nexus available')
        if not self.units(UnitTypeId.PROBE).exists:
            return self.record_failure(action_id, 'No Probe available')
        if not self.structures(UnitTypeId.CYBERNETICSCORE).exists:
            return self.record_failure(action_id, 'No Cybernetics Core available')
        if not self.can_afford(UnitTypeId.STARGATE):
            return self.record_failure(action_id, 'Cannot afford Stargate')
        await self.handle_action_build_building(UnitTypeId.STARGATE, building_limits=buildind_limits)
        print('建设VS')

    async def handle_action_28(self):
        action_id = 28
        print(f'action={action_id}')

        if not self.structures(UnitTypeId.PYLON).exists:
            return self.record_failure(action_id, 'No Pylon available')
        if not self.structures(UnitTypeId.NEXUS).exists:
            return self.record_failure(action_id, 'No Nexus available')
        if not self.units(UnitTypeId.PROBE).exists:
            return self.record_failure(action_id, 'No Probe available')
        if not self.structures(UnitTypeId.CYBERNETICSCORE).exists:
            return self.record_failure(action_id, 'No Cybernetics Core available')
        if not self.structures(UnitTypeId.TWILIGHTCOUNCIL).exists:
            return self.record_failure(action_id, 'No Twilight Council available')
        if not self.can_afford(UnitTypeId.TEMPLARARCHIVE):
            return self.record_failure(action_id, 'Cannot afford Templar Archive')
        await self.handle_action_build_building(UnitTypeId.TEMPLARARCHIVE)
        print('建设VT')

    async def handle_action_29(self):
        action_id = 29
        print(f'action={action_id}')
        if not self.structures(UnitTypeId.PYLON).exists:
            return self.record_failure(action_id, 'No Pylon available')
        if not self.structures(UnitTypeId.NEXUS).exists:
            return self.record_failure(action_id, 'No Nexus available')
        if not self.units(UnitTypeId.PROBE).exists:
            return self.record_failure(action_id, 'No Probe available')
        if not self.structures(UnitTypeId.CYBERNETICSCORE).exists:
            return self.record_failure(action_id, 'No Cybernetics Core available')
        if not self.structures(UnitTypeId.TWILIGHTCOUNCIL).exists:
            return self.record_failure(action_id, 'No Twilight Council available')
        if not self.can_afford(UnitTypeId.DARKSHRINE):
            return self.record_failure(action_id, 'Cannot afford Dark Shrine')
        await self.handle_action_build_building(UnitTypeId.DARKSHRINE)

        print('建设VD')

    async def handle_action_30(self):
        action_id = 30
        print(f'action={action_id}')

        if not self.structures(UnitTypeId.PYLON).exists:
            return self.record_failure(action_id, 'No Pylon available')
        if not self.structures(UnitTypeId.NEXUS).exists:
            return self.record_failure(action_id, 'No Nexus available')
        if not self.units(UnitTypeId.PROBE).exists:
            return self.record_failure(action_id, 'No Probe available')
        if not self.structures(UnitTypeId.CYBERNETICSCORE).exists:
            return self.record_failure(action_id, 'No Cybernetics Core available')
        if not self.structures(UnitTypeId.ROBOTICSFACILITY).exists:
            return self.record_failure(action_id, 'No Robotics Facility available')
        if not self.can_afford(UnitTypeId.ROBOTICSBAY):
            return self.record_failure(action_id, 'Cannot afford Robotics Bay')
        await self.handle_action_build_building(UnitTypeId.ROBOTICSBAY)
        print('建设VB')

    async def handle_action_31(self):
        action_id = 31
        print(f'action={action_id}')
        if not self.structures(UnitTypeId.PYLON).exists:
            return self.record_failure(action_id, 'No Pylon available')
        if not self.structures(UnitTypeId.NEXUS).exists:
            return self.record_failure(action_id, 'No Nexus available')
        if not self.units(UnitTypeId.PROBE).exists:
            return self.record_failure(action_id, 'No Probe available')
        if not self.structures(UnitTypeId.CYBERNETICSCORE).exists:
            return self.record_failure(action_id, 'No Cybernetics Core available')
        if not self.structures(UnitTypeId.STARGATE).exists:
            return self.record_failure(action_id, 'No Stargate available')
        if not self.can_afford(UnitTypeId.FLEETBEACON):
            return self.record_failure(action_id, 'Cannot afford Fleet Beacon')
        await self.handle_action_build_building(UnitTypeId.FLEETBEACON)
        print('建设VF')

    async def handle_action_32(self):
        action_id = 32
        print(f'action={action_id}')
        building_limits = {
            '00:00-05:00': 1,  # 从游戏开始到5分钟内，只能有一个Photon Cannon
            '05:00-10:00': 3,  # 从5分钟到10分钟内，只能有两个Photon Cannon
            '10:00-15:00': 5,  # 从10分钟到15分钟内，只能有三个Photon Cannon
            '15:00-20:00': 7,  # 从15分钟到20分钟内，只能有四个Photon Cannon
        }
        if not self.structures(UnitTypeId.PYLON).exists:
            return self.record_failure(action_id, 'No Pylon available')
        if not self.structures(UnitTypeId.NEXUS).exists:
            return self.record_failure(action_id, 'No Nexus available')
        if not self.units(UnitTypeId.PROBE).exists:
            return self.record_failure(action_id, 'No Probe available')
        if not self.structures(UnitTypeId.CYBERNETICSCORE).exists:
            return self.record_failure(action_id, 'No Cybernetics Core available')
        if not self.structures(UnitTypeId.FORGE).exists:
            return self.record_failure(action_id, 'No Forge')
        if self.structures(UnitTypeId.PHOTONCANNON).amount + self.already_pending(UnitTypeId.PHOTONCANNON) > 3:
            return self.record_failure(action_id, 'Photon Cannon limit reached')
        if not self.can_afford(UnitTypeId.PHOTONCANNON):
            return self.record_failure(action_id, 'Cannot afford  Photon Cannon')
        await self.handle_action_build_building(UnitTypeId.PHOTONCANNON, building_limits=building_limits)
        print('建设BC')

    async def handle_action_33(self):
        action_id = 33
        print(f'action={action_id}')
        building_limits = {
            '00:00-05:00': 1,  #
            '05:00-10:00': 3,  #
            '10:00-15:00': 5,  #
            '15:00-20:00': 7,  #
        }
        if not self.structures(UnitTypeId.PYLON).exists:
            return self.record_failure(action_id, 'No Pylon available')
        if not self.structures(UnitTypeId.NEXUS).exists:
            return self.record_failure(action_id, 'No Nexus available')
        if not self.units(UnitTypeId.PROBE).exists:
            return self.record_failure(action_id, 'No Probe available')
        if not self.structures(UnitTypeId.CYBERNETICSCORE).exists:
            return self.record_failure(action_id, 'No Cybernetics Core available')
        if not self.structures(UnitTypeId.FORGE).exists:
            return self.record_failure(action_id, 'No Forge')
        if self.structures(UnitTypeId.SHIELDBATTERY).amount + self.already_pending(UnitTypeId.SHIELDBATTERY) > 3:
            return self.record_failure(action_id, 'Shield Battery limit reached')
        if not self.can_afford(UnitTypeId.SHIELDBATTERY):
            return self.record_failure(action_id, 'Cannot afford Shield Battery')
        await self.handle_action_build_building(UnitTypeId.SHIELDBATTERY, building_limits=building_limits)
        print('建设BB')

    async def handle_action_34(self):
        action_id = 34
        print(f'action={action_id}')

        if not self.structures(UnitTypeId.PYLON).exists:
            return self.record_failure(action_id, 'Pylon does not exist')

        if not self.structures(UnitTypeId.NEXUS).exists:
            return self.record_failure(action_id, 'Nexus does not exist')

        if not self.structures(UnitTypeId.CYBERNETICSCORE).exists:
            return self.record_failure(action_id, 'Cybernetics Core does not exist')

        by = self.structures(UnitTypeId.CYBERNETICSCORE).random
        abilities = await self.get_available_abilities(by)
        if self.structures(UnitTypeId.CYBERNETICSCORE).ready and self.already_pending(UpgradeId.WARPGATERESEARCH) == 0:
            if self.can_afford(UpgradeId.WARPGATERESEARCH) and by.is_idle and AbilityId.RESEARCH_WARPGATE in abilities:
                by.research(UpgradeId.WARPGATERESEARCH)
                print('研究折跃门')
                return 0.010

        return self.record_failure(action_id, 'Cannot afford Warp Gate research or Cybernetics Core is not idle')

    async def handle_action_35(self):
        upgrade_id = UpgradeId.PROTOSSAIRWEAPONSLEVEL1
        ability_id = AbilityId.CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL1
        description = '研究空军1攻'
        return await self.research_upgrade(35, upgrade_id, ability_id, description)

    async def handle_action_36(self):
        upgrade_id = UpgradeId.PROTOSSAIRWEAPONSLEVEL2
        ability_id = AbilityId.CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL2
        description = '研究空军2攻'
        return await self.research_upgrade(36, upgrade_id, ability_id, description)

    async def handle_action_37(self):
        upgrade_id = UpgradeId.PROTOSSAIRWEAPONSLEVEL3
        ability_id = AbilityId.CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL3
        description = '研究空军3攻'
        return await self.research_upgrade(37, upgrade_id, ability_id, description)

    async def handle_action_38(self):
        upgrade_id = UpgradeId.PROTOSSAIRARMORSLEVEL1
        ability_id = AbilityId.CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL1
        description = '研究空军1防'
        return await self.research_upgrade(38, upgrade_id, ability_id, description)

    async def handle_action_39(self):
        upgrade_id = UpgradeId.PROTOSSAIRARMORSLEVEL2
        ability_id = AbilityId.CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL2
        description = '研究空军2防'
        return await self.research_upgrade(39, upgrade_id, ability_id, description)

    async def handle_action_40(self):
        upgrade_id = UpgradeId.PROTOSSAIRARMORSLEVEL3
        ability_id = AbilityId.CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL3
        description = '研究空军3防'
        return await self.research_upgrade(40, upgrade_id, ability_id, description)

    async def handle_action_41(self):
        upgrade_id = UpgradeId.ADEPTPIERCINGATTACK
        ability_id = AbilityId.RESEARCH_ADEPTRESONATINGGLAIVES
        description = '研究使徒攻速'
        return await self.research_twilight_upgrade(41, upgrade_id, ability_id, description)

    async def handle_action_42(self):
        upgrade_id = UpgradeId.BLINKTECH
        ability_id = AbilityId.RESEARCH_BLINK
        description = '研究闪烁追猎'
        return await self.research_twilight_upgrade(42, upgrade_id, ability_id, description)

    async def handle_action_43(self):
        upgrade_id = UpgradeId.CHARGE
        ability_id = AbilityId.RESEARCH_CHARGE
        description = '研究冲锋狂热者'
        return await self.research_twilight_upgrade(43, upgrade_id, ability_id, description)

    async def handle_action_44(self):
        return await self.research_forge_upgrade(44, UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1,
                                                 AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1, '研究地面1攻')

    async def handle_action_45(self):
        return await self.research_forge_upgrade(45, UpgradeId.PROTOSSGROUNDWEAPONSLEVEL2,
                                                 AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2, '研究地面2攻')

    async def handle_action_46(self):
        return await self.research_forge_upgrade(46, UpgradeId.PROTOSSGROUNDWEAPONSLEVEL3,
                                                 AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3, '研究地面3攻')

    async def handle_action_47(self):
        return await self.research_forge_upgrade(47, UpgradeId.PROTOSSGROUNDARMORSLEVEL1,
                                                 AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1, '研究地面1防')

    async def handle_action_48(self):
        return await self.research_forge_upgrade(48, UpgradeId.PROTOSSGROUNDWEAPONSLEVEL2,
                                                 AbilityId.FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2, '研究地面2防')

    async def handle_action_49(self):
        return await self.research_forge_upgrade(49, UpgradeId.PROTOSSGROUNDARMORSLEVEL3,
                                                 AbilityId.FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3, '研究地面3防')

    async def handle_action_50(self):
        return await self.research_forge_upgrade(50, UpgradeId.PROTOSSSHIELDSLEVEL1,
                                                 AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL1, '研究1盾')

    async def handle_action_51(self):
        return await self.research_forge_upgrade(51, UpgradeId.PROTOSSSHIELDSLEVEL2,
                                                 AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL2, '研究2盾')

    async def handle_action_52(self):
        return await self.research_forge_upgrade(52, UpgradeId.PROTOSSSHIELDSLEVEL3,
                                                 AbilityId.FORGERESEARCH_PROTOSSSHIELDSLEVEL3, '研究3盾')

    async def handle_action_53(self):
        return await self.research_roboticsbay_upgrade(53, UpgradeId.EXTENDEDTHERMALLANCE,
                                                       AbilityId.RESEARCH_EXTENDEDTHERMALLANCE, '研究巨像射程')

    async def handle_action_54(self):
        return await self.research_roboticsbay_upgrade(54, UpgradeId.GRAVITICDRIVE, AbilityId.RESEARCH_GRAVITICDRIVE,
                                                       '研究棱镜速度')

    async def handle_action_55(self):
        return await self.research_roboticsbay_upgrade(55, UpgradeId.OBSERVERGRAVITICBOOSTER,
                                                       AbilityId.RESEARCH_GRAVITICBOOSTER, '研究OB速度')

    async def handle_action_56(self):
        action_id = 56
        print(f'action={action_id}')
        # 前置条件检查
        if not self.structures(UnitTypeId.PYLON).exists:
            return self.record_failure(action_id, 'Pylon does not exist')

        if not self.units(UnitTypeId.PROBE).exists:
            return self.record_failure(action_id, 'Probe does not exist')

        if not self.structures(UnitTypeId.NEXUS).exists:
            return self.record_failure(action_id, 'Nexus does not exist')

        if not self.structures(UnitTypeId.TEMPLARARCHIVE).exists:
            return self.record_failure(action_id, 'Templar archive does not exist')

        # 获取随机的TEMPLARARCHIVE实例
        vt = self.structures(UnitTypeId.TEMPLARARCHIVE).random
        abilities = await self.get_available_abilities(vt)
        upgrade_id = UpgradeId.PSISTORMTECH
        description = 'psi storm'
        ability_id = AbilityId.RESEARCH_PSISTORM
        # 检查是否可以研究指定的升级
        if not self.structures(UnitTypeId.TEMPLARARCHIVE).ready:
            return self.record_failure(action_id, 'Templar archive is not ready')

        if self.already_pending(upgrade_id) != 0:
            return self.record_failure(action_id, f'Upgrade {description} is already pending')

        if not self.can_afford(upgrade_id):
            return self.record_failure(action_id, f'Cannot afford {description}')

        if not vt.is_idle:
            return self.record_failure(action_id, 'Templar archive is not idle')

        if ability_id not in abilities:
            return self.record_failure(action_id, f'Ability {description} is not available')

        vt.research(upgrade_id)
        print(description)
        return 0.010

    async def handle_action_57(self):
        return await self.research_fleetbeacon_upgrade(57, UpgradeId.VOIDRAYSPEEDUPGRADE,
                                                       AbilityId.FLEETBEACONRESEARCH_RESEARCHVOIDRAYSPEEDUPGRADE,
                                                       '研究虚空速度')

    async def handle_action_58(self):
        return await self.research_fleetbeacon_upgrade(58, UpgradeId.PHOENIXRANGEUPGRADE,
                                                       AbilityId.RESEARCH_PHOENIXANIONPULSECRYSTALS, '研究凤凰射程')

    async def handle_action_59(self):
        return await self.research_fleetbeacon_upgrade(59, UpgradeId.TEMPESTGROUNDATTACKUPGRADE,
                                                       AbilityId.FLEETBEACONRESEARCH_TEMPESTRESEARCHGROUNDATTACKUPGRADE,
                                                       '研究风暴对建筑攻击')

    async def handle_action_60(self):
        return await self.handle_scouting(UnitTypeId.PROBE, 60)

    async def handle_action_61(self):
        return await self.handle_scouting(UnitTypeId.OBSERVER, 61)

    async def handle_action_62(self):
        return await self.handle_scouting(UnitTypeId.ZEALOT, 62)

    async def handle_action_63(self):
        return await self.handle_scouting(UnitTypeId.PHOENIX, 63)

    async def handle_action_64(self):
        return await self.handle_action_attack(64, iteration=self.iteration)

    async def handle_action_65(self):
        action_id = 65
        print(f'action={action_id}')

        # Check if army supply is greater than 0
        if self.supply_army <= 0:
            return self.record_failure(action_id, 'Army supply is 0 or less')

        # Define the set of units to consider for retreating
        retreating_units = {
            UnitTypeId.ZEALOT, UnitTypeId.ARCHON, UnitTypeId.STALKER,
            UnitTypeId.ADEPT, UnitTypeId.HIGHTEMPLAR, UnitTypeId.DARKTEMPLAR,
            UnitTypeId.OBSERVER, UnitTypeId.PHOENIX, UnitTypeId.CARRIER, UnitTypeId.VOIDRAY,
            UnitTypeId.TEMPEST, UnitTypeId.ORACLE, UnitTypeId.COLOSSUS,
            UnitTypeId.DISRUPTOR, UnitTypeId.WARPPRISM, UnitTypeId.IMMORTAL,
            UnitTypeId.CHANGELINGZEALOT
        }

        # Get units to retreat
        units_to_retreat = self.units.of_type(retreating_units)
        if not units_to_retreat.exists:
            return self.record_failure(action_id, 'No units available to retreat')

        try:
            # Choose the closest nexus to move to
            closest_nexus = units_to_retreat.closest_to(self.enemy_start_locations[0])
            for retreat_unit in units_to_retreat:
                retreat_unit.move(closest_nexus)
            print('Retreat initiated')
        except Exception as e:
            return self.record_failure(action_id, f'Retreat failed due to: {e}')

    async def handle_action_66(self):
        print("chronoboost nexus")
        return await self.apply_chronoboost(66, UnitTypeId.NEXUS, 2, 'base')

    async def handle_action_67(self):
        print("chronoboost cybernetics core")
        return await self.apply_chronoboost(67, UnitTypeId.CYBERNETICSCORE, 0, 'cybernetics core (by)')

    async def handle_action_68(self):
        print("chronoboost twilight council")
        return await self.apply_chronoboost(68, UnitTypeId.TWILIGHTCOUNCIL, 4, 'twilight council (vc)')

    async def handle_action_69(self):
        print("chronoboost stargate")
        return await self.apply_chronoboost(69, UnitTypeId.STARGATE, 4, 'stargate (vs)')

    async def handle_action_70(self):
        print("chronoboost forge")
        return await self.apply_chronoboost(70, UnitTypeId.FORGE, 4, 'forge (bf)')

    async def handle_action_71(self):
        print("empty action")
        pass

    async def on_step(self, iteration: int):
        self.iteration = iteration
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
        print("action", self.transaction['action'])
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
        if self.time_formatted >= "15:00":
            await self.attack()
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
            # print("self.temp_failure_list", self.temp_failure_list)
            # print("self.transaction['action_failures']", self.transaction['action_failures'])
            # print("self.transaction['action_executed']", self.transaction['action_executed'])
            self.temp_failure_list.clear()  # 清空临时列表

        self.isReadyForNextStep.set()
    async def attack(self):
        if self.army_supply >= 10:
            attack_units = [UnitTypeId.ZEALOT, UnitTypeId.ARCHON, UnitTypeId.STALKER, UnitTypeId.SENTRY,
                            UnitTypeId.ADEPT, UnitTypeId.HIGHTEMPLAR, UnitTypeId.DARKTEMPLAR,
                            UnitTypeId.OBSERVER, UnitTypeId.PHOENIX, UnitTypeId.CARRIER, UnitTypeId.VOIDRAY,
                            UnitTypeId.TEMPEST, UnitTypeId.ORACLE, UnitTypeId.COLOSSUS,
                            UnitTypeId.DISRUPTOR, UnitTypeId.WARPPRISM, UnitTypeId.IMMORTAL,
                            UnitTypeId.CHANGELINGZEALOT]
            if any(self.units(unit_type).amount > 0 for unit_type in attack_units):
                enemy_start_location_cleared = not self.enemy_units.exists and self.is_visible(
                    self.enemy_start_locations[0])

                if enemy_start_location_cleared:
                    for unit_type in attack_units:
                        await self.assign_units_to_resource_clusters(unit_type)
                else:
                    for unit_type in attack_units:
                        units = self.units(unit_type).idle
                        for unit in units:
                            unit.attack(self.enemy_start_locations[0])

    async def assign_units_to_resource_clusters(self, unit_type):
        units = self.units(unit_type).idle
        resource_clusters = self.expansion_locations_list

        if units.exists and resource_clusters:
            # 为每个单位随机分配一个目标资源点
            for unit in units:
                target = random.choice(resource_clusters)
                unit.attack(target)
    # async def attack(self):
    #     ATTACK_UNITS = [
    #         UnitTypeId.ZEALOT, UnitTypeId.ARCHON, UnitTypeId.STALKER, UnitTypeId.SENTRY, UnitTypeId.ADEPT,
    #         UnitTypeId.HIGHTEMPLAR, UnitTypeId.DARKTEMPLAR, UnitTypeId.OBSERVER, UnitTypeId.PHOENIX,
    #         UnitTypeId.CARRIER, UnitTypeId.VOIDRAY, UnitTypeId.TEMPEST, UnitTypeId.ORACLE, UnitTypeId.COLOSSUS,
    #         UnitTypeId.DISRUPTOR, UnitTypeId.WARPPRISM, UnitTypeId.IMMORTAL, UnitTypeId.CHANGELINGZEALOT
    #     ]
    #
    #     if self.army_supply >= 10:  # 如果军队规模超过了10
    #         for unit_type in ATTACK_UNITS:
    #             for unit in self.units(unit_type).idle:  # 选择每种类型的空闲单位
    #                 unit.attack(self.enemy_start_locations[0])  # 让它们攻击敌人的起始位置
    #
    #         # 检查敌人的起始位置是否已清空并对所有单位可见
    #         enemy_start_location_cleared = (
    #                 not self.enemy_units.exists and self.is_visible(self.enemy_start_locations[0])
    #         )
    #
    #         if enemy_start_location_cleared:
    #             # 如果敌人的起始位置已经被清空，将部队重新分配到资源点
    #             await self.assign_units_to_resource_clusters()
    #
    # async def assign_units_to_resource_clusters(self):
    #     self.assigned_to_clusters = True
    #
    #     # 获取所有进攻的的军事单位
    #     MILITARY_UNITS = [unit for unit in self.get_military_units() if unit not in self.defend_units]
    #     # 获取所有资源集群位置
    #     resource_clusters = self.expansion_locations_list
    #
    #     if MILITARY_UNITS and resource_clusters:
    #         # 计算每个资源集群需要分配的单位数量
    #         group_size = len(MILITARY_UNITS) // len(resource_clusters)
    #
    #         # 将军事单位分组并分配给每个资源集群
    #         for i, target in enumerate(resource_clusters):
    #             for unit in MILITARY_UNITS[i * group_size:(i + 1) * group_size]:
    #                 unit.attack(target)
    #                 unit.assigned_resource_cluster = True  # 标记该单位已经被分配

    @staticmethod
    def neighbors4(position, distance=1) -> Set[Point2]:
        """
        Returns the four adjacent positions (top, bottom, left, right) to the given position.

        Args:
        - position (Point2): The reference position.
        - distance (int, default=1): The distance from the reference position.

        Returns:
        - Set[Point2]: A set containing the four adjacent positions.
        """
        p = position
        d = distance
        return {
            Point2((p.x - d, p.y)),  # Left
            Point2((p.x + d, p.y)),  # Right
            Point2((p.x, p.y - d)),  # Bottom
            Point2((p.x, p.y + d))  # Top
        }

    def neighbors8(self, position, distance=1) -> Set[Point2]:
        """
        Returns the eight adjacent positions (top, bottom, left, right, and the four diagonals) to the given position.

        Args:
        - position (Point2): The reference position.
        - distance (int, default=1): The distance from the reference position.

        Returns:
        - Set[Point2]: A set containing the eight adjacent positions.
        """
        p = position
        d = distance
        # Get the four direct neighbors (top, bottom, left, right)
        direct_neighbors = self.neighbors4(position, distance)
        # Get the four diagonal neighbors
        diagonal_neighbors = {
            Point2((p.x - d, p.y - d)),  # Bottom-left
            Point2((p.x - d, p.y + d)),  # Top-left
            Point2((p.x + d, p.y - d)),  # Bottom-right
            Point2((p.x + d, p.y + d))  # Top-right
        }
        return direct_neighbors | diagonal_neighbors


def protoss_agent_vs_build_in(transaction, lock, map_name, isReadyForNextStep, game_end_event, done_event,
                              opposite_race,
                              difficulty, replay_folder, process_id, args):
    # 计算log的基础目录
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 根据agent_type决定保存路径
    if args.agent_type in ["random", "llama2", "glm2", "chatgpt","gpt4","glm3","gpt"]:
        base_dir = os.path.join(current_dir, '..', '..', 'log', f'{args.agent_type}_log')
    else:
        print(f"Unknown agent_type: {args.agent_type}. Defaulting to random_log.")
        base_dir = os.path.join(current_dir, '..', '..', 'log', 'random_log')

    # 创建replay的文件夹
    replay_folder = os.path.join(base_dir, f"game_{args.current_time}_{process_id}")

    # 如果目录不存在，创建它
    if not os.path.exists(replay_folder):
        os.makedirs(replay_folder)

    map = map_name

    result = run_game(maps.get(map),
                      [Bot(Race.Protoss, Protoss_Bot(transaction, lock, isReadyForNextStep)),
                       Computer(map_race(opposite_race), map_difficulty(difficulty))],
                      realtime=False,
                      save_replay_as=f'{replay_folder}/{args.current_time}_{map}_player_race_PROTOSS_VS_BUILD_IN_AI_{difficulty}_{opposite_race}_process_{process_id}.SC2Replay')

    with lock:
        transaction['done'] = True
        transaction['result'] = result
    done_event.set()  # Set done_event when the game is over
    game_end_event.set()  # Set game_end_event when the game is over


