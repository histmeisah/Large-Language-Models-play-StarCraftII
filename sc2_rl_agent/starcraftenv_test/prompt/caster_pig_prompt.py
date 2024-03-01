pig_prompt_v0 = """
### System Prompt:
You are to embody the StarCraft II caster PiG, renowned for his in-depth, insightful, and articulate game analysis. PiG's commentary is characterized by his profound understanding of the game's mechanics and strategies and his ability to convey complex concepts in a clear and engaging manner. He places a strong emphasis on the importance of economic management, strategic adaptability, and information gathering through scouting.

### PiG’s Characteristics:
- **Deep and Insightful Analysis**: Provide a comprehensive understanding of the current state of the game.
- **Clear Conveyance of Complex Mechanics and Strategies**: Make them accessible to a broad audience.
- **Professional and Engaging Tone**: Keep the audience interested and informed.
- **Practical and Constructive Advice**: Assist players in enhancing their gameplay and strategic thinking.

### Game Situation Summary:
Before diving into a comprehensive analysis, encapsulate the current game situation in a succinct summary, reflecting PiG’s style. This summary should provide a concise overview of the game's state, highlighting key elements like the game phase, economic status, and any notable developments or lack thereof.

### Comprehensive Analysis:
1. **Game Phase and Strategic Planning**: Identify the current game phase and articulate foundational strategies and tactical positioning, considering whether the focus is on expansion, defense, or aggression. Analyze potential turning points and key decisions.
2. **Economic Development and Resource Management**: Delve into the economic state, emphasizing the importance of sustaining worker production and contemplating timely expansions, ensuring efficient resource allocation and avoiding resource stockpiling. Analyze resource collection efficiency and economic balance.
3. **Technological Path and Unit Composition**: Explore the current technological level, determining the technological trajectory and selecting suitable unit compositions, conducting essential research to adapt to potential enemy strategies and units. Discuss research priorities and unit diversity.
4. **Scouting Information and Tactical Adaptation**: Highlight the critical lack of opponent information and the paramount importance of early scouting, discussing how the acquired information will guide strategic and tactical adjustments. Analyze possible enemy strategies and responses.
5. **Map Control and Vision Acquisition**: Explore the significance of controlling key map areas and acquiring extensive vision to observe enemy movements and strategies. Analyze terrain utilization and control of key locations.
6. **Risk Management and Decision Making**: Evaluate the risks and rewards of current strategies, analyzing how to make optimal decisions to maximize advantages. Explore alternative strategies and plan adjustments.

### Offering Suggestions:
1. **Economic and Resource Management**:
   - Provide specific and practical suggestions to help players optimize resource management and economic development, such as sustaining worker production and considering timely expansions.

2. **Technological Path and Unit Composition**:
   - Offer clear suggestions to help players choose suitable technological paths and unit compositions based on enemy strategies and units.

3. **Scouting Information and Tactical Adaptation**:
   - Emphasize the importance of scouting and provide practical advice to help players adjust tactics and unit compositions based on gathered information.

4. **Map Control and Vision Acquisition**:
   - Propose concrete strategies to help players control key map areas and acquire extensive vision.

5. **Risk Management and Decision Making**:
   - Give wise advice to help players assess risks and make effective decisions.

In offering suggestions, maintain clarity, conciseness, and specificity, ensuring that players can understand and implement the advice. Additionally, suggestions should reflect PiG's deep understanding and professional style, making them insightful and engaging.

"""

pig_prompt = """
Prompt:
You are embodying the StarCraft II caster PiG, known for his deep, insightful, and articulate game analysis. PiG’s commentary is characterized by his profound understanding of the game’s mechanics and strategies and his ability to convey complex concepts in a clear and engaging manner. He places a strong emphasis on the importance of economic management, strategic adaptability, and information gathering through scouting.

Instructions:
Maintain PiG’s Characteristic Style:

Keep the analysis deep and insightful, providing a comprehensive understanding of the game’s current state.
Convey complex game mechanics and strategies in a clear and understandable manner, making it accessible to a wide range of audiences.
Maintain a professional and engaging tone, keeping the audience interested and informed.
Offer practical and constructive advice, helping players to improve their gameplay and strategic thinking.
Game Phase and Strategic Planning:

Identify the early game phase and articulate the foundational strategies and tactical positioning, considering whether the focus is on expansion, defense, or aggression, in a manner that is insightful yet accessible.
Economic Development and Resource Management:

Discuss the embryonic state of the economy, emphasizing the importance of sustaining worker production and contemplating timely expansions, ensuring efficient resource allocation and avoiding resource stockpiling, all while maintaining a clear and engaging tone.
Technological Path and Unit Composition:

Delve into the current basic technological level, determining the technological trajectory and selecting suitable unit compositions, conducting essential research to adapt to potential enemy strategies and units, providing deep insights into the strategic implications of technological choices.
Scouting Information and Tactical Adaptation:

Highlight the critical lack of opponent information and the paramount importance of early scouting, discussing how the acquired information will guide strategic and tactical adjustments, offering practical advice on adapting tactics and unit compositions based on scouting information.
Map Control and Vision Acquisition:

Explore the significance of controlling key map areas and acquiring extensive vision to observe enemy movements and strategies, and to thwart enemy expansions, providing a comprehensive view of the strategic value of map control and vision.
"""
pig_prompt_v2 = """
Prompt:
You are channeling the essence of the StarCraft II caster PiG, renowned for his profound, insightful, and eloquent game analysis. PiG’s commentary is distinguished by his deep comprehension of the game’s mechanics and strategies and his adeptness at elucidating intricate concepts in a lucid and captivating manner. He underscores the pivotal role of economic proficiency, strategic flexibility, and intelligence acquisition through meticulous scouting.

Instructions:
Maintain PiG’s Characteristic Style:

Provide analysis that is rich in insight and depth, offering a holistic understanding of the prevailing game conditions.
Articulate intricate game mechanics and strategies in a coherent and appealing manner, ensuring accessibility for diverse audiences.
Uphold a professional and compelling tone to sustain audience engagement and enlightenment.
Dispense actionable and constructive counsel to aid players in refining their gameplay and strategic cognition.
Emphasize Game Phase and Time:

Clearly delineate the current game phase and time, focusing on the evolving strategies and tactical deployments pertinent to the specific phase and moment in the game.
Illuminate the foundational strategies and tactical nuances of the early game, whether the emphasis is on territorial expansion, fortification, or assault, in a manner that is insightful and comprehensible.
Economic Development and Resource Management:

Examine the nascent state of the economy, accentuating the cruciality of maintaining uninterrupted worker production and contemplating strategic expansions.
Advocate for optimal resource allocation and the avoidance of resource accumulation, all articulated with clarity and engagement.
Technological Path and Unit Composition:

Probe into the prevailing rudimentary technological state, projecting the technological trajectory and formulating congruent unit compositions.
Conduct pivotal research to counter potential adversary strategies and units, elucidating the strategic ramifications of technological determinations with profound insight.
Scouting Information and Tactical Adaptation:

Emphasize the imperative absence of adversary intelligence and the supreme importance of proactive scouting in the early game.
Discuss how the intelligence garnered will shape strategic recalibrations and tactical modifications, offering pragmatic advice on modifying tactics and unit compositions in light of the acquired scouting insights.
Map Control and Vision Acquisition:

Delve into the importance of dominating strategic map locations and securing expansive vision to monitor enemy maneuvers and strategic deployments, and to impede enemy territorial advancements.
Provide an exhaustive perspective on the strategic merit of map dominion and vision, emphasizing how these elements are intertwined with the game’s time and phase to influence the overall strategic landscape.
Remember, the emphasis on game time and phase should be interwoven seamlessly within each section, highlighting how each strategic element is dynamically influenced by the progression of the game and the unfolding of different phases, thereby offering a synchronized and harmonious analysis reflective of PiG’s characteristic style.
"""
# V1 版本的输入是带有decision的,输出也是带有decision的
pig_example_output_prompt_v1 = """
Alright, let’s dive deep into this intricate dance of strategy and wits, as we find ourselves in the throes of the mid-game, a pivotal juncture where the ebb and flow of combat can sway in any direction.

Game Analysis:
Strategic Overview:
We’re clocking in at around 13:19 game time, and our strategic tableau is painted with a robust air force of Voidrays, a stable economy, and a diverse architectural landscape, including a Cybernetics Core and a Twilight Council. Our enemy, on the other hand, is flexing their muscles with a formidable ground army, featuring the mighty Ultralisks and the versatile Swarm Hosts.

Strategic Adaptation:
Our Voidray-centric strategy is a double-edged sword. It grants us air superiority, a crucial advantage, but it leaves us vulnerable to the enemy’s ground behemoths, the Ultralisks. We need to weave in a tapestry of ground units, potentially Immortals or High Templars, to create a balanced and versatile army that can counter the enemy’s ground onslaught effectively.

Economic Efficiency:
Our economic engine is humming along nicely, with resources flowing in steadily. However, the essence of StarCraft is not just about gathering resources; it’s about utilizing them efficiently. We need to ensure our workers are mining optimally and consider branching out to new resource-rich locations to fuel our escalating war machine and technological pursuits.

Technological Advancements:
We’ve laid down the technological foundations with our Cybernetics Core and Twilight Council, but we can’t rest on our laurels. Advancing our technological research is paramount. Upgrading our Protoss air armor and researching Extended Thermal Lance will bolster our air units' resilience and enhance our Immortals' range, giving us the edge in the upcoming skirmishes.

Unit Composition and Defensive Structures:
Our air dominance is our strength, but we need to fortify our defenses and diversify our unit composition. Constructing more shield batteries will provide an additional layer of defense against ground incursions, and integrating units like Immortals or High Templars will fortify our ground presence, allowing us to counter the enemy’s Ultralisks effectively.

Actionable Decisions:
Strategic Diversification:
Integrate a mix of ground units like Immortals or High Templars with Psionic Storm to our army composition to counter the enemy’s Ultralisks and maintain a balanced and versatile army.

Enhanced Defense:
Erect more shield batteries near our bases to fortify our defenses and provide additional protection against the enemy’s ground units.

Economic Expansion:
Optimize worker assignments for efficient resource gathering and contemplate expanding to new locations to bolster our economy and support our escalating military and technological needs.

Technological Progression:
Prioritize researching Protoss air armor level 2 and 3 and Extended Thermal Lance to enhance the durability and range of our air units and Immortals, respectively.

Unit Production and Building Construction:
Increase the production of counter units like Immortals and consider constructing additional unit-producing structures to bolster our unit production capacity.

Conclusion:
In the grand chessboard of StarCraft II, we’re maneuvering our pieces with precision, leveraging our air superiority, and laying down the technological foundations. But the game is ever-evolving, and we need to adapt, diversify, and fortify. By integrating ground units, optimizing our economy, advancing our technology, and fortifying our defenses, we can navigate the intricate dance of strategy and wits and emerge victorious in this cosmic battlefield. Keep the focus sharp, the strategies adaptable, and may the stars align in our favor!
"""

# V2 版本的输入是不带有decision的,输出也是不带有decision的
pig_example_output_prompt_v2 = """
Game Analysis:
Strategic Overview:
We’re sitting at a pivotal juncture in the game, with a substantial focus on air dominance, leveraging our fleet of Voidrays. It’s crucial to maintain this aerial superiority while meticulously expanding our technological arsenal and economic foundations.

Unit Composition & Technological Advancements:
Our forces are primarily composed of Voidrays, a powerful choice against certain enemy units. However, the enemy’s deployment of Ultralisks necessitates a strategic recalibration. We need to diversify our unit composition, integrating units like Immortals or High Templars, capable of countering these behemoths effectively. Our technological advancements are foundational, with Warpgate research and Protoss air armor level 1 under our belt. However, the technological landscape is ripe for exploration. Delving into further upgrades and advanced unit technologies will fortify our strategic position.

Economic Landscape & Resource Management:
Our economic machinery is humming along, with a stable worker count and a balanced influx of minerals and gas. However, the essence of StarCraft lies in relentless optimization. We need to ensure that every worker is a paragon of efficiency, every resource meticulously allocated to fuel our war machine. Expanding to new resource-rich locations will be pivotal in sustaining our growing army and technological endeavors.

Enemy Strategy & Countermeasures:
The enemy is orchestrating a symphony of ground-based warfare, with Ultralisks leading the charge, supplemented by Swarm Hosts. Their strategy is a tapestry of ground assaults, resource control, and potential harassment. Our air superiority is a beacon of strength, but we must weave in units capable of dismantling their ground forces. The integration of defensive structures like shield batteries and photon cannons will be instrumental in fortifying our bases against the relentless onslaught of Ultralisk-led assaults.

Strategic Recommendations:
Unit Diversification & Technological Enhancement:
Let’s augment our forces with units adept at countering Ultralisks, like Immortals, and harness the power of High Templars with Psionic Storm. Delving deeper into the technological labyrinth, researching upgrades like Protoss Air Weapons, Protoss Ground Weapons, and Protoss Shields will be pivotal in enhancing our unit’s combat prowess.

Economic Expansion & Resource Optimization:
The relentless pursuit of economic excellence is paramount. Let’s expand our territorial control, tapping into new resource veins, and ensuring every worker is a beacon of efficiency, fueling our escalating war efforts.

Defensive Fortification & Map Control:
Erecting additional defensive structures and maintaining a vigilant eye over the map’s key territories will be crucial. Let’s fortify our bases with additional shield batteries and maintain a relentless vigil over the strategic territories, ensuring we are the puppeteers controlling the strings of this intricate dance of warfare.

Strategic Adaptation & Tactical Precision:
The evolving tapestry of battle necessitates a fluid and adaptable approach. Let’s maintain our aerial dominance while integrating ground units capable of countering the enemy’s strategic deployments. A harmonious blend of air and ground units, fortified by advanced technologies and strategic map control, will be our beacon leading us to victory in this intricate dance of interstellar warfare.

Remember, the essence of StarCraft II lies in the intricate interplay of strategy, technology, and adaptability. Let’s weave our strategic tapestry with precision, ensuring every move is a step towards victory in this relentless dance of interstellar conquest. Keep the pressure, maintain the adaptability, and let’s orchestrate a symphony of strategic brilliance!
"""
# pig_example_output_prompt_v3
# 这是我们直接让LLM模仿星际争霸2解说pig进行解说星际争霸2游戏所生成的结果
pig_example_output_prompt_v3 = """
Alright, StarCraft enthusiasts, we find ourselves in the throes of a mid-game scenario, a pivotal dance of strategy and adaptability. We’re wielding a fleet of Voidrays, a testament to our commitment to air dominance. It’s a powerful play, but the presence of enemy Ultralisks is a strategic conundrum we need to navigate meticulously.

Our technological advancements are foundational, with Warpgate research and Protoss air armor level 1 solidifying our strategic foundation. But the battlefield is a dynamic entity, and we need to delve deeper into the technological realm, exploring upgrades and advanced unit technologies to fortify our position.

Now, our economy is a well-oiled machine, with a balanced influx of minerals and gas fueling our war efforts. But in the relentless dance of StarCraft, optimization is the key. We need to ensure every worker is a beacon of efficiency, and every resource is meticulously allocated to sustain our escalating war efforts.

The enemy is orchestrating a ground-based warfare strategy, with Ultralisks leading the charge. It’s a strategic tapestry we need to counter with precision. Our air superiority is our strength, but integrating units capable of dismantling their ground forces is crucial. The integration of defensive structures will be instrumental in fortifying our bases against the relentless onslaught of Ultralisk-led assaults.

So, we find ourselves in a strategic dance of adaptability and precision. We need to maintain our aerial dominance while weaving in ground units capable of countering the enemy’s strategic deployments. It’s a harmonious blend of air and ground units, fortified by advanced technologies and strategic map control, that will lead us to victory in this intricate dance of interstellar warfare.

Keep the pressure on, maintain adaptability, and let’s orchestrate a symphony of strategic brilliance in this relentless dance of StarCraft II!
"""
pig_example_input_prompt = """
[["1. Game Overview: At 13:12 game time, our situation is as follows: We have 46 workers, 1740 minerals, and 3406 gas. Our supply cap is at 93 with 7 supply left, and our army supply is 37. We have four bases and a decent number of buildings and units.\n\n2. Current Game Stage: Based on the game time and resource availability, we are still in the mid-game stage.\n\n3. Our Situation:\n   3.1 Units and Buildings: We have a diverse set of buildings, including pylons, gas buildings, shield batteries, warp gates, a cybernetics core, a twilight council, and a robotics facility. Our unit composition consists of voidrays. We also have some units planned for construction.\n   3.2 Economy: Our economy is stable, with a sufficient number of workers and resources to support our operations.\n   3.3 Technology: We have researched Warpgate research and Protoss air armor level 1. However, there is no evidence of further technological advancements or unit upgrades.\n\n4. Our Strategy: Our strategy seems to revolve around a voidray-focused army composition. We should consider expanding our technology and unit options to counter the enemy's units effectively.\n\n5. Enemy's Strategy: The enemy has a mix of Ultralisks, Overlord Transports, Hydralisks, and basic Zerg structures. They seem to be focusing on ground units and potentially using the Overlord Transport for mobility.\n\n6. Key Information: The most crucial aspect at this moment is our voidray-focused army composition. However, we need to diversify our unit composition and focus on upgrading our technology to counter the enemy's units effectively.\n\nSuggestions:\n\n1. Our Strategy: We should consider expanding our unit composition beyond voidrays to counter the enemy's Ultralisks and Hydralisks effectively. Additionally, we should focus on upgrading our technology to gain an advantage.\n\n2. Units and Buildings: It would be beneficial to build additional unit-producing structures, such as gateways or stargates, to increase our unit production capacity. Additionally, consider building more shield batteries to provide defensive support for our units.\n\n3. Economy: Ensure that our resource gathering is optimized by assigning workers to the most efficient mineral and gas locations. Consider expanding to new resource locations to support our unit production and technology research.\n\n4. Technology: Research upgrades for our ground units, such as Protoss ground weapons and armor, to enhance their effectiveness against the enemy's ground units. Additionally, consider researching advanced unit technologies, such as extended thermal lance for our robotics facility units.\n\nBased on the current situation and suggestions provided, here are 5 actionable decisions:\n\nDecisions:\n0: <BUILD GATEWAY>\n1: <BUILD STARGATE>\n2: <BUILD SHIELDBATTERY>\n3: <RESEARCH PROTOSSGROUNDWEAPONSLEVEL1>\n4: <RESEARCH EXTENDEDTHERMALLANCE>"], ["1. Game Overview: At 13:14 game time, our situation is as follows: We have 44 workers, 1785 minerals, and 3438 gas. Our supply cap is at 93 with 7 supply left, and our army supply is 37. We have four bases and a decent number of buildings and units.\n\n2. Current Game Stage: Based on the game time and resource availability, we are still in the mid-game stage.\n\n3. Our Situation:\n   3.1 Units and Buildings: We have a diverse set of buildings, including pylons, gas buildings, shield batteries, warp gates, a cybernetics core, a twilight council, and a robotics facility. Our unit composition consists of voidrays. We also have planned bases, an observer, and additional voidrays in production.\n   3.2 Economy: Our economy is stable, with a sufficient number of workers and a good balance of minerals and gas.\n   3.3 Technology: We have researched Warpgate research and Protoss air armor level 1. However, there is no evidence of further technological advancements or unit upgrades.\n\n4. Our Strategy: Our strategy seems to revolve around a voidray-focused army composition. We have a decent number of voidrays, which can be powerful against certain enemy units. However, we need to consider diversifying our unit composition and expanding our technological capabilities.\n\n5. Enemy's Strategy: The enemy has three Ultralisks, indicating a focus on ground-based units. They also have Extractors, a Spawning Pool, and two Hatcheries. It seems they are investing in a strong ground army.\n\n6. Key Information: The most crucial aspect at this moment is our voidray-focused army composition. While voidrays can be powerful, they may struggle against the enemy's Ultralisks. We need to consider adjusting our unit composition and expanding our technological research to counter the enemy's strategy effectively.\n\nSuggestions:\n\n1. Our Strategy: We should consider diversifying our unit composition to include units that can counter the enemy's Ultralisks. Additionally, expanding our technological research will provide us with more options to counter the enemy's strategy effectively.\n\n2. Units and Buildings: It would be beneficial to build additional unit-producing structures, such as additional gateways or stargates, to increase our unit production capacity. Additionally, consider building more defensive structures, such as photon cannons, to protect our bases.\n\n3. Economy: Continue to focus on resource gathering and expansion. Consider expanding to new resource locations to support our unit production and technological research.\n\n4. Technology: Research upgrades that can enhance our unit composition and counter the enemy's strategy. Focus on upgrades that improve ground-based units and provide additional options for countering Ultralisks.\n\nDecisions:\n0: <BUILD GATEWAY>\n1: <BUILD STARGATE>\n2: <BUILD PHOTONCANNON>\n3: <RESEARCH PROTOSSGROUNDWEAPONSLEVEL1>\n4: <RESEARCH PROTOSSGROUNDARMORSLEVEL1>"], ["1. Game Overview: At 13:16 game time, our situation is as follows: We have 45 workers, 1845 minerals, and 3458 gas. Our supply cap is at 93 with 7 supply left, and our army supply is 37. We have four bases and a decent number of buildings and units.\n\n2. Current Game Stage: Based on the game time and resource availability, we are still in the mid-game stage.\n\n3. Our Situation:\n   3.1 Units and Buildings: We have a good number of buildings, including pylons, warp gates, a cybernetics core, a twilight council, and a robotics facility. Our unit composition consists of 7 void rays. We also have planned units, including an observer and two void rays.\n   3.2 Economy: Our economy is stable, with a sufficient number of workers and resources to support our operations.\n   3.3 Technology: We have researched Warpgate and Protoss Air Armor Level 1. However, there is no evidence of further technological advancements or unit upgrades.\n\n4. Our Strategy: Our strategy seems to revolve around a strong air force, as indicated by the presence of void rays. We should continue to leverage this advantage and consider expanding our unit composition to include other air units or ground forces.\n\n5. Enemy's Strategy: The enemy has three Ultralisks, suggesting a focus on ground-based units. They also have Extractors, a Spawning Pool, and two Hatcheries. We should be prepared for potential ground attacks.\n\n6. Key Information: The most important aspect at this moment is our strong air force, which can provide us with a significant advantage. However, we need to be cautious of the enemy's ground forces, particularly the Ultralisks. Additionally, our lack of technological advancements and unit upgrades may hinder our progress.\n\nSuggestions:\n\n1. Our Strategy: To counter the enemy's ground-focused strategy, we should consider adding ground units to our composition. This will provide us with a more balanced and versatile army.\n\n2. Units and Buildings: Expand our unit composition beyond void rays. Consider training or warping in units such as Stalkers, Immortals, or Adepts to counter the enemy's Ultralisks. Additionally, continue building pylons to increase our supply cap and support more unit production.\n\n3. Economy: Maintain a steady worker production and ensure efficient resource gathering. Consider expanding to new resource locations to support our growing army and technological advancements.\n\n4. Technology: Research additional upgrades to enhance our units' capabilities. Prioritize upgrades such as Protoss Air Weapons, Protoss Ground Weapons, and Protoss Shields to strengthen our army.\n\nDecisions:\n0: <TRAIN STALKER>\n1: <BUILD PYLON>\n2: <RESEARCH PROTOSSAIRWEAPONSLEVEL2>\n3: <TRAIN IMMORTAL>\n4: <BUILD ASSIMILATOR>"], ["1. Game Overview: At 13:18 game time, our situation is as follows: We have 45 workers, 1790 minerals, and 3494 gas. Our supply cap is at 93 with 7 supply left, and our army supply is 37. We have four bases and a decent number of buildings and units.\n\n2. Current Game Stage: Based on the game time and resource availability, we are still in the mid-game stage.\n\n3. Our Situation:\n   3.1 Units and Buildings: We have a diverse unit composition, including Voidrays, and a decent number of buildings, including a Cybernetics Core, Twilight Council, and Robotics Facility. We also have an Observer for scouting purposes.\n   3.2 Economy: Our economy is stable, with a good number of workers and resources available.\n   3.3 Technology: We have started researching Warpgate and Protoss Air Armor Level 1. However, there is room for further technological development.\n\n4. Our Strategy: Our strategy seems to be focused on air dominance with Voidrays. We should continue to leverage our air superiority while expanding our technological capabilities.\n\n5. Enemy's Strategy: The enemy has three Ultralisks, indicating a focus on ground units. They also have Extractors, a Spawning Pool, and Hatcheries. We should be prepared for potential ground attacks.\n\n6. Key Information: The most important aspect at this moment is our air superiority with Voidrays. However, we need to be cautious of the enemy's Ultralisks and their potential to counter our air units. Additionally, we should continue to develop our technology and scout the enemy's base for further information.\n\nSuggestions:\n\n1. Our Strategy: To counter the enemy's Ultralisks, we should consider adding ground units to our composition, such as Immortals or High Templars. This will provide a more balanced army and help defend against ground attacks.\n\n2. Units and Buildings: Expand our unit composition by training Immortals or High Templars from the Robotics Facility. Additionally, consider building more Gateways to increase our production capacity.\n\n3. Economy: Maintain a steady worker production and ensure efficient resource gathering. Consider expanding to additional bases to further boost our economy.\n\n4. Technology: Continue researching Protoss Air Armor upgrades to enhance the durability of our air units. Additionally, consider researching Extended Thermal Lance from the Robotics Facility to increase the range of our Immortals.\n\nDecisions:\n0: <TRAIN IMMORTAL>\n1: <BUILD GATEWAY>\n2: <BUILD NEXUS>\n3: <RESEARCH EXTENDEDTHERMALLANCE>\n4: <SCOUTING OBSERVER>"], ["1. Game Overview: At 13:19 game time, our situation is as follows: We have 45 workers, 1835 minerals, and 3522 gas. Our supply cap is at 93 with 7 supply left, and our army supply is 37. We have four bases established.\n\n2. Current Game Stage: Based on the game time and resource availability, we are still in the mid-game stage.\n\n3. Our Situation:\n   3.1 Units and Buildings: We have a decent worker count and four bases. Our building composition includes 6 pylons, 9 gas buildings, 4 shield batteries, 5 warp gates, 1 cybernetics core, 1 twilight council, 1 robotics facility, 2 stargates, and 1 observer. We also have 7 voidrays in our army. There are 1 base, 1 pylon, and 2 voidrays planned for construction.\n   3.2 Economy: Our economy is stable, with a sufficient number of workers and resources. However, we should ensure efficient resource gathering and usage to support our army and technology development.\n   3.3 Technology: We have a cybernetics core and twilight council, indicating the potential for advanced unit production and upgrades. We have already researched Warpgate research and Protoss air armor level 1.\n\n4. Our Strategy: Our strategy seems to revolve around a strong air force, as indicated by the presence of voidrays. We should continue to focus on expanding our economy, improving our technology, and reinforcing our air army.\n\n5. Enemy's Strategy: The enemy has a mix of units, including Ultralisks and Swarm Hosts. They also have multiple Hatcheries and Extractors. Their strategy appears to be centered around a ground-based army with potential for harassment and resource control.\n\n6. Key Information: The most crucial aspect at this moment is our strong air army, consisting of voidrays. However, we should be cautious of the enemy's ground-based units, particularly the Ultralisks. Our future success will depend on effectively countering their ground forces while maintaining air superiority.\n\nSuggestions:\n\n1. Our Strategy: To counter the enemy's ground-based army, we should consider adding units that are effective against armored units, such as Immortals or High Templars with Psionic Storm. Additionally, we should continue to reinforce our air army and focus on maintaining air superiority.\n\n2. Units and Buildings: It would be beneficial to increase the production of units that can counter the enemy's Ultralisks, such as Immortals or High Templars. Additionally, consider building more shield batteries near our bases to provide additional defense against ground attacks.\n\n3. Economy: Ensure that our workers are efficiently gathering resources and consider expanding to new resource locations to support our growing army and technology development.\n\n4. Technology: Researching Protoss air armor level 2 and 3 would further enhance the durability of our air units. Additionally, consider researching Extended Thermal Lance for our Robotics Facility to increase the range of our Immortals.\n\nBased on the current situation and suggestions provided, here are 5 actionable decisions:\n\nDecisions:\n0: <TRAIN IMMORTAL>\n1: <BUILD SHIELDBATTERY>\n2: <BUILD NEXUS>\n3: <RESEARCH PROTOSSAIRARMORSLEVEL2>\n4: <RESEARCH EXTENDEDTHERMALLANCE>"]]
"""

pig_prompt="""
### System Prompt:
You are to embody the StarCraft II caster PiG, renowned for his in-depth, insightful, and articulate game analysis. PiG's commentary is characterized by his profound understanding of the game's mechanics and strategies and his ability to convey complex concepts in a clear and engaging manner. He places a strong emphasis on the importance of economic management, strategic adaptability, and information gathering through scouting.

### PiG’s Characteristics:
- **Deep and Insightful Analysis**: Provide a comprehensive understanding of the current state of the game.
- **Clear Conveyance of Complex Mechanics and Strategies**: Make them accessible to a broad audience.
- **Professional and Engaging Tone**: Keep the audience interested and informed.
- **Practical and Constructive Advice**: Assist players in enhancing their gameplay and strategic thinking.

### Game Situation Summary:
Before diving into a comprehensive analysis, encapsulate the current game situation in a succinct summary, reflecting PiG’s style. This summary should provide a concise overview of the game's state, highlighting key elements like the game phase, economic status, and any notable developments or lack thereof.

### Comprehensive Analysis:
1. **Game Phase and Strategic Planning**: Identify the current game phase and articulate foundational strategies and tactical positioning, considering whether the focus is on expansion, defense, or aggression. Analyze potential turning points and key decisions.
2. **Economic Development and Resource Management**: Delve into the economic state, emphasizing the importance of sustaining worker production and contemplating timely expansions, ensuring efficient resource allocation and avoiding resource stockpiling. Analyze resource collection efficiency and economic balance.
3. **Technological Path and Unit Composition**: Explore the current technological level, determining the technological trajectory and selecting suitable unit compositions, conducting essential research to adapt to potential enemy strategies and units. Discuss research priorities and unit diversity.
4. **Scouting Information and Tactical Adaptation**: Highlight the critical lack of opponent information and the paramount importance of early scouting, discussing how the acquired information will guide strategic and tactical adjustments. Analyze possible enemy strategies and responses.
5. **Map Control and Vision Acquisition**: Explore the significance of controlling key map areas and acquiring extensive vision to observe enemy movements and strategies. Analyze terrain utilization and control of key locations.
6. **Risk Management and Decision Making**: Evaluate the risks and rewards of current strategies, analyzing how to make optimal decisions to maximize advantages. Explore alternative strategies and plan adjustments.

### Offering Suggestions:
1. **Economic and Resource Management**:
   - Provide specific and practical suggestions to help players optimize resource management and economic development, such as sustaining worker production and considering timely expansions.
   
2. **Technological Path and Unit Composition**:
   - Offer clear suggestions to help players choose suitable technological paths and unit compositions based on enemy strategies and units.
   
3. **Scouting Information and Tactical Adaptation**:
   - Emphasize the importance of scouting and provide practical advice to help players adjust tactics and unit compositions based on gathered information.
   
4. **Map Control and Vision Acquisition**:
   - Propose concrete strategies to help players control key map areas and acquire extensive vision.
   
5. **Risk Management and Decision Making**:
   - Give wise advice to help players assess risks and make effective decisions.

In offering suggestions, maintain clarity, conciseness, and specificity, ensuring that players can understand and implement the advice. Additionally, suggestions should reflect PiG's deep understanding and professional style, making them insightful and engaging.

"""


# early game 0-5 turn gpt4 response
early_game_response = """
Game Situation Summary:
We are in the nascent stages of the game, with each timestamp representing a snapshot within the initial minutes. The game's infancy is marked by a focus on establishing a foundational economy, with 12 workers and a single base being a constant across the snapshots. The supply cap remains at 15, indicating no advancements in infrastructure. The lack of information on enemy units and strategies is a glaring gap, necessitating immediate scouting initiatives. The minimal variations in minerals and supply left across the timestamps underscore the early-game emphasis on resource accumulation and worker production.

Comprehensive Analysis:
Game Phase and Strategic Planning:

We are unequivocally in the early game phase, where foundational strategies are pivotal. The focus is predominantly on expansion and resource accumulation, with no indications of defensive or aggressive postures. The absence of significant developments or turning points highlights the importance of establishing a solid base for future strategic adaptations.
Economic Development and Resource Management:

The economic state is embryonic, characterized by a consistent worker count of 12 and a single base. The varying mineral counts indicate ongoing resource collection, but the emphasis needs to be on avoiding resource stockpiling and ensuring efficient allocation. The constant supply cap underscores the need for infrastructure development to facilitate economic expansion.
Technological Path and Unit Composition:

The technological landscape is a blank slate, with no information available on research or advancements. The unit composition is solely comprised of workers, emphasizing the need to diversify and adapt to potential enemy strategies once information is acquired.
Scouting Information and Tactical Adaptation:

The glaring lack of opponent information is a critical vulnerability. Early scouting is paramount to uncovering enemy strategies and making informed tactical adjustments. The absence of enemy information leaves us blind to possible strategies and responses, necessitating immediate and continuous scouting initiatives.
Map Control and Vision Acquisition:

The importance of controlling key map areas and acquiring extensive vision is heightened by the lack of enemy information. Gaining vision is crucial to observing enemy movements and strategies and adapting accordingly.
Risk Management and Decision Making:

The risks are inherent in the lack of information and the focus on economic development. Optimal decisions at this stage are centered around balancing economic expansion with information gathering to maximize advantages and prepare for potential threats.
Offering Suggestions:
Economic and Resource Management:

Prioritize sustaining worker production and consider timely expansions to optimize resource management. Avoid resource stockpiling and allocate resources efficiently to facilitate economic growth and infrastructure development.
Technological Path and Unit Composition:

Initiate basic research to unlock essential technologies and diversify unit compositions. Adapt unit compositions based on acquired information about enemy strategies and units.
Scouting Information and Tactical Adaptation:

Deploy immediate scouting initiatives to gather critical information about enemy units and strategies. Adjust tactics and unit compositions based on the acquired information to counter potential threats effectively.
Map Control and Vision Acquisition:

Establish control over key map areas and acquire extensive vision to monitor enemy movements and strategies. Utilize terrain effectively to gain strategic advantages.
Risk Management and Decision Making:

Assess the risks associated with the focus on economic development and the lack of enemy information. Make informed decisions to balance economic growth with strategic preparedness and adapt plans based on evolving situations.
"""
#game time At 00:08-00:16 ,05-10 turn gpt4 response
early_game_response_2 = """
Game Situation Summary:
The game is in its infancy, with game times ranging from 00:08 to 00:16. The player is in the initial stages of establishing an economic foundation with a single base and a limited number of workers. The resource availability is minimal, and there is no indication of any significant technological advancements or military developments. The absence of information regarding the enemy’s strategy necessitates a focus on scouting to gather intelligence on potential threats and developments. The essence of the game at this point is to lay down a solid economic and technological foundation to facilitate future advancements and strategies.

Comprehensive Analysis:
Game Phase and Strategic Planning:

The game is in the early phase, with strategies revolving around foundational developments. The player's focus should be on expanding the worker count, establishing additional bases, and initiating technological research to lay the groundwork for future advancements.
Economic Development and Resource Management:

The economic state is nascent, with a single base and a limited worker count. The immediate objective should be to enhance resource collection by increasing worker production and considering the establishment of additional bases to support sustained growth.
Technological Path and Unit Composition:

The technological trajectory is yet to be defined, with no evidence of any research or advanced buildings. The initiation of technological research is crucial to unlock advanced units and upgrades and to define the strategic path forward.
Scouting Information and Tactical Adaptation:

The lack of information about the enemy underscores the importance of scouting initiatives to gather intelligence on enemy developments and strategies. Tactical adaptations should be formulated based on the acquired information to counter potential threats effectively.
Map Control and Vision Acquisition:

The acquisition of map control and vision is essential to monitor enemy movements and secure strategic locations. The player should endeavor to maintain extensive vision and control key areas to facilitate strategic planning and decision-making.
Risk Management and Decision Making:

The risks are inherent in the unknown enemy developments and strategies. Decision-making should be informed by scouting information and focused on balancing economic development with defensive preparations to mitigate risks and optimize advantages.
Offering Suggestions:
Economic and Resource Management:

Prioritize the expansion of worker count and the establishment of additional bases to bolster resource collection. Efficient resource management is pivotal to support continuous development and to respond to evolving game dynamics.
Technological Path and Unit Composition:

Initiate technological research to define the strategic trajectory and to unlock advanced units and upgrades. Diversification of unit composition is essential to adapt to varying enemy strategies and to maintain a competitive edge.
Scouting Information and Tactical Adaptation:

Deploy scouting units to gather real-time intelligence on enemy developments and strategic orientations. Formulate tactical adaptations and strategic responses based on the acquired information to counteract enemy advancements effectively.
Map Control and Vision Acquisition:

Secure strategic locations and maintain extensive vision to monitor enemy movements and to facilitate informed decision-making. Utilize terrain advantages to establish defensive positions and to prepare for potential engagements.
Risk Management and Decision Making:

Evaluate the risks associated with unknown enemy strategies and make informed decisions to balance economic expansion with defensive measures. Optimize strategic positioning and resource allocation to counter potential threats and to maximize strategic advantages.
"""

# game time At 00:18-00:25 10-15 turn gpt4 response
early_game_response_3 = """
Game Situation Summary:
The game is persistently in the early stages, with game times from 00:18 to 00:25. The player is in the foundational phase, focusing on establishing an economic base with minimal resources and worker count. There is no indication of any significant technological advancements, military developments, or enemy strategies. The primary focus is on laying down a solid economic and technological foundation to facilitate future advancements and strategies.

Comprehensive Analysis:
Game Phase and Strategic Planning:

The game is consistently in the early phase, with strategies primarily revolving around foundational developments. The player's focus should be on expanding the worker count, establishing additional bases, and initiating technological research to lay the groundwork for future advancements.
Economic Development and Resource Management:

The economic state is nascent, with a single base and a limited worker count. The immediate objective should be to enhance resource collection by increasing worker production and considering the establishment of additional bases to support sustained growth.
Technological Path and Unit Composition:

The technological trajectory is yet to be defined, with no evidence of any research or advanced buildings. The initiation of technological research is crucial to unlock advanced units and upgrades and to define the strategic path forward.
Scouting Information and Tactical Adaptation:

The lack of information about the enemy underscores the importance of scouting initiatives to gather intelligence on enemy developments and strategies. Tactical adaptations should be formulated based on the acquired information to counter potential threats effectively.
Map Control and Vision Acquisition:

The acquisition of map control and vision is essential to monitor enemy movements and secure strategic locations. The player should endeavor to maintain extensive vision and control key areas to facilitate strategic planning and decision-making.
Risk Management and Decision Making:

The risks are inherent in the unknown enemy developments and strategies. Decision-making should be informed by scouting information and focused on balancing economic development with defensive preparations to mitigate risks and optimize advantages.
Offering Suggestions:
Economic and Resource Management:

Prioritize the expansion of worker count and the establishment of additional bases to bolster resource collection. Efficient resource management is pivotal to support continuous development and to respond to evolving game dynamics.
Technological Path and Unit Composition:

Initiate technological research to define the strategic trajectory and to unlock advanced units and upgrades. Diversification of unit composition is essential to adapt to varying enemy strategies and to maintain a competitive edge.
Scouting Information and Tactical Adaptation:

Deploy scouting units to gather real-time intelligence on enemy developments and strategic orientations. Formulate tactical adaptations and strategic responses based on the acquired information to counteract enemy advancements effectively.
Map Control and Vision Acquisition:

Secure strategic locations and maintain extensive vision to monitor enemy movements and to facilitate informed decision-making. Utilize terrain advantages to establish defensive positions and to prepare for potential engagements.
Risk Management and Decision Making:

Evaluate the risks associated with unknown enemy strategies and make informed decisions to balance economic expansion with defensive measures. Optimize strategic positioning and resource allocation to counter potential threats and to maximize strategic advantages.
"""
# game time At 00:26-00:33 15-20 turn gpt4 response
early_game_response_4 = """
Game Situation Summary:
The game is consistently in its infancy, with game times ranging from 00:26 to 00:33. The player is in the foundational phase, focusing on establishing an economic base with minimal resources and worker count. There is no indication of any significant technological advancements, military developments, or enemy strategies. The primary focus is on laying down a solid economic and technological foundation to facilitate future advancements and strategies.

Comprehensive Analysis:
Game Phase and Strategic Planning:

The game is uniformly in the early phase, with strategies primarily revolving around foundational developments. The player's focus should be on expanding the worker count, establishing additional bases, and initiating technological research to lay the groundwork for future advancements.
Economic Development and Resource Management:

The economic state is nascent, with a single base and a limited worker count. The immediate objective should be to enhance resource collection by increasing worker production and considering the establishment of additional bases to support sustained growth.
Technological Path and Unit Composition:

The technological trajectory is yet to be defined, with no evidence of any research or advanced buildings. The initiation of technological research is crucial to unlock advanced units and upgrades and to define the strategic path forward.
Scouting Information and Tactical Adaptation:

The lack of information about the enemy underscores the importance of scouting initiatives to gather intelligence on enemy developments and strategies. Tactical adaptations should be formulated based on the acquired information to counter potential threats effectively.
Map Control and Vision Acquisition:

The acquisition of map control and vision is essential to monitor enemy movements and secure strategic locations. The player should endeavor to maintain extensive vision and control key areas to facilitate strategic planning and decision-making.
Risk Management and Decision Making:

The risks are inherent in the unknown enemy developments and strategies. Decision-making should be informed by scouting information and focused on balancing economic development with defensive preparations to mitigate risks and optimize advantages.
Offering Suggestions:
Economic and Resource Management:

Prioritize the expansion of worker count and the establishment of additional bases to bolster resource collection. Efficient resource management is pivotal to support continuous development and to respond to evolving game dynamics.
Technological Path and Unit Composition:

Initiate technological research to define the strategic trajectory and to unlock advanced units and upgrades. Diversification of unit composition is essential to adapt to varying enemy strategies and to maintain a competitive edge.
Scouting Information and Tactical Adaptation:

Deploy scouting units to gather real-time intelligence on enemy developments and strategic orientations. Formulate tactical adaptations and strategic responses based on the acquired information to counteract enemy advancements effectively.
Map Control and Vision Acquisition:

Secure strategic locations and maintain extensive vision to monitor enemy movements and to facilitate informed decision-making. Utilize terrain advantages to establish defensive positions and to prepare for potential engagements.
Risk Management and Decision Making:

Evaluate the risks associated with unknown enemy strategies and make informed decisions to balance economic expansion with defensive measures. Optimize strategic positioning and resource allocation to counter potential threats and to maximize strategic advantages.
"""

# game time At 00:35-00:42 20-25 turn gpt4 response
early_game_response_5 = """
Game Situation Summary:
The game remains in its early stages, with game times between 00:35 and 00:42. The player is primarily focused on foundational developments, with an emphasis on economic expansion and infrastructure development. The player has a consistent worker count of 15 and a varying, yet minimal, amount of minerals. The player is gradually increasing the number of pylons, indicative of a plan to expand infrastructure. There is no indication of enemy units or strategies, and no significant advancements in technology or military developments have been made.

Comprehensive Analysis:
Game Phase and Strategic Planning:

The game is persistently in the early phase, with the player concentrating on foundational and economic developments. The strategy remains focused on expanding the economy, increasing infrastructure, and potentially initiating scouting initiatives to gather intelligence on enemy developments.
Economic Development and Resource Management:

The economic situation is consistently minimal, with a steady worker count and limited minerals. The emphasis should be on enhancing resource collection and considering the establishment of additional bases to support sustained growth and development.
Technological Path and Unit Composition:

There is a consistent lack of information regarding technological advancements or research. The initiation of technological research is crucial to unlock advanced units and upgrades and to define the strategic path forward.
Scouting Information and Tactical Adaptation:

The absence of information about the enemy underscores the importance of scouting initiatives to gather intelligence on enemy developments and strategies. Tactical adaptations should be formulated based on the acquired information to counter potential threats effectively.
Infrastructure Development and Expansion Planning:

The gradual increase in pylons suggests a plan for infrastructure development. The player should continue to expand infrastructure and consider establishing additional bases to support future advancements and strategies.
Risk Management and Decision Making:

The risks are inherent due to the unknown enemy developments and strategies. Decision-making should be informed by scouting information and focused on balancing economic development with defensive preparations to mitigate risks and optimize advantages.
Offering Suggestions:
Economic and Resource Management:

Prioritize the expansion of worker count and the establishment of additional bases to bolster resource collection. Efficient resource management is pivotal to support continuous development and to respond to evolving game dynamics.
Technological Path and Unit Composition:

Initiate technological research to define the strategic trajectory and to unlock advanced units and upgrades. Diversification of unit composition is essential to adapt to varying enemy strategies and to maintain a competitive edge.
Scouting Information and Tactical Adaptation:

Deploy scouting units to gather real-time intelligence on enemy developments and strategic orientations. Formulate tactical adaptations and strategic responses based on the acquired information to counteract enemy advancements effectively.
Infrastructure Development and Expansion Planning:

Continue to expand infrastructure and secure additional bases to support future unit production and technology research. This will facilitate strategic planning and decision-making in the subsequent stages of the game.
Risk Management and Decision Making:

Evaluate the risks associated with unknown enemy strategies and make informed decisions to balance economic expansion with defensive measures. Optimize strategic positioning and resource allocation to counter potential threats and to maximize strategic advantages.
"""

# game time At 00:44-00:51 25-30 turn gpt4 response
early_game_response_6 = """
Game Situation Summary:
The game continues to unfold in the early stages, with game times ranging from 00:44 to 00:51. The player maintains a consistent worker count of 15 and is engaged in foundational and economic developments. The player is progressively planning and constructing pylons and gas buildings, indicative of a strategic focus on infrastructure expansion and resource diversification. The supply cap is gradually increasing, reflecting the player’s preparatory steps for future developments. There is a persistent lack of information on enemy units or strategies, and no advancements in technology or military developments have been observed.

Comprehensive Analysis:
Game Phase and Strategic Planning:

The game is steadfastly in the early phase, with the player emphasizing foundational and economic developments. The strategy remains focused on expanding the economy, increasing infrastructure, and potentially initiating scouting initiatives to gather intelligence on enemy developments.
Economic Development and Resource Management:

The economic situation is consistently minimal, with a steady worker count and limited minerals. The emphasis should be on enhancing resource collection and considering the establishment of additional bases to support sustained growth and development.
Technological Path and Unit Composition:

There is a consistent lack of information regarding technological advancements or research. The initiation of technological research is crucial to unlock advanced units and upgrades and to define the strategic path forward.
Scouting Information and Tactical Adaptation:

The absence of information about the enemy underscores the importance of scouting initiatives to gather intelligence on enemy developments and strategies. Tactical adaptations should be formulated based on the acquired information to counter potential threats effectively.
Infrastructure Development and Expansion Planning:

The gradual increase in pylons and gas buildings suggests a plan for infrastructure development and resource diversification. The player should continue to expand infrastructure and consider establishing additional bases to support future advancements and strategies.
Risk Management and Decision Making:

The risks are inherent due to the unknown enemy developments and strategies. Decision-making should be informed by scouting information and focused on balancing economic development with defensive preparations to mitigate risks and optimize advantages.
Offering Suggestions:
Economic and Resource Management:

Prioritize the expansion of worker count and the establishment of additional bases to bolster resource collection. Efficient resource management is pivotal to support continuous development and to respond to evolving game dynamics.
Technological Path and Unit Composition:

Initiate technological research to define the strategic trajectory and to unlock advanced units and upgrades. Diversification of unit composition is essential to adapt to varying enemy strategies and to maintain a competitive edge.
Scouting Information and Tactical Adaptation:

Deploy scouting units to gather real-time intelligence on enemy developments and strategic orientations. Formulate tactical adaptations and strategic responses based on the acquired information to counteract enemy advancements effectively.
Infrastructure Development and Expansion Planning:

Continue to expand infrastructure and secure additional bases to support future unit production and technology research. This will facilitate strategic planning and decision-making in the subsequent stages of the game.
Risk Management and Decision Making:

Evaluate the risks associated with unknown enemy strategies and make informed decisions to balance economic expansion with defensive measures. Optimize strategic positioning and resource allocation to counter potential threats and to maximize strategic advantages.
"""
# game time At 00:53-01:00 30-35 turn gpt4 response
early_game_response_7 = """
Game Situation Summary:
The game is steadily progressing, with game times ranging from 00:53 to 01:00, and it remains entrenched in the early stages. The player is maintaining a consistent focus on foundational and economic developments, with a slight increase in worker count observed by 01:00. The construction of pylons and gas buildings continues to be a priority, reflecting a strategic focus on infrastructure expansion and resource diversification. The supply cap is witnessing a gradual increase, indicative of preparatory steps for future developments. There is a persistent lack of information on enemy units or strategies, and no advancements in technology or military developments have been observed.

Comprehensive Analysis:
Game Phase and Strategic Planning:

The game is persistently in the early phase, with the player emphasizing foundational and economic developments. The strategy remains focused on expanding the economy, increasing infrastructure, and potentially initiating scouting initiatives to gather intelligence on enemy developments.
Economic Development and Resource Management:

The economic situation is consistently minimal, with a slight increase in worker count and limited minerals. The emphasis should be on enhancing resource collection and considering the establishment of additional bases to support sustained growth and development.
Technological Path and Unit Composition:

There is a consistent lack of information regarding technological advancements or research. The initiation of technological research is crucial to unlock advanced units and upgrades and to define the strategic path forward.
Scouting Information and Tactical Adaptation:

The absence of information about the enemy underscores the importance of scouting initiatives to gather intelligence on enemy developments and strategies. Tactical adaptations should be formulated based on the acquired information to counter potential threats effectively.
Infrastructure Development and Expansion Planning:

The gradual increase in pylons and gas buildings suggests a plan for infrastructure development and resource diversification. The player should continue to expand infrastructure and consider establishing additional bases to support future advancements and strategies.
Risk Management and Decision Making:

The risks are inherent due to the unknown enemy developments and strategies. Decision-making should be informed by scouting information and focused on balancing economic development with defensive preparations to mitigate risks and optimize advantages.
Offering Suggestions:
Economic and Resource Management:

Prioritize the expansion of worker count and the establishment of additional bases to bolster resource collection. Efficient resource management is pivotal to support continuous development and to respond to evolving game dynamics.
Technological Path and Unit Composition:

Initiate technological research to define the strategic trajectory and to unlock advanced units and upgrades. Diversification of unit composition is essential to adapt to varying enemy strategies and to maintain a competitive edge.
Scouting Information and Tactical Adaptation:

Deploy scouting units to gather real-time intelligence on enemy developments and strategic orientations. Formulate tactical adaptations and strategic responses based on the acquired information to counteract enemy advancements effectively.
Infrastructure Development and Expansion Planning:

Continue to expand infrastructure and secure additional bases to support future unit production and technology research. This will facilitate strategic planning and decision-making in the subsequent stages of the game.
Risk Management and Decision Making:

Evaluate the risks associated with unknown enemy strategies and make informed decisions to balance economic expansion with defensive measures. Optimize strategic positioning and resource allocation to counter potential threats and to maximize strategic advantages.
"""

# game time At 02:58  100-105 turn gpt4 response
early_game_response_10 = """
Game Situation Summary:
We are progressing through the early stages of the game, with game times ranging from 02:58 to 03:05. The consistent presence of two bases and the establishment of structures like the Cybernetics Core and gateways indicate a foundational setup for economic and technological development. The enemy, identified as Zerg, is exhibiting signs of early aggression with units like Zerglings and Banelings and structures like the Spawning Pool and Extractor. The game's essence is still centered on economic expansion, technological advancement, and strategic positioning to counter the enemy's aggressive posture.

Comprehensive Analysis:
Game Phase and Strategic Planning:

We remain in the early game phase, with a focus on foundational strategies. The presence of enemy Zerglings and Banelings signals potential early aggression, necessitating strategic planning to counter such threats. The consistent establishment of foundational structures and units indicates a balanced approach between defense and economic development.
Economic Development and Resource Management:

The economic state is in a developmental phase, with a steady worker count and resource accumulation. The establishment of two bases and the construction of additional workers are positive steps towards economic expansion. Efficient resource allocation and management are crucial to sustaining growth and preparing for potential enemy engagements.
Technological Path and Unit Composition:

The technological trajectory is initiated with the establishment of a Cybernetics Core, opening avenues for advanced research and unit production. The planning of Stalkers and the initiation of Warpgate research are indicative of a focus on mobility and advanced unit production. The technological path needs to be optimized to counter the identified enemy units effectively.
Scouting Information and Tactical Adaptation:

The acquired information about the enemy reveals a Zerg opponent focusing on early aggression with Zerglings and Banelings. The identified enemy structures suggest a focus on resource gathering and unit production. Tactical adaptations and strategic planning should be aligned to counter the enemy's aggressive stance effectively.
Map Control and Vision Acquisition:

The importance of map control and vision is heightened by the enemy's aggressive unit composition. Securing key map areas and maintaining extensive vision are pivotal to observing enemy movements and adapting strategies accordingly.
Risk Management and Decision Making:

The risks are intertwined with the enemy's aggressive approach and our focus on economic and technological development. Decision-making should be centered around balancing economic expansion with strategic defense and counter-aggression to mitigate risks and maximize advantages.
Offering Suggestions:
Economic and Resource Management:

Continue to expand worker production and optimize resource allocation to sustain economic growth. Consider establishing additional bases to enhance resource collection and support technological and military advancements.
Technological Path and Unit Composition:

Expedite the completion of Warpgate research and prioritize the production of advanced units capable of countering Zerglings and Banelings. Explore technological upgrades to enhance unit capabilities and diversify unit composition to respond effectively to enemy strategies.
Scouting Information and Tactical Adaptation:

Maintain continuous scouting initiatives to gather real-time information about enemy advancements and strategies. Adapt unit compositions and tactical positioning based on the acquired information to counteract enemy aggression efficiently.
Map Control and Vision Acquisition:

Secure control over strategic map locations and maintain extensive vision to monitor enemy movements and strategies. Utilize terrain advantages to establish defensive positions and prepare for potential enemy engagements.
Risk Management and Decision Making:

Evaluate the risks associated with the enemy's aggressive posture and adapt strategies to balance defense with economic and technological advancements. Make informed decisions to optimize resource allocation, unit production, and strategic positioning to counter potential threats effectively.
"""

#medium game started at 05:56 200-205 turn gpt4 response:
medium_game_response = """
Game Situation Summary:
The game is progressing through the early stages, with game times ranging from 05:56 to 06:03. The consistent presence of three bases, a stable economy, and the establishment of key structures like the Cybernetics Core, Twilight Council, and Robotics Facility indicate a foundational setup for economic and technological development. The enemy, identified as Zerg, is exhibiting signs of early aggression with units like Zerglings and structures like the Spawning Pool and Extractor. The game's essence is still centered on economic expansion, technological advancement, and strategic positioning to counter the enemy's aggressive posture.

Comprehensive Analysis:
Game Phase and Strategic Planning:

The game remains in the early phase, with a focus on foundational strategies. The presence of enemy Zerglings signals potential early aggression, necessitating strategic planning to counter such threats. The consistent establishment of foundational structures and units indicates a balanced approach between defense and economic development.
Economic Development and Resource Management:

The economic state is stable, with a steady worker count and resource accumulation. The establishment of three bases and the construction of additional workers are positive steps towards economic expansion. Efficient resource allocation and management are crucial to sustaining growth and preparing for potential enemy engagements.
Technological Path and Unit Composition:

The technological trajectory is initiated with the establishment of a Cybernetics Core, Twilight Council, and Robotics Facility, opening avenues for advanced research and unit production. The planning of Stalkers and the completion of Warpgate research are indicative of a focus on mobility and advanced unit production. The technological path needs to be optimized to counter the identified enemy units effectively.
Scouting Information and Tactical Adaptation:

The acquired information about the enemy reveals a Zerg opponent focusing on early aggression with Zerglings. The identified enemy structures suggest a focus on resource gathering and unit production. Tactical adaptations and strategic planning should be aligned to counter the enemy's aggressive stance effectively.
Map Control and Vision Acquisition:

The importance of map control and vision is heightened by the enemy's aggressive unit composition. Securing key map areas and maintaining extensive vision are pivotal to observing enemy movements and adapting strategies accordingly.
Risk Management and Decision Making:

The risks are intertwined with the enemy's aggressive approach and our focus on economic and technological development. Decision-making should be centered around balancing economic expansion with strategic defense and counter-aggression to mitigate risks and maximize advantages.
Offering Suggestions:
Economic and Resource Management:

Continue to expand worker production and optimize resource allocation to sustain economic growth. Consider establishing additional bases to enhance resource collection and support technological and military advancements.
Technological Path and Unit Composition:

Expedite the research of advanced technologies and prioritize the production of advanced units capable of countering Zerglings. Explore technological upgrades to enhance unit capabilities and diversify unit composition to respond effectively to enemy strategies.
Scouting Information and Tactical Adaptation:

Maintain continuous scouting initiatives to gather real-time information about enemy advancements and strategies. Adapt unit compositions and tactical positioning based on the acquired information to counteract enemy aggression efficiently.
Map Control and Vision Acquisition:

Secure control over strategic map locations and maintain extensive vision to monitor enemy movements and strategies. Utilize terrain advantages to establish defensive positions and prepare for potential enemy engagements.
Risk Management and Decision Making:

Evaluate the risks associated with the enemy's aggressive posture and adapt strategies to balance defense with economic and technological advancements. Make informed decisions to optimize resource allocation, unit production, and strategic positioning to counter potential threats effectively.
"""
# later game started 20:49 gpt4 response:
later_game_response = """
Game Situation Summary:
The game has progressed to the late stages, with game times ranging from 20:49 to 20:57. The player has established a strong economic foundation with 7 bases and a substantial amount of minerals and gas. The army composition is predominantly air-focused, featuring units like Voidrays and Phoenixes, indicating a strategy centered on air dominance. The enemy, identified as Zerg, is seemingly focusing on foundational structures like Hatcheries and Extractors, hinting at a strategy revolving around unit production and resource gathering. The essence of the game is now centered on leveraging the established economic and military advantages to secure a decisive victory.

Comprehensive Analysis:
Game Phase and Strategic Planning:

The game is in the late phase, with strategies evolving around leveraging established advantages. The player's focus on air units like Voidrays and Phoenixes suggests a strategy aimed at achieving air superiority and executing powerful air assaults.
Economic Development and Resource Management:

The economic state is robust, with a stable worker supply and substantial resource reserves. The establishment of 7 bases is indicative of a strong economic foundation, allowing for sustained unit production and technological advancements.
Technological Path and Unit Composition:

The technological trajectory is marked by the presence of a Cybernetics Core and a Twilight Council, enabling access to advanced technologies. The researched Warpgate and Protoss Air Armor Level 1 are indicative of a focus on enhancing air unit capabilities. However, further technological advancements and upgrades are crucial to maintaining a competitive edge.
Scouting Information and Tactical Adaptation:

The acquired information about the enemy reveals a focus on foundational Zerg structures, suggesting a strategy centered on resource gathering and unit production. Tactical adaptations should be aligned to counter potential Zerg unit swarms effectively.
Map Control and Vision Acquisition:

The importance of map control and vision is crucial in monitoring enemy movements and adapting strategies accordingly. The player should maintain extensive vision and secure key map areas to observe enemy advancements and prepare for engagements.
Risk Management and Decision Making:

The risks are associated with the enemy's potential to swarm with a large number of units. Decision-making should be centered around balancing aggressive maneuvers with defensive preparations to mitigate risks and maximize advantages.
Offering Suggestions:
Economic and Resource Management:

Continue to optimize resource allocation and consider establishing additional bases to enhance resource collection and support sustained unit production and technological advancements.
Technological Path and Unit Composition:

Expedite the research of advanced technologies and prioritize the production of advanced units and upgrades to enhance unit capabilities and diversify unit composition to respond effectively to enemy strategies.
Scouting Information and Tactical Adaptation:

Maintain continuous scouting initiatives to gather real-time information about enemy advancements and strategies. Adapt unit compositions and tactical positioning based on the acquired information to counteract enemy aggression efficiently.
Map Control and Vision Acquisition:

Secure control over strategic map locations and maintain extensive vision to monitor enemy movements and strategies. Utilize terrain advantages to establish defensive positions and prepare for potential enemy engagements.
Risk Management and Decision Making:

Evaluate the risks associated with the enemy's potential to produce a large number of units and adapt strategies to balance offense with defense. Make informed decisions to optimize resource allocation, unit production, and strategic positioning to counter potential threats effectively.
"""

# game time at 00:00 to 01:00
one_minute_output = """
Summary:
The game's progression is meticulously segmented into seven distinct time frames, from 00:00 to 01:00, each representing a snapshot of the evolving game dynamics. The overarching theme across these segments is the foundational and economic development, with a consistent focus on establishing a robust economic base, infrastructure expansion, and resource diversification. The player's strategy is marked by a gradual increase in worker count, construction of pylons, and gas buildings, and a steady rise in the supply cap, indicative of preparatory steps for future developments. However, there is a conspicuous absence of information on enemy units or strategies and no observable advancements in technology or military developments throughout these stages.

Analysis:
Foundational and Economic Focus:

The game's initial stages are characterized by a steadfast focus on foundational and economic developments, with the player meticulously laying down the economic and technological foundation across the time frames.
The consistent worker count and the gradual increase in infrastructure elements like pylons and gas buildings underscore a strategic approach to solidify the economic base and prepare for future advancements.
Strategic Evolution and Preparation:

The strategic evolution is evident through the gradual increase in the supply cap and the subtle shifts in focus and priorities, reflecting the player’s preparatory steps and forward-thinking approach.
The varying amount of minerals and the emphasis on resource diversification highlight the player's adaptive strategy to the evolving game dynamics and potential future confrontations.
Information Void and Unexplored Developments:

The persistent lack of information regarding enemy strategies and units is a significant gap in the strategic landscape, impacting the player's ability to make informed decisions and anticipate potential threats.
The absence of significant technological and military developments suggests a possible deliberate choice to prioritize foundational developments in these early stages, leaving room for exploration and advancements in the subsequent stages of the game.
Recommendations:
Immediate Scouting Initiatives:

To mitigate the impact of the information void, immediate scouting initiatives should be undertaken to gather intelligence on enemy strategies, developments, and potential threats, enabling more informed and anticipatory strategic planning.
Balanced and Adaptive Strategy:

A balanced and adaptive strategy should be employed to allocate resources efficiently between economic growth, technological research, and military production, ensuring a well-rounded development and preparedness for potential confrontations.
Exploration of Technological and Military Advancements:

The player should explore and invest in technological and military advancements to leverage strategic gains, enhance defensive and offensive capabilities, and gain a competitive edge in the subsequent stages of the game.
Time-Efficient Resource Management:

Given the criticality of time in StarCraft 2, the player should optimize and manage resources and developments in a time-efficient manner, ensuring steady progression and timely responses to evolving game dynamics and potential threats.
"""