from sc2_rl_agent.starcraftenv_test.techtree.techtree import Building, Unit, Upgrade
from typing import List, Dict, Any, Optional
from sc2_rl_agent.starcraftenv_test.techtree.StarCraftTechTree import StarCraftTechTree


class ProtossTechTree(StarCraftTechTree):
    """
    Protoss 科技树类，它继承自基础的 StarCraftTechTree 类。
    该类的目的是为了预加载 Protoss 种族的科技树，并为用户提供查询接口。
    """

    def __init__(self):
        """
        初始化 Protoss 科技树。
        """
        super().__init__()
        self._init_buildings()
        self._init_units()
        self._init_technologies()

    def _init_buildings(self):
        """初始化 Protoss 的建筑"""
        """initial building"""
        self.nexus = Building("Nexus")
        self.pylon = Building("Pylon")
        self.assimilator = Building("Assimilator")

        """nexus unlocked buildings"""
        self.gateway = Building("Gateway", prerequisite_buildings=[self.nexus])
        self.forge = Building("Forge", prerequisite_buildings=[self.nexus])

        """gate unlocked buildings"""
        self.cybernetics_core = Building("Cybernetics Core", prerequisite_buildings=[self.gateway])

        """cybernetics core unlocked buildings"""
        self.robotics_facility = Building("Robotics Facility", prerequisite_buildings=[self.cybernetics_core])
        self.stargate = Building("StarGate", prerequisite_buildings=[self.cybernetics_core])
        self.twilight_council = Building("Twilight Council", prerequisite_buildings=[self.cybernetics_core])
        self.shield_battery = Building("Shield Battery", prerequisite_buildings=[self.cybernetics_core])

        """forge unlocked buildings"""
        self.photon_cannon = Building("Photon Cannon", prerequisite_buildings=[self.forge])

        """robotics facility unlocked buildings"""
        self.robotics_bay = Building("Robotics Bay", prerequisite_buildings=[self.robotics_facility])

        """stargate unlocked buildings"""
        self.fleet_beacon = Building("Fleet Beacon", prerequisite_buildings=[self.stargate])

        """twilight_council unlocked buildings"""
        self.templar_archive = Building("Templar Archive", prerequisite_buildings=[self.twilight_council])
        self.dark_shrine = Building("Dark Shrine", prerequisite_buildings=[self.twilight_council])

        # 加入到科技树
        """initial building"""
        self.add_building(self.nexus)
        self.add_building(self.pylon)
        self.add_building(self.assimilator)

        """nexus unlocked buildings"""
        self.add_building(self.gateway)
        self.add_building(self.forge)

        """gate unlocked buildings"""
        self.add_building(self.cybernetics_core)

        """cybernetics core unlocked buildings"""
        self.add_building(self.robotics_facility)
        self.add_building(self.stargate)
        self.add_building(self.twilight_council)
        self.add_building(self.shield_battery)

        """forge unlocked buildings"""
        self.add_building(self.photon_cannon)

        """robotics facility unlocked buildings"""
        self.add_building(self.robotics_bay)

        """stargate unlocked buildings"""
        self.add_building(self.fleet_beacon)

        """twilight_council unlocked buildings"""
        self.add_building(self.templar_archive)
        self.add_building(self.dark_shrine)

        self.add_building(self.robotics_bay)

    def _init_units(self):
        """初始化 Protoss 的单位"""

        """nexus unlocked unit"""
        self.probe = Unit("Probe", prerequisite_buildings=[self.nexus])

        """gateway unlocked unit"""
        self.zealot = Unit("Zealot", prerequisite_buildings=[self.gateway])

        """cybernetics core unlocked unit"""
        self.stalker = Unit("Stalker", prerequisite_buildings=[self.cybernetics_core])
        self.adept = Unit("Adept", prerequisite_buildings=[self.cybernetics_core])
        self.sentry = Unit("Sentry", prerequisite_buildings=[self.cybernetics_core])

        """robotics facility unlocked unit"""
        self.observer = Unit("Observer", prerequisite_buildings=[self.robotics_facility])
        self.immortal = Unit("Immortal", prerequisite_buildings=[self.robotics_facility])
        self.warp_prism = Unit("Warp Prism", prerequisite_buildings=[self.robotics_facility])

        """robotics bay unlocked unit"""
        self.colossus = Unit("Colossus", prerequisite_buildings=[self.robotics_bay])
        self.disruptor = Unit("Disruptor", prerequisite_buildings=[self.robotics_bay])

        """stargate unlocked unit"""
        self.phoenix = Unit("Phoenix", prerequisite_buildings=[self.stargate])
        self.oracle = Unit("Oracle", prerequisite_buildings=[self.stargate])
        self.void_ray = Unit("Void Ray", prerequisite_buildings=[self.stargate])

        """fleet beacon unlocked unit"""
        self.tempest = Unit("Tempest", prerequisite_buildings=[self.fleet_beacon])
        self.carrier = Unit("Carrier", prerequisite_buildings=[self.fleet_beacon])
        self.mothership = Unit("Mothership", prerequisite_buildings=[self.fleet_beacon])

        """templar archive unlocked unit"""
        self.high_templar = Unit("High Templar", prerequisite_buildings=[self.templar_archive])

        """dark shrine unlocked unit"""
        self.dark_templar = Unit("Dark Templar", prerequisite_buildings=[self.dark_shrine])

        """templar unlocked unit"""
        self.archon = Unit("Archon", prerequisite_units=[self.dark_templar, self.high_templar])

        # 加入到科技树
        """nexus unlocked unit"""
        self.add_unit(self.probe)

        """gateway unlocked unit"""
        self.add_unit(self.zealot)

        """cybernetics core unlocked unit"""
        self.add_unit(self.stalker)
        self.add_unit(self.adept)
        self.add_unit(self.sentry)

        """robotics facility unlocked unit"""
        self.add_unit(self.observer)
        self.add_unit(self.immortal)
        self.add_unit(self.warp_prism)

        """robotics bay unlocked unit"""
        self.add_unit(self.colossus)
        self.add_unit(self.disruptor)

        """stargate unlocked unit"""
        self.add_unit(self.phoenix)
        self.add_unit(self.oracle)
        self.add_unit(self.void_ray)

        """fleet beacon unlocked unit"""
        self.add_unit(self.tempest)
        self.add_unit(self.carrier)
        self.add_unit(self.mothership)

        """templar archive unlocked unit"""
        self.add_unit(self.high_templar)

        """dark shrine unlocked unit"""
        self.add_unit(self.dark_templar)

        """templar unlocked unit"""
        self.add_unit(self.archon)

    def _init_technologies(self):
        """初始化 Protoss 的科技"""
        """cybernetics core unlocked technology"""
        self.warpgate_research = Upgrade("Warp Gate Research", prerequisite_buildings=[self.cybernetics_core])

        """cybernetics core L1 upgrade"""
        self.air_weapon_level_1 = Upgrade("Air Weapon Level 1", prerequisite_buildings=[self.cybernetics_core])
        self.air_armor_level_1 = Upgrade("Air Armor Level 1", prerequisite_buildings=[self.cybernetics_core])

        """cybernetics core L2 upgrade"""
        self.air_weapon_level_2 = Upgrade("Air Weapon Level 2", prerequisite_buildings=[self.fleet_beacon],
                                          prerequisite_upgrades=[self.air_weapon_level_1])
        self.air_armor_level_2 = Upgrade("Air Armor Level 2", prerequisite_buildings=[self.fleet_beacon],
                                         prerequisite_upgrades=[self.air_armor_level_1])

        """cybernetics core L3 upgrade"""

        self.air_weapon_level_3 = Upgrade("Air Weapon Level 3", prerequisite_buildings=[self.fleet_beacon],
                                          prerequisite_upgrades=[self.air_weapon_level_2])
        self.air_armor_level_3 = Upgrade("Air Armor Level 3", prerequisite_buildings=[self.fleet_beacon],
                                         prerequisite_upgrades=[self.air_armor_level_2])

        """Forge unlocked technology"""
        """Forge L1 upgrade"""
        self.ground_weapon_level_1 = Upgrade("Ground Weapon Level 1", prerequisite_buildings=[self.forge])
        self.ground_armor_level_1 = Upgrade("Ground Armor Level 1", prerequisite_buildings=[self.forge])
        self.ground_shield_level_1 = Upgrade("Ground Shield Level 1", prerequisite_buildings=[self.forge])

        """twilight council unlocked technology"""
        self.charge = Upgrade("Charge", prerequisite_buildings=[self.twilight_council])
        self.blink = Upgrade("Blink", prerequisite_buildings=[self.twilight_council])
        self.resonating_glaives = Upgrade("Resonating Glaives", prerequisite_buildings=[self.twilight_council])

        """Forge L2 upgrade"""
        self.ground_weapon_level_2 = Upgrade("Ground Weapon Level 2", prerequisite_buildings=[self.twilight_council],
                                             prerequisite_upgrades=[self.ground_weapon_level_1])
        self.ground_armor_level_2 = Upgrade("Ground Armor Level 2", prerequisite_buildings=[self.twilight_council],
                                            prerequisite_upgrades=[self.ground_armor_level_1])
        self.shields_level_2 = Upgrade("Shields Level 2", prerequisite_buildings=[self.twilight_council],
                                       prerequisite_upgrades=[self.ground_shield_level_1])

        """Forge L3 upgrade"""
        self.ground_weapon_level_3 = Upgrade("Ground Weapon Level 3", prerequisite_buildings=[self.twilight_council],
                                             prerequisite_upgrades=[self.ground_weapon_level_2])
        self.ground_armor_level_3 = Upgrade("Ground Armor Level 3", prerequisite_buildings=[self.twilight_council],
                                            prerequisite_upgrades=[self.ground_armor_level_2])
        self.shields_level_3 = Upgrade("Shields Level 3", prerequisite_buildings=[self.twilight_council],
                                       prerequisite_upgrades=[self.shields_level_2])

        """Robotics bay unlocked technology"""
        self.extended_thermal_lance = Upgrade("Extended Thermal Lance", prerequisite_buildings=[self.robotics_bay])
        self.gravitivc_drive = Upgrade("Gravitic Drive", prerequisite_buildings=[self.robotics_bay])
        self.observer_gravitic_boosters = Upgrade("Observer Gravitic Boosters",
                                                  prerequisite_buildings=[self.robotics_bay])

        """Fleet beacon unlocked technology"""
        self.void_ray_speed_upgrade = Upgrade("Void Ray Speed Upgrade", prerequisite_buildings=[self.fleet_beacon])
        self.phoneix_range_upgrade = Upgrade("Phoneix Range Upgrade", prerequisite_buildings=[self.fleet_beacon])
        self.tempest_ground_attack_upgrade = Upgrade("Tempest Ground Attack Upgrade",
                                                     prerequisite_buildings=[self.fleet_beacon])

        """Templar archive unlocked technology"""
        self.psi_storm = Upgrade("Psi Storm", prerequisite_buildings=[self.templar_archive])

        """Dark shrine unlocked technology"""
        self.shadow_stride = Upgrade("Shadow Stride", prerequisite_buildings=[self.dark_shrine])

        # 加入到科技树
        self.add_upgrade(self.warpgate_research)
        """Forge L1 upgrade"""
        self.add_upgrade(self.ground_weapon_level_1)
        self.add_upgrade(self.ground_armor_level_1)
        self.add_upgrade(self.ground_shield_level_1)

        """twilight council unlocked technology"""
        self.add_upgrade(self.charge)
        self.add_upgrade(self.blink)
        self.add_upgrade(self.resonating_glaives)

        """Forge L2 upgrade"""
        self.add_upgrade(self.ground_weapon_level_2)
        self.add_upgrade(self.ground_armor_level_2)
        self.add_upgrade(self.shields_level_2)

        """Forge L3 upgrade"""
        self.add_upgrade(self.ground_weapon_level_3)
        self.add_upgrade(self.ground_armor_level_3)
        self.add_upgrade(self.shields_level_3)

        """Robotics bay unlocked technology"""
        self.add_upgrade(self.extended_thermal_lance)
        self.add_upgrade(self.gravitivc_drive)
        self.add_upgrade(self.observer_gravitic_boosters)

        """Fleet beacon unlocked technology"""
        self.add_upgrade(self.void_ray_speed_upgrade)
        self.add_upgrade(self.phoneix_range_upgrade)
        self.add_upgrade(self.tempest_ground_attack_upgrade)

        """Templar archive unlocked technology"""
        self.add_upgrade(self.psi_storm)

        """Dark shrine unlocked technology"""
        self.add_upgrade(self.shadow_stride)

        """cybernetics core L1 upgrade"""
        self.add_upgrade(self.air_weapon_level_1)
        self.add_upgrade(self.air_armor_level_1)

        """cybernetics core L2 upgrade"""
        self.add_upgrade(self.air_weapon_level_2)
        self.add_upgrade(self.air_armor_level_2)

        """cybernetics core L3 upgrade"""
        self.add_upgrade(self.air_weapon_level_3)
        self.add_upgrade(self.air_armor_level_3)

    # 可以在这里添加其他方法或功能
    def get_building_unlocks(self, building_name: str):
        """
        查询指定建筑解锁的所有建筑、单位和技术。

        输入:
        - building_name (str): 建筑的名称。

        返回:
        - dict: 包含 "buildings"、"units" 和 "technologies" 三个键的字典，它们的值都是列表。

        示例:
        get_building_unlocks("Robotics Facility")
        返回: {'buildings': ['Robotics Bay'], 'units': ['Immortal'], 'technologies': []}
        """
        return super().get_building_unlocks(building_name)

    def get_full_prerequisites(self, tech_name: str, category: str = "buildings", depth: int = None, visited=None,
                               current_depth=1) -> Dict[int, Dict[str, List[str]]]:
        """
        查询指定技术名称的全部先决条件。
        """
        return super().get_full_prerequisites(tech_name, category, depth, visited, current_depth)
    def get_unit_prerequisites(self, unit_name: str):
        """
        Retrieve the prerequisites required to produce a specific Protoss unit.

        :param unit_name: The name of the Protoss unit.
        :return: A dictionary listing all prerequisites categorized as "buildings", "units", and "upgrades".

        Example:
            tech_tree = ProtossTechTree()
            prerequisites = tech_tree.get_unit_prerequisites("Stalker")
            print(prerequisites)
            # Might return:
            # {'buildings': ['Cybernetics Core'], 'units': [], 'upgrades': []}
        """
        return super().get_unit_prerequisites(unit_name)

    def get_upgrade_prerequisites(self, upgrade_name: str):
        """
        Retrieve the prerequisites required for a specific Protoss upgrade.

        :param upgrade_name: The name of the Protoss upgrade.
        :return: A dictionary listing all prerequisites categorized as "buildings", "units", and "upgrades".

        Example:
            tech_tree = ProtossTechTree()
            prerequisites = tech_tree.get_upgrade_prerequisites("Warp Gate Research")
            print(prerequisites)
            # Might return:
            # {'buildings': ['Cybernetics Core'], 'units': [], 'upgrades': []}
        """
        return super().get_upgrade_prerequisites(upgrade_name)

    def extract_prerequisites_names(self, tech_name: str, category: str = "buildings", depth: int = None) -> List[str]:
        """
        Extract the names of all prerequisites for a given technology in the Protoss tech tree.

        This function fetches the entire chain of prerequisites for the specified technology
        and returns a list of their names. It's useful for quickly identifying all the requirements
        to reach a specific tech without needing to navigate through nested dictionaries.

        :param tech_name: The name of the technology (building, unit, or upgrade).
        :param category: The category of the technology. It can be "buildings", "units", or "upgrades".
        :param depth: The depth to which prerequisites should be fetched.
                      If None, it fetches all levels of prerequisites.
                      If set to a number, it fetches prerequisites only up to that depth.
        :return: A list containing the names of all prerequisites for the given technology.

        Example:
            tech_tree = ProtossTechTree()

            prerequisites = tech_tree.extract_prerequisites_names("Stalker")
            print(prerequisites)
            # Might return:
            # ['Gateway', 'Cybernetics Core']

            prerequisites_depth_1 = tech_tree.extract_prerequisites_names("Stalker", depth=1)
            print(prerequisites_depth_1)
            # Might return:
            # ['Cybernetics Core']
        """
        full_prerequisites = self.get_full_prerequisites(tech_name, category, depth)

        # Extract all prerequisite names
        prerequisites_names = []
        for depth_key in full_prerequisites:
            for cat_key in full_prerequisites[depth_key]:
                prerequisites_names.extend(full_prerequisites[depth_key][cat_key])

        return list(set(prerequisites_names))  # Return a deduplicated list


    def extract_prerequisites_structure(self, tech_name: str, category: str = "buildings", depth: int = None) -> Dict[
        int, Dict[str, str]]:
        """
        Extract a structured representation of all prerequisites for a given technology in the Protoss tech tree.

        :param tech_name: The name of the technology (building, unit, or upgrade).
        :param category: The category of the technology. It can be "buildings", "units", or "upgrades".
        :param depth: The depth to which prerequisites should be fetched.
                      If None, it fetches all levels of prerequisites.
                      If set to a number, it fetches prerequisites only up to that depth.
        :return: A dictionary where each key is a depth level and values are another dictionary containing
                 the technologies and their category.

        Example:
            tech_tree = ProtossTechTree()

            prerequisites = tech_tree.extract_prerequisites_structure("Stalker")
            # Might return:
            # {1: {'Stalker': 'units'},
            #  2: {'Cybernetics Core': 'buildings'},
            #  3: {'Gateway': 'buildings'},
            #  4: {'Nexus': 'buildings'}}
        """
        full_prerequisites = self.get_full_prerequisites(tech_name, category, depth)

        # Convert the structure from depth-wise to tech-wise
        structured_prerequisites = {}
        for depth_key in full_prerequisites:
            structured_prerequisites[depth_key] = {}
            for cat_key in full_prerequisites[depth_key]:
                for tech in full_prerequisites[depth_key][cat_key]:
                    structured_prerequisites[depth_key][tech] = cat_key

        # Filter out empty depths
        structured_prerequisites = {k: v for k, v in structured_prerequisites.items() if v}

        return structured_prerequisites


protoss_tech_tree = ProtossTechTree()
print(protoss_tech_tree.get_full_prerequisites("Gateway"))
print(protoss_tech_tree.extract_prerequisites_names("Psi Storm",category="upgrades"))
print(protoss_tech_tree.get_building_unlocks("Cybernetics Core"))
print(protoss_tech_tree.get_unit_prerequisites("Dark Templar"))
print(protoss_tech_tree.get_upgrade_prerequisites("Psi Storm"))
print(protoss_tech_tree.extract_prerequisites_structure("Shields Level 3",category="upgrades"))




