from sc2_rl_agent.starcraftenv_test.utils.action_info import ActionDescriptions
from sc2_rl_agent.starcraftenv_test.prompt.prompt import StarCraftIIPrompt_V3

action_desc = ActionDescriptions("Protoss")
action_dict = action_desc.action_descriptions
# print("action_dict:",action_dict)
sc2prompt = StarCraftIIPrompt_V3(race="Protoss", K="5", action_dict=action_dict, game_style="")
system_prompt, example_input_prompt, example_output_prompt = sc2prompt.generate_prompts()
example_prompt = [example_input_prompt.format(K_1=4), example_output_prompt]
print(system_prompt)
print(example_input_prompt)
print(example_output_prompt)
