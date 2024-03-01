from datetime import datetime

import argparse
import multiprocessing
import copy
import wandb
from sc2_rl_agent.starcraftenv_test.worker import *
from sc2_rl_agent.starcraftenv_test.utils.action_info import ActionDescriptions
from sc2_rl_agent.starcraftenv_test.config.config import LADDER_MAP_2023, DIFFICULTY_LEVELS,AI_BUILD_LEVELS

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

    parser.add_argument('--difficulty', type=str, default=DIFFICULTY_LEVELS[4],
                        help='Game difficulty level when playing against build-in AI. Only valid for single bot.')

    parser.add_argument('--player1_race', type=str, default='Zerg',
                        help='Player 1 race. Use "Protoss" or "Zerg". Only valid for two agents.')

    parser.add_argument('--player2_race', type=str, default='Protoss',
                        help='Player 2 race. Use "Protoss" or "Zerg". Only valid for two agents.')

    parser.add_argument('--process_id', type=str, default='-1', help='-1 means not multiprocess worker'
                                                                     '0-100 means multiprocess id.')
    parser.add_argument('--current_time', type=str, default=datetime.now().strftime('%Y%m%d_%H%M%S'),
                        help='Current time. Default is current system time.')
    parser.add_argument('--agent_type', type=str, default="gemini",
                        help='Agent type. Use "random" or "gemini" or "prompt1" or "gpt" or"glm-4" or "claude2","qwen_7b","APU"')

    parser.add_argument('--LLM_model_name', type=str, default="gemini-pro",help="gpt-3.5-turbo-16k,gemini-pro,glm-4")
    parser.add_argument('--LLM_temperature', type=float, default=0.1)

    parser.add_argument('--LLM_api_key', type=str, default="your-key")
    parser.add_argument('--LLM_api_base', type=str, default="your-api-base")
    parser.add_argument('--num_processes', type=int, default=1, help='Number of processes to spawn.')
    parser.add_argument('--real_time', type=bool, default=False, help='True or False')
    parser.add_argument('--ai_build', type=str, default=AI_BUILD_LEVELS[0], help='ai build level')
    original_args = parser.parse_args()


    processes = []
    for i in range(original_args.num_processes):
        args_copy = copy.deepcopy(original_args)
        args_copy.process_id = str(i)
        # 根据 agent_type 选择对应的 worker
        if args_copy.agent_type == 'random':
            target_worker = random_worker
        elif args_copy.agent_type == 'chatgpt':
            target_worker = chatgpt_worker
        elif args_copy.agent_type =='prompt1':
            target_worker=prompt1_worker
        elif args_copy.agent_type == 'gemini':
            target_worker=gemini_worker
        # elif args_copy.agent_type == 'glm-4':
        #     target_worker=glm4_worker
        # Due to package issues, we cannot use glm-4 for now
        elif args_copy.agent_type =="claude2":
            target_worker=claude2_worker
        elif args_copy.agent_type == 'qwen_7b':
            target_worker=qwen7b_worker
        elif args_copy.agent_type =="llama2_7b":
            target_worker=llama2_7b_worker
        elif args_copy.agent_type =="APU":
            target_worker=APU_worker
        # 可以在此添加更多的条件来选择其他类型的 worker
        else:
            raise ValueError(f"Unknown agent type: {args_copy.agent_type}")

        p = multiprocessing.Process(target=target_worker, args=(args_copy,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()
