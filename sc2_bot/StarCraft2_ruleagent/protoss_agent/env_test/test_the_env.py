from datetime import datetime

import argparse
import wandb
import argparse

import wandb

from sc2_rl_agent.starcraftenv_test.config.config import LADDER_MAP_2023, DIFFICULTY_LEVELS
from sc2_bot.StarCraft2_ruleagent.protoss_agent.for_test_env import VsBuildIn
from sc2_bot.StarCraft2_ruleagent.protoss_agent.env_test.random_agent import RandomAgent
from sc2_bot.StarCraft2_ruleagent.protoss_agent.env_test.llm_agent import LLM_Agent

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


def None_agent_test(agent, env):
    observation, _ = env.reset()  # Get initial L1_observation
    done = False

    while not done:
        action = agent.action(observation)
        observation, reward, done, result, info = env.step(action)
        if done:
            break
    # # 当所有的任务完成后，发送一个 "DONE" 消息到队列中，让日志记录进程结束


def llm_agent_test(agent, env):
    observation, _ = env.reset()  # Get initial L1_observation
    done = False

    while not done:
        action = agent.action(observation)
        observation, reward, done, result, info = env.step(action)
        if done:
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='StarCraft II environment testing tool.')

    parser.add_argument('--num_agents', type=str, default='single',
                        help='Choose "single" for single bot or "two" for two agents.')

    parser.add_argument('--env_type', type=str, default='text', help='Environment type.')

    parser.add_argument('--map_pool', type=list, default=LADDER_MAP_2023, help='List of maps for the game.')

    parser.add_argument('--map_idx', type=int, default=1, help='Index of the map to use from the map pool.')

    parser.add_argument('--player_race', type=str, default='Protoss',
                        help='Player race. Use "Protoss" or "Zerg". Only valid for single bot.')

    parser.add_argument('--opposite_race', type=str, default='Terran',
                        help='Opponent race. Use "Protoss" or "Zerg". Only valid for single bot.')

    parser.add_argument('--opposite_type', type=str, default='build_in',
                        help='Opponent bot type. Use "rule" or "build_in". "rule" means bot AI designed by makers, "build_in" means official Blizzard AI. Only valid for single bot.')

    parser.add_argument('--opposite_bot', type=str, default='hydra_ling_bane_bot',
                        help='Opponent bot type when playing against rule AI. Only valid for single bot.')

    parser.add_argument('--difficulty', type=str, default=DIFFICULTY_LEVELS[4],
                        help='Game difficulty level when playing against build-in AI. Only valid for single bot.')

    parser.add_argument('--player1_race', type=str, default='Zerg',
                        help='Player 1 race. Use "Protoss" or "Zerg". Only valid for two agents.')

    parser.add_argument('--player2_race', type=str, default='Protoss',
                        help='Player 2 race. Use "Protoss" or "Zerg". Only valid for two agents.')
    parser.add_argument('--replay_folder', type=str,
                        default=r'D:\pythoncode\TextStarCraft2\sc2_rl_agent\starcraftenv_test\test_replay',
                        help='Folder to save replays.')
    parser.add_argument('--process_id', type=str, default='-1', help='-1 means not multiprocess worker'
                                                                     '0-100 means multiprocess id.')
    parser.add_argument('--current_time', type=str, default=datetime.now().strftime('%Y%m%d_%H%M%S'),
                        help='Current time. Default is current system time.')
    parser.add_argument('--agent_type', type=str, default="random",
                        help='Agent type. Use "random" or "llama2" or "glm2" or "gpt"')

    args = parser.parse_args()
    """
    random agent test
    """
    # env = VsBuildIn(args)
    # agent = RandomAgent()
    # None_agent_test(agent, env)

    """
    llm agent test
    """
    env = VsBuildIn(args)
    system_prompt = " In this game of StarCraft II, we are representing the Protoss race against the Terran opponent. Our strategic approach involves primarily producing Stalkers and Zealots for offensive operations against the enemy."
    host = '172.18.116.172'
    port = 2222
    agent = LLM_Agent(
        system_prompt=system_prompt,
        port=port,
        host=host

    )
    None_agent_test(agent, env)
