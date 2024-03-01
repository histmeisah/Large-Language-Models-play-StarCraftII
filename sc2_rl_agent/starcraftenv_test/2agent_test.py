from datetime import datetime

import argparse

from sc2_rl_agent.starcraftenv_test.utils.action_info import ActionDescriptions
from sc2_rl_agent.starcraftenv_test.config.config import LADDER_MAP_2023
from sc2_rl_agent.starcraftenv_test.env.starcraft_env import StarCraftEnvSelector
from sc2_rl_agent.starcraftenv_test.agent.random_agent import RandomAgent
from sc2_rl_agent.starcraftenv_test.agent.chatgpt_agent import ChatGPTAgent
from sc2_rl_agent.starcraftenv_test.agent.prompt1_agent import Prompt1_Agent
from sc2_rl_agent.starcraftenv_test.agent.vs_llm.gemini_vs_llm_agent import Gemini_vs_llm_Agent
from sc2_rl_agent.starcraftenv_test.prompt.prompt import *

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

        agent1_new_obs = new_observations[1]
        agent2_new_obs = new_observations[2]
        agent1_obs = agent1_new_obs
        agent2_obs = agent2_new_obs
        dones = new_dones

        if all(dones.values()):
            break


def initialize_agent(args, player_id):
    """初始化指定类型的代理"""
    if player_id == 2:
        player_race = args.player1_race
        agent_type = args.agent1_type
        LLM_model_name =args.agent1_LLM_model_name
        LLM_api_key = args.agent1_LLM_api_key
        LLM_api_base=args.agent1_LLM_api_base
        LLM_temperature = args.agent1_LLM_temperature

    elif player_id ==1:
        player_race = args.player2_race
        agent_type = args.agent2_type
        LLM_model_name =args.agent2_LLM_model_name
        LLM_api_key = args.agent2_LLM_api_key
        LLM_api_base=args.agent2_LLM_api_base
        LLM_temperature = args.agent2_LLM_temperature
    else:
        raise ValueError(f"We only support 2 players")
    action_description = ActionDescriptions(player_race)
    action_dict = action_description.action_descriptions

    prompt = StarCraftIIPrompt_V4(race=player_race, K="5", action_dict=action_dict)
    system_prompt, example_input_prompt, example_output_prompt = prompt.generate_prompts()
    example_prompt = [example_input_prompt.format(K_1=4), example_output_prompt]

    if agent_type == "random":
        return RandomAgent(model_name=LLM_model_name, api_key=LLM_api_key, api_base=LLM_api_base,
                           system_prompt=system_prompt, temperature=LLM_temperature,
                           example_prompt=example_prompt,
                           args=args, action_description=action_description)
    elif agent_type == "chatgpt":
        return ChatGPTAgent(model_name=LLM_model_name, api_key=LLM_api_key,
                            api_base=LLM_api_base, system_prompt=system_prompt,
                            temperature=LLM_temperature, example_prompt=example_prompt,
                            args=args, action_description=action_description)
    elif agent_type == "prompt1":
        return Prompt1_Agent(model_name=LLM_model_name, api_key=LLM_api_key,
                             api_base=LLM_api_base, system_prompt=system_prompt,
                             temperature=LLM_temperature, example_prompt=example_prompt,
                             args=args, action_description=action_description)
    elif agent_type == "gemini":
        return Gemini_vs_llm_Agent(model_name=LLM_model_name, api_key=LLM_api_key,
                                   api_base=LLM_api_base, system_prompt=system_prompt,
                                   temperature=LLM_temperature,player_id=player_id, example_prompt=example_prompt,
                                   args=args, action_description=action_description)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='StarCraft II environment testing tool.')

    parser.add_argument('--num_agents', type=str, default='two',
                        help='Choose "single" for single bot or "two" for two agents.')

    parser.add_argument('--env_type', type=str, default='text', help='Environment type.')

    parser.add_argument('--map_pool', type=list, default=LADDER_MAP_2023, help='List of maps for the game.')

    parser.add_argument('--map_idx', type=int, default=1, help='Index of the map to use from the map pool.')

    parser.add_argument('--player1_race', type=str, default='Protoss',
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
    parser.add_argument('--real_time', type=bool, default=False, help='True or False')

    parser.add_argument('--agent1_LLM_model_name', type=str, default="random")
    parser.add_argument('--agent1_LLM_temperature', type=float, default=0)
    parser.add_argument('--agent1_LLM_api_key', type=str, default="your-key")
    parser.add_argument('--agent1_LLM_api_base', type=str, default="your-api-base")

    parser.add_argument('--agent2_LLM_model_name', type=str, default="random")
    parser.add_argument('--agent2_LLM_temperature', type=float, default=0)
    parser.add_argument('--agent2_LLM_api_key', type=str, default="your-key")
    parser.add_argument('--agent2_LLM_api_base', type=str, default="your-api-base")
    parser.add_argument('--opposite_type', type=str, default='llm',
                        help='Opponent bot type. Use "rule" or "build_in". "rule" means bot AI designed by makers, "build_in" means official Blizzard AI. Only valid for single bot.')

    args = parser.parse_args()
    selector = StarCraftEnvSelector(args)
    env = selector.create_env()

    agent1 = initialize_agent(args, player_id=1)
    agent2 = initialize_agent(args, player_id=2)

    agent_vs_agent_test(agent1=agent1, agent2=agent2, env=env)
