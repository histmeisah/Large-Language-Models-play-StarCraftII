class StarCraftIIPrompt_old:
    def __init__(self, race, K, action_dict):
        self.race = race
        self.K = K
        self.action_dict = action_dict

    def generate_prompts(self):
        self.system_prompt = f"""
        You are an AI trained in analyzing and summarizing StarCraft II games. You understand the nuances and strategies of the {self.race} race. 
        Based on the summaries of multiple rounds in a game, we want you to analyze the game progression in a structured way. Your analysis should include the following aspects:
        1. Information Overview: Provide a brief overview of the current situation based on all the rounds.
        2. Current Game Stage: Determine the stage of the game based on the information of all rounds. Is it the early game, mid-game, or late game?
        3. Our Current Strategy: From the information of all rounds, infer what our strategy might be.
        4. Enemy's Strategy: Infer what the enemy's strategy might be, based on the information available.
        5. Key Information: Highlight the most important aspects from all rounds that have significantly influenced the game.

        Then, provide suggestions for improvements based on the overall game situation and the strategies being employed by both sides. These suggestions should be concise and specific. Do not suggest advanced strategies or actions that are not applicable to the current stage of the game.

        Finally, make {self.K} decisions from action_dict{self.action_dict} based on the current situation and the suggestions provided. These decisions should be specific and actionable. Do not make decisions that are not applicable to the current stage of the game.
        """

        self.example_input_prompt = "chunk0: At 12:05 game time, our current StarCraft II situation is as follows:\n\nResources:\n- Game time: 12:05\n- Worker supply: 53\n- Mineral: 460\n- Gas: 3392\n- Supply cap: 124\n- Supply used: 124\n- Army supply: 65\n\nBuildings:\n- Nexus count: 4\n- Pylon count: 8\n- Gas buildings count: 8\n- Gateway count: 1\n- Forge count: 1\n- Photon cannon count: 4\n- Shield battery count: 4\n- Warp gate count: 25\n- Cybernetics core count: 1\n- Twilight council count: 2\n- Robotics facility count: 3\n\nUnits:\n- Probe count: 53\n- Zealot count: 7\n- Stalker count: 25\n- Observer count: 1\n\nPlanning:\n\nPlanning structure:\n- Planning gateway count: 1\n\nPlanning unit:\n- Planning stalker count: 2\n\nResearch:\n\nCybernetics core:\n- Warpgate research status: 1\n- Protoss air weapon level 1 research status: 0.24722224473953247\n\nForge:\n- Protoss ground armor level 1 research status: 0.22794115543365479\n- Protoss ground weapon level 1 research status: 1\n- Protoss ground weapon level 2 research status: 1\n\nTwilight council:\n- Blink research status: 1\n- Charge research status: 1\n\nEnemy:\n\nUnit:\n- Enemy unittypeid.zergling: 1\n\nStructure:\n- Enemy unittypeid.hatchery: 2\n- Enemy unittypeid.extractor: 1\n- Enemy unittypeid.sporecrawler: 1\n\n\n,...,chunk{K_1}"

        self.example_output_prompt = """
        1. Information Overview:
        Time: 12:05 - 12:06 game time.
        Resources: Limited minerals (460-490) but high gas reserves (around 3400). Full supply usage at 124 with an army supply of 65.
        Buildings: Strong focus on Warp Gates (25), decent number of Nexuses (4), Pylons (8), Gas Buildings (8), and defensive structures (Photon Cannons and Shield Batteries).
        Units: A considerable number of Stalkers (25) and Zealots (7), moderate Probe count (53-54), and one Observer.
        Research: Completed Warpgate, Protoss ground weapons levels 1 and 2, Blink, and Charge. Ongoing research in Protoss air weapons and ground armor level 1.        
        2. Current Game Stage:
        The game is in the mid to late game phase. This is indicated by the high number of warp gates, advanced research (like Blink and Charge), and a fully utilized supply cap.

        3. Our Current Strategy:
        Stalker-heavy army composition, supported by some Zealots.
        Defensive posture with numerous Photon Cannons and Shield Batteries.
        Tech focus with ongoing upgrades and multiple tech buildings.
        Resource management issues, particularly with minerals, suggesting either heavy spending or inadequate gathering.        
        4. Enemy's Strategy:
        Zerg opponent with limited visible information (few Zerglings, Hatcheries, Extractors, and Spore Crawlers).
        Possibly focusing on macro play or hiding tech/army composition.
        Lack of aggressive engagement so far.        
        5c. Key Information:
        High Gas, Low Minerals: Indicates a possible imbalance in resource management.
        Heavy investment in Stalkers: Suggests a preference for mobile engagements.
        Defensive Setup: Suggests either anticipation of aggression or a more passive strategy.
        Research Focus: Indicates a plan for technologically advanced units or upgrades.

        Suggestions:

        High Gas, Low Minerals: Indicates a possible imbalance in resource management.
        Heavy investment in Stalkers: Suggests a preference for mobile engagements.
        Defensive Setup: Suggests either anticipation of aggression or a more passive strategy.
        Research Focus: Indicates a plan for technologically advanced units or upgrades.


        Decisions:
        0: <TRAIN IMMORTAL>
        1: <BUILD PYLON>
        2: <SCOUTING PROBE>
        3: <RESEARCH PROTOSSGROUNDARMORSLEVEL1>
        4: <CHRONOBOOST NEXUS>
        """
        return self.system_prompt, self.example_input_prompt, self.example_output_prompt











class StarCraftIIPrompt_V1:
    def __init__(self, race, K, action_dict, game_style):
        self.race = race.lower()
        self.game_style = game_style.lower()
        self.race_specific_prompt = {
            "protoss": "For Protoss, the Chrono Boost ability available at the Nexus is crucial. It accelerates the production and research speed of a building. Important buildings that benefit from Chrono Boost include the Nexus itself (for probe production), the Gateway (for basic unit production), the Robotics Facility (for advanced unit production), and various tech buildings (for research upgrades). Keeping an optimal usage of Nexus's energy for Chrono Boost can significantly improve efficiency.",
            "zerg": "For Zerg, larvae are a unique resource used for the production of all Zerg units. Larvae spawn naturally from Hatcheries, Lairs, or Hives, but their production rate can be significantly increased with the Queen's Inject Larva ability. Managing larvae effectively and ensuring a consistent usage of the Inject Larva ability is essential for Zerg to maintain a steady production of units."
        }
        self.game_style_specific_prompt = {
            "protoss": {
                "aggressive": """Utilize Astrea's 2 base blink all-in strategy for early aggression against Zerg. 
                Focus on Stalkers and Adepts, tech up quickly, and maximize unit mobility with Warp Prism. Use Adepts 
                for harassment, maintain Stalker control, and capitalize on Zerg over-droning.""",

                "air_superiority": """Seek aerial dominance against Zerg with the 'pvz_fast_carriers' tactic. 
                Prioritize Carriers and Void Rays, tech up quickly, and expand your economy. Emphasize Protoss Air 
                Weapons upgrades, secure bases with Photon Cannons, and maintain strong defenses with Shield 
                Batteries.""",

                "immortal_archon_push": """Leverage the Immortal-Archon combo for a powerful mid-game push. Tech up 
                swiftly, focus on Immortals, morph High Templars into Archons, and use a Warp Prism for unit 
                mobility. Aim to overpower defenses with the combined strength of Immortals and Archons.""",
                "4_base_zealot_archon": """Adopt a 4 base Zealot-Archon strategy against opponents. Start with a 
                defensive Stargate opening, producing a few Void Rays. Expand your economy rapidly, and prioritize 
                ground unit attack and shield upgrades. Produce a massive Zealot and Archon force (using High 
                Templars) for a devastating assault.""",

                "fast_4rd_base_zealot_stalker": """Embrace the fast-4rd base and Zealot-Stalker tactic. Begin with a 
                Stargate, focusing on Void Rays for early defense. Rapidly expand bases, boosting ground unit attack 
                and shields. Mass produce Zealots and Stalkers for frontline battles. Transition to Colossus for 
                enhanced offensive capabilities as resources permit."""
            },
        }

        self.system_prompt = f"""
        You are an AI trained in analyzing and summarizing StarCraft II games. You understand the nuances and strategies of the {self.race} race. Your primary strategy focus for this game is '{self.game_style}'.

        To aid your analysis, here's a brief on the specific characteristics of the {self.race} race:
        {self.race_specific_prompt.get(self.race)}

        Additionally, the primary strategy focus '{self.game_style}' for this game is detailed as follows:
        {self.game_style_specific_prompt.get(self.race).get(self.game_style)}

        Based on the summaries of multiple rounds in a game, we want you to analyze the game progression in a structured way. Your analysis should include the following aspects:
        1. Game Overview: Provide a brief overview of the current situation based on all the rounds.
        2. Current Game Stage: Determine the stage of the game based on the information of all rounds. Is it the early game, mid-game, or late game?
        3. Our Situation: Describe our current status in terms of:
            3.1 Units and Buildings: Analyze the state of our units and buildings.
            3.2 Economy: Evaluate our economic condition, including resource collection and usage.
            3.3 Technology: Describe the status of our technological research and what technologies we have unlocked so far. Analyze our technology tree, indicating the available and potential upgrades or units.
        4. Our Strategy: Infer our potential strategy based on our current situation, the game style, and the information of all rounds.
        5. Enemy's Strategy: Infer the enemy's potential strategy, based on the available information.
        6. Key Information: Highlight the most important aspects from all rounds that have significantly influenced the game.

        Based on the game situation and strategies used by both sides, provide specific suggestions for the following areas:

        1. Our Strategy: Propose adjustments to our current strategy to counter the enemy's moves and capitalize on our strengths.
        2. Units and Buildings: Offer ways to enhance our unit composition and improve our building layout, suited to the current stage of the game.
        3. Economy: Recommend better practices for resource gathering and usage, in line with our strategic needs.
        4. Technology: Suggest focused research paths to gain technological advantages, considering our current research status and technology tree.

        Lastly, consider the current situation and the suggestions provided, make {K} actionable and specific decisions from the action dictionary{action_dict}. This dictionary comprises four categories of actions: unit production, building construction, technology research, and other actions. Remember to align these decisions with the current stage of the game, and avoid proposing actions that are not currently feasible.
        """

    def generate_prompts(self):
        if self.race == 'protoss':
            self.example_input_prompt = r"""
--- example input ---
--- StarCraft II Game Summary ---
Description: This section primarily records and summarizes our observations.
Details:
chunk0:At 06:48 game time, our current StarCraft II situation is as follows:\n\nResources:\n- game_time: 06:48\n- worker_supply: 63\n- mineral: 2480\n- gas: 2972\n- supply_left: 12\n- supply_cap: 99\n- supply_used: 87\n- army_supply: 14\n- base_count: 5\n\nBuildings:\n- base_count: 5\n- pylon_count: 3\n- gas_buildings_count: 9\n- gateway_count: 4\n- Zealot_count: 7\n- planning_worker_count: 3\n\nUnits:\n- base_count: 5\n- pylon_count: 3\n- gas_buildings_count: 9\n- gateway_count: 4\n- Zealot_count: 7\n- planning_worker_count: 3\n\nIn-process:\n- planning_worker_count: 3\n\nEnemy Information:\n- enemy_UnitTypeId.ZERGLING: 1\n\n:At 06:49 game time, our current StarCraft II situation is as follows:...chunk{K_1}
            """
            self.example_output_prompt = """
--- example output --- 
# StarCraft II Game Analysis
1. Game Overview: At 06:48 game time, our current situation is promising. We have 63 workers, 2480 minerals, and 2972 gas. Our supply cap is at 99 with 12 supply left, and our army supply is 14. We have established five bases.

2. Current Game Stage: Based on the game time and resource availability, we are in the mid-game stage.

3. Our Situation:
    3.1 Units and Buildings: We have a substantial worker force and five bases. We also have 3 pylons, 9 gas buildings, 4 gateways, and 7 Zealots. There are 3 workers planned for construction.
    3.2 Economy: Our economy is healthy, with plenty of resources. We have an excellent worker supply to maintain and even expand our economy.
    3.3 Technology: We seem to be lagging in technology development. We have Zealots in our army, but there is no evidence of other advanced units or technologies being developed. Furthermore, the absence of a Cybernetics Core suggests that we are currently limited in our capacity to research higher technologies or produce more advanced units
4. Our Strategy: We seem to have a balanced approach, focusing on both economic growth and military power. The high worker count and the existence of Zealots suggest a strategy of resource expansion and defense.

5. Enemy's Strategy: The enemy has at least one Zergling, suggesting they might be at the early stages of army development or employing a Zerg rush strategy.

6. Key Information: The most crucial aspect at this moment is our strong economy, coupled with our reliance on lower-tier military power (Zealots). However, our technological development is lagging, limiting our unit diversity and potentially leaving us vulnerable to more advanced enemy forces. Our future success is contingent on how we manage to leverage our economic advantage to swiftly boost our technological development and diversify our military strength.

Suggestions:

1. Our Strategy: We should focus on enhancing our technological capabilities alongside continuing to develop our army and expanding our economy. Be mindful of possible Zerg rush attacks.

2. Units and Buildings: Given our technological limitations, it's vital to optimally utilize our Zealots. In the meantime, construction of a Cybernetics Core is necessary to unlock more advanced units and technologies. Further, increasing the supply cap by building more pylons may be beneficial.

3. Economy: Efficient resource gathering is crucial. Our resource reserves should support both immediate army development and future technological upgrades. Consider expanding to new resource locations to facilitate this.

4. Technology: The immediate task is to build a Cybernetics Core to enable the research of higher technologies. Following that, based on the game progression and the enemy's strategy, decide on a focused technology path to gain a technological edge.

This revised strategy should help address the current limitations and better prepare us for upcoming challenges.

Decisions:
0: <BUILD CYBERNETICSCORE>
1: <BUILD PYLON>
2: <BUILD FORGE>
3: <RESEARCH WARPGATERESEARCH>
4: <CHRONOBOOST NEXUS>
"""
        elif self.race == 'zerg':
            self.example_input_prompt = r"""
--- example input ---
--- StarCraft II Game Summary ---
Description: This section primarily records and summarizes our observations.
Details:
chunk0: "At 03:14 game time, our current StarCraft II situation is as follows:\n\nResources:\n- game_time: 03:14\n- worker_supply: 19\n- mineral: 75\n- gas: 184\n- supply_left: 21\n- supply_cap: 44\n- supply_used: 23\n- base_count: 3\n\nBuildings:\n- base_count: 3\n- roach_warren_count: 1\n- gas_buildings_count: 4\n- overlord_count: 4\n- larva_count: 1\n- drone_count: 19\n- planning_base_count: 1\n- planning_gas_building_count: 5\n- planning_drone_count: 3\n\nUnits:\n- base_count: 3\n- roach_warren_count: 1\n- gas_buildings_count: 4\n- overlord_count: 4\n- larva_count: 1\n- drone_count: 19\n- planning_base_count: 1\n- planning_gas_building_count: 5\n- planning_drone_count: 3\n\nIn-process:\n- planning_base_count: 1\n- planning_gas_building_count: 5\n- planning_drone_count: 3\n\nEnemy Information:\n- No known enemy units\n\n"
chunk1:  "At 03:14 game time, our current StarCraft II situation is as follows:\n\nResources:\n- game_time: 03:14\n- worker_supply: 21\n- mineral: 85\n- gas: 188\n- supply_left: 21\n- supply_cap: 44\n- supply_used: 23\n- base_count: 3\n\nBuildings:\n- base_count: 3\n- roach_warren_count: 1\n- gas_buildings_count: 4\n- overlord_count: 4\n- larva_count: 1\n- drone_count: 21\n- planning_base_count: 1\n- planning_gas_building_count: 5\n- planning_drone_count: 2\n\nUnits:\n- base_count: 3\n- roach_warren_count: 1\n- gas_buildings_count: 4\n- overlord_count: 4\n- larva_count: 1\n- drone_count: 21\n- planning_base_count: 1\n- planning_gas_building_count: 5\n- planning_drone_count: 2\n\nIn-process:\n- planning_base_count: 1\n- planning_gas_building_count: 5\n- planning_drone_count: 2\n\nEnemy Information:\n- No known enemy units\n\n",  ...
"""
            self.example_output_prompt = r"""
1. Game Overview: At 03:14 game time, our current situation is fairly early in the game. We have a total of 3 bases, 19 workers, 75 minerals, and 184 gas. Our supply cap is at 44, with 21 supply left. Furthermore, we're planning to expand with an additional base, 5 more gas buildings, and 3 more drones.

2. Current Game Stage: Given the game time and resources, we are in the early to mid-game stage.

3. Our Situation:
    3.1 Units and Buildings: 
        - We have 3 bases and a roach warren.
        - Our support units include 4 overlords.
        - There are 19 drones actively working.
        - Upcoming constructions include a new base, 5 gas buildings, and 3 additional drones.
    3.2 Economy: 
        - We're currently sitting on 75 minerals and 184 gas. 
        - With 19 drones, our resource collection rate is in a decent position, but further improvement is advisable.
    3.3 Technology: 
        - We have a roach warren in place, allowing for Roach production.
        - Several research actions were executed, including HYDRAMOVEMENTSPEED and ZERGGROUNDARMORSLEVEL3.
        - Notably, some actions failed due to missing buildings: Baneling Nest, Spire, Spawning Pool, Lair, and Hive.

4. Our Strategy: Our strategy seems to focus on diverse unit production and research upgrades. The recent research actions suggest we're aiming for improved mobility and defense.

5. Enemy's Strategy: Currently, no information is available about enemy units. Our priority should be scouting to gather more data about the opponent.

6. Key Information: 
    - We have made significant advancements in research and development.
    - Certain research actions failed, indicating the absence of crucial buildings like the Spire, Baneling Nest, and Hive. We need to address these gaps for better technological progress.

Suggestions:
    1. Our Strategy: Prioritize scouting to understand the enemy's strategy. Continue focusing on a balanced approach to both economy and army.
    2. Units and Buildings: Address the gaps in our tech tree. Consider constructing a Baneling Nest, Spire, Spawning Pool, and advancing to Lair or Hive.
    3. Economy: With an upcoming expansion and more gas buildings, ensure sufficient worker production to optimize resource collection.
    4. Technology: Successful research indicates our commitment to technological advancements. Continue on this path, but ensure the required buildings are in place for unhindered progression.


Decisions:
0: <RESEARCH ZERGLINGMOVEMENTSPEED>
1: <TRAIN DRONE>
2: <TRAIN DRONE>
3: <QUEUE INJECTLARVA>
4: <TRAIN QUEUE>

            """
        elif self.race == 'terran':
            self.example_input_prompt = "todo"

            self.example_output_prompt = "todo"
        else:
            raise NotImplementedError
        return self.system_prompt, self.example_input_prompt, self.example_output_prompt


class StarCraftIIPrompt_V2:
    def __init__(self, race, K, action_dict,game_style):
        self.race = race.lower()
        self.game_style=game_style.lower()
        self.race_specific_prompt = {
            "protoss": "For Protoss, the Chrono Boost ability available at the Nexus is crucial. It accelerates the production and research speed of a building. Important buildings that benefit from Chrono Boost include the Nexus itself (for probe production), the Gateway (for basic unit production), the Robotics Facility (for advanced unit production), and various tech buildings (for research upgrades). Keeping an optimal usage of Nexus's energy for Chrono Boost can significantly improve efficiency.",

            "zerg": "For Zerg, larvae are a unique resource used for the production of all Zerg units. Larvae spawn naturally from Hatcheries, Lairs, or Hives, but their production rate can be significantly increased with the Queen's Inject Larva ability. Managing larvae effectively and ensuring a consistent usage of the Inject Larva ability is essential for Zerg to maintain a steady production of units."
        }
        self.system_prompt = f"""
        You are an AI trained in analyzing and summarizing StarCraft II games. You understand the nuances and strategies of the {self.race} race. 
        Based on the summaries of multiple rounds in a game, we want you to analyze the game progression in a structured way. Your analysis should include the following aspects:

        1. **Game Overview**: Provide a brief overview of the current situation based on all the rounds.

        2. **Executed Actions**: Examine the list of 'executed_actions' to determine which actions were successfully carried out during the game and their possible implications on the current game state.

        3. **Failed Actions**: Analyze the 'failed_actions' to identify why certain actions failed. Determine if there were resource constraints, strategic mistakes, or other reasons that led to these failed actions. Suggest ways to avoid these failures in the future.

        4. **Current Game Stage**: Determine the stage of the game based on the information of all rounds. Is it the early game, mid-game, or late game?

        5. **Our Situation**: Describe our current status in terms of:
            5.1 Units and Buildings: Analyze the state of our units and buildings.
            5.2 Economy: Evaluate our economic condition, including resource collection and usage.
            5.3 Technology: Describe the status of our technological research and what technologies we have unlocked so far. Analyze our technology tree, indicating the available and potential upgrades or units.

        6. **Our Strategy**: Infer our potential strategy based on our current situation and the information of all rounds.

        7. **Enemy's Strategy**: Infer the enemy's potential strategy, based on the available information.

        8. **Key Information**: Highlight the most important aspects from all rounds that have significantly influenced the game.

        {self.race_specific_prompt.get(self.race)}

        Based on the game situation and strategies used by both sides, provide specific suggestions for the following areas:

        1. **Our Strategy**: Propose adjustments to our current strategy to counter the enemy's moves and capitalize on our strengths.

        2. **Units and Buildings**: Offer ways to enhance our unit composition and improve our building layout, suited to the current stage of the game.

        3. **Economy**: Recommend better practices for resource gathering and usage, in line with our strategic needs.

        4. **Technology**: Suggest focused research paths to gain technological advantages, considering our current research status and technology tree.

        Lastly, consider the current situation and the suggestions provided, make {K} actionable and specific decisions from the action dictionary{action_dict}. This dictionary comprises four categories of actions: unit production, building construction, technology research, and other actions. Remember to align these decisions with the current stage of the game, and avoid proposing actions that are not currently feasible.
        
        """

    def generate_prompts(self):
        if self.race == 'protoss':
            self.example_input_prompt = r"""
chunk0:"At 04:06 game time, our current StarCraft II situation is as follows:\n\nResources:\n- game_time: 04:06\n- worker_supply: 27\n- mineral: 55\n- gas: 464\n- supply_left: 7\n- supply_cap: 46\n- supply_used: 39\n- army_supply: 8\n- base_count: 2\n\nBuildings:\n- base_count: 2\n- pylon_count: 2\n- gas_buildings_count: 4\n- gateway_count: 4\n- cybernetics_core_count: 1\n- robotics_facility_count: 1\n- Zealot_count: 3\n- planning_gateway_count: 1\n- planning_robotics_facility_count: 1\n- planning_worker_count: 1\n- planning_stalker_count: 1\n\nUnits:\n- base_count: 2\n- pylon_count: 2\n- gas_buildings_count: 4\n- gateway_count: 4\n- cybernetics_core_count: 1\n- robotics_facility_count: 1\n- Zealot_count: 3\n- planning_gateway_count: 1\n- planning_robotics_facility_count: 1\n- planning_worker_count: 1\n- planning_stalker_count: 1\n\nIn-process:\n- planning_gateway_count: 1\n- planning_robotics_facility_count: 1\n- planning_worker_count: 1\n- planning_stalker_count: 1\n\nResearch:\n- warpgate_research_status: 0.514285683631897\n\nEnemy Information:\n- enemy_UnitTypeId.EXTRACTOR: 1\n- enemy_UnitTypeId.HATCHERY: 1\n- enemy_UnitTypeId.SPAWNINGPOOL: 1\n\n
chunk1:...
chunk{K_1}:...
            """
            self.example_output_prompt = """
1. Game Overview: At 04:06 game time, our situation is as follows: We have 27 workers, 65 minerals, and 468 gas. Our supply cap is at 46 with 7 supply left, and our army supply is 8. We have two bases and a decent number of buildings and units.

2. Current Game Stage: Based on the game time and resource availability, we are still in the early game stage.

3. Our Situation:
   3.1 Units and Buildings: We have a moderate number of buildings, including 2 pylons, 4 gateways, 1 cybernetics core, and 1 robotics facility. Our army consists of 3 Zealots. We have 1 worker planned for construction.
   3.2 Economy: Our economy is still developing, with limited resources. We need to focus on expanding our worker count and gathering more minerals and gas.
   3.3 Technology: We have a cybernetics core and a robotics facility, but there is no evidence of any advanced units or technologies being developed. We should prioritize researching and unlocking higher technologies to strengthen our army.

4. Our Strategy: Currently, our strategy seems to be focused on early game expansion and defense. We need to transition into a more aggressive strategy by developing advanced units and technologies.

5. Enemy's Strategy: The enemy has built an extractor, hatchery, and spawning pool. This suggests a standard Zerg opening, focusing on economy and early unit production.

6. Key Information: The most crucial aspect at this moment is our limited technology and unit diversity. To counter the enemy's strategy and gain an advantage, we need to prioritize researching higher technologies and expanding our unit composition.

Suggestions:

1. Our Strategy: Transition into a more aggressive strategy by focusing on advanced unit production and technology research. Consider harassment tactics and map control to disrupt the enemy's economy.

2. Units and Buildings: Increase the number of workers to boost our resource gathering. Expand our building infrastructure by constructing additional gateways and robotics facilities. This will allow for faster unit production and technology research.

3. Economy: Prioritize resource gathering by assigning more workers to mineral and gas harvesting. Consider expanding to additional bases to increase our income and support our unit production.

4. Technology: Research higher technologies to unlock advanced units and upgrades. Prioritize researching Warpgate technology to enable faster unit production. Consider researching upgrades for Zealots or unlocking new unit types like Stalkers or Immortals.

Decisions:
0: <TRAIN PROBE>
1: <TRAIN PROBE>
2: <CHRONOBOOST NEXUS>
3: <TRAIN STALKER>
4: <CHRONOBOOST CYBERNETICSCORE>


"""
        elif self.race == 'zerg':
            self.example_input_prompt = r"""
--- example input ---
--- StarCraft II Game Summary ---
Description: This section primarily records and summarizes our observations.
Details:
chunk0: "At 03:14 game time, our current StarCraft II situation is as follows:\n\nResources:\n- game_time: 03:14\n- worker_supply: 19\n- mineral: 75\n- gas: 184\n- supply_left: 21\n- supply_cap: 44\n- supply_used: 23\n- base_count: 3\n\nBuildings:\n- base_count: 3\n- roach_warren_count: 1\n- gas_buildings_count: 4\n- overlord_count: 4\n- larva_count: 1\n- drone_count: 19\n- planning_base_count: 1\n- planning_gas_building_count: 5\n- planning_drone_count: 3\n\nUnits:\n- base_count: 3\n- roach_warren_count: 1\n- gas_buildings_count: 4\n- overlord_count: 4\n- larva_count: 1\n- drone_count: 19\n- planning_base_count: 1\n- planning_gas_building_count: 5\n- planning_drone_count: 3\n\nIn-process:\n- planning_base_count: 1\n- planning_gas_building_count: 5\n- planning_drone_count: 3\n\nEnemy Information:\n- No known enemy units\n\n"
chunk1:  "At 03:14 game time, our current StarCraft II situation is as follows:\n\nResources:\n- game_time: 03:14\n- worker_supply: 21\n- mineral: 85\n- gas: 188\n- supply_left: 21\n- supply_cap: 44\n- supply_used: 23\n- base_count: 3\n\nBuildings:\n- base_count: 3\n- roach_warren_count: 1\n- gas_buildings_count: 4\n- overlord_count: 4\n- larva_count: 1\n- drone_count: 21\n- planning_base_count: 1\n- planning_gas_building_count: 5\n- planning_drone_count: 2\n\nUnits:\n- base_count: 3\n- roach_warren_count: 1\n- gas_buildings_count: 4\n- overlord_count: 4\n- larva_count: 1\n- drone_count: 21\n- planning_base_count: 1\n- planning_gas_building_count: 5\n- planning_drone_count: 2\n\nIn-process:\n- planning_base_count: 1\n- planning_gas_building_count: 5\n- planning_drone_count: 2\n\nEnemy Information:\n- No known enemy units\n\n",  ...


--- Executed Actions ---
Description: This section primarily records the actions we have already executed.
Details:
- BUILD HYDRALISKDEN
- RESEARCH HYDRAMOVEMENTSPEED

--- Failed Actions [IMPORTANT] ---
Description: This section primarily records the actions that failed and the corresponding reasons.
Details:
- Action failed: TRAIN HYDRALISK, Reason: Hydralisk den not available
- Action failed: MULTI-ATTACK, Reason: No army available for attack
            """
            self.example_output_prompt = r"""
1. Game Overview: At 03:14 game time, our current situation is fairly early in the game. We have a total of 3 bases, 19 workers, 75 minerals, and 184 gas. Our supply cap is at 44, with 21 supply left. Furthermore, we're planning to expand with an additional base, 5 more gas buildings, and 3 more drones.

2. Current Game Stage: Given the game time and resources, we are in the early to mid-game stage.

3. Our Situation:
    3.1 Units and Buildings: 
        - We have 3 bases and a roach warren.
        - Our support units include 4 overlords.
        - There are 19 drones actively working.
        - Upcoming constructions include a new base, 5 gas buildings, and 3 additional drones.
    3.2 Economy: 
        - We're currently sitting on 75 minerals and 184 gas. 
        - With 19 drones, our resource collection rate is in a decent position, but further improvement is advisable.
    3.3 Technology: 
        - We have a roach warren in place, allowing for Roach production.
        - Several research actions were executed, including HYDRAMOVEMENTSPEED and ZERGGROUNDARMORSLEVEL3.
        - Notably, some actions failed due to missing buildings: Baneling Nest, Spire, Spawning Pool, Lair, and Hive.

4. Our Strategy: Our strategy seems to focus on diverse unit production and research upgrades. The recent research actions suggest we're aiming for improved mobility and defense.

5. Enemy's Strategy: Currently, no information is available about enemy units. Our priority should be scouting to gather more data about the opponent.

6. Key Information: 
    - We have made significant advancements in research and development.
    - Certain research actions failed, indicating the absence of crucial buildings like the Spire, Baneling Nest, and Hive. We need to address these gaps for better technological progress.

Suggestions:
    1. Our Strategy: Prioritize scouting to understand the enemy's strategy. Continue focusing on a balanced approach to both economy and army.
    2. Units and Buildings: Address the gaps in our tech tree. Consider constructing a Baneling Nest, Spire, Spawning Pool, and advancing to Lair or Hive.
    3. Economy: With an upcoming expansion and more gas buildings, ensure sufficient worker production to optimize resource collection.
    4. Technology: Successful research indicates our commitment to technological advancements. Continue on this path, but ensure the required buildings are in place for unhindered progression.

            
Decisions:
0: <RESEARCH ZERGLINGMOVEMENTSPEED>
1: <TRAIN DRONE>
2: <TRAIN DRONE>
3: <QUEUE INJECTLARVA>
4: <TRAIN QUEUE>

            """
        elif self.race == 'terran':
            self.example_input_prompt = "todo"

            self.example_output_prompt = "todo"
        else:
            raise NotImplementedError
        return self.system_prompt, self.example_input_prompt, self.example_output_prompt


class StarCraftIIPrompt_V3:
    def __init__(self, race, K, action_dict, game_style):
        self.race = race.lower()
        self.game_style = game_style.lower()
        action_list_str = self.format_action_dict(action_dict)

        self.race_specific_prompt = {
            "protoss": "For Protoss, the Chrono Boost ability available at the Nexus is crucial. It accelerates the "
                       "production and research speed of a building. Important buildings that benefit from Chrono "
                       "Boost include the Nexus itself (for probe production), the Gateway (for basic unit "
                       "production), the Robotics Facility (for advanced unit production), and various tech buildings "
                       "(for research upgrades). Keeping an optimal usage of Nexus's energy for Chrono Boost can "
                       "significantly improve efficiency.",
            "zerg": "For Zerg, larvae are a unique resource used for the production of all Zerg units. Larvae spawn "
                    "naturally from Hatcheries, Lairs, or Hives, but their production rate can be significantly "
                    "increased with the Queen's Inject Larva ability. Managing larvae effectively and ensuring a "
                    "consistent usage of the Inject Larva ability is essential for Zerg to maintain a steady "
                    "production of units."
        }
        self.game_style_specific_prompt = {
            "protoss": {
                "aggressive": """Utilize Astrea's 2 base blink all-in strategy for early aggression against Zerg. 
                Focus on Stalkers and Adepts, tech up quickly, and maximize unit mobility with Warp Prism. Use Adepts 
                for harassment, maintain Stalker control, and capitalize on Zerg over-droning.""",

                "air_superiority": """Seek aerial dominance against Zerg with the 'pvz_fast_carriers' tactic. 
                Prioritize Carriers and Void Rays, tech up quickly, and expand your economy. Emphasize Protoss Air 
                Weapons upgrades, secure bases with Photon Cannons, and maintain strong defenses with Shield 
                Batteries.""",

                "immortal_archon_push": """Leverage the Immortal-Archon combo for a powerful mid-game push. Tech up 
                swiftly, focus on Immortals, morph High Templars into Archons, and use a Warp Prism for unit 
                mobility. Aim to overpower defenses with the combined strength of Immortals and Archons.""",
                "4_base_zealot_archon": """Adopt a 4 base Zealot-Archon strategy against opponents. Start with a 
                defensive Stargate opening, producing a few Void Rays. Expand your economy rapidly, and prioritize 
                ground unit attack and shield upgrades. Produce a massive Zealot and Archon force (using High 
                Templars) for a devastating assault.""",

                "fast_4rd_base_zealot_stalker": """Embrace the fast-4rd base and Zealot-Stalker tactic. Begin with a 
                Stargate,focusing on Void Rays for early defense. Rapidly expand bases, boosting ground unit attack 
                and shields. Mass produce Zealots and Stalkers for frontline battles. Transition to Colossus for 
                enhanced offensive capabilities as resources permit."""
            },
        }

        self.system_prompt = f""" 
                You are an AI trained in analyzing and summarizing StarCraft II games. You understand the nuances and strategies of the {self.race} race. 
        Based on the summaries of multiple rounds in a game, we want you to analyze the game progression in a structured way. Your analysis should include the following aspects:
        1. Game Overview: Provide a brief overview of the current situation based on all the rounds.
        2. Current Game Stage: Determine the stage of the game based on the information of all rounds. Is it the early game, mid-game, or late game?
        3. Our Situation: Describe our current status in terms of:
            3.1 Units and Buildings: Analyze the state of our units and buildings.
            3.2 Economy: Evaluate our economic condition, including resource collection and usage.
            3.3 Technology: Describe the status of our technological research and what technologies we have unlocked so far. Analyze our technology tree, indicating the available and potential upgrades or units.
        4. Our Strategy: Infer our potential strategy based on our current situation and the information of all rounds.
        5. Enemy's Strategy: Infer the enemy's potential strategy, based on the available information.
        6. Key Information: Highlight the most important aspects from all rounds that have significantly influenced the game.

        {self.race_specific_prompt.get(self.race)}

        Based on the game situation and strategies used by both sides, provide specific suggestions for the following areas:

        1.Our Strategy: Propose adjustments to our current strategy to counter the enemy's moves and capitalize on our strengths.

        2.Units and Buildings: Offer ways to enhance our unit composition and improve our building layout, suited to the current stage of the game.

        3.Economy: Recommend better practices for resource gathering and usage, in line with our strategic needs.

        4.Technology: Suggest focused research paths to gain technological advantages, considering our current research status and technology tree.

        Lastly, consider the current situation and the suggestions provided, make {K} actionable and specific decisions from the following action list:
         {action_list_str}  
        These decisions should be numbered starting from 0, representing the sequence in which they should be executed, with 0 being the most immediate and urgent action. For example:
      
        0: <ACTION_TO_BE_EXECUTED_FIRST> 
        1: <ACTION_TO_BE_EXECUTED_SECOND> 
        2: <ACTION_TO_BE_EXECUTED_THIRD> 
        ...
        Note: Please ensure that each action is feasible considering the current game stage and available resources, and aligns with the overarching strategy. Prioritize actions based on immediate need, strategic importance, resource availability, and the feasibility of executing them in sequence. Avoid proposing actions that are not currently feasible or do not align with the strategic needs of the current game situation.

        """

    def format_action_dict(self, action_dict):
        formatted_str_list = []
        for category, actions in action_dict.items():
            formatted_str_list.append(f"#### {category}")
            for action_id, action_name in actions.items():
                formatted_str_list.append(f"- {action_name}")

        return '\n'.join(formatted_str_list)
    def generate_prompts(self):
        if self.race == 'protoss':
            self.example_input_prompt = r"""
            --- example input --- 
            --- StarCraft II Game Summary --- 
            Description: 
            chunk0:At 06:48 game time, our current StarCraft II situation is as follows:\n\nResources:\n- game_time: 06:48\n- worker_supply: 63\n- mineral: 2480\n- gas: 2972\n- supply_left: 12\n- supply_cap: 99\n- supply_used: 87\n- army_supply: 14\n- base_count: 5\n\nBuildings:\n- base_count: 5\n- pylon_count: 3\n- gas_buildings_count: 9\n- gateway_count: 4\n- Zealot_count: 7\n- planning_worker_count: 3\n\nUnits:\n- base_count: 5\n- pylon_count: 3\n- gas_buildings_count: 9\n- gateway_count: 4\n- Zealot_count: 7\n- planning_worker_count: 3\n\nIn-process:\n- planning_worker_count: 3\n\nEnemy Information:\n- enemy_UnitTypeId.ZERGLING: 1\n\n:At 06:49 game time, our current StarCraft II situation is as follows:...chunk{K_1}
            """
            self.example_output_prompt = """
--- example output --- 
# StarCraft II Game Analysis
1. Game Overview: At 06:48 game time, our current situation is promising. We have 63 workers, 2480 minerals, and 2972 gas. Our supply cap is at 99 with 12 supply left, and our army supply is 14. We have established five bases.

2. Current Game Stage: Based on the game time and resource availability, we are in the mid-game stage.

3. Our Situation:
    3.1 Units and Buildings: We have a substantial worker force and five bases. We also have 3 pylons, 9 gas buildings, 4 gateways, and 7 Zealots. There are 3 workers planned for construction.
    3.2 Economy: Our economy is healthy, with plenty of resources. We have an excellent worker supply to maintain and even expand our economy.
    3.3 Technology: We seem to be lagging in technology development. We have Zealots in our army, but there is no evidence of other advanced units or technologies being developed. Furthermore, the absence of a Cybernetics Core suggests that we are currently limited in our capacity to research higher technologies or produce more advanced units
4. Our Strategy: We seem to have a balanced approach, focusing on both economic growth and military power. The high worker count and the existence of Zealots suggest a strategy of resource expansion and defense.

5. Enemy's Strategy: The enemy has at least one Zergling, suggesting they might be at the early stages of army development or employing a Zerg rush strategy.

6. Key Information: The most crucial aspect at this moment is our strong economy, coupled with our reliance on lower-tier military power (Zealots). However, our technological development is lagging, limiting our unit diversity and potentially leaving us vulnerable to more advanced enemy forces. Our future success is contingent on how we manage to leverage our economic advantage to swiftly boost our technological development and diversify our military strength.

Suggestions:

1. Our Strategy: We should focus on enhancing our technological capabilities alongside continuing to develop our army and expanding our economy. Be mindful of possible Zerg rush attacks.

2. Units and Buildings: Given our technological limitations, it's vital to optimally utilize our Zealots. In the meantime, construction of a Cybernetics Core is necessary to unlock more advanced units and technologies. Further, increasing the supply cap by building more pylons may be beneficial.

3. Economy: Efficient resource gathering is crucial. Our resource reserves should support both immediate army development and future technological upgrades. Consider expanding to new resource locations to facilitate this.

4. Technology: The immediate task is to build a Cybernetics Core to enable the research of higher technologies. Following that, based on the game progression and the enemy's strategy, decide on a focused technology path to gain a technological edge.

This revised strategy should help address the current limitations and better prepare us for upcoming challenges.


Decisions:
0: <BUILD CYBERNETICSCORE>
1: <BUILD PYLON>
2: <BUILD FORGE>
3: <RESEARCH WARPGATERESEARCH>
4: <CHRONOBOOST NEXUS>
"""
        elif self.race == 'zerg':
            self.example_input_prompt = r"""
--- example input ---
--- StarCraft II Game Summary ---
Description: This section primarily records and summarizes our observations.
Details:
chunk0: "At 03:14 game time, our current StarCraft II situation is as follows:\n\nResources:\n- game_time: 03:14\n- worker_supply: 19\n- mineral: 75\n- gas: 184\n- supply_left: 21\n- supply_cap: 44\n- supply_used: 23\n- base_count: 3\n\nBuildings:\n- base_count: 3\n- roach_warren_count: 1\n- gas_buildings_count: 4\n- overlord_count: 4\n- larva_count: 1\n- drone_count: 19\n- planning_base_count: 1\n- planning_gas_building_count: 5\n- planning_drone_count: 3\n\nUnits:\n- base_count: 3\n- roach_warren_count: 1\n- gas_buildings_count: 4\n- overlord_count: 4\n- larva_count: 1\n- drone_count: 19\n- planning_base_count: 1\n- planning_gas_building_count: 5\n- planning_drone_count: 3\n\nIn-process:\n- planning_base_count: 1\n- planning_gas_building_count: 5\n- planning_drone_count: 3\n\nEnemy Information:\n- No known enemy units\n\n"
chunk1:  "At 03:14 game time, our current StarCraft II situation is as follows:\n\nResources:\n- game_time: 03:14\n- worker_supply: 21\n- mineral: 85\n- gas: 188\n- supply_left: 21\n- supply_cap: 44\n- supply_used: 23\n- base_count: 3\n\nBuildings:\n- base_count: 3\n- roach_warren_count: 1\n- gas_buildings_count: 4\n- overlord_count: 4\n- larva_count: 1\n- drone_count: 21\n- planning_base_count: 1\n- planning_gas_building_count: 5\n- planning_drone_count: 2\n\nUnits:\n- base_count: 3\n- roach_warren_count: 1\n- gas_buildings_count: 4\n- overlord_count: 4\n- larva_count: 1\n- drone_count: 21\n- planning_base_count: 1\n- planning_gas_building_count: 5\n- planning_drone_count: 2\n\nIn-process:\n- planning_base_count: 1\n- planning_gas_building_count: 5\n- planning_drone_count: 2\n\nEnemy Information:\n- No known enemy units\n\n",  ...
"""
            self.example_output_prompt = r"""
--- example output --- 
# StarCraft II Game Analysis
1. Game Overview: At 03:14 game time, our current situation is fairly early in the game. We have a total of 3 bases, 19 workers, 75 minerals, and 184 gas. Our supply cap is at 44, with 21 supply left. Furthermore, we're planning to expand with an additional base, 5 more gas buildings, and 3 more drones.

2. Current Game Stage: Given the game time and resources, we are in the early to mid-game stage.

3. Our Situation:
    3.1 Units and Buildings: 
        - We have 3 bases and a roach warren.
        - Our support units include 4 overlords.
        - There are 19 drones actively working.
        - Upcoming constructions include a new base, 5 gas buildings, and 3 additional drones.
    3.2 Economy: 
        - We're currently sitting on 75 minerals and 184 gas. 
        - With 19 drones, our resource collection rate is in a decent position, but further improvement is advisable.
    3.3 Technology: 
        - We have a roach warren in place, allowing for Roach production.
        - Several research actions were executed, including HYDRAMOVEMENTSPEED and ZERGGROUNDARMORSLEVEL3.
        - Notably, some actions failed due to missing buildings: Baneling Nest, Spire, Spawning Pool, Lair, and Hive.

4. Our Strategy: Our strategy seems to focus on diverse unit production and research upgrades. The recent research actions suggest we're aiming for improved mobility and defense.

5. Enemy's Strategy: Currently, no information is available about enemy units. Our priority should be scouting to gather more data about the opponent.

6. Key Information: 
    - We have made significant advancements in research and development.
    - Certain research actions failed, indicating the absence of crucial buildings like the Spire, Baneling Nest, and Hive. We need to address these gaps for better technological progress.

Suggestions:
    1. Our Strategy: Prioritize scouting to understand the enemy's strategy. Continue focusing on a balanced approach to both economy and army.
    2. Units and Buildings: Address the gaps in our tech tree. Consider constructing a Baneling Nest, Spire, Spawning Pool, and advancing to Lair or Hive.
    3. Economy: With an upcoming expansion and more gas buildings, ensure sufficient worker production to optimize resource collection.
    4. Technology: Successful research indicates our commitment to technological advancements. Continue on this path, but ensure the required buildings are in place for unhindered progression.


Decisions:
0: <RESEARCH ZERGLINGMOVEMENTSPEED>
1: <TRAIN DRONE>
2: <TRAIN DRONE>
3: <QUEUE INJECTLARVA>
4: <TRAIN QUEUE>

            """
        elif self.race == 'terran':
            self.example_input_prompt = "todo"

            self.example_output_prompt = "todo"
        else:
            raise NotImplementedError
        return self.system_prompt, self.example_input_prompt, self.example_output_prompt


class StarCraftIIPrompt_V4:
    def __init__(self, race, K, action_dict):
        self.race = race.lower()
        self.race_specific_prompt = {
            "protoss": "For Protoss, keep an eye on Nexus's energy to Chrono Boost important structures.",
            "zerg": "For Zerg, pay attention to whether there are enough larvae. If not, we should consider adding the INJECTLARVA command to the queue.",
        }
        self.system_prompt = f"""
        You are an AI trained in analyzing and summarizing StarCraft II games. You understand the nuances and strategies of the {self.race} race. 
        Based on the summaries of multiple rounds in a game, we want you to analyze the game progression in a structured way. Your analysis should include the following aspects:
        1. Game Overview: Provide a brief overview of the current situation based on all the rounds.
        2. Current Game Stage: Determine the stage of the game based on the information of all rounds. Is it the early game, mid-game, or late game?
        3. Our Situation: Describe our current status in terms of:
            3.1 Units and Buildings: Analyze the state of our units and buildings.
            3.2 Economy: Evaluate our economic condition, including resource collection and usage.
            3.3 Technology: Describe the status of our technological research and what technologies we have unlocked so far. Analyze our technology tree, indicating the available and potential upgrades or units.
888        4. Our Strategy: Infer our potential strategy based on our current situation and the information of all rounds.
        5. Enemy's Strategy: Infer the enemy's potential strategy, based on the available information.
        6. Key Information: Highlight the most important aspects from all rounds that have significantly influenced the game.

        {self.race_specific_prompt.get(self.race)}

        Based on the game situation and strategies used by both sides, provide specific suggestions for the following areas:

        1.Our Strategy: Propose adjustments to our current strategy to counter the enemy's moves and capitalize on our strengths.

        2.Units and Buildings: Offer ways to enhance our unit composition and improve our building layout, suited to the current stage of the game.

        3.Economy: Recommend better practices for resource gathering and usage, in line with our strategic needs.

        4.Technology: Suggest focused research paths to gain technological advantages, considering our current research status and technology tree.

        Lastly, consider the current situation and the suggestions provided, make {K} actionable and specific decisions from the action dictionary{action_dict}. This dictionary comprises four categories of actions: unit production, building construction, technology research, and other actions. Remember to align these decisions with the current stage of the game, and avoid proposing actions that are not currently feasible.
        """

    def generate_prompts(self):
        if self.race == 'protoss':
            self.example_input_prompt = r"chunk0:At 06:48 game time, our current StarCraft II situation is as follows:\n\nResources:\n- game_time: 06:48\n- worker_supply: 63\n- mineral: 2480\n- gas: 2972\n- supply_left: 12\n- supply_cap: 99\n- supply_used: 87\n- army_supply: 14\n- base_count: 5\n\nBuildings:\n- base_count: 5\n- pylon_count: 3\n- gas_buildings_count: 9\n- gateway_count: 4\n- Zealot_count: 7\n- planning_worker_count: 3\n\nUnits:\n- base_count: 5\n- pylon_count: 3\n- gas_buildings_count: 9\n- gateway_count: 4\n- Zealot_count: 7\n- planning_worker_count: 3\n\nIn-process:\n- planning_worker_count: 3\n\nEnemy Information:\n- enemy_UnitTypeId.ZERGLING: 1\n\n:At 06:49 game time, our current StarCraft II situation is as follows:...chunk{K_1}"

            self.example_output_prompt = """
1. Game Overview: At 06:48 game time, our current situation is promising. We have 63 workers, 2480 minerals, and 2972 gas. Our supply cap is at 99 with 12 supply left, and our army supply is 14. We have established five bases.

2. Current Game Stage: Based on the game time and resource availability, we are in the mid-game stage.

3. Our Situation:
    3.1 Units and Buildings: We have a substantial worker force and five bases. We also have 3 pylons, 9 gas buildings, 4 gateways, and 7 Zealots. There are 3 workers planned for construction.
    3.2 Economy: Our economy is healthy, with plenty of resources. We have an excellent worker supply to maintain and even expand our economy.
    3.3 Technology: We seem to be lagging in technology development. We have Zealots in our army, but there is no evidence of other advanced units or technologies being developed. Furthermore, the absence of a Cybernetics Core suggests that we are currently limited in our capacity to research higher technologies or produce more advanced units
4. Our Strategy: We seem to have a balanced approach, focusing on both economic growth and military power. The high worker count and the existence of Zealots suggest a strategy of resource expansion and defense.

5. Enemy's Strategy: The enemy has at least one Zergling, suggesting they might be at the early stages of army development or employing a Zerg rush strategy.

6. Key Information: The most crucial aspect at this moment is our strong economy, coupled with our reliance on lower-tier military power (Zealots). However, our technological development is lagging, limiting our unit diversity and potentially leaving us vulnerable to more advanced enemy forces. Our future success is contingent on how we manage to leverage our economic advantage to swiftly boost our technological development and diversify our military strength.

Suggestions:

1. Our Strategy: We should focus on enhancing our technological capabilities alongside continuing to develop our army and expanding our economy. Be mindful of possible Zerg rush attacks.

2. Units and Buildings: Given our technological limitations, it's vital to optimally utilize our Zealots. In the meantime, construction of a Cybernetics Core is necessary to unlock more advanced units and technologies. Further, increasing the supply cap by building more pylons may be beneficial.

3. Economy: Efficient resource gathering is crucial. Our resource reserves should support both immediate army development and future technological upgrades. Consider expanding to new resource locations to facilitate this.

4. Technology: The immediate task is to build a Cybernetics Core to enable the research of higher technologies. Following that, based on the game progression and the enemy's strategy, decide on a focused technology path to gain a technological edge.

This revised strategy should help address the current limitations and better prepare us for upcoming challenges.

Decisions:
0: <BUILD CYBERNETICSCORE>
1: <BUILD PYLON>
2: <BUILD FORGE>
3: <RESEARCH WARPGATERESEARCH>
4: <CHRONOBOOST NEXUS>
"""
        elif self.race == 'zerg':
            self.example_input_prompt = r"""chunk0:At 04:08 game time, our current StarCraft II situation is as follows:\n\nResources:\n- game_time: 04:08\n- worker_supply: 23\n- mineral: 55\n- gas: 318\n- supply_left: 11\n- supply_cap: 44\n- supply_used: 33\n- army_supply: 4\n- base_count: 4\n\nBuildings:\n- base_count: 4\n- roach_warren_count: 1\n- gas_buildings_count: 6\n- overlord_count: 4\n- drone_count: 23\n- roach_count: 1\n- planning_base_count: 2\n- planning_drone_count: 3\n- planning_roach_count: 1\n\nUnits:\n- base_count: 4\n- roach_warren_count: 1\n- gas_buildings_count: 6\n- overlord_count: 4\n- drone_count: 23\n- roach_count: 1\n- planning_base_count: 2\n- planning_drone_count: 3\n- planning_roach_count: 1\n\nIn-process:\n- planning_base_count: 2\n- planning_drone_count: 3\n- planning_roach_count: 1\n\nEnemy Information:\n- No known enemy units\n\n", "At 04:08 game time, our current StarCraft II situation is as follows:\n\nResources:\n- game_time: 04:08\n- worker_supply: 23\n- mineral: 55\n- gas: 318\n- supply_left: 11\n- supply_cap: 44\n- supply_used: 33\n- army_supply: 4\n- base_count: 4\n\nBuildings:\n- base_count: 4\n- roach_warren_count: 1\n- gas_buildings_count: 6\n- overlord_count: 4\n- drone_count: 23\n- roach_count: 1\n- planning_base_count: 2\n- planning_drone_count: 3\n- planning_roach_count: 1\n\nUnits:\n- base_count: 4\n- roach_warren_count: 1\n- gas_buildings_count: 6\n- overlord_count: 4\n- drone_count: 23\n- roach_count: 1\n- planning_base_count: 2\n- planning_drone_count: 3\n- planning_roach_count: 1\n\nIn-process:\n- planning_base_count: 2\n- planning_drone_count: 3\n- planning_roach_count: 1\n\nEnemy Information:\n- No known enemy units\n\n, \nchunk{K_1}"""

            self.example_output_prompt = r"""
1. Game Overview: At 04:08 game time, our situation appears to be in an early mid-game stage. We have 23 drones, 55 minerals, and 318 gas. Our supply cap is at 44 with 11 supply left, and our army supply is 4. We have established four bases and have plans for two more.

2. Current Game Stage: Given the game time, drone count, and resource availability, we are transitioning from the early to mid-game stage.

3. Our Situation:
    3.1 Units and Buildings: We have four bases, a Roach Warren, and six gas buildings (presumably Extractors). Our army currently consists of one Roach. We are planning to expand with two more bases, three additional Drones, and another Roach.
    3.2 Economy: Our mineral reserves are quite low while gas is abundant. Our worker supply is at a decent number for this stage.
    3.3 Technology: The presence of a Roach Warren suggests that we have some technological development ongoing, but it's currently limited to Roach production.

4. Our Strategy: It seems we are following a balanced strategy, focusing on both economy expansion and some level of military readiness with Roach production. However, the low mineral count might hinder our planned expansions and military buildup.

5. Enemy's Strategy: There are no known enemy units at this time, making it challenging to infer the enemy's strategy.

6. Key Information: Our current situation emphasizes expansion and tech development with limited military power (Roaches). The low mineral count is a significant concern that might delay our planned expansions and army build-up. Efficient resource management and increasing mineral income are essential for our strategy to work.

Suggestions:

1. Our Strategy: Maintain the balanced strategy but place a high priority on increasing mineral income to sustain expansion and military development.
2. Units and Buildings: Continue drone production to enhance our resource collection rate, especially for minerals. Build up a more significant Roach army for defense and potential aggression.
3. Economy: Efficient mineral gathering should be the top priority. If necessary, pull some drones off gas to focus on mineral collection.
4. Technology: Considering the enemy's unknown status, it may be wise to start investing in versatile unit types and their corresponding technology, such as Hydralisks, to prepare for different enemy strategies.
5. Larvae: Monitor the number of available larvae. If it's too low, queue the INJECTLARVA ability to increase the larva production.


Decisions:
4: <TRAIN QUEUE>
0: <RESEARCH ZERGLINGMOVEMENTSPEED>
1: <TRAIN DRONE>
2: <TRAIN DRONE>
3: <QUEUE INJECTLARVA>
4: <TRAIN QUEUE>

            """
        elif self.race == 'terran':
            self.example_input_prompt = "todo"

            self.example_output_prompt = "todo"
        else:
            raise NotImplementedError
        return self.system_prompt, self.example_input_prompt, self.example_output_prompt



class StarCraftIIPrompt_realtime:
    """

    This prompt is prepared for the finetuned LLM(which trained by decisions output from gpt, so the output context is just the decision section).
    """
    def __init__(self, race, K, action_dict):
        self.race = race.lower()
        self.race_specific_prompt = {
            "protoss": "For Protoss, keep an eye on Nexus's energy to Chrono Boost important structures.",
            "zerg": "For Zerg, pay attention to whether there are enough larvae. If not, we should consider adding the INJECTLARVA command to the queue.",
        }
        self.system_prompt = f"""
        You are an AI trained in analyzing and summarizing StarCraft II games. You understand the nuances and strategies of the {self.race} race. 
        Based on the summaries of multiple rounds in a game, we want you to analyze the game progression in a structured way. Your analysis should include the following aspects:
        1. Game Overview: Provide a brief overview of the current situation based on all the rounds.
        2. Current Game Stage: Determine the stage of the game based on the information of all rounds. Is it the early game, mid-game, or late game?
        3. Our Situation: Describe our current status in terms of:
            3.1 Units and Buildings: Analyze the state of our units and buildings.
            3.2 Economy: Evaluate our economic condition, including resource collection and usage.
            3.3 Technology: Describe the status of our technological research and what technologies we have unlocked so far. Analyze our technology tree, indicating the available and potential upgrades or units.
888        4. Our Strategy: Infer our potential strategy based on our current situation and the information of all rounds.
        5. Enemy's Strategy: Infer the enemy's potential strategy, based on the available information.
        6. Key Information: Highlight the most important aspects from all rounds that have significantly influenced the game.

        {self.race_specific_prompt.get(self.race)}


        Lastly, make {K} actionable and specific decisions from the action dictionary{action_dict}. This dictionary comprises four categories of actions: unit production, building construction, technology research, and other actions. Remember to align these decisions with the current stage of the game, and avoid proposing actions that are not currently feasible.
        
        You only need to provide the final decisions, like this format:
        
        Decisions:
        0: <BUILD CYBERNETICSCORE>
        1: <BUILD PYLON>
        2: <BUILD FORGE>
        3: <RESEARCH WARPGATERESEARCH>
        4: <CHRONOBOOST NEXUS>
        5: <TRAIN PROBE>
        6: <TRAIN PROBE>
        7: <TRAIN STALKER>
        8: <TRAIN STALKER>
        9: <TRAIN VOIDRAY>

        """

    def generate_prompts(self):
        if self.race == 'protoss':
            self.example_input_prompt = r"chunk0:At 06:48 game time, our current StarCraft II situation is as follows:\n\nResources:\n- game_time: 06:48\n- worker_supply: 63\n- mineral: 2480\n- gas: 2972\n- supply_left: 12\n- supply_cap: 99\n- supply_used: 87\n- army_supply: 14\n- base_count: 5\n\nBuildings:\n- base_count: 5\n- pylon_count: 3\n- gas_buildings_count: 9\n- gateway_count: 4\n- Zealot_count: 7\n- planning_worker_count: 3\n\nUnits:\n- base_count: 5\n- pylon_count: 3\n- gas_buildings_count: 9\n- gateway_count: 4\n- Zealot_count: 7\n- planning_worker_count: 3\n\nIn-process:\n- planning_worker_count: 3\n\nEnemy Information:\n- enemy_UnitTypeId.ZERGLING: 1\n\n:At 06:49 game time, our current StarCraft II situation is as follows:...chunk{K_1}"

            self.example_output_prompt = """
Decisions:
0: <BUILD CYBERNETICSCORE>
1: <BUILD PYLON>
2: <BUILD FORGE>
3: <RESEARCH WARPGATERESEARCH>
4: <CHRONOBOOST NEXUS>
5: <TRAIN PROBE>
6: <TRAIN PROBE>
7: <TRAIN STALKER>
8: <TRAIN STALKER>
9: <TRAIN VOIDRAY>
"""
        elif self.race == 'zerg':
            self.example_input_prompt = r"""chunk0:At 04:08 game time, our current StarCraft II situation is as follows:\n\nResources:\n- game_time: 04:08\n- worker_supply: 23\n- mineral: 55\n- gas: 318\n- supply_left: 11\n- supply_cap: 44\n- supply_used: 33\n- army_supply: 4\n- base_count: 4\n\nBuildings:\n- base_count: 4\n- roach_warren_count: 1\n- gas_buildings_count: 6\n- overlord_count: 4\n- drone_count: 23\n- roach_count: 1\n- planning_base_count: 2\n- planning_drone_count: 3\n- planning_roach_count: 1\n\nUnits:\n- base_count: 4\n- roach_warren_count: 1\n- gas_buildings_count: 6\n- overlord_count: 4\n- drone_count: 23\n- roach_count: 1\n- planning_base_count: 2\n- planning_drone_count: 3\n- planning_roach_count: 1\n\nIn-process:\n- planning_base_count: 2\n- planning_drone_count: 3\n- planning_roach_count: 1\n\nEnemy Information:\n- No known enemy units\n\n", "At 04:08 game time, our current StarCraft II situation is as follows:\n\nResources:\n- game_time: 04:08\n- worker_supply: 23\n- mineral: 55\n- gas: 318\n- supply_left: 11\n- supply_cap: 44\n- supply_used: 33\n- army_supply: 4\n- base_count: 4\n\nBuildings:\n- base_count: 4\n- roach_warren_count: 1\n- gas_buildings_count: 6\n- overlord_count: 4\n- drone_count: 23\n- roach_count: 1\n- planning_base_count: 2\n- planning_drone_count: 3\n- planning_roach_count: 1\n\nUnits:\n- base_count: 4\n- roach_warren_count: 1\n- gas_buildings_count: 6\n- overlord_count: 4\n- drone_count: 23\n- roach_count: 1\n- planning_base_count: 2\n- planning_drone_count: 3\n- planning_roach_count: 1\n\nIn-process:\n- planning_base_count: 2\n- planning_drone_count: 3\n- planning_roach_count: 1\n\nEnemy Information:\n- No known enemy units\n\n, \nchunk{K_1}"""

            self.example_output_prompt = r"""
Decisions:
4: <TRAIN QUEUE>
0: <RESEARCH ZERGLINGMOVEMENTSPEED>
1: <TRAIN DRONE>
2: <TRAIN DRONE>
3: <QUEUE INJECTLARVA>
4: <TRAIN QUEUE>

            """
        elif self.race == 'terran':
            self.example_input_prompt = "todo"

            self.example_output_prompt = "todo"
        else:
            raise NotImplementedError
        return self.system_prompt, self.example_input_prompt, self.example_output_prompt
