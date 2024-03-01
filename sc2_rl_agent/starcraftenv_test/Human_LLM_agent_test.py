from datetime import datetime

import argparse

from sc2_rl_agent.starcraftenv_test.utils.action_info import ActionDescriptions
from sc2_rl_agent.starcraftenv_test.config.config import LADDER_MAP_2023
from sc2_rl_agent.starcraftenv_test.env.starcraft_env import StarCraftEnvSelector
from sc2_rl_agent.starcraftenv_test.agent.vs_human.qwen_vs_human_agent import Qwen_vs_Human_Agent
from sc2_rl_agent.starcraftenv_test.prompt.prompt import *

"""
地图池

    laddermap_2023 = ['Altitude LE', 'Ancient Cistern LE', 'Babylon LE', 'Dragon Scales LE', 'Gresvan LE',
                      'Neohumanity LE', 'Royal Blood LE']

build in ai 难度

'Difficulty.values',
  full_name='SC2APIProtocol.Difficulty',
  values=['VeryEasy', 'Easy', 'Medium', 'MediumHard', 'Hard', 'Harder''VeryHard''CheatVision''CheatMoney','CheatInsane']
  terran_bot = [marine_marauder_Bot,marine_tank_Bot,tank_heller_thor_Bot]
  protoss_bot =[WarpGateBot]
  zerg_bot = [hydra_ling_bane_bot,roach_ling_baneling_bot,roach_hydra_bot]

"""


def agent_test(agent, env):
    observation, _ = env.reset()  # Get initial observation
    done = False

    while not done:
        action = agent.action(observation)
        observation, reward, done, result, info = env.step(action)

        if done:
            break



def real_time_test(args):
    # 初始化环境
    selector = StarCraftEnvSelector(args)
    env = selector.create_env()

    # 获取行动描述
    action_description = ActionDescriptions(env.player_race)
    action_dict = action_description.action_descriptions
    print("action_dict", action_dict)

    # 生成提示
    sc2prompt = StarCraftIIPrompt_realtime(race=args.player_race, K="10", action_dict=action_dict)
    system_prompt, example_input_prompt, example_output_prompt = sc2prompt.generate_prompts()
    example_prompt = [example_input_prompt.format(K_1=9), example_output_prompt]

    # 创建并测试agent
    if args.agent_type == 'qwen':

        agent = Qwen_vs_Human_Agent(
                            system_prompt, example_prompt,
                            args, action_description)
        agent_test(agent, env)
    else:
        raise ValueError(f"Unknown agent type: {args.agent_type}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='StarCraft II environment testing tool.')

    parser.add_argument('--num_agents', type=str, default='Human',
                        help='In human vs LLM agent, we set as Human.')

    parser.add_argument('--env_type', type=str, default='text', help='Environment type.')

    parser.add_argument('--map_pool', type=list, default=LADDER_MAP_2023, help='List of maps for the game.')

    parser.add_argument('--map_idx', type=int, default=1, help='Index of the map to use from the map pool.')

    parser.add_argument('--Human_race', type=str, default='Zerg',
                        help='The Human player race. Use "Protoss" or "Zerg". ')

    parser.add_argument('--player_race', type=str, default='Protoss',
                        help='The llm agent Player race. Use "Protoss" or "Zerg". ')

    parser.add_argument('--current_time', type=str, default=datetime.now().strftime('%Y%m%d_%H%M%S'),
                        help='Current time. Default is current system time.')

    parser.add_argument('--agent_type', type=str, default="qwen",
                        help='The LLM Agent type. Use "random" or "llama2" or "glm2" or "chatgpt,"qwen"')


    parser.add_argument('--real_time', type=bool, default=True, help='In Human vs ai, please always set True')
    args = parser.parse_args()
    real_time_test(args)

