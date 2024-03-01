import multiprocessing

from sc2 import maps
from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer

from hydra_ling_bane import hydra_ling_bane_bot

laddermap_2023 = ['Altitude LE', 'Ancient Cistern LE', 'Babylon LE', 'Dragon Scales LE', 'Gresvan LE',
                  'Neohumanity LE', 'Royal Blood LE']
def run_bot(index):
    print(f"Running bot {index}")
    run_game(
        maps.get(laddermap_2023[index]),
        [Bot(Race.Zerg, hydra_ling_bane_bot()), Computer(Race.Terran, Difficulty.Hard)],
        realtime=False,
        save_replay_as=f'massive_lings_{index}.SC2Replay',
    )

if __name__ == "__main__":
    processes = []
    for i in range(4):  # Create 4 processes
        p = multiprocessing.Process(target=run_bot, args=(i,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()