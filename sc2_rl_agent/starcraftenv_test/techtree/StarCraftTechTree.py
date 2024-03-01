from sc2_rl_agent.starcraftenv_test.techtree.techtree import Building, Unit, Upgrade
from typing import List, Dict, Any, Optional



class StarCraftTechTree:
    def __init__(self):
        # Dictionaries to store buildings, units, and upgrades.
        # 初始化三个字典，分别存储建筑、单位和技术。
        self.buildings = {}
        self.units = {}
        self.upgrades = {}

    def _add_prerequisites_to_unlocks(self, tech):
        """
        Private helper function to update the 'unlocks' attributes of tech's prerequisites.
        私有辅助函数，用于更新技术的先决条件的 'unlocks' 属性。
        """
        tech_type = None
        if isinstance(tech, Building):
            tech_type = 'buildings'
        elif isinstance(tech, Unit):
            tech_type = 'units'
        elif isinstance(tech, Upgrade):
            tech_type = 'upgrades'
        else:
            raise ValueError(f"Unknown tech type: {type(tech)}")

        for prereq in tech.prerequisites["buildings"]:
            self.buildings[prereq.name].unlocks[tech_type].append(tech)

        for prereq in tech.prerequisites["units"]:
            self.units[prereq.name].unlocks[tech_type].append(tech)

        for prereq in tech.prerequisites["upgrades"]:
            self.upgrades[prereq.name].unlocks[tech_type].append(tech)


    def add_building(self, building: Building):
        """
        Add a building to the tech tree and update relevant unlocks.
        向技术树中添加一个建筑并更新相关的解锁。
        """
        self.buildings[building.name] = building
        self._add_prerequisites_to_unlocks(building)

    def add_unit(self, unit: Unit):
        """
        Add a unit to the tech tree and update relevant unlocks.
        向技术树中添加一个单位并更新相关的解锁。
        """
        self.units[unit.name] = unit
        self._add_prerequisites_to_unlocks(unit)

    def add_upgrade(self, upgrade: Upgrade):
        """
        Add an upgrade to the tech tree and update relevant unlocks.
        向技术树中添加一个升级并更新相关的解锁。
        """
        self.upgrades[upgrade.name] = upgrade
        self._add_prerequisites_to_unlocks(upgrade)

    def get_building_unlocks(self, building_name: str):
        """
        Get all the buildings, units, and upgrades a building unlocks.
        获取一个建筑解锁的所有建筑、单位和技术。
        """
        if building_name in self.buildings:
            building = self.buildings[building_name]
            return {
                "buildings": [b.name for b in building.unlocks['buildings']],
                "units": [u.name for u in building.unlocks['units']],
                "upgrades": [t.name for t in building.unlocks['upgrades']]
            }
        else:
            return {"buildings": [], "units": [], "upgrades": []}

    def get_building_prerequisites(self, building_name: str):
        """
        Retrieves the prerequisites for a building.
        检索建筑的先决条件。
        """
        if building_name not in self.buildings:
            return None

        prerequisites = {}
        for category, items in self.buildings[building_name].prerequisites.items():
            prerequisites[category] = [item.name for item in items]

        return prerequisites

    def get_unit_prerequisites(self, unit_name: str):
        """
        Retrieves the prerequisites for a unit.
        检索单位的先决条件。
        """
        if unit_name not in self.units:
            return None

        prerequisites = {}
        for category, items in self.units[unit_name].prerequisites.items():
            prerequisites[category] = [item.name for item in items]

        return prerequisites

    def get_upgrade_prerequisites(self, upgrade_name: str):
        """
        Retrieves the prerequisites for an upgrade.
        检索升级的先决条件。
        """
        if upgrade_name not in self.upgrades:
            return None

        prerequisites = {}
        for category, items in self.upgrades[upgrade_name].prerequisites.items():
            prerequisites[category] = [item.name for item in items]

        return prerequisites

    def get_full_prerequisites(self, tech_name: str, category: str = "building", depth: int = None, visited=None,
                               current_depth=1) -> Dict[int, Dict[str, List[str]]]:
        """
        Recursively retrieves the full list of prerequisites for a technology.
        递归地检索某项技术所需的全部先决条件。
        """
        # Base cases
        if depth is not None and (not isinstance(depth, int) or depth < 0):
            raise ValueError(f"Invalid depth: {depth}. Expected a non-negative integer or None.")

        if depth == 0:
            return {}

        if category not in ["buildings", "units", "upgrades"]:
            raise ValueError(f"Invalid category: {category}. Expected 'buildings', 'units', or 'upgrades'.")

        tech = None
        if category == "buildings":
            tech = self.buildings.get(tech_name)
        elif category == "units":
            tech = self.units.get(tech_name)
        elif category == "upgrades":
            tech = self.upgrades.get(tech_name)

        if not tech:
            raise ValueError(f"Tech '{tech_name}' of type '{category}' not found.")

        if visited is None:
            visited = set()
        elif tech_name in visited:
            raise ValueError(f"Detected a cyclic dependency involving {tech_name}.")
        visited.add(tech_name)

        prerequisites = {current_depth: {"buildings": [], "units": [], "upgrades": []}}

        for cat, items in tech.prerequisites.items():
            prerequisites[current_depth][cat].extend([prereq.name for prereq in items])

            for prereq in items:
                sub_prerequisites = self.get_full_prerequisites(prereq.name, cat,
                                                                depth=depth - 1 if depth else None,
                                                                visited=visited.copy(),
                                                                current_depth=current_depth + 1)
                for sub_depth, sub_prereq in sub_prerequisites.items():
                    if sub_depth in prerequisites:
                        for sub_cat, sub_items in sub_prereq.items():
                            prerequisites[sub_depth][sub_cat].extend(sub_items)
                    else:
                        prerequisites[sub_depth] = sub_prereq

        # Removing duplicates
        for depth_key in prerequisites:
            for cat_key in prerequisites[depth_key]:
                prerequisites[depth_key][cat_key] = list(set(prerequisites[depth_key][cat_key]))

        return prerequisites


def test_starcraft_tech_tree():
    # 创建 StarCraftTechTree 对象
    tech_tree = StarCraftTechTree()

    # 添加建筑
    nexus = Building("Nexus")
    tech_tree.add_building(nexus)  # 确保首先添加 Nexus

    gateway = Building("Gateway", prerequisite_buildings=[nexus])
    tech_tree.add_building(gateway)

    cybernetics_core = Building("Cybernetics Core", prerequisite_buildings=[gateway])
    tech_tree.add_building(cybernetics_core)

    robotics_facility = Building("Robotics Facility", prerequisite_buildings=[cybernetics_core])
    tech_tree.add_building(robotics_facility)

    robotics_bay = Building("Robotics Bay", prerequisite_buildings=[robotics_facility])
    tech_tree.add_building(robotics_bay)

    forge = Building("Forge", prerequisite_buildings=[nexus])
    tech_tree.add_building(forge)

    twilight_council = Building("Twilight Council", prerequisite_buildings=[cybernetics_core])
    tech_tree.add_building(twilight_council)

    dark_shrine = Building("Dark Shrine", prerequisite_buildings=[twilight_council])
    tech_tree.add_building(dark_shrine)

    templar_archive = Building("Templar Archive", prerequisite_buildings=[twilight_council])
    tech_tree.add_building(templar_archive)

    # 添加单位
    zealot = Unit("Zealot", prerequisite_buildings=[gateway])
    tech_tree.add_unit(zealot)

    stalker = Unit("Stalker", prerequisite_buildings=[cybernetics_core])
    tech_tree.add_unit(stalker)

    immortal = Unit("Immortal", prerequisite_buildings=[robotics_facility])
    tech_tree.add_unit(immortal)

    # 添加升级
    warpgate_research = Upgrade("Warp Gate Research", prerequisite_buildings=[cybernetics_core])
    tech_tree.add_upgrade(warpgate_research)

    ground_armor_level_1 = Upgrade("Ground Armor Level 1", prerequisite_buildings=[forge])
    tech_tree.add_upgrade(ground_armor_level_1)

    ground_armor_level_2 = Upgrade("Ground Armor Level 2", prerequisite_upgrades=[ground_armor_level_1],
                                   prerequisite_buildings=[twilight_council])
    tech_tree.add_upgrade(ground_armor_level_2)

    ground_armor_level_3 = Upgrade("Ground Armor Level 3", prerequisite_upgrades=[ground_armor_level_2],
                                   prerequisite_buildings=[twilight_council])
    tech_tree.add_upgrade(ground_armor_level_3)

    dark_templar = Unit("Dark Templar", prerequisite_buildings=[dark_shrine])
    tech_tree.add_unit(dark_templar)

    high_templar = Unit("High Templar", prerequisite_buildings=[templar_archive])
    tech_tree.add_unit(high_templar)

    archon = Unit("Archon", prerequisite_units=[dark_templar, high_templar])
    tech_tree.add_unit(archon)

    # 测试并输出结果
    print("Full prerequisites for Robotics Bay:")
    print(tech_tree.get_full_prerequisites("Robotics Bay", category="buildings"))

    print("Full prerequisites for Immortal:")
    print(tech_tree.get_full_prerequisites("Immortal", category="units"))

    print("Full prerequisites for Warp Gate Research:")
    print(tech_tree.get_full_prerequisites("Warp Gate Research", category="upgrades"))

    print("\nFull prerequisites for Ground Armor Level 3:")
    print(tech_tree.get_full_prerequisites("Ground Armor Level 3", category="upgrades", depth=2))

    print("\nRequired units for Archon:")
    print(tech_tree.get_unit_prerequisites("Archon"))

    print("type of tech_tree.buildings", type(tech_tree.buildings))
    print("type of tech_tree.units", type(tech_tree.units))
    print("type of tech_tree.upgrades", type(tech_tree.upgrades))


# test_starcraft_tech_tree()
