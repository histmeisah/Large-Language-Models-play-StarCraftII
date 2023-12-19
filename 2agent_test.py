from datetime import datetime

import argparse

from utils.action_info import ActionDescriptions
from config.config import LADDER_MAP_2023
from env.starcraft_env import StarCraftEnvSelector
from agent.random_agent import RandomAgent
from prompt.prompt import *

"""
地图池

    laddermap_2023 = ['Altitude LE', 'Ancient Cistern LE', 'Babylon LE', 'Dragon Scales LE', 'Gresvan LE',
                      'Neohumanity LE', 'Royal Blood LE']

"""


def agent_vs_agent_test(agent1, agent2, env):
    observations = env.reset()  # Get initial observations for both agents
    agent1_obs, agent2_obs = observations

    dones = {'1': False, '2': False}

    while not all(dones.values()):
        action1 = agent1.action(agent1_obs)
        action2 = agent2.action(agent2_obs)

        new_observations, rewards, new_dones, results, infos = env.step([action1, action2])
        print("new_observations:", new_observations)
        print("type of new observations:", type(new_observations))
        agent1_new_obs = new_observations[1]
        agent2_new_obs = new_observations[2]
        # print("Agent1 action_failures:", agent1_new_obs['action_failures'])
        # print("Agent2 action_failures:", agent2_new_obs['action_failures'])
        print("in agent test")
        print(type(agent1_new_obs))
        print(agent1_new_obs)
        print("____")
        agent1_obs = agent1_new_obs
        agent2_obs = agent2_new_obs
        dones = new_dones

        if all(dones.values()):
            break



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='StarCraft II environment testing tool.')

    parser.add_argument('--num_agents', type=str, default='two',
                        help='Choose "single" for single bot or "two" for two agents.')

    parser.add_argument('--env_type', type=str, default='text', help='Environment type.')

    parser.add_argument('--map_pool', type=list, default=LADDER_MAP_2023, help='List of maps for the game.')

    parser.add_argument('--map_idx', type=int, default=1, help='Index of the map to use from the map pool.')

    parser.add_argument('--player1_race', type=str, default='Zerg',
                        help='Player 1 race. Use "Protoss" or "Zerg". Only valid for two agents.')

    parser.add_argument('--player2_race', type=str, default='Protoss',
                        help='Player 2 race. Use "Protoss" or "Zerg". Only valid for two agents.')

    parser.add_argument('--process_id', type=str, default='-1', help='-1 means not multiprocess worker'
                                                                     '0-100 means multiprocess id.')
    parser.add_argument('--current_time', type=str, default=datetime.now().strftime('%Y%m%d_%H%M%S'),
                        help='Current time. Default is current system time.')
    parser.add_argument('--agent1_type', type=str, default="random",
                        help='Agent type. Use "random" or "llama2" or "glm2" or "gpt"')
    parser.add_argument('--agent2_type', type=str, default="random",
                        help='Agent type. Use "random" or "llama2" or "glm2" or "gpt"')
    parser.add_argument('--replay_folder', type=str,
                        default=r'D:\pythoncode\TextStarCraft2\sc2_rl_agent\starcraftenv_test\test_replay',
                        help='Folder to save replays.')
    parser.add_argument('--game_style', type=str, default=None,
                        help='Game style to use for the strategy. Choices are "aggressive", "air_superiority", '
                             '"immortal_archon_push", "4_base_zealot_archon", "fast_4rd_zealot_stalker".')
    args = parser.parse_args()
    selector = StarCraftEnvSelector(args)
    env = selector.create_env()

    # LLM_model_name = "gpt-3.5-turbo"
    LLM_model_name = "gpt-3.5-turbo-16k"

    LLM_temperature = 0
    # LLM_api_key = "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"

    # LLM_api_key = "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"
    # LLM_api_base = "https://api.openai.com/v1"

    LLM_api_key = "sk-rgkyVo6FAxjqaSND31124f475b5f4469B8134dD2Df3678D4"
    LLM_api_base = "https://api.wzunjh.top/v1"
    # LLM_api_key = "sk-w9gpAUUSP6KYBqQpC3C9DfFc687d458aA74b77E9C735BeE2"
    # LLM_api_base = "https://api.wzunjh.top/v1"

    """
    test glm2 agent
    """

    # glm2_agent = Glm2Agent(model_name=LLM_model_name, api_key=LLM_api_key, api_base=LLM_api_base,
    #                        system_prompt=system_prompt, example_prompt=example_prompt,
    #                        temperature=LLM_temperature, args=args, action_description=action_description)
    # glm2_agent_test(glm2_agent, env)

    """
    test gpt agent
    """
    # gpt_agent = ChatGPTAgent(model_name=LLM_model_name, api_key=LLM_api_key, api_base=LLM_api_base,
    #                          system_prompt=system_prompt, example_prompt=example_prompt,
    #                          temperature=LLM_temperature, args=args, action_description=action_description)
    # gpt_agent_test(gpt_agent, env)
    """
    test llama2 agent
    """
    # llama2_agent = Llama2Agent(model_name=LLM_model_name, api_key=LLM_api_key, api_base=LLM_api_base,
    #                           system_prompt=system_prompt, example_prompt=example_prompt,
    #                           temperature=LLM_temperature, args=args, action_description=action_description)
    # llama2_agent_test(llama2_agent, env)
    """
    test random agent
    """
    GAME_STYLES = ["aggressive", "air_superiority", "immortal_archon_push", "4_base_zealot_archon",
                   "fast_4rd_zealot_stalker"]

    player1_action_description = ActionDescriptions(env.player1_race)
    player1_action_dict = player1_action_description.action_descriptions
    player1_prompt = StarCraftIIPrompt_V3(race=args.player1_race, K="5", action_dict=player1_action_dict,game_style=GAME_STYLES[0])
    player1_system_prompt, player1_example_input_prompt, player1_example_output_prompt = player1_prompt.generate_prompts()
    player1_example_prompt = [player1_example_input_prompt.format(K_1=4), player1_example_output_prompt]
    agent1 = RandomAgent(model_name=LLM_model_name, api_key=LLM_api_key, api_base=LLM_api_base,
                         system_prompt=player1_system_prompt, temperature=LLM_temperature,
                         example_prompt=player1_example_prompt,
                         args=args, action_description=player1_action_description)

    player2_action_description = ActionDescriptions(env.player2_race)
    player2_action_dict = player2_action_description.action_descriptions
    player2_prompt = StarCraftIIPrompt_V3(race=args.player2_race, K="5", action_dict=player2_action_dict,game_style=GAME_STYLES[0])
    player2_system_prompt, player2_example_input_prompt, player1_example_output_prompt = player2_prompt.generate_prompts()
    player2_example_prompt = [player2_example_input_prompt.format(K_1=4), player1_example_output_prompt]
    agent2 = RandomAgent(model_name=LLM_model_name, api_key=LLM_api_key, api_base=LLM_api_base,
                         system_prompt=player2_system_prompt, temperature=LLM_temperature,
                         example_prompt=player2_example_prompt,
                         args=args, action_description=player2_action_description)

    agent_vs_agent_test(agent1=agent1, agent2=agent2, env=env)
