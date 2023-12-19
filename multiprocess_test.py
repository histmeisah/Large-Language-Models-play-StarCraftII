from datetime import datetime

import argparse
import multiprocessing
import copy
import wandb
from worker import gpt_worker
from utils.action_info import ActionDescriptions
from config.config import LADDER_MAP_2023, DIFFICULTY_LEVELS

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








def gpt_agent_test(agent, env):
    wandb.login(key='a51e8268ce285c7e63ccc7a6d685e6ea85c48101')
    config = {
        "LLM_model_name": "gpt-3.5-turbo",
        "LLM_temperature": 0,
        "action_interval": 10,
        "request_delay": 0.2,
        "chunk_window": 5,
        "action_window": 10,
        "action_mix_rate": 0.5,
        "last_k": 5,

    }
    wandb.init(project="TextStarCraft2", config=config)
    observation, _ = env.reset()  # Get initial L1_observation
    done = False

    while not done:
        action = agent.action(observation)
        observation, reward, done, result, info = env.step(action)

        if done:
            break
    # # 当所有的任务完成后，发送一个 "DONE" 消息到队列中，让日志记录进程结束


def random_agent_test(agent, env):
    observation, _ = env.reset()  # Get initial L1_observation
    done = False

    action_description = ActionDescriptions(env.player_race)
    action_dict = action_description.action_descriptions
    while not done:
        action = agent.action(observation)
        observation, reward, done, result, info = env.step(action)
        print("observation[action_failures]", observation['action_failures'])
        if done:
            break
    # # 当所有的任务完成后，发送一个 "DONE" 消息到队列中，让日志记录进程结束


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='StarCraft II environment testing tool.')

    parser.add_argument('--num_agents', type=str, default='single',
                        help='Choose "single" for single bot or "two" for two agents.')

    parser.add_argument('--env_type', type=str, default='text', help='Environment type.')

    parser.add_argument('--map_pool', type=list, default=LADDER_MAP_2023, help='List of maps for the game.')

    parser.add_argument('--map_idx', type=int, default=1, help='Index of the map to use from the map pool.')

    parser.add_argument('--player_race', type=str, default='Protoss',
                        help='Player race. Use "Protoss" or "Zerg". Only valid for single bot.')

    parser.add_argument('--opposite_race', type=str, default='Zerg',
                        help='Opponent race. Use "Protoss" or "Zerg". Only valid for single bot.')

    parser.add_argument('--opposite_type', type=str, default='build_in',
                        help='Opponent bot type. Use "rule" or "build_in". "rule" means bot AI designed by makers, "build_in" means official Blizzard AI. Only valid for single bot.')

    parser.add_argument('--opposite_bot', type=str, default='WarpGateBot',
                        help='Opponent bot type when playing against rule AI. Only valid for single bot.')

    parser.add_argument('--difficulty', type=str, default=DIFFICULTY_LEVELS[5],
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
    parser.add_argument('--agent_type', type=str, default="gpt",
                        help='Agent type. Use "random" or "llama2" or "glm2" or "gpt"')

    parser.add_argument('--LLM_model_name', type=str, default="gpt-3.5-turbo-16k")
    parser.add_argument('--LLM_temperature', type=float, default=0)

    parser.add_argument('--LLM_api_key', type=str, default="")
    parser.add_argument('--LLM_api_base', type=str, default="")
    parser.add_argument('--num_processes', type=int, default=2, help='Number of processes to spawn.')
    parser.add_argument('--game_style', type=str, default=None,
                        help='Game style to use for the strategy. Choices are "aggressive", "air_superiority", '
                             '"immortal_archon_push", "4_base_zealot_archon", "fast_4rd_zealot_stalker".')

    original_args = parser.parse_args()
    GAME_STYLES = ["aggressive", "air_superiority", "immortal_archon_push", "4_base_zealot_archon",
                   "fast_4rd_zealot_stalker"]

    """
    random worker
    """
    # processes = []
    # for i in range(original_args.num_processes):
    #     args_copy = copy.deepcopy(original_args)
    #     args_copy.process_id = str(i)
    #     args_copy.game_style = GAME_STYLES[i % len(GAME_STYLES)]  # 轮流为每个进程分配一个game_style
    #
    #     p = multiprocessing.Process(target=random_worker, args=(args_copy,))
    #     processes.append(p)
    #     p.start()
    #
    # for p in processes:
    #     p.join()
    """
    gpt worker
    """
    processes = []
    for i in range(original_args.num_processes):
        args_copy = copy.deepcopy(original_args)
        args_copy.process_id = str(i)
        args_copy.game_style = GAME_STYLES[i % len(GAME_STYLES)]  # 轮流为每个进程分配一个game_style

        p = multiprocessing.Process(target=gpt_worker, args=(args_copy,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()
