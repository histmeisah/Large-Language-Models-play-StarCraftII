import random
from typing import Set
from math import sin, cos, pi
from typing import List, Any, Union
from loguru import logger
from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty,AIBuild
from sc2.data import Race
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.position import Point2
from sc2.units import Units

ATTACK_START_THRESHOLD = 70
ATTACK_STOP_THRESHOLD = 40
SOME_DELAY = 100
NEARBY_ENEMY_DISTANCE = 20
WAIT_ITER_FOR_KILL_VISIBLE = 200
WAIT_ITER_FOR_CLUSTER_ASSIGN = 400
CRITICAL_BUILDING_DISTANCE = 3  # 或者其他适合的值
# 定义常量
DEFEND_UNIT_COUNT = 5  # 防守单位的数量
DEFEND_UNIT_ASSIGN_INTERVAL = 200  # 重新划分防守单位的间隔步数

LADDER_MAP_2023 = [
    'Altitude LE',
    'Ancient Cistern LE',
    'Babylon LE',
    'Dragon Scales LE',
    'Gresvan LE',
    'Neohumanity LE',
    'Royal Blood LE'
]

MIN_DISTANCE = 3  # 这个值可以根据实际情况调整
BUILDING_DISTANCE = 7
EXCLUDED_UNITS = {UnitTypeId.LARVA, UnitTypeId.CHANGELING, UnitTypeId.EGG}


# map pool 2022 season 1

# pylint: disable=W0231
class WarpGateBot(BotAI):

    def __init__(self):
        # Initialize inherited class
        self.proxy_built = False
        self.main_base = None
        self.second_base = None
        self.third_base = None
        self.forth_base = None
        self.produce_zealot = False
        self.produce_stalker = False
        self.produce_high_templar = False
        self.army_units: Units = []
        self.worker_tag_list = []
        self.upgrade_tag_list = []
        self.flag = True
        self.add_on = False
        self.attacking = False
        self.auto_mode = False
        self.vespenetrigger = False
        self.rally_defend = True
        self.morph_archon = False
        self.zealot_train = False
        self.stalker_train = False
        self.ht_train = False
        self.dt_train = False
        self.sentry_train = False
        self.expansion_flag = False
        self.proxy_flag = False
        self.iteration = 0
        self.p = None

        self.spreading_units = False
        self.is_attacking = False  # 判断是否在进攻
        self.assigned_to_clusters = False  # 判断是否分配了进攻单位
        self.units_keeping_vision = False  # 敌方基地是否有单位在视野范围内
        self.main_enemy_base_cleared = False
        self.clear_base_iteration = 99999999
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

        self.military_unit_types = {
            UnitTypeId.ZEALOT, UnitTypeId.ARCHON, UnitTypeId.VOIDRAY, UnitTypeId.STALKER,
            UnitTypeId.ADEPT, UnitTypeId.HIGHTEMPLAR, UnitTypeId.DARKTEMPLAR, UnitTypeId.OBSERVER,
            UnitTypeId.PHOENIX, UnitTypeId.CARRIER, UnitTypeId.VOIDRAY, UnitTypeId.TEMPEST,
            UnitTypeId.ORACLE, UnitTypeId.COLOSSUS, UnitTypeId.DISRUPTOR, UnitTypeId.WARPPRISM,
            UnitTypeId.IMMORTAL, UnitTypeId.CHANGELINGZEALOT
        }

    # pylint: disable=R0912
    async def on_step(self, iteration):  # implement on_step function
        print("iteration:", iteration)
        print("temp1:", self.temp1)
        print("temp2:", self.temp2)
        print("rally_defend:", self.rally_defend)
        self.iteration = iteration

        await self.procedure()  # call procedure function
        await self.distribute_workers()
        await self.defend(iteration)
        await self.attack(iteration)
        if self.auto_mode:
            await self.building_supply()
            await self.expansion()
            await self.produce_worker()
            await self.build_vespene()
        if self.workers.amount >= 66:
            await self.CHRONOBOOSTENERGYCOST_upgrade()
        if self.expansion_flag == True:
            await self.expansion()
        if self.zealot_train == True:
            await self.train_zealot()
        if self.stalker_train == True:
            await self.train_stalker()
        if self.ht_train:
            await self.train_ht()
            await self.train_archon()
        if self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready and self.structures(
                UnitTypeId.FORGE).ready and self.workers.amount >= 66:
            await self.CHRONOBOOSTENERGYCOST_upgrade()
        await self.stalker_blink()
        await self.research_blink()
        print("len defend_units:", len(self.defend_units))
        print("defend_units:", self.defend_units)
        print("military_units:",self.get_military_units())
        print("len military_units:",len(self.get_military_units()))

    def record_failure(self, action, reason):
        pass
    async def warp_unit(self, unit_type: UnitTypeId, initial_reference_point: Point2,
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
        action_id = 0
        # 如果需要额外的科技建筑，则进行检查
        if required_buildings:
            for building in required_buildings:
                if not self.structures(building).exists:
                    return self.record_failure(action_id, f'{building.name} not available')

        # 检查是否是允许折跃的单位类型
        if unit_type not in {UnitTypeId.ZEALOT, UnitTypeId.STALKER, UnitTypeId.DARKTEMPLAR, UnitTypeId.SENTRY,
                             UnitTypeId.ADEPT, UnitTypeId.HIGHTEMPLAR}:
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
    async def produce_bg_unit(self, unit_type: UnitTypeId, required_buildings: List[UnitTypeId] = None):
        action_id = 0


        # 检查Warp Gate的研究状态
        warp_gate_research_status = self.already_pending_upgrade(UpgradeId.WARPGATERESEARCH)

        if warp_gate_research_status == 1:
            # 检查是否有水晶塔存在
            if not self.structures(UnitTypeId.PYLON).ready.exists:
                return self.record_failure(action_id, 'No pylons available')

            # 获取最接近敌方起始位置的水晶塔作为参考点
            proxy = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0]).position

            # 尝试从折跃门折跃单位
            await self.warp_unit( unit_type, proxy,required_buildings=required_buildings)
            print(f'折跃{unit_type.name}')
        else:
            # 尝试从传送门生产单位
            success = await self.train_from_gateway( unit_type, required_buildings)
            if success:
                print(f'训练{unit_type.name}')

    async def train_from_gateway(self,  unit_type: UnitTypeId,
                                 required_buildings: List[UnitTypeId] = None):
        """
        从传送门训练指定的单位。

        :param action_id: 动作ID，用于记录失败原因。
        :param unit_type: 想要训练的单位类型。
        :param required_buildings: 训练该单位所需的额外建筑列表。
        :return: 如果成功返回True，否则返回False。
        """
        action_id=0
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

    def get_military_units(self):
        return self.units.of_type(self.military_unit_types)

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
            if position.distance_to(resource.position) < BUILDING_DISTANCE + resource.radius:
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

    def find_optimal_building_position_for_base(self, base_position: Point2, max_distance=15) -> Point2:
        for distance in range(1, max_distance + 1):
            candidate_positions = list(self.neighbors8(base_position, distance))
            valid_positions = [pos for pos in candidate_positions if self.is_position_valid_for_building(pos)]
            if valid_positions:
                building_positions = [building.position for building in self.structures(
                    {UnitTypeId.GATEWAY,UnitTypeId.FORGE,UnitTypeId.CYBERNETICSCORE,UnitTypeId.STARGATE,UnitTypeId.TWILIGHTCOUNCIL,UnitTypeId.ROBOTICSFACILITY,
                     UnitTypeId.TEMPLARARCHIVE,UnitTypeId.DARKSHRINE,UnitTypeId.FLEETBEACON,UnitTypeId.ROBOTICSBAY,UnitTypeId.SHIELDBATTERY,UnitTypeId.PHOTONCANNON})]

                def key_function(pos):
                    if not building_positions:
                        return 0
                    return min(pos.distance_to(p) for p in building_positions)

                best_position = max(valid_positions, key=key_function)
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
    async def handle_action_build_building(self, building_type: UnitTypeId):
        # 如果无法负担费用，则直接返回
        if not self.can_afford(building_type):
            print(f"Cannot afford {building_type}")
            return

        if building_type in {UnitTypeId.PHOTONCANNON, UnitTypeId.SHIELDBATTERY}:
            # 确定外侧基地
            enemy_start = self.enemy_start_locations[0]
            outermost_base = min(self.townhalls, key=lambda base: base.distance_to(enemy_start))

            # 找到附近的建筑位置
            best_position = self.find_optimal_building_position_for_base(outermost_base.position, max_distance=8)

        else:
            best_base = self.find_best_base_for_building(building_type)
            if not best_base:
                print(f"No suitable base found for {building_type}")
                return

            # 优先找到最佳位置
            best_position = self.find_optimal_building_position_for_base(best_base.position)

            # 如果在这个最佳基地找不到合适的位置，则尝试在其他基地找到合适的位置
            if not best_position:
                print(f"No suitable position found near best base for {building_type}. Trying alternative bases.")

                for base in self.townhalls:
                    if base.position != best_base.position:
                        best_position = self.find_optimal_building_position_for_base(base.position)
                        if best_position:
                            break

            # 如果在所有基地都找不到理想位置，尝试寻找次佳位置
            if not best_position:
                print("Trying suboptimal positions...")

                adjusted_building_distance = 10  # 可以根据需要进行调整
                best_position = self.find_optimal_building_position_for_base(best_base.position,
                                                                             max_distance=adjusted_building_distance)

                # 如果还是找不到，尝试扩展搜索范围
                if not best_position:
                    print("Expanding search range...")
                    expanded_search_range = 30  # 可以根据需要进行调整
                    best_position = self.find_optimal_building_position_for_base(best_base.position,
                                                                                 max_distance=expanded_search_range)

        if not best_position:
            print(f"Still no suitable position found for {building_type}. Aborting.")
            return

        await self.build(building_type, near=best_position)
        print(f"Building {building_type}")


    def is_position_valid_for_pylon(self, position: Point2) -> bool:
        # 检查与其他建筑的距离
        if self.structures(UnitTypeId.PYLON).exists:
            pylons = self.structures(UnitTypeId.PYLON)
        if self.structures.exists:
            for structure in self.structures:
                # 如果与其他建筑的距离小于MIN_DISTANCE，则此位置不适合建造水晶塔
                if position.distance_to(structure.position) < MIN_DISTANCE:
                    return False

        # 特别检查与ASSIMILATOR的距离，因为它们可能影响气体采集
        if self.structures(UnitTypeId.ASSIMILATOR).exists:
            for assimilator in self.structures(UnitTypeId.ASSIMILATOR):
                # 与ASSIMILATOR的距离应该比与其他建筑的距离要大，这里我们使用了1.5倍的MIN_DISTANCE
                if position.distance_to(assimilator.position) < MIN_DISTANCE * 1.5:  # 这里可以调整倍数来改变距离
                    return False

        # 检查与资源的距离，确保不会影响资源采集
        for resource in self.resources:
            if position.distance_to(resource.position) < MIN_DISTANCE:
                return False

        # 检查是否在其他水晶塔的能量范围之外，确保能量场能够覆盖更大的区域
        if self.structures(UnitTypeId.PYLON).exists:
            pylons = self.structures(UnitTypeId.PYLON)
            for pylon in pylons:
                if position.distance_to(pylon.position) < MIN_DISTANCE:
                    return False

        return True

    def find_optimal_pylon_position_for_base(self, base_position: Point2) -> Point2:
        # 为基地生成候选位置，包括基地本身和它的8个相邻位置
        candidate_positions = [base_position] + list(self.neighbors8(base_position, distance=8))
        # 从候选位置中筛选出有效的位置
        valid_positions = [pos for pos in candidate_positions if self.is_position_valid_for_pylon(pos)]
        pylons = self.structures(UnitTypeId.PYLON)
        pylon_positions = [pylon.position for pylon in pylons]
        if not valid_positions:
            return base_position

        # 如果没有已有的水晶塔，直接返回一个有效位置
        if not pylon_positions:
            return valid_positions[0]

        # 选择最优位置，这是与已有水晶塔距离最远的位置
        best_position = max(valid_positions, key=lambda pos: min(pos.distance_to(p) for p in pylon_positions))
        return best_position

    def find_best_base_for_pylon(self):
        pylons = self.structures(UnitTypeId.PYLON)
        base_positions = [base.position for base in self.townhalls]
        pylon_positions = [pylon.position for pylon in pylons]
        base_pylon_counts = {}
        # 计算每个基地附近的水晶塔数量
        for base_pos in base_positions:
            count = sum(1 for pylon_pos in pylon_positions if base_pos.distance_to(pylon_pos) <= 10)
            base_pylon_counts[base_pos] = count
        # 返回附近水晶塔数量最少的基地，确保我们的水晶塔能够覆盖更多的基地
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

    async def procedure(self):
        if self.time_formatted == '00:00':
            if self.start_location == Point2((160.5, 46.5)):
                self.Location = -1  # detect location
            else:
                self.Location = 1
            await self.chat_send("(glhf)")
            self.main_base = self.townhalls.first
        elif '00:00' <= self.time_formatted <= '01:00':
            nexus = self.townhalls.first
            if nexus.is_idle and self.can_afford(UnitTypeId.PROBE):
                nexus.train(UnitTypeId.PROBE)
            if '00:17' <= self.time_formatted <= '00:25':
                if self.supply_used <= 15 and self.already_pending(UnitTypeId.PYLON) + self.structures(
                        UnitTypeId.PYLON).amount == 0:
                    if self.can_afford(UnitTypeId.PYLON):
                        best_base = self.find_best_base_for_pylon()
                        best_position = self.find_optimal_pylon_position_for_base(best_base)
                        await self.build(UnitTypeId.PYLON, near=best_position, placement_step=2)
            elif '00:20' <= self.time_formatted <= '01:00':
                if '00:38' <= self.time_formatted <= '00:42':
                    pylon = self.structures(UnitTypeId.PYLON).random
                    if self.supply_used == 16 and self.already_pending(UnitTypeId.GATEWAY) + self.structures(
                            UnitTypeId.GATEWAY).amount == 0:
                        if self.can_afford(UnitTypeId.GATEWAY):
                            await self.handle_action_build_building(UnitTypeId.GATEWAY)
                if '00:40' <= self.time_formatted <= '01:00' and self.already_pending(UnitTypeId.GATEWAY) == 1:
                    if not nexus.is_idle and not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                        nexuses = self.structures(UnitTypeId.NEXUS)
                        abilities = await self.get_available_abilities(nexuses)
                        for loop_nexus, abilities_nexus in zip(nexuses, abilities):
                            if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities_nexus:
                                loop_nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus)
                                break
                    if '00:48' <= self.time_formatted <= '00:51' and self.structures(
                            UnitTypeId.ASSIMILATOR).amount + self.already_pending(UnitTypeId.ASSIMILATOR) < 1:
                        if 16 <= self.workers.amount <= 20 and self.can_afford(
                                UnitTypeId.ASSIMILATOR) and self.already_pending(UnitTypeId.GATEWAY) == 1:
                            vespenes = self.vespene_geyser.closer_than(15, self.main_base).random
                            if self.can_afford(UnitTypeId.ASSIMILATOR):
                                await self.build(UnitTypeId.ASSIMILATOR, vespenes)
        elif '01:00' <= self.time_formatted <= '02:00':
            nexus = self.townhalls.first
            if nexus.is_idle and self.can_afford(UnitTypeId.PROBE) and self.already_pending(UnitTypeId.PROBE) == 0:
                nexus.train(UnitTypeId.PROBE)
            if '01:25' <= self.time_formatted <= '01:40' and self.structures(UnitTypeId.GATEWAY).ready:
                if self.can_afford(UnitTypeId.NEXUS) and 19 <= self.workers.amount <= 22:
                    if self.townhalls.amount + self.already_pending(UnitTypeId.NEXUS) < 2:
                        await self.expand_now()
            if '01:39' <= self.time_formatted <= '01:44' and self.structures(
                    UnitTypeId.CYBERNETICSCORE).amount + self.already_pending(UnitTypeId.CYBERNETICSCORE) == 0:
                pylon = self.structures(UnitTypeId.PYLON).random
                if self.structures(UnitTypeId.GATEWAY).ready and self.can_afford(
                        UnitTypeId.CYBERNETICSCORE) and self.already_pending(UnitTypeId.NEXUS):
                    await self.handle_action_build_building(UnitTypeId.CYBERNETICSCORE)
            elif '01:44' <= self.time_formatted <= '01:59':

                if 20 <= self.supply_used <= 22 and self.structures(
                        UnitTypeId.ASSIMILATOR).ready and self.already_pending(
                    UnitTypeId.CYBERNETICSCORE) == 1 and self.already_pending(UnitTypeId.NEXUS) == 1:
                    if self.can_afford(UnitTypeId.ASSIMILATOR):
                        for nexus in self.townhalls.ready:
                            vgs = self.vespene_geyser.closer_than(15, nexus)
                            for vg in vgs:
                                if not self.can_afford(UnitTypeId.ASSIMILATOR):
                                    break
                                worker = self.select_build_worker(vg.position)
                                if worker is None:
                                    break
                                if not self.units(UnitTypeId.ASSIMILATOR).closer_than(1.0, vg).exists:
                                    worker.build(UnitTypeId.ASSIMILATOR, vg)
                if self.already_pending(UnitTypeId.PYLON) + self.structures(UnitTypeId.PYLON).amount == 1:
                    if self.supply_left <= 2:
                        if self.can_afford(UnitTypeId.PYLON):
                            best_base = self.find_best_base_for_pylon()
                            best_position = self.find_optimal_pylon_position_for_base(best_base)
                            await self.build(UnitTypeId.PYLON, near=best_position, placement_step=2)
        elif '02:00' <= self.time_formatted <= '03:00':
            bases = self.townhalls
            for base in bases:
                if base.is_idle and self.can_afford(UnitTypeId.PROBE):
                    base.train(UnitTypeId.PROBE)
            if '02:10' <= self.time_formatted <= '02:40':
                if self.structures(UnitTypeId.PYLON).amount == 2 and self.supply_left >= 3:
                    nexus = self.main_base
                    if not nexus.is_idle and not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                        nexuses = self.structures(UnitTypeId.NEXUS)
                        abilities = await self.get_available_abilities(nexuses)
                        for loop_nexus, abilities_nexus in zip(nexuses, abilities):
                            if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities_nexus:
                                loop_nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus)
                                break
                if self.structures(UnitTypeId.CYBERNETICSCORE).ready and self.can_afford(
                        UnitTypeId.TWILIGHTCOUNCIL) and not self.already_pending(UnitTypeId.ADEPT):
                    pylon = self.structures(UnitTypeId.PYLON).random
                    if self.structures(UnitTypeId.STARGATE).amount + self.already_pending(
                            UnitTypeId.STARGATE) == 0:
                        await self.handle_action_build_building(UnitTypeId.STARGATE)

                if (
                        self.structures(UnitTypeId.CYBERNETICSCORE).ready and self.can_afford(
                    AbilityId.RESEARCH_WARPGATE)
                        and self.already_pending_upgrade(UpgradeId.WARPGATERESEARCH) == 0
                ):
                    ccore = self.structures(UnitTypeId.CYBERNETICSCORE).ready.first
                    ccore.research(UpgradeId.WARPGATERESEARCH)
                if self.structures(UnitTypeId.CYBERNETICSCORE).ready and self.already_pending(
                        UnitTypeId.STARGATE) != 0 and self.can_afford(UnitTypeId.ADEPT):
                    if self.structures(UnitTypeId.GATEWAY).idle:
                        gate = self.structures(UnitTypeId.GATEWAY).random
                        if self.supply_left >= 3 and self.can_afford(UnitTypeId.ADEPT) and self.already_pending(
                                UnitTypeId.ADEPT) + self.units(UnitTypeId.ADEPT).amount <= 1:
                            await self.produce_bg_unit(UnitTypeId.ADEPT,
                                                       required_buildings=[UnitTypeId.CYBERNETICSCORE])
                if self.already_pending(UnitTypeId.ADEPT) and not self.structures(UnitTypeId.GATEWAY).idle:
                    gate = self.structures(UnitTypeId.GATEWAY).random
                    if not gate.is_idle and not gate.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                        nexuses = self.structures(UnitTypeId.NEXUS)
                        abilities = await self.get_available_abilities(nexuses)
                        for loop_nexus, abilities_nexus in zip(nexuses, abilities):
                            if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities_nexus:
                                loop_nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, gate)
                                break
                if self.already_pending(UnitTypeId.ADEPT) and self.already_pending(
                        UnitTypeId.STARGATE) and self.already_pending(UnitTypeId.STARGATE) and not self.already_pending(
                    UpgradeId.WARPGATERESEARCH):
                    if self.structures(UnitTypeId.CYBERNETICSCORE).ready and self.can_afford(
                            UpgradeId.WARPGATERESEARCH):
                        by = self.structures(UnitTypeId.CYBERNETICSCORE).random
                        if by.is_idle:
                            by.research(UpgradeId.WARPGATERESEARCH)
            elif '02:40' <= self.time_formatted <= '03:00':
                if self.structures(UnitTypeId.CYBERNETICSCORE).ready and self.already_pending(
                        UnitTypeId.STARGATE) != 0 and self.can_afford(UnitTypeId.STALKER):
                    if self.structures(UnitTypeId.GATEWAY).idle and self.units(
                            UnitTypeId.STALKER).amount + self.already_pending(UnitTypeId.STALKER) <= 1:
                        gate = self.structures(UnitTypeId.GATEWAY).random
                        if self.supply_left >= 3 and self.can_afford(UnitTypeId.STALKER):
                            await self.produce_bg_unit(UnitTypeId.STALKER,
                                                       required_buildings=[UnitTypeId.CYBERNETICSCORE])

                bases = self.townhalls
                for base in bases:
                    if base != self.main_base:
                        self.second_base = base
                if self.second_base != None:
                    if self.structures(UnitTypeId.NEXUS).amount == 2:
                        if not self.second_base.is_idle and not self.second_base.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                            nexuses = self.structures(UnitTypeId.NEXUS)
                            abilities = await self.get_available_abilities(nexuses)
                            for loop_nexus, abilities_nexus in zip(nexuses, abilities):
                                if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities_nexus:
                                    loop_nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, self.second_base)
                                    break
        elif '03:00' <= self.time_formatted <= '04:00':

            bases = self.townhalls
            for base in bases:
                if base.is_idle and self.can_afford(UnitTypeId.PROBE):
                    base.train(UnitTypeId.PROBE)

            if '03:00' <= self.time_formatted <= '03:15':
                vs = self.structures(UnitTypeId.STARGATE).random
                if self.structures(UnitTypeId.STARGATE).ready and self.structures(UnitTypeId.NEXUS).amount == 2:
                    if self.structures(UnitTypeId.STARGATE).idle and self.can_afford(
                            UnitTypeId.VOIDRAY) and self.supply_left >= 4:
                        if vs.is_idle and self.can_afford(UnitTypeId.VOIDRAY):
                            vs.train(UnitTypeId.VOIDRAY)
                if not self.structures(UnitTypeId.STARGATE).idle and self.already_pending(UnitTypeId.VOIDRAY):
                    if self.structures(UnitTypeId.NEXUS).amount == 2:
                        if not vs.is_idle and not vs.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                            nexuses = self.structures(UnitTypeId.NEXUS)
                            abilities = await self.get_available_abilities(nexuses)
                            for loop_nexus, abilities_nexus in zip(nexuses, abilities):
                                if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities_nexus:
                                    loop_nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, vs)
                                    break
                if self.already_pending(UnitTypeId.VOIDRAY) and self.supply_used >= 39 and self.already_pending(
                        UnitTypeId.PYLON) == 0:
                    if self.can_afford(UnitTypeId.PYLON):
                        best_base = self.find_best_base_for_pylon()
                        best_position = self.find_optimal_pylon_position_for_base(best_base)
                        await self.build(UnitTypeId.PYLON, near=best_position, placement_step=2)


            elif '03:15' <= self.time_formatted <= '03:50':
                if self.structures(UnitTypeId.CYBERNETICSCORE).ready and self.already_pending(
                        UnitTypeId.STARGATE) != 0 and self.can_afford(UnitTypeId.ADEPT):
                    if self.structures(UnitTypeId.GATEWAY).idle:
                        gate = self.structures(UnitTypeId.GATEWAY).random
                        if self.supply_left >= 3 and self.can_afford(UnitTypeId.STALKER) and self.already_pending(
                                UnitTypeId.STALKER) + self.units(UnitTypeId.STALKER).amount <= 2:
                            await self.produce_bg_unit(UnitTypeId.STALKER,
                                                       required_buildings=[UnitTypeId.CYBERNETICSCORE])
                if self.structures(UnitTypeId.GATEWAY).amount + self.already_pending(UnitTypeId.GATEWAY) == 1:
                    await self.handle_action_build_building(UnitTypeId.GATEWAY)

                if self.supply_left <= 4 and self.can_afford(UnitTypeId.PYLON) and self.already_pending(
                        UnitTypeId.PYLON) == 0:
                    best_base = self.find_best_base_for_pylon()
                    best_position = self.find_optimal_pylon_position_for_base(best_base)
                    await self.build(UnitTypeId.PYLON, near=best_position, placement_step=2)
                nexuses = self.structures(UnitTypeId.NEXUS)
                nexus = nexuses.random
                if not nexus.is_idle and not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                    abilities = await self.get_available_abilities(nexuses)
                    for loop_nexus, abilities_nexus in zip(nexuses, abilities):
                        if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities_nexus:
                            loop_nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus)
                            break
                if self.supply_left <= 4 and self.can_afford(UnitTypeId.PYLON) and self.already_pending(
                        UnitTypeId.NEXUS):
                    if self.can_afford(UnitTypeId.PYLON):
                        best_base = self.find_best_base_for_pylon()
                        best_position = self.find_optimal_pylon_position_for_base(best_base)
                        await self.build(UnitTypeId.PYLON, near=best_position, placement_step=2)
            elif '03:50' <= self.time_formatted <= '04:00':
                if self.already_pending(UnitTypeId.NEXUS) and self.supply_left >= 4:
                    if self.structures(UnitTypeId.STARGATE).idle and self.can_afford(UnitTypeId.VOIDRAY):
                        vs = self.structures(UnitTypeId.STARGATE).random
                        if vs.is_idle and self.can_afford(UnitTypeId.VOIDRAY):
                            vs.train(UnitTypeId.VOIDRAY)
        elif '04:00' <= self.time_formatted <= '05:00':
            bases = self.townhalls
            for base in bases:
                if base.is_idle and self.can_afford(UnitTypeId.PROBE) and self.supply_left >= 3:
                    base.train(UnitTypeId.PROBE)
            if '04:00' <= self.time_formatted <= '04:20':
                if self.structures(
                        UnitTypeId.PYLON).amount <= 4 and self.supply_used >= 48 and self.townhalls.amount + self.already_pending(
                    UnitTypeId.NEXUS) < 3:
                    if self.can_afford(UnitTypeId.NEXUS) and self.already_pending(
                            UnitTypeId.NEXUS) == 0:
                        if self.can_afford(UnitTypeId.NEXUS):
                            await self.expand_now()
                if self.supply_left <= 4 and self.can_afford(UnitTypeId.PYLON) and self.already_pending(
                        UnitTypeId.PYLON) < 2:
                    best_base = self.find_best_base_for_pylon()
                    best_position = self.find_optimal_pylon_position_for_base(best_base)
                    await self.build(UnitTypeId.PYLON, near=best_position, placement_step=2)

                if self.already_pending(UnitTypeId.NEXUS) and self.can_afford(UnitTypeId.ASSIMILATOR):
                    nexus = self.second_base
                    vgs = self.vespene_geyser.closer_than(15, nexus)
                    for vg in vgs:
                        if not self.can_afford(UnitTypeId.ASSIMILATOR):
                            break
                        worker = self.select_build_worker(vg.position)
                        if worker is None:
                            break
                        if not self.gas_buildings or not self.gas_buildings.closer_than(1, vg):
                            worker.build_gas(vg)
                            worker.stop(queue=True)
                if self.structures(UnitTypeId.CYBERNETICSCORE).ready and self.can_afford(
                        UnitTypeId.SHIELDBATTERY) and self.structures(
                    UnitTypeId.SHIELDBATTERY).amount + self.already_pending(UnitTypeId.SHIELDBATTERY) == 0:
                    await self.handle_action_build_building(UnitTypeId.SHIELDBATTERY)
            elif '04:20' <= self.time_formatted <= '05:00':
                if self.structures(UnitTypeId.TWILIGHTCOUNCIL).amount + self.already_pending(
                        UnitTypeId.TWILIGHTCOUNCIL) == 0:
                    if self.can_afford(UnitTypeId.TWILIGHTCOUNCIL):
                        await self.handle_action_build_building(UnitTypeId.TWILIGHTCOUNCIL)
                if self.structures(UnitTypeId.FORGE).amount + self.already_pending(UnitTypeId.FORGE) == 0:
                    if self.can_afford(UnitTypeId.FORGE):
                        await self.handle_action_build_building(UnitTypeId.FORGE)
                if self.supply_left <= 4 and self.can_afford(UnitTypeId.PYLON) and self.already_pending(
                        UnitTypeId.PYLON) < 2:
                    best_base = self.find_best_base_for_pylon()
                    best_position = self.find_optimal_pylon_position_for_base(best_base)
                    await self.build(UnitTypeId.PYLON, near=best_position, placement_step=2)
                if self.can_afford(UnitTypeId.STALKER) and self.supply_left >= 4:
                    if self.units(UnitTypeId.STALKER).amount < 4:
                        proxy = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0])
                        await self.warp_stalker()
                if self.can_afford(UnitTypeId.VOIDRAY) and self.supply_left >= 4 and self.units(
                        UnitTypeId.VOIDRAY).amount < 3:
                    vs = self.structures(UnitTypeId.STARGATE).random
                    vs.train(UnitTypeId.VOIDRAY)

        elif '05:00' <= self.time_formatted <= '07:00':
            if self.townhalls.amount >= 3 and self.third_base == None and self.forth_base == None:
                nexuses = self.townhalls
                for nexus in nexuses:
                    if nexus != self.main_base and nexus != self.second_base:
                        self.third_base = nexus
            self.expansion_flag = True
            vc = self.structures(UnitTypeId.TWILIGHTCOUNCIL).first
            if self.structures(UnitTypeId.FORGE).exists:
                bf = self.structures(UnitTypeId.FORGE).random
            else:
                await self.handle_action_build_building(UnitTypeId.FORGE)
            if self.townhalls.amount >= 3:
                self.auto_mode = True
                self.zealot_train = True
            if self.units(UnitTypeId.STALKER).amount + self.already_pending(UnitTypeId.STALKER) <= 8:
                await self.warp_stalker()
            if self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready:
                if self.structures(UnitTypeId.TEMPLARARCHIVE).amount + self.already_pending(
                        UnitTypeId.TEMPLARARCHIVE) == 0:
                    await self.handle_action_build_building(UnitTypeId.TEMPLARARCHIVE)

                if self.can_afford(UpgradeId.CHARGE) and vc.is_idle:
                    vc.research(UpgradeId.CHARGE)
            if self.structures(UnitTypeId.FORGE).ready:
                if self.can_afford(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1):
                    bf.research(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1)
            if self.structures(UnitTypeId.TEMPLARARCHIVE).ready:
                self.stalker_train = True
        elif '07:00' <= self.time_formatted:
            if self.proxy_flag == False and self.p == None:
                p = self.game_info.map_center.towards(self.enemy_start_locations[0], 15)
                self.p = p
                await self.build(UnitTypeId.PYLON, near=p)
                self.proxy_flag = True
            if self.townhalls.amount >= 4 and self.forth_base == None:
                nexuses = self.townhalls
                for nexus in nexuses:
                    if nexus != self.main_base and nexus != self.second_base and nexus != self.third_base:
                        self.forth_base = nexus

            elif '07:00' <= self.time_formatted and self.can_afford(UnitTypeId.ZEALOT):
                if self.units(UnitTypeId.ZEALOT).amount + self.already_pending(
                        UnitTypeId.ZEALOT) < 25 and self.supply_left >= 2:
                    await self.warp_zealot()

    async def train_zealot(self):
        if self.structures(UnitTypeId.PYLON).exists and self.can_afford(UnitTypeId.ZEALOT):
            if '05:00' <= self.time_formatted <= '07:00' and self.workers.amount >= 44:
                if self.units(UnitTypeId.ZEALOT).amount + self.already_pending(
                        UnitTypeId.ZEALOT) < 15 and self.supply_left >= 2:
                    await self.warp_zealot()
            elif '07:00' <= self.time_formatted <= '09:00' and self.can_afford(UnitTypeId.ZEALOT):
                if self.units(UnitTypeId.ZEALOT).amount + self.already_pending(
                        UnitTypeId.ZEALOT) < 35 and self.supply_left >= 2:
                    await self.warp_zealot()
            elif '09:00' <= self.time_formatted and self.can_afford(UnitTypeId.ZEALOT):
                if self.minerals >= 2000:
                    if self.units(UnitTypeId.ZEALOT).amount + self.already_pending(
                            UnitTypeId.ZEALOT) < 50 and self.supply_left >= 2:
                        await self.warp_zealot()

                if self.units(UnitTypeId.ZEALOT).amount + self.already_pending(
                        UnitTypeId.ZEALOT) < 30 and self.supply_left >= 2:
                    await self.warp_zealot()

    async def train_stalker(self):
        if self.structures(UnitTypeId.PYLON).exists and self.can_afford(UnitTypeId.STALKER):
            if '05:00' <= self.time_formatted <= '07:00' and self.workers.amount >= 44:
                if self.units(UnitTypeId.STALKER).amount + self.already_pending(
                        UnitTypeId.STALKER) < 8 and self.supply_left >= 2:
                    await self.warp_stalker()
            elif '07:00' <= self.time_formatted <= '09:00' and self.can_afford(UnitTypeId.STALKER):
                if self.units(UnitTypeId.STALKER).amount + self.already_pending(
                        UnitTypeId.STALKER) < 15 and self.supply_left >= 2:
                    await self.warp_stalker()
            elif '09:00' <= self.time_formatted and self.can_afford(UnitTypeId.STALKER):
                if self.units(UnitTypeId.STALKER).amount + self.already_pending(
                        UnitTypeId.STALKER) < 20 and self.supply_left >= 2:
                    await self.warp_stalker()

    async def train_ht(self):
        if self.structures(UnitTypeId.PYLON).exists and self.can_afford(UnitTypeId.HIGHTEMPLAR):
            if '05:00' <= self.time_formatted <= '07:00' and self.workers.amount >= 60:
                if self.units(UnitTypeId.HIGHTEMPLAR).amount + self.already_pending(UnitTypeId.HIGHTEMPLAR) + \
                        self.units(UnitTypeId.ARCHON).amount * 2 + self.already_pending(
                    UnitTypeId.ARCHON) * 2 < 4 and self.supply_left >= 2:
                    await self.warp_ht()
            elif '07:00' <= self.time_formatted <= '09:00' and self.can_afford(UnitTypeId.HIGHTEMPLAR):
                if self.units(UnitTypeId.HIGHTEMPLAR).amount + self.already_pending(UnitTypeId.HIGHTEMPLAR) + \
                        self.units(UnitTypeId.ARCHON).amount * 2 + self.already_pending(
                    UnitTypeId.ARCHON) * 2 < 8 and self.supply_left >= 2:
                    await self.warp_ht()

            elif '09:00' <= self.time_formatted and self.can_afford(UnitTypeId.HIGHTEMPLAR):
                if self.units(UnitTypeId.HIGHTEMPLAR).amount + self.already_pending(UnitTypeId.HIGHTEMPLAR) + \
                        self.units(UnitTypeId.ARCHON).amount * 2 + self.already_pending(
                    UnitTypeId.ARCHON) * 2 < 14 and self.supply_left >= 2:
                    await self.warp_ht()

    async def train_dt(self):
        if self.structures(UnitTypeId.PYLON).exists and self.can_afford(UnitTypeId.DARKTEMPLAR):
            if '05:00' <= self.time_formatted <= '07:00' and self.workers.amount >= 30:
                if self.units(UnitTypeId.DARKTEMPLAR).amount + self.already_pending(
                        UnitTypeId.DARKTEMPLAR) < 4 and self.supply_left >= 2:
                    await self.warp_dt()
            elif '07:00' <= self.time_formatted <= '09:00' and self.can_afford(UnitTypeId.STALKER):
                if self.units(UnitTypeId.DARKTEMPLAR).amount + self.already_pending(
                        UnitTypeId.DARKTEMPLAR) < 6 and self.supply_left >= 2:
                    await self.warp_dt()
            elif '09:00' <= self.time_formatted and self.can_afford(UnitTypeId.DARKTEMPLAR):
                if self.units(UnitTypeId.DARKTEMPLAR).amount + self.already_pending(
                        UnitTypeId.DARKTEMPLAR) < 8 and self.supply_left >= 2:
                    await self.warp_dt()

    async def train_sentry(self):
        if self.structures(UnitTypeId.PYLON).exists and self.can_afford(UnitTypeId.STALKER):
            if '05:00' <= self.time_formatted <= '07:00' and self.workers.amount >= 30:
                if self.units(UnitTypeId.SENTRY).amount + self.already_pending(
                        UnitTypeId.SENTRY) < 2 and self.supply_left >= 2:
                    await self.warp_sentry()
            elif '07:00' <= self.time_formatted <= '09:00' and self.can_afford(UnitTypeId.SENTRY):
                if self.units(UnitTypeId.SENTRY).amount + self.already_pending(
                        UnitTypeId.SENTRY) < 7 and self.supply_left >= 2:
                    await self.warp_sentry()
            elif '09:00' <= self.time_formatted and self.can_afford(UnitTypeId.SENTRY):
                if self.units(UnitTypeId.SENTRY).amount + self.already_pending(
                        UnitTypeId.SENTRY) < 2 and self.supply_left >= 2:
                    await self.warp_sentry()

    async def train_archon(self):
        if self.units(UnitTypeId.HIGHTEMPLAR).exists:
            hts = self.units(UnitTypeId.HIGHTEMPLAR)
            for ht in hts:
                ht(AbilityId.MORPH_ARCHON)

    async def warp_stalker(self):
        proxy = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0]).position
        required_buildings = [UnitTypeId.CYBERNETICSCORE]
        await self.produce_bg_unit(UnitTypeId.STALKER, required_buildings=required_buildings)



    async def warp_zealot(self):
        if self.structures(UnitTypeId.WARPGATE).exists and self.can_afford(UnitTypeId.ZEALOT) and self.supply_left >= 2:
            await self.produce_bg_unit(UnitTypeId.ZEALOT)

    async def warp_ht(self):
        proxy = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0])

        warpgate = self.structures(UnitTypeId.WARPGATE).random
        abilities = await self.get_available_abilities(warpgate)
        # all the units have the same cooldown anyway so let's just look at ZEALOT
        if AbilityId.WARPGATETRAIN_HIGHTEMPLAR in abilities and self.can_afford(UnitTypeId.HIGHTEMPLAR):
            pos = proxy.position.to2.random_on_distance(4)
            placement = await self.find_placement(AbilityId.WARPGATETRAIN_HIGHTEMPLAR, pos, placement_step=1)
            if placement is None:
                # return ActionResult.CantFindPlacementLocation
                logger.info("can't place")
                return
            warpgate.warp_in(UnitTypeId.HIGHTEMPLAR, placement)

    async def warp_dt(self):
        proxy = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0])

        warpgate = self.structures(UnitTypeId.WARPGATE).random
        abilities = await self.get_available_abilities(warpgate)
        # all the units have the same cooldown anyway so let's just look at ZEALOT
        if AbilityId.WARPGATETRAIN_DARKTEMPLAR in abilities and self.can_afford(UnitTypeId.DARKTEMPLAR):
            pos = proxy.position.to2.random_on_distance(4)
            placement = await self.find_placement(AbilityId.WARPGATETRAIN_DARKTEMPLAR, pos, placement_step=1)
            if placement is None:
                # return ActionResult.CantFindPlacementLocation
                logger.info("can't place")
                return
            warpgate.warp_in(UnitTypeId.DARKTEMPLAR, placement)

    async def warp_sentry(self):
        proxy = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0])

        warpgate = self.structures(UnitTypeId.WARPGATE).random
        abilities = await self.get_available_abilities(warpgate)
        # all the units have the same cooldown anyway so let's just look at ZEALOT
        if AbilityId.WARPGATETRAIN_SENTRY in abilities and self.can_afford(UnitTypeId.SENTRY):
            pos = proxy.position.to2.random_on_distance(4)
            placement = await self.find_placement(AbilityId.WARPGATETRAIN_SENTRY, pos, placement_step=1)
            if placement is None:
                # return ActionResult.CantFindPlacementLocation
                logger.info("can't place")
                return
            warpgate.warp_in(UnitTypeId.SENTRY, placement)

    async def produce_worker(self):
        if self.townhalls and self.supply_workers <= 67 and self.supply_left >= 3:
            base = self.townhalls.random
            if base.is_idle and self.can_afford(UnitTypeId.PROBE):
                base.train(UnitTypeId.PROBE)
        nexus = self.townhalls.random
        if not nexus.is_idle and not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
            nexuses = self.structures(UnitTypeId.NEXUS)
            abilities = await self.get_available_abilities(nexuses)
            for loop_nexus, abilities_nexus in zip(nexuses, abilities):
                if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities_nexus:
                    loop_nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus)
                    break

    async def CHRONOBOOSTENERGYCOST_upgrade(self):
        if self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready:
            vc = self.structures(UnitTypeId.TWILIGHTCOUNCIL).random
            if not vc.is_idle and not vc.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                nexuses = self.structures(UnitTypeId.NEXUS)
                abilities = await self.get_available_abilities(nexuses)
                for loop_nexus, abilities_nexus in zip(nexuses, abilities):
                    if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities_nexus:
                        loop_nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, vc)

        if self.structures(UnitTypeId.FORGE).ready:
            bf = self.structures(UnitTypeId.FORGE).random
            if not bf.is_idle and not bf.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                nexuses = self.structures(UnitTypeId.NEXUS)
                abilities = await self.get_available_abilities(nexuses)
                for loop_nexus, abilities_nexus in zip(nexuses, abilities):
                    if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities_nexus:
                        loop_nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, bf)

    async def build_vespene(self):
        for nexus in self.structures(UnitTypeId.NEXUS).ready:
            gases = self.vespene_geyser.closer_than(10, nexus)
            for gas in gases:
                # 检查是否有足够的资源建造同化炉
                if not self.can_afford(UnitTypeId.ASSIMILATOR):
                    return

                # 检查气矿周围是否已有工人正在前往建造
                moving_workers = [worker for worker in self.workers.closer_than(5, gas) if worker.is_moving]
                if moving_workers:
                    continue

                # 选择一个建造工人
                worker = self.select_build_worker(gas.position)
                if worker is None:
                    return

                # 如果气矿周围没有同化炉，就分配工人去建造
                if not self.units(UnitTypeId.ASSIMILATOR).closer_than(1.0, gas).exists:
                    worker.build(UnitTypeId.ASSIMILATOR, gas)
                    return  # 建造完一个同化炉后结束函数执行

    async def building_supply(self):
        # 定义选择最佳位置的函数

        # 05:00 - 06:00 时间段
        if '05:00' <= self.time_formatted <= '06:00':
            if self.supply_left <= 3 and self.already_pending(UnitTypeId.PYLON) <= 2 and not self.supply_cap == 200:
                if self.can_afford(UnitTypeId.PYLON):
                    best_base = self.find_best_base_for_pylon()
                    best_position = self.find_optimal_pylon_position_for_base(best_base)

                    await self.build(UnitTypeId.PYLON, near=best_position, placement_step=2)

        # 06:00 - 07:00 时间段
        if '06:00' <= self.time_formatted <= '07:00':
            if self.supply_left <= 5 and self.already_pending(UnitTypeId.PYLON) <= 4 and not self.supply_cap == 200:
                if self.can_afford(UnitTypeId.PYLON):
                    best_base = self.find_best_base_for_pylon()
                    best_position = self.find_optimal_pylon_position_for_base(best_base)
                    await self.build(UnitTypeId.PYLON, near=best_position, placement_step=2)

        # 06:00 - 08:00 时间段
        if '06:00' <= self.time_formatted <= '08:00':
            if self.supply_left <= 5 and self.already_pending(UnitTypeId.PYLON) <= 3 and not self.supply_cap == 200:
                if self.can_afford(UnitTypeId.PYLON):
                    best_base = self.find_best_base_for_pylon()
                    best_position = self.find_optimal_pylon_position_for_base(best_base)
                    await self.build(UnitTypeId.PYLON, near=best_position, placement_step=2)

        # 08:00 - 10:00 时间段
        if '08:00' <= self.time_formatted <= '10:00':
            if self.supply_left <= 7 and self.already_pending(UnitTypeId.PYLON) <= 4 and not self.supply_cap == 200:
                if self.can_afford(UnitTypeId.PYLON):
                    best_base = self.find_best_base_for_pylon()
                    best_position = self.find_optimal_pylon_position_for_base(best_base)
                    await self.build(UnitTypeId.PYLON, near=best_position, placement_step=2)

        # 10:00 之后的时间段
        if '10:00' <= self.time_formatted:
            if self.supply_left <= 7 and self.already_pending(UnitTypeId.PYLON) <= 4 and not self.supply_cap == 200:
                if self.can_afford(UnitTypeId.PYLON):
                    best_base = self.find_best_base_for_pylon()
                    best_position = self.find_optimal_pylon_position_for_base(best_base)
                    await self.build(UnitTypeId.PYLON, near=best_position, placement_step=2)

    async def expansion(self):
        if self.time_formatted <= '09:00':
            if self.minerals > 1000:
                if not self.already_pending(UnitTypeId.NEXUS) and self.can_afford(
                        UnitTypeId.NEXUS) and self.townhalls.amount + self.already_pending(UnitTypeId.NEXUS) < 5:
                    location = await self.get_next_expansion()
                    if location:
                        worker = self.select_build_worker(location)
                        if worker and self.can_afford(UnitTypeId.NEXUS):
                            worker.build(UnitTypeId.NEXUS, location)
        elif self.time_formatted >= '09:00':
            if self.minerals > 1000:
                if not self.already_pending(UnitTypeId.NEXUS) and self.can_afford(
                        UnitTypeId.COMMANDCENTER) and self.townhalls.amount + self.already_pending(
                    UnitTypeId.NEXUS) < 7:
                    location = await self.get_next_expansion()
                    if location:
                        worker = self.select_build_worker(location)
                        if worker and self.can_afford(UnitTypeId.NEXUS):
                            worker.build(UnitTypeId.NEXUS, location)
        if self.minerals > 500 and self.vespene > 300 and self.time_formatted <= '08:00':
            if self.structures(UnitTypeId.GATEWAY).amount + self.structures(
                    UnitTypeId.WARPGATE).amount + self.already_pending(
                UnitTypeId.GATEWAY) < 10 and self.already_pending(
                UnitTypeId.GATEWAY) <= 4 and self.can_afford(UnitTypeId.GATEWAY):
                if self.can_afford(UnitTypeId.GATEWAY):
                    await self.handle_action_build_building(UnitTypeId.GATEWAY)

        if self.minerals > 700 and self.vespene > 400 and '08:00' <= self.time_formatted <= '12:00':
            if self.structures(UnitTypeId.GATEWAY).amount + self.structures(
                    UnitTypeId.WARPGATE).amount + self.already_pending(
                UnitTypeId.GATEWAY) < 14 and self.already_pending(
                UnitTypeId.GATEWAY) <= 4 and self.can_afford(UnitTypeId.GATEWAY):
                if self.can_afford(UnitTypeId.GATEWAY):
                    await self.handle_action_build_building(UnitTypeId.GATEWAY)

        if self.minerals > 1000 and '14:00' <= self.time_formatted and self.townhalls.amount >= 4:

            if self.structures(UnitTypeId.GATEWAY).amount + self.structures(
                    UnitTypeId.WARPGATE).amount < 20 and self.already_pending(
                UnitTypeId.GATEWAY) <= 4 and self.can_afford(UnitTypeId.GATEWAY):
                if self.can_afford(UnitTypeId.GATEWAY):
                    if self.can_afford(UnitTypeId.GATEWAY):
                        await self.handle_action_build_building(UnitTypeId.GATEWAY)

    async def attack(self, iteration):
        # 设定进攻目标为敌方的主基地出生点
        target = self.enemy_start_locations[0]

        # 根据军队规模决定是否开始进攻
        if self.supply_army > ATTACK_START_THRESHOLD:
            self.is_attacking = True
        elif self.supply_army < ATTACK_STOP_THRESHOLD:
            self.is_attacking = False

        # 如果决定进攻
        if self.is_attacking and self.supply_army > 70:
            if not self.temp1:
                # 重新设置防守列表
                self.assign_defend_units(iteration)

            MILITARY_UNITS = [unit for unit in self.get_military_units() if unit not in self.defend_units]
            # 进攻逻辑
            if not self.rally_defend:
                if not self.temp1 or not self.temp2:
                    nearby_enemies = self.enemy_units.closer_than(NEARBY_ENEMY_DISTANCE, target) + \
                                     self.enemy_structures.closer_than(NEARBY_ENEMY_DISTANCE, target)

                    assigned_targets = set()

                    for unit in MILITARY_UNITS:
                        if unit.order_target in nearby_enemies and unit.order_target not in assigned_targets:
                            assigned_targets.add(unit.order_target)
                            continue

                        unassigned_enemies = [enemy for enemy in nearby_enemies if enemy not in assigned_targets]
                        if unassigned_enemies:
                            closest_enemy = min(unassigned_enemies, key=lambda enemy: unit.distance_to(enemy))
                            assigned_targets.add(closest_enemy)
                            unit.attack(closest_enemy)
                        else:
                            unit.attack(target)

                    # 判断是否已经接近敌方基地，如果是，则表示进攻已经开始
                    if any(unit.distance_to(target) < 10 for unit in MILITARY_UNITS):
                        self.temp1 = True

                # 如果敌方基地附近没有敌人，认为基地已被摧毁
                if not self.temp2:
                    if not (self.enemy_units.closer_than(20, target) or self.enemy_structures.closer_than(20, target)):
                        self.temp2 = True

                # 如果进攻已开始，并且敌方基地已被摧毁，执行新的战略
                if self.temp1 and self.temp2:
                    # 攻击可见敌人
                    if iteration - self.last_attack_visible_iter >= WAIT_ITER_FOR_KILL_VISIBLE:
                        if self.enemy_units:
                            for unit in MILITARY_UNITS:
                                unit.attack(self.enemy_units.closest_to(unit.position))
                        self.last_attack_visible_iter = iteration

                    # 分配单位到资源点
                    if iteration - self.last_cluster_assignment_iter >= WAIT_ITER_FOR_CLUSTER_ASSIGN:
                        await self.assign_units_to_resource_clusters()
                        self.last_cluster_assignment_iter = iteration
    #
    # async def attack(self, iteration):
    #     # 设定进攻目标为敌方的主基地出生点
    #     target = self.enemy_start_locations[0]
    #
    #     if self.supply_army > ATTACK_START_THRESHOLD:
    #         self.is_attacking = True
    #     elif self.supply_army < ATTACK_STOP_THRESHOLD:
    #         self.is_attacking = False
    #
    #     if self.is_attacking and self.supply_army > 70:
    #         if not self.temp1:
    #             # 重新设置防守列表
    #             self.assign_defend_units(iteration)
    #
    #         MILITARY_UNITS = [unit for unit in self.get_military_units() if unit not in self.defend_units]
    #         print("MILITARY_UNITS", MILITARY_UNITS)
    #         print("len if MILITARY_UNITS", len(MILITARY_UNITS))
    #         if not self.rally_defend:
    #             if not self.temp1 or not self.temp2:
    #                 # 获取目标附近的所有敌方单位和建筑
    #                 nearby_enemies = self.enemy_units.closer_than(NEARBY_ENEMY_DISTANCE,
    #                                                               target) + self.enemy_structures.closer_than(
    #                     NEARBY_ENEMY_DISTANCE, target)
    #
    #                 # 创建一个集合来跟踪已经被分配目标的敌人
    #                 assigned_targets = set()
    #
    #                 # 为每个单位分配一个目标
    #                 for unit in MILITARY_UNITS:
    #                     if unit.order_target in nearby_enemies and unit.order_target not in assigned_targets:  # 如果单位的当前目标仍然有效，并且没有其他单位 targeting 它
    #                         assigned_targets.add(unit.order_target)  # 记录这个目标，以免其他单位重复 targeting
    #                         continue
    #
    #                     # 寻找一个未被分配的最近敌人
    #                     unassigned_enemies = [enemy for enemy in nearby_enemies if enemy not in assigned_targets]
    #                     if unassigned_enemies:
    #                         closest_enemy = min(unassigned_enemies, key=lambda enemy: unit.distance_to(enemy))
    #                         assigned_targets.add(closest_enemy)  # 记录这个目标，以免其他单位重复 targeting
    #                         unit.attack(closest_enemy)
    #                     else:
    #                         # 如果附近没有未分配的敌人，单位应向主要目标（例如敌方基地）前进
    #                         unit.attack(target)
    #
    #                 if any(unit.distance_to(target) < 10 for unit in MILITARY_UNITS):
    #                     self.temp1 = True
    #             elif not self.temp2:
    #                 if not (self.enemy_units.closer_than(20, target) or self.enemy_structures.closer_than(20, target)):
    #                     self.temp2 = True
    #
    #             # 如果满足条件
    #             if self.temp1 and self.temp2:
    #                 # 每隔WAIT_ITER_FOR_KILL_VISIBLE步数进攻所有可见的敌方单位
    #                 if iteration - self.last_attack_visible_iter >= WAIT_ITER_FOR_KILL_VISIBLE:
    #                     if self.enemy_units:
    #                         for unit in MILITARY_UNITS:
    #                             unit.attack(self.enemy_units.closest_to(unit.position))
    #                     self.last_attack_visible_iter = iteration
    #
    #                 # 每隔WAIT_ITER_FOR_CLUSTER_ASSIGN步数分散部队到资源点
    #                 if iteration - self.last_cluster_assignment_iter >= WAIT_ITER_FOR_CLUSTER_ASSIGN:
    #                     await self.assign_units_to_resource_clusters()
    #                     self.last_cluster_assignment_iter = iteration



    async def assign_units_to_resource_clusters(self):
        self.assigned_to_clusters = True

        # 获取所有进攻的的军事单位
        MILITARY_UNITS = [unit for unit in self.get_military_units() if unit not in self.defend_units]
        # 获取所有资源集群位置
        resource_clusters = self.expansion_locations_list

        if MILITARY_UNITS and resource_clusters:
            # 计算每个资源集群需要分配的单位数量
            group_size = len(MILITARY_UNITS) // len(resource_clusters)

            # 将军事单位分组并分配给每个资源集群
            for i, target in enumerate(resource_clusters):
                for unit in MILITARY_UNITS[i * group_size:(i + 1) * group_size]:
                    unit.attack(target)
                    unit.assigned_resource_cluster = True  # 标记该单位已经被分配


    async def defend(self, iteration):
        EXCLUDED_UNITS = {UnitTypeId.OVERSEER}
        DEFEND_UNIT_ASSIGN_INTERVAL = 10  # 这里假设你有一个间隔时间，你可以根据需要调整
        MILITARY_UNITS = self.get_military_units()

        close_enemy_units = [enemy for enemy in self.enemy_units if enemy.type_id not in EXCLUDED_UNITS and
                             any(nexus.distance_to(enemy) < 20 for nexus in self.townhalls)]
        close_enemy_count = len(close_enemy_units)

        # 如果没有开始进攻，所有单位都可以防守
        if not self.temp1:
            defending_units = MILITARY_UNITS
        else:
            # 判断是否需要重新划分防守单位
            if not self.defend_units or iteration - self.last_defend_units_assign_iter >= DEFEND_UNIT_ASSIGN_INTERVAL:
                self.assign_defend_units(iteration)

            defending_units = self.defend_units

        # 欧氏距离函数
        def euclidean_distance(unit1, unit2):
            return ((unit1.position.x - unit2.position.x) ** 2 + (unit1.position.y - unit2.position.y) ** 2) ** 0.5

        # 根据敌人数量判断如何防守
        if close_enemy_count > 10:
            self.rally_defend = True
            additional_defenders = [unit for unit in MILITARY_UNITS if unit not in defending_units][
                                   :close_enemy_count // 2]
            defending_units.extend(additional_defenders)
            for unit in defending_units:
                if close_enemy_units:  # 添加检查
                    closest_enemy = min(close_enemy_units, key=lambda enemy: euclidean_distance(unit, enemy))
                    unit.attack(closest_enemy)
        elif close_enemy_count > 0:
            for unit in defending_units:
                if close_enemy_units:  # 添加检查
                    closest_enemy = min(close_enemy_units, key=lambda enemy: euclidean_distance(unit, enemy))
                    unit.attack(closest_enemy)
        else:
            self.rally_defend = False



    def select_target(self) -> Point2:
        # 要排除的单位类型
        EXCLUDED_UNITS = {UnitTypeId.LARVA, UnitTypeId.CHANGELING, UnitTypeId.EGG}

        # 如果有敌方建筑，随机选择一个作为目标
        if self.enemy_structures:
            return random.choice(self.enemy_structures).position
        # 如果没有敌方建筑但有敌方单位，从非排除的单位中随机选择一个作为目标
        elif self.enemy_units:
            valid_enemy_units = [unit for unit in self.enemy_units if unit.type_id not in EXCLUDED_UNITS]
            if valid_enemy_units:  # 如果还有有效的敌方单位
                return random.choice(valid_enemy_units).position
        # 如果没有有效的敌方单位或建筑，选择敌方的出生点作为目标
        return self.enemy_start_locations[0]

    async def research_blink(self):
        if UpgradeId.CHARGE in self.state.upgrades and self.structures(UnitTypeId.TWILIGHTCOUNCIL).exists:
            vc = self.structures(UnitTypeId.TWILIGHTCOUNCIL).random
            abilities = await self.get_available_abilities(vc)
            if self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready and self.already_pending(UpgradeId.BLINKTECH) == 0:
                if self.can_afford(UpgradeId.BLINKTECH) and vc.is_idle and AbilityId.RESEARCH_BLINK in abilities:
                    vc.research(UpgradeId.BLINKTECH)

    async def stalker_blink(self):
        if self.units(UnitTypeId.STALKER).exists and UpgradeId.BLINKTECH in self.state.upgrades:

            stalkers = self.units(UnitTypeId.STALKER)
            for stalker in stalkers:
                abilities = await self.get_available_abilities(stalker)
                if (
                        stalker.health_percentage < .5
                        and stalker.shield_health_percentage < .3
                        and AbilityId.EFFECT_BLINK_STALKER in abilities
                ):
                    if self.enemy_units:
                        enemy = self.enemy_units.closest_to(stalker)
                        stalker(AbilityId.EFFECT_BLINK_STALKER, stalker.position.towards(enemy, -6))

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
        maps.get(LADDER_MAP_2023[0]),
        [Bot(Race.Protoss, WarpGateBot()), Computer(Race.Terran, Difficulty.Medium, ai_build=AIBuild.Timing)],
        realtime=False,
    )


if __name__ == "__main__":
    main()
