class StarCraftIIPrompt:
    def __init__(self, race, K, action_dict,game_style):
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
        4. Our Strategy: Infer our potential strategy based on our current situation and the information of all rounds.
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