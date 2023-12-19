from utils.path_utils import *
start = r"F:\python_code\TextStarCraft2\sc2_rl_agent\starcraftenv_test\agent\chatgpt_agent.py"
target = r"F:\python_code\TextStarCraft2\sc2_rl_agent\utils\actionvdb\action_vdb"
path_result = calculate_relative_path(start=start,target=target)
print(path_result)