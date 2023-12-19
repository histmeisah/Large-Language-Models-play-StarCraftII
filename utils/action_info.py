class ActionDescriptions:
    def __init__(self, race):
        self.flattened_actions = {}
        self.race = race
        self.action_descriptions = {}  # 初始化为空字典
        self.action_dict_len = 0  # 初始化为0
        self.action_descriptions = self.init_actions_by_race(race)
        self.action_dict_len = len(self.action_descriptions)
        self._flatten_actions()
        self.empty_action_id = self.action_dict_len - 1  # 空动作的索引

    def init_actions_by_race(self, race):
        if race == "Protoss":
            return self.init_protoss_actions()
        elif race == "Zerg":
            return self.init_zerg_actions()
        elif race == "Terran":
            return self.init_terran_actions()
        else:
            raise ValueError("Invalid race")

    def _flatten_actions(self):
        for category, actions in self.action_descriptions.items():
            self.flattened_actions.update(actions)
    def init_protoss_actions(self):

        return {
            'TRAIN UNIT': {
                0: 'TRAIN PROBE', 1: 'TRAIN ZEALOT', 2: 'TRAIN ADEPT', 3: 'TRAIN STALKER',
                4: 'TRAIN SENTRY', 5: 'TRAIN HIGHTEMPLAR', 6: 'TRAIN DARKTEMPLAR', 7: 'TRAIN VOIDRAY',
                8: 'TRAIN CARRIER', 9: 'TRAIN TEMPEST', 10: 'TRAIN ORACLE', 11: 'TRAIN PHOENIX',
                12: 'TRAIN MOTHERSHIP', 13: 'TRAIN OBSERVER', 14: 'TRAIN IMMORTAL',
                15: 'TRAIN WARPPRISM', 16: 'TRAIN COLOSSUS', 17: 'TRAIN DISRUPTOR', 18: 'MORPH ARCHON'},
            'BUILD STRUCTURE': {
                19: 'BUILD PYLON', 20: 'BUILD ASSIMILATOR', 21: 'BUILD NEXUS',
                22: 'BUILD GATEWAY', 23: 'BUILD CYBERNETICSCORE',
                24: 'BUILD FORGE', 25: 'BUILD TWILIGHTCOUNCIL',
                26: 'BUILD ROBOTICSFACILITY', 27: 'BUILD STARGATE', 28: 'BUILD TEMPLARARCHIVE',
                29: 'BUILD DARKSHRINE', 30: 'BUILD ROBOTICSBAY',
                31: 'BUILD FLEETBEACON', 32: 'BUILD PHOTONCANNON', 33: 'BUILD SHIELDBATTERY'},
            'RESEARCH TECHNIQUE': {
                34: 'RESEARCH WARPGATERESEARCH', 35: 'RESEARCH PROTOSSAIRWEAPONSLEVEL1',
                36: 'RESEARCH PROTOSSAIRWEAPONSLEVEL2',
                37: 'RESEARCH PROTOSSAIRWEAPONSLEVEL3',
                38: 'RESEARCH PROTOSSAIRARMORSLEVEL1', 39: 'RESEARCH PROTOSSAIRARMORSLEVEL2',
                40: 'RESEARCH PROTOSSAIRARMORSLEVEL3', 41: 'RESEARCH ADEPTPIERCINGATTACK',
                42: 'RESEARCH BLINKTECH', 43: 'RESEARCH CHARGE', 44: 'RESEARCH PROTOSSGROUNDWEAPONSLEVEL1',
                45: 'RESEARCH PROTOSSGROUNDWEAPONSLEVEL2', 46: 'RESEARCH PROTOSSGROUNDWEAPONSLEVEL3',
                47: 'RESEARCH PROTOSSGROUNDARMORSLEVEL1',
                48: 'RESEARCH PROTOSSGROUNDARMORSLEVEL2',
                49: 'RESEARCH PROTOSSGROUNDARMORSLEVEL3', 50: 'RESEARCH PROTOSSSHIELDSLEVEL1',
                51: 'RESEARCH PROTOSSSHIELDSLEVEL2', 52: 'RESEARCH PROTOSSSHIELDSLEVEL3',
                53: 'RESEARCH EXTENDEDTHERMALLANCE', 54: 'RESEARCH GRAVITICDRIVE',
                55: 'RESEARCH OBSERVERGRAVITICBOOSTER', 56: 'RESEARCH PSISTORMTECH',
                57: 'RESEARCH VOIDRAYSPEEDUPGRADE', 58: 'RESEARCH PHOENIXRANGEUPGRADE',
                59: 'RESEARCH TEMPESTGROUNDATTACKUPGRADE'},
            'OTHER ACTION': {
                60: 'SCOUTING PROBE',
                61: 'SCOUTING OBSERVER',
                62: 'SCOUTING ZEALOT',
                63: 'SCOUTING PHOENIX',
                64: 'MULTI-ATTACK',
                65: 'MULTI-RETREAT',
                66: 'CHRONOBOOST NEXUS',
                67: 'CHRONOBOOST CYBERNETICSCORE',
                68: 'CHRONOBOOST TWILIGHTCOUNCIL',
                69: 'CHRONOBOOST STARGATE',
                70: 'CHRONOBOOST FORGE',
                71: 'EMPTY ACTION'}}

    def init_zerg_actions(self):

        return {
            'TRAIN UNIT': {
                0: 'TRAIN OVERLORD', 1: 'TRAIN DRONE', 2: 'TRAIN QUEEN', 3: 'TRAIN ZERGLING',
                4: 'TRAIN ROACH', 5: 'TRAIN HYDRALISK', 6: 'TRAIN MUTALISK',
                7: 'TRAIN CORRUPTOR', 8: 'TRAIN INFESTOR ', 9: 'TRAIN SWARMHOST',
                10: 'TRAIN ULTRALISK', 11: 'TRAIN VIPER', 12: 'MORPH BANELING',
                13: 'MORPH RAVAGER', 14: 'MORPH LURKER', 15: 'MORPH BROODLORD',
                16: 'MORPH OVERSEER'},
            'BUILD STRUCTURE': {
                17: 'BUILD EXTRACTOR', 18: 'BUILD HATCHERY', 19: 'BUILD SPAWNINGPOOL',
                20: 'BUILD BANELINGNEST', 21: 'BUILD ROACHWARREN',
                22: 'BUILD HYDRALISKDEN', 23: 'BUILD LAIR',
                24: 'BUILD HIVE', 25: 'BUILD EVOLUTIONCHAMBER',
                26: 'BUILD INFESTATIONPIT', 27: 'BUILD SPIRE',
                28: 'BUILD GREATERSPIRE', 29: 'BUILD ULTRALISKCAVERN',
                30: 'BUILD LURKERDEN', 31: 'BUILD SPORECRAWLER', 32: 'BUILD SPINECRAWLER'},
            'RESEARCH TECHNIQUE': {
                33: 'RESEARCH ZERGLINGMOVEMENTSPEED', 34: 'RESEARCH ZERGLINGATTACKSPEED',
                35: 'RESEARCH BANELINGMOVEMENTSPEED', 36: 'RESEARCH ROACHMOVEMENTSPEED',
                37: 'RESEARCH TUNNELINGCLAWS', 38: 'RESEARCH OVERLORDSPEED', 39: 'RESEARCH BURROW',
                40: 'RESEARCH HYDRAMOVEMENTSPEED', 41: 'RESEARCH EVOLVEGROOVEDSPINES',
                42: 'RESEARCH ZERGMELEEWEAPONSLEVEL1',
                43: 'RESEARCH ZERGMELEEWEAPONSLEVEL2', 44: 'RESEARCH ZERGMELEEWEAPONSLEVEL3',
                45: 'RESEARCH ZERGMISSILEWEAPONSLEVEL1',
                46: 'RESEARCH ZERGMISSILEWEAPONSLEVEL2', 47: 'RESEARCH ZERGMISSILEWEAPONSLEVEL3',
                48: 'RESEARCH ZERGGROUNDARMORSLEVEL1',
                49: 'RESEARCH ZERGGROUNDARMORSLEVEL2', 50: 'RESEARCH ZERGGROUNDARMORSLEVEL3',
                51: 'RESEARCH INFESTORENERGYUPGRADE', 52: 'RESEARCH NEURALPARASITE',
                53: 'RESEARCH ZERGFLYERWEAPONSLEVEL1', 54: 'RESEARCH ZERGFLYERWEAPONSLEVEL2',
                55: 'RESEARCH ZERGFLYERWEAPONSLEVEL3', 56: 'RESEARCH ZERGFLYERARMORSLEVEL1',
                57: 'RESEARCH ZERGFLYERARMORSLEVEL2',
                58: 'RESEARCH ZERGFLYERARMORSLEVEL3',
                59: 'RESEARCH CHITINOUSPLATING', 60: 'RESEARCH ANABOLICSYNTHESIS', 61: 'RESEARCH LURKERRANGE',
                62: "RESEARCH DIGGINGCLAWS"},
            'OTHER ACTION': {
                63: 'SCOUTING ZERGLING', 64: 'SCOUTING OVERLORD', 65: 'SCOUTING OVERSEER', 66: 'MULTI-ATTACK',
                67: 'MULTI-RETREAT',
                68: 'QUEEN INJECTLARVA', 69: 'EMPTY ACTION'}}

    def init_terran_actions(self):
        return {
            # now we have none actions for terran
            # 用你的实际Terran动作描述来替换
            0: "执行Terran动作0",
            1: "执行Terran动作1",
            # ……
        }

    def get_action_description(self, action_id):
        """
        根据动作id返回动作描述
        :param action_id:
        :return:
        """
        return self.action_descriptions.get(action_id, "未知动作")

    def get_action_code(self, action_description):
        """
        根据动作描述返回动作id
        :param action_description:
        :return:
        """
        for action_code, description in self.action_descriptions.items():
            if description == action_description:
                return action_code
        raise ValueError(f"没有找到与描述 '{action_description}' 对应的动作编码。")


# action_desc = ActionDescriptions("Protoss")
# actions_list = list(action_desc.flattened_actions.values())  # 将 dict_values 对象转换为列表
# print(actions_list)  # 这将打印出一个由动作描述组成的列表
# print(len(actions_list))  # 这将打印出动作的数量
#
# print(type(actions_list[0]))