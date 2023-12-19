from utils.path_utils import *

start_path = r"F:\python_code\TextStarCraft2\sc2_rl_agent\starcraftenv_test\config\test_path.py"
end_path = r"F:\python_code\TextStarCraft2\sc2_rl_agent\starcraftenv_test\utils\actionvdb"
path_temp = calculate_relative_path(start=start_path, target=end_path)
print(path_temp)