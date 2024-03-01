class StarCraftIIPrompt_V2:
    def __init__(self, race, K, action_dict, game_style):
        self.race = race.lower()
        self.game_style = game_style.lower()
        self.race_specific_prompt = {
            "protoss": "For Protoss, the Chrono Boost ability available at the Nexus is crucial. It accelerates the production and research speed of a building. Important buildings that benefit from Chrono Boost include the Nexus itself (for probe production), the Gateway (for basic unit production), the Robotics Facility (for advanced unit production), and various tech buildings (for research upgrades). Keeping an optimal usage of Nexus's energy for Chrono Boost can significantly improve efficiency.",

            "zerg": "For Zerg, larvae are a unique resource used for the production of all Zerg units. Larvae spawn naturally from Hatcheries, Lairs, or Hives, but their production rate can be significantly increased with the Queen's Inject Larva ability. Managing larvae effectively and ensuring a consistent usage of the Inject Larva ability is essential for Zerg to maintain a steady production of units."
        }
        self.system_prompt = f"""
You are an AI expert in analyzing and strategizing for StarCraft II games, with specialized understanding of the nuances and strengths of the Protoss race. Given detailed game summaries from multiple rounds, you are expected to dissect the game's progression meticulously and provide insights, considering the unique aspects and abilities of the Protoss, in the following structured manner:
1. Game Overview:

Synthesize a concise overview of the game's current scenario, integrating how Protoss characteristics have influenced the game dynamics and outcomes so far.
2. Current Game Stage:

Classify the current phase of the game. Discuss how the typical Protoss strategies might be evolving at this stage, whether it's early, mid, or late-game scenarios.
3. Our Situation (As Protoss):

Detail our current standing, integrating Protoss-specific insights:
3.1 Units and Buildings: Examine the composition and status of our Protoss forces and structures, emphasizing the unique units (like Immortals, Colossi, or High Templars) and their current utilization.
3.2 Economy: Evaluate our resource management, considering Protoss's economic strategies, such as Chrono Boost utilization on Nexus to accelerate resource gathering or tech development.
3.3 Technology: Analyze our technological edge, focusing on Protoss-specific advancements, such as Warp Gate tech, Psionic abilities, or shield upgrades.
4. Our Strategy:

Infer the overarching strategy we are pursuing. How does it leverage the strengths of the Protoss race, such as strong defenses (e.g., Photon Cannons, Shield Batteries), powerful AOE attacks, or advanced teleportation abilities (e.g., Warp Prism harass, Mothership recalls)?
5. Enemy's Strategy:

Deduce possible strategies employed by our opponent(s), discussing how typical Protoss responses might counter these tactics.
6. Key Information:

Highlight any Protoss-specific game changers or pivotal moments from the rounds, such as successful Dark Templar harasses, effective Psionic Storms, or the deployment of the Golden Armada.
7. Strategic Suggestions:
Based on your analysis, provide Protoss-tailored strategic guidance on:
7.1 Our Strategy: Suggest adaptations in our Protoss gameplay to counter emerging threats or capitalize on weaknesses identified in the enemy camp. Consider aspects like expanding the Warp Gate network for rapid response, deploying Disruptors for their potent AOE, or leveraging Stargates for air superiority.
7.2 Units and Buildings: Recommend enhancements in our Protoss unit composition or infrastructure, such as incorporating more Archons against bio units or increasing the number of Robotics Facilities for continuous Colossi production.
7.3 Economy: Propose improvements in our Protoss economic setup, such as optimizing Chrono Boost allocations, expanding to resource-rich areas securely with shielded defenses, or establishing hidden expansions.
7.4 Technology: Direct towards Protoss-specific technological edges that could turn the tide, like pursuing advanced shield upgrades, unlocking the Mothership's abilities, or researching Storm for High Templars.

8. Decisions:
Action Dictionary:
{action_dict}
Given the current game dynamics, list 5 immediate, actionable decisions that align with Protoss capabilities and strengths. These directives should leverage Protoss-specific units, structures, technologies, and strategies. Remember to follow the 'action dictionary' in selecting actions. 
A placeholder is provided below to insert the appropriate actions from your action dictionary.

1.[Decision Title] (e.g., "Enhance Military Presence")
   - Reason: Here, you need to articulate why this decision is crucial to your current game strategy. This should be grounded in the game's present context, taking into account resources, opponents, and strategic advantages. (For instance, "Strengthening our military capabilities is essential for defense and preparing for upcoming offensives, necessitating the training of more combat-ready units.")
   - Action: Select a specific action from the 'action dictionary' that actualizes the goal outlined in the Reason. This should be a clear directive indicating what precise steps will be taken in the game. (e.g., "<TRAIN ZEALOT>" indicating that you're investing resources to train more Zealot units.)
...
5. [Decision Title] (e.g., "Enhance Military Presence")
"""
    def generate_prompts(self):
        if self.race == 'protoss':
            self.example_input_prompt = r"""
chunk0:Game Snapshot: 11:54
Economy: Minerals at 620, Gas at 331. Operating on 5 bases. Strong resource pool, consider allocating more for army diversification or aggressive expansion.
Supply: Maxed out (139/139). Immediate expansion needed for continued growth and to maintain military momentum.
Military: Army supply robust at 78, heavy on air and mechanical units. Main force includes Colossi (4), Voidrays (5), minimal ground troop presence. Expand unit roster for flexibility against potential counters.
Production: Intense focus on technology with 12 Robotics Facilities, 5 Stargates, but no active Forges indicating a lack of upgrades. Assess necessity for ground support and initiate upgrade sequences.
Upcoming Units: Plans indicate additional Colossus and Voidrays. Be cautious of reliance on limited unit types; potential vulnerability if enemy adapts.
Opponent: Zerg presence minimal with only basic structures identified. Possible concealment of advanced forces or expansions; increased scouting imperative.
Quick Focus: Address supply limit, broaden military spectrum, enhance reconnaissance particularly in uncharted Zerg territory to pre-empt possible hidden threats.
Recommended Actions: Initiate aggressive scouting, manage supply constraints, diversify unit composition, and consider defensive and offensive upgrades.
......
chunk{K_1}:...
            """
            self.example_output_prompt = """
1.Game Overview:
    The game is in a critical phase where economic advantages and a sturdy defense have been established. However, the Protoss characteristics of adaptability and advanced technology seem underutilized. The current gameplay is heavily reliant on standard units and structures, with less emphasis on the unique aspects of Protoss that can shift battle tides, such as psionic abilities or advanced teleportation.

2.Current Game Stage:
    We are in what appears to be the mid-game, where conflicts become more frequent and decisive. Typical Protoss strategies at this stage might involve preparing for aggressive expansion or fortifying current positions with advanced units like Colossi and potentially introducing Psionic units like High Templars for their game-changing abilities.

3.Our Situation (As Protoss):

    3.1 Units and Buildings: The unit composition is robust but conventional, with a reliance on Colossi for ground control and Voidrays for air dominance. There seems to be a lack of use of specialized Protoss units, such as High Templars, which could introduce powerful Psionic abilities into the fray. The building infrastructure is geared towards tech advancement, but without the support of Forges, the potential for unit upgrades remains untapped.

    3.2 Economy: The resource management indicates a conservative strategy, with significant resources being stockpiled and not reinvested into the game. There's no evidence of Chrono Boost being applied effectively to expedite resource gathering or tech development, which is a missed strategic advantage specific to Protoss gameplay.

    3.3 Technology: While there's an emphasis on tech structures, indicating a potential focus on advanced units, the absence of key Protoss advancements is notable. The benefits of Warp Gate technology for rapid deployment, Psionic abilities for battlefield control, and shield upgrades for enhanced unit durability seem overlooked.

4.Our Strategy:
    The overarching strategy is defensive and preparatory, with indications of gearing up for significant tech-based aggression. However, this approach is not fully exploiting Protoss strengths, particularly the race's capacity for powerful defenses like Photon Cannons and Shield Batteries, AOE attacks through units like High Templars, and mobility advantages via Warp Prisms.

5.Enemy's Strategy:
    The opponent, likely employing Zerg's typical guerrilla warfare style, could be planning to overwhelm with numbers or using high-tier units that have been evolved. Protoss counter-strategies should include leveraging high-ground advantages, employing Psionic abilities for crowd control, and potentially utilizing Dark Templars for harassment and ambushes.

6.Key Information:
    The critical juncture was the continuous supply cap from 11:54 to 11:55, restricting the Protoss player's ability to expand their forces or respond to immediate threats. This constraint significantly limits the player's options and mobility on the battlefield.

7.Strategic Suggestions:

    7.1 Our Strategy: Adapt by incorporating more harassment into gameplay, utilizing Warp Prisms for their advanced teleportation abilities for sneak attacks. Expand the Warp Gate network to ensure rapid troop deployment across the map, offering both offensive and defensive flexibility.

    7.2 Units and Buildings: Enhance the army's composition by introducing more Psionic units like High Templars or Archons. These units' abilities can decisively turn battles, especially against biological swarms typical of Zerg opponents. Additionally, increase Robotics Facilities to ensure continuous production of key units like Colossi and Immortals.

    7.3 Economy: Optimize resource allocation by employing Chrono Boost more effectively on Nexus points, ensuring quicker resource accumulation or faster tech development. Also, consider expanding to new, resource-rich areas while fortifying with typical Protoss defenses.

    7.4 Technology: Prioritize obtaining Protoss-specific tech advantages like advanced shield upgrades and Psionic Storm for High Templars. These tech enhancements could offer a significant edge in upcoming conflicts.

8.Immediate, Actionable Decisions:

    1. [Economic Augmentation]
    Reason: A thriving economy forms the backbone of every strategic move in the game, especially for resource-intensive Protoss strategies. Probes are indispensable in ensuring a steady flow of resources, as they're responsible for harvesting minerals and gas, fundamental for all kinds of unit production, technology research, and building construction.
    Action: <TRAIN PROBE>
    
    2. [Enhance Military Presence]
    Reason: Strengthening military capabilities is essential, considering the current game's demands. Training more combat-ready units, particularly those with specialized abilities like High Templars, can introduce a level of battlefield control that the current army composition lacks.
    Action: <TRAIN HIGHTEMPLAR>

    3. [Boosting Economy]
    Reason: With the game's dynamics at this minute, it's evident that a robust economy is not just an advantage but a necessity. Accelerating resource gathering will fund continuous military production and advanced research, providing the sustenance for Protoss's tech-heavy strategies.
    Action: <CHRONOBOOST NEXUS>

    4. [Airpower Capability Enhancement]
    Reason: Dominance in the skies can often dictate the flow of the battle in StarCraft II. Building a Stargate allows for the production of powerful Protoss air units, offering a strategic advantage by enabling a varied assault strategy and the ability to respond swiftly to enemy air threats.
    Action: <BUILD STARGATE>
    
    5. [Fortify and Expand]
    Reason: Sustainable growth is a key strategy at this point. It's not enough to hold existing territories; secure expansions are essential for resource advantage. Establishing new bases ensures economic stability, while fortifications protect these investments, creating a multifaceted defense strategy.
    Action: <BUILD NEXUS>
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
