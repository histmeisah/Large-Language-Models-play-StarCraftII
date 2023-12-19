system_prompt = """
You are an advanced strategic analysis AI with expertise in StarCraft II game analytics. You understand the game's mechanics, strategies, and player decision-making processes.

Task: You are provided with raw game data from a StarCraft II match. Your job is to translate this into a detailed, insightful strategic report that a player can use to understand their current game standing and make informed decisions. The report should mirror professional game analysis and provide comprehensive insights in a format that's easily digestible at a glance.

Instructions: Transform the raw data into a structured report with the following sections and details:

1. Current Protoss Situation (Specify Game Time): Provide a timestamp for current game data reference.

2. Resources and Economy: Highlight current mineral and vespene gas counts, the number of workers, and the number of bases. Translate these figures into an assessment of the player's economic health and map control.

3. Supply Situation: Detail the supply cap, supply used, and supply left, providing insight into resource utilization efficiency and population management.

4. Army Composition and Defense: Break down the army supply and unit types (including special units like Colossi, Voidrays, Observers). Note the absence of certain unit types and the number of defensive structures. Interpret these details to assess the player's defensive and offensive capabilities.

5. Production and Technology: Enumerate production facilities (like Robotics Facilities, Stargates, Warp Gates) and ongoing researches. Highlight any imbalances or focused investments in the player's approach, indicating potential strategic predispositions.

6. Planned Structures and Units: Discuss any upcoming expansions or unit production that points toward future strategies, emphasizing on planned economic or military advancements.

7. Enemy Forces Observation: Based on available intel, provide a summary of the opponent's potential strategy, unit composition, economic status, and defensive setup. Focus on information that can guide proactive strategy adjustments.

Each section should not only present data but also interpret what it signifies for the player's current situation, potential strategies, and best possible moves. Conclude with a brief synthesis of the player's standing, offering a quick insight or tip that reinforces their strategy confidence.

Remember, clarity and precision are vital. The player should be able to read the report and instantly comprehend their game standing and strategic options.
"""

example_input_prompt_1 = """
'game_time': '11:54', 'worker_supply': 54, 'mineral': 620, 'gas': 331, 'supply_left': 0, 'supply_cap': 139, 'supply_used': 139, 'army_supply': 78, 'enemy_units_count': 0, 'base_count': 5, 'pylon_count': 8, 'gas_buildings_count': 10, 'gateway_count': 0, 'forge_count': 0, 'photon_cannon_count': 0, 'shield_battery_count': 4, 'warp_gate_count': 7, 'cybernetics_core_count': 1, 'twilight_council_count': 1, 'robotics_facility_count': 12, 'statgate_count': 5, 'templar_archives_count': 0, 'dark_shrine_count': 0, 'robotics_bay_count': 1, 'fleet_beacon_count': 0, 'Zealot_count': 0, 'stalker_count': 1, 'sentry_count': 0, 'adept_count': 0, 'high_templar_count': 0, 'dark_templar_count': 0, 'immortal_count': 0, 'colossus_count': 4, 'disruptor_count': 1, 'archon_count': 0, 'observer_count': 3, 'warp_prism_count': 0, 'phoenix_count': 2, 'voidray_count': 5, 'Oracle_count': 0, 'Carrier_count': 0, 'tempest_count': 0, 'mothership_count': 0, 'planning_base_count': 0, 'planning_pylon_count': 0, 'planning_gas_buildings_count': 0, 'planning_gateway_count': 0, 'planning_forge_count': 0, 'planning_photon_cannon_count': 0, 'planning_shield_battery_count': 0, 'planning_warp_gate_count': 0, 'planning_cybernetics_core_count': 0, 'planning_twilight_council_count': 0, 'planning_robotics_facility_count': 0, 'planning_statgate_count': 0, 'planning_templar_archives_count': 0, 'planning_dark_shrine_count': 0, 'planning_robotics_bay_count': 0, 'planning_fleet_beacon_count': 0, 'planning_worker_count': 0, 'planning_Zealot_count': 0, 'planning_stalker_count': 0, 'planning_sentry_count': 0, 'planning_adept_count': 0, 'planning_high_templar_count': 0, 'planning_dark_templar_count': 0, 'planning_immortal_count': 0, 'planning_colossus_count': 1, 'planning_disruptor_count': 0, 'planning_archon_count': 0.0, 'planning_observer_count': 0, 'planning_warp_prism_count': 0, 'planning_phoenix_count': 0, 'planning_voidray_count': 4, 'planning_Oracle_count': 0, 'planning_Carrier_count': 0, 'planning_tempest_count': 0, 'planning_mothership_count': 0, 'warpgate_research_status': 1, 'protoss_air_armor_level_1_research_status': 0, 'protoss_air_armor_level_2_research_status': 0, 'protoss_air_armor_level_3_research_status': 0, 'protoss_ground_armor_level_1_research_status': 0, 'protoss_ground_armor_level_2_research_status': 0, 'protoss_ground_armor_level_3_research_status': 0, 'protoss_ground_weapon_level_1_research_status': 0, 'protoss_ground_weapon_level_2_research_status': 0, 'protoss_ground_weapon_level_3_research_status': 0, 'protoss_shield_level_1_research_status': 0, 'protoss_shield_level_2_research_status': 0, 'protoss_shield_level_3_research_status': 0, 'enemy_UnitTypeId.EXTRACTOR': 1, 'enemy_UnitTypeId.HATCHERY': 1, 'enemy_UnitTypeId.SPAWNINGPOOL': 1

"""

example_output_prompt_1 = """
Game Snapshot: 11:54

Economy: Minerals at 620, Gas at 331. Operating on 5 bases. Strong resource pool, consider allocating more for army diversification or aggressive expansion.
Supply: Maxed out (139/139). Immediate expansion needed for continued growth and to maintain military momentum.
Military: Army supply robust at 78, heavy on air and mechanical units. Main force includes Colossi (4), Voidrays (5), minimal ground troop presence. Expand unit roster for flexibility against potential counters.
Production: Intense focus on technology with 12 Robotics Facilities, 5 Stargates, but no active Forges indicating a lack of upgrades. Assess necessity for ground support and initiate upgrade sequences.
Upcoming Units: Plans indicate additional Colossus and Voidrays. Be cautious of reliance on limited unit types; potential vulnerability if enemy adapts.
Opponent: Zerg presence minimal with only basic structures identified. Possible concealment of advanced forces or expansions; increased scouting imperative.
Quick Focus: Address supply limit, broaden military spectrum, enhance reconnaissance particularly in uncharted Zerg territory to pre-empt possible hidden threats.
Recommended Actions: Initiate aggressive scouting, manage supply constraints, diversify unit composition, and consider defensive and offensive upgrades.
"""

example_input_prompt_2 = """
{'game_time': '11:54', 'worker_supply': 54, 'mineral': 625, 'gas': 331, 'supply_left': 0, 'supply_cap': 139, 'supply_used': 139, 'army_supply': 78, 'enemy_units_count': 0, 'base_count': 5, 'pylon_count': 8, 'gas_buildings_count': 10, 'gateway_count': 0, 'forge_count': 0, 'photon_cannon_count': 0, 'shield_battery_count': 4, 'warp_gate_count': 7, 'cybernetics_core_count': 1, 'twilight_council_count': 1, 'robotics_facility_count': 12, 'statgate_count': 5, 'templar_archives_count': 0, 'dark_shrine_count': 0, 'robotics_bay_count': 1, 'fleet_beacon_count': 0, 'Zealot_count': 0, 'stalker_count': 1, 'sentry_count': 0, 'adept_count': 0, 'high_templar_count': 0, 'dark_templar_count': 0, 'immortal_count': 0, 'colossus_count': 4, 'disruptor_count': 1, 'archon_count': 0, 'observer_count': 3, 'warp_prism_count': 0, 'phoenix_count': 2, 'voidray_count': 5, 'Oracle_count': 0, 'Carrier_count': 0, 'tempest_count': 0, 'mothership_count': 0, 'planning_base_count': 0, 'planning_pylon_count': 0, 'planning_gas_buildings_count': 0, 'planning_gateway_count': 0, 'planning_forge_count': 0, 'planning_photon_cannon_count': 0, 'planning_shield_battery_count': 0, 'planning_warp_gate_count': 0, 'planning_cybernetics_core_count': 0, 'planning_twilight_council_count': 0, 'planning_robotics_facility_count': 0, 'planning_statgate_count': 0, 'planning_templar_archives_count': 0, 'planning_dark_shrine_count': 0, 'planning_robotics_bay_count': 0, 'planning_fleet_beacon_count': 0, 'planning_worker_count': 0, 'planning_Zealot_count': 0, 'planning_stalker_count': 0, 'planning_sentry_count': 0, 'planning_adept_count': 0, 'planning_high_templar_count': 0, 'planning_dark_templar_count': 0, 'planning_immortal_count': 0, 'planning_colossus_count': 1, 'planning_disruptor_count': 0, 'planning_archon_count': 0.0, 'planning_observer_count': 0, 'planning_warp_prism_count': 0, 'planning_phoenix_count': 0, 'planning_voidray_count': 4, 'planning_Oracle_count': 0, 'planning_Carrier_count': 0, 'planning_tempest_count': 0, 'planning_mothership_count': 0, 'warpgate_research_status': 1, 'protoss_air_armor_level_1_research_status': 0, 'protoss_air_armor_level_2_research_status': 0, 'protoss_air_armor_level_3_research_status': 0, 'protoss_ground_armor_level_1_research_status': 0, 'protoss_ground_armor_level_2_research_status': 0, 'protoss_ground_armor_level_3_research_status': 0, 'protoss_ground_weapon_level_1_research_status': 0, 'protoss_ground_weapon_level_2_research_status': 0, 'protoss_ground_weapon_level_3_research_status': 0, 'protoss_shield_level_1_research_status': 0, 'protoss_shield_level_2_research_status': 0, 'protoss_shield_level_3_research_status': 0, 'enemy_UnitTypeId.EXTRACTOR': 1, 'enemy_UnitTypeId.HATCHERY': 1, 'enemy_UnitTypeId.SPAWNINGPOOL': 1}

"""
example_out_prompt_2 = """
Game Snapshot: 11:54

Economy: Minerals at 625, Gas at 331. Operating on 5 bases. Resources stable; consider more spending on units or expansion.
Supply: At cap (139/139). Immediate increase needed to continue unit production.
Military: Army supply at 78; tech-focused. Main units: Colossi (4), Voidrays (5). Need more variety and scouting info on enemy.
Production: Heavy tech with 12 Robotics, 5 Stargates. Ground support and upgrades limited.
Upcoming Units: Additional Colossus and Voidrays planned. Watch for over-specialization.
Opponent: Zerg basic structures spotted. Potential tech-up or expansion unseen; scouting advised.
Quick Focus: Expand supply, diversify army, scout Zerg territory for hidden advancements.
Recommended Actions: Scout, supply management, unit diversification.
"""

example_input_prompt_3 = """
{'game_time': '11:54', 'worker_supply': 54, 'mineral': 630, 'gas': 347, 'supply_left': 0, 'supply_cap': 139, 'supply_used': 139, 'army_supply': 78, 'enemy_units_count': 0, 'base_count': 5, 'pylon_count': 8, 'gas_buildings_count': 10, 'gateway_count': 0, 'forge_count': 0, 'photon_cannon_count': 0, 'shield_battery_count': 4, 'warp_gate_count': 7, 'cybernetics_core_count': 1, 'twilight_council_count': 1, 'robotics_facility_count': 12, 'statgate_count': 5, 'templar_archives_count': 0, 'dark_shrine_count': 0, 'robotics_bay_count': 1, 'fleet_beacon_count': 0, 'Zealot_count': 0, 'stalker_count': 1, 'sentry_count': 0, 'adept_count': 0, 'high_templar_count': 0, 'dark_templar_count': 0, 'immortal_count': 0, 'colossus_count': 4, 'disruptor_count': 1, 'archon_count': 0, 'observer_count': 3, 'warp_prism_count': 0, 'phoenix_count': 2, 'voidray_count': 5, 'Oracle_count': 0, 'Carrier_count': 0, 'tempest_count': 0, 'mothership_count': 0, 'planning_base_count': 0, 'planning_pylon_count': 0, 'planning_gas_buildings_count': 0, 'planning_gateway_count': 0, 'planning_forge_count': 0, 'planning_photon_cannon_count': 0, 'planning_shield_battery_count': 0, 'planning_warp_gate_count': 0, 'planning_cybernetics_core_count': 0, 'planning_twilight_council_count': 0, 'planning_robotics_facility_count': 0, 'planning_statgate_count': 0, 'planning_templar_archives_count': 0, 'planning_dark_shrine_count': 0, 'planning_robotics_bay_count': 0, 'planning_fleet_beacon_count': 0, 'planning_worker_count': 0, 'planning_Zealot_count': 0, 'planning_stalker_count': 0, 'planning_sentry_count': 0, 'planning_adept_count': 0, 'planning_high_templar_count': 0, 'planning_dark_templar_count': 0, 'planning_immortal_count': 0, 'planning_colossus_count': 1, 'planning_disruptor_count': 0, 'planning_archon_count': 0.0, 'planning_observer_count': 0, 'planning_warp_prism_count': 0, 'planning_phoenix_count': 0, 'planning_voidray_count': 4, 'planning_Oracle_count': 0, 'planning_Carrier_count': 0, 'planning_tempest_count': 0, 'planning_mothership_count': 0, 'warpgate_research_status': 1, 'protoss_air_armor_level_1_research_status': 0, 'protoss_air_armor_level_2_research_status': 0, 'protoss_air_armor_level_3_research_status': 0, 'protoss_ground_armor_level_1_research_status': 0, 'protoss_ground_armor_level_2_research_status': 0, 'protoss_ground_armor_level_3_research_status': 0, 'protoss_ground_weapon_level_1_research_status': 0, 'protoss_ground_weapon_level_2_research_status': 0, 'protoss_ground_weapon_level_3_research_status': 0, 'protoss_shield_level_1_research_status': 0, 'protoss_shield_level_2_research_status': 0, 'protoss_shield_level_3_research_status': 0, 'enemy_UnitTypeId.EXTRACTOR': 1, 'enemy_UnitTypeId.HATCHERY': 1, 'enemy_UnitTypeId.SPAWNINGPOOL': 1}

"""
example_out_prompt_3 = """
Game Snapshot: 11:54

Economy: Minerals at 630, Gas at 347, running on 5 bases. Resources slightly increased, indicating underutilization. Recommended reallocation for rapid military mobilization or strategic advancement.
Supply: Capped (139/139), with no room for additional units. Critical need to expand supply immediately to sustain momentum.
Military: Army supply stable at 78, primarily composed of air and mechanized units: 4 Colossi, 5 Voidrays, minimal ground forces. Advise reinforcement with diverse unit types for adaptability in battle.
Production: Technologically advanced with 12 Robotics Facilities and 5 Stargates, but lack of Forges suggests upgrades are neglected. Initiate ground support enhancements and unit upgrades for balanced offense and defense.
Upcoming Units: Projection indicates continued production of Colossi and Voidrays. Caution against over-dependence on certain units that may lead to strategic inflexibility.
Opponent: Minimal Zerg infrastructure observed, suggesting either a hidden transition to advanced units or expansion. Immediate, comprehensive scouting required to uncover potential concealed threats.
Quick Focus: Expand supply capacity urgently, invest in unit diversity, and intensify reconnaissance efforts, particularly in unexplored Zerg domains to counteract unseen developments.
Recommended Actions: Prioritize supply expansion, diversify troop composition, initiate upgrade research, and enhance scouting to gain intelligence on Zerg movements and strategies.
"""

example_input_prompt_4 = """
Game Snapshot: 11:54

Economy:

Minerals slightly increased to 635, Gas up to 351.
Operating on 5 bases; the economy is stable but underutilized. Immediate reinvestment necessary for military growth or tech advancements.
Supply:

At maximum capacity (139/139). Supply block is critical; immediate action needed for further progression.
No planned pylons; prioritize pylon construction to expand supply.
Military:

Army supply fixed at 78. Main composition includes high-tech units (Colossi, Voidrays) but lacks diversity and frontline units.
Ground force is almost non-existent (only 1 Stalker), and no defensive structures (Photon Cannons) are present or planned, indicating vulnerabilities.
Production:

Significant emphasis on technology with 12 Robotics Facilities and 5 Stargates; however, no Forges for upgrades, which could put units at a disadvantage in upcoming skirmishes.
No changes in production facilities planned, suggesting a potential stagnation in strategy adaptability.
Upcoming Units:

Additional Colossus and 4 Voidrays in the pipeline. Risk of predictable strategy and unit composition remains high.
Opponent:

Basic Zerg infrastructure identified (Extractor, Hatchery, Spawning Pool), but lack of scouting information leaves current Zerg capabilities or strategy largely unknown.
Quick Focus:

Immediate expansion of supply through pylon construction.
Diversification and increase of army units, including frontline soldiers.
Defensive and offensive upgrades needed via Forge construction and research initiation.
Enhanced scouting to ascertain Zerg strategy and adapt accordingly.
Recommended Actions:

Start constructing additional pylons to alleviate the supply block.
Balance unit composition by incorporating more ground troops and consider adding defensive structures for base security.
Establish Forge(s) for ground and air upgrades to strengthen army resilience and firepower.
Deploy scouting units (e.g., Observers) to gather intelligence on the Zerg's unit composition, tech progression, and potential expansions. Immediate and continuous reconnaissance is essential for strategic adaptability.
"""
example_out_prompt_4 = """
Game Snapshot: 11:54

Economy: Minerals at 650, Gas at 351. Operating on 5 bases. Resources stable; consider more spending on units or expansion.

Supply: At cap (139/139). Immediate increase needed to continue unit production.

Military: Army supply at 78; tech-focused. Main units: Colossi (4), Voidrays (5). Need more variety and scouting info on enemy.

Production: Heavy tech with 12 Robotics, 5 Stargates. Ground support and upgrades limited.

Upcoming Units: Additional Colossus and Voidrays planned. Watch for over-specialization.

Opponent: Zerg basic structures spotted. Potential tech-up or expansion unseen; scouting advised.

Quick Focus: Expand supply, diversify army, scout Zerg territory for hidden advancements.

Recommended Actions:

Initiate pylon construction to expand supply capacity promptly.
Consider adding versatility to the army by introducing ground units and anti-air capabilities, given the current heavy focus on Colossi and Voidrays.
Implement scouting missions, possibly with Observers or Phoenixes, to gather intelligence on Zerg forces, identifying their unit mix, tech developments, and expansion efforts.
Initiate upgrades by building a Forge and starting key research to enhance unit effectiveness, particularly since there's a noticeable lack of ground and air unit upgrades.
Evaluate economic stability and consider preparing for expansion or tech advancements to utilize resource accumulation efficiently.
"""
example_input_prompt_5 = """
{'game_time': '11:55', 'worker_supply': 54, 'mineral': 655, 'gas': 355, 'supply_left': 0, 'supply_cap': 139, 'supply_used': 139, 'army_supply': 78, 'enemy_units_count': 0, 'base_count': 5, 'pylon_count': 8, 'gas_buildings_count': 10, 'gateway_count': 0, 'forge_count': 0, 'photon_cannon_count': 0, 'shield_battery_count': 4, 'warp_gate_count': 7, 'cybernetics_core_count': 1, 'twilight_council_count': 1, 'robotics_facility_count': 12, 'statgate_count': 5, 'templar_archives_count': 0, 'dark_shrine_count': 0, 'robotics_bay_count': 1, 'fleet_beacon_count': 0, 'Zealot_count': 0, 'stalker_count': 1, 'sentry_count': 0, 'adept_count': 0, 'high_templar_count': 0, 'dark_templar_count': 0, 'immortal_count': 0, 'colossus_count': 4, 'disruptor_count': 1, 'archon_count': 0, 'observer_count': 3, 'warp_prism_count': 0, 'phoenix_count': 2, 'voidray_count': 5, 'Oracle_count': 0, 'Carrier_count': 0, 'tempest_count': 0, 'mothership_count': 0, 'planning_base_count': 0, 'planning_pylon_count': 0, 'planning_gas_buildings_count': 0, 'planning_gateway_count': 0, 'planning_forge_count': 0, 'planning_photon_cannon_count': 0, 'planning_shield_battery_count': 0, 'planning_warp_gate_count': 0, 'planning_cybernetics_core_count': 0, 'planning_twilight_council_count': 0, 'planning_robotics_facility_count': 0, 'planning_statgate_count': 0, 'planning_templar_archives_count': 0, 'planning_dark_shrine_count': 0, 'planning_robotics_bay_count': 0, 'planning_fleet_beacon_count': 0, 'planning_worker_count': 0, 'planning_Zealot_count': 0, 'planning_stalker_count': 0, 'planning_sentry_count': 0, 'planning_adept_count': 0, 'planning_high_templar_count': 0, 'planning_dark_templar_count': 0, 'planning_immortal_count': 0, 'planning_colossus_count': 1, 'planning_disruptor_count': 0, 'planning_archon_count': 0.0, 'planning_observer_count': 0, 'planning_warp_prism_count': 0, 'planning_phoenix_count': 0, 'planning_voidray_count': 4, 'planning_Oracle_count': 0, 'planning_Carrier_count': 0, 'planning_tempest_count': 0, 'planning_mothership_count': 0, 'warpgate_research_status': 1, 'protoss_air_armor_level_1_research_status': 0, 'protoss_air_armor_level_2_research_status': 0, 'protoss_air_armor_level_3_research_status': 0, 'protoss_ground_armor_level_1_research_status': 0, 'protoss_ground_armor_level_2_research_status': 0, 'protoss_ground_armor_level_3_research_status': 0, 'protoss_ground_weapon_level_1_research_status': 0, 'protoss_ground_weapon_level_2_research_status': 0, 'protoss_ground_weapon_level_3_research_status': 0, 'protoss_shield_level_1_research_status': 0, 'protoss_shield_level_2_research_status': 0, 'protoss_shield_level_3_research_status': 0, 'enemy_UnitTypeId.EXTRACTOR': 1, 'enemy_UnitTypeId.HATCHERY': 1, 'enemy_UnitTypeId.SPAWNINGPOOL': 1}

"""
example_out_prompt_5 = """
Game Snapshot: 11:55

Economy: Minerals at 655, Gas at 355. Operating on 5 bases. Slight resource accumulation indicating potential inefficiencies in spending or production.

Supply: Maxed out (139/139). Urgent need for more Pylons to continue production.

Military: Army supply stable at 78, predominantly advanced units (Colossi, Voidrays). No basic infantry, potential vulnerability. Disruptor presence noted, but overall force lacks diversity.

Production: Intense focus on tech with 12 Robotics Facilities, 5 Stargates, but no Forges indicating no ongoing upgrades. Risk of being technologically outpaced in engagements.

Upcoming Units: More Colossi and Voidrays planned, risking predictability and imbalance in force composition.

Opponent: Minimal information on Zerg opponent with only basic structures identified. Lack of intelligence on enemy movements or strategies.

Quick Focus: Resolve supply block, initiate scouting, diversify forces, consider upgrades, optimize resource use.

Recommended Actions:

Immediate construction of Pylons.
Initiate scouting using existing units or structures.
Introduce varied units into the army composition, potentially lower-tech options for balance.
Establish Forges for upgrade potentials.
Strategic planning considering opponent's potential hidden advancements or expansions.

"""
