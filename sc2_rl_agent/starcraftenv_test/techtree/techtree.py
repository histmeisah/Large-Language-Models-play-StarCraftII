class Tech:
    """
    The base class for all StarCraft upgrades, be it buildings, units, or upgrades.
    """
    def __init__(self,
                 name: str,
                 prerequisite_buildings: list = None,
                 prerequisite_units: list = None,
                 prerequisite_upgrades: list = None,
                 unlocks: dict = None,
                 required: dict = None,
                 **kwargs):
        """
        :param name: Name of the technology.
        :param prerequisite_buildings: List of building upgrades required before this can be accessed.
        :param prerequisite_units: List of unit upgrades required before this can be accessed.
        :param prerequisite_upgrades: List of upgrade upgrades required before this can be accessed.
        :param unlocks: Dict with keys 'units', 'buildings', 'upgrades' representing what this tech unlocks.
        :param required: Dict with keys 'units', 'buildings', 'upgrades' representing what this tech requires.
        """
        self.name = name
        self.prerequisites = {
            "buildings": prerequisite_buildings or [],
            "units": prerequisite_units or [],
            "upgrades": prerequisite_upgrades or []
        }
        self.unlocks = {
            "units": unlocks.get("units", []) if unlocks else [],
            "buildings": unlocks.get("buildings", []) if unlocks else [],
            "upgrades": unlocks.get("upgrades", []) if unlocks else []
        }
        self.required = {
            "units": required.get("units", []) if required else [],
            "buildings": required.get("buildings", []) if required else [],
            "upgrades": required.get("upgrades", []) if required else []
        }

        for key, value in kwargs.items():
            setattr(self, key, value)



class Building(Tech):
    """
    Represents a StarCraft building.
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class Unit(Tech):
    """
    Represents a StarCraft unit. Units may have costs associated with them and a build time.
    """
    def __init__(self, name, cost=None, build_time=None, **kwargs):
        super().__init__(name, **kwargs)
        self.cost = cost
        self.build_time = build_time


class Upgrade(Tech):
    """
    Represents a StarCraft upgrade. Upgrades can enhance units or buildings in various ways.
    """
    def __init__(self, name, effect=None, **kwargs):
        super().__init__(name, **kwargs)
        self.effect = effect

