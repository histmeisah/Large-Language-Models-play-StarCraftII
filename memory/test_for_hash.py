import hashlib
import timeit

text = "1. Game Overview: At 00:00 game time, our current situation is in the very early stages of the game. We have 12 workers, 50 minerals, and a supply cap of 15 with 3 supply left. We have established one base.\n\n2. Current Game Stage: Based on the limited resources and lack of information about the enemy, we are in the early game stage.\n\n3. Our Situation:\n    3.1 Units and Buildings: We have a small worker force and only one base. No other units or buildings have been mentioned.\n    3.2 Economy: Our economy is just starting, with minimal resources available. We need to focus on expanding our resource collection.\n    3.3 Technology: There is no information about our technological research or unlocked technologies.\n\n4. Our Strategy: In the early game, our strategy should be centered around resource gathering, base expansion, and scouting to gather information about the enemy's strategy.\n\n5. Enemy's Strategy: Since there is no information about enemy units, we cannot infer their strategy at this point.\n\n6. Key Information: The most important aspect at this stage is to quickly establish additional bases and increase our worker count to boost resource collection. Scouting is also crucial to gather information about the enemy's strategy.\n\nSuggestions:\n\n1. Our Strategy: Focus on expanding our economy by training more workers and establishing additional bases. Prioritize scouting to gather information about the enemy's strategy.\n\n2. Units and Buildings: Train more workers to increase resource collection. Consider building additional bases to expand our economy.\n\n3. Economy: Efficiently gather resources by assigning workers to mine minerals and gas. Expand to new resource locations to increase our income.\n\n4. Technology: In the early game, it is essential to prioritize resource gathering and base expansion over technological research. However, consider building a Cybernetics Core to unlock more advanced units and technologies in the future.\n\nDecisions:\n0: <TRAIN PROBE>\n1: <BUILD NEXUS>\n2: <BUILD ASSIMILATOR>\n3: <SCOUTING PROBE>\n4: <CHRONOBOOST NEXUS>"  # 替换为您的文本

def calculate_hash():
    return hashlib.md5(text.encode('utf-8')).hexdigest()



def sha256_hash() -> str:
    sha256 = hashlib.sha256()
    sha256.update(text.encode('utf-8'))
    return sha256.hexdigest()

hash_value = sha256_hash()
execution_time = timeit.timeit(sha256_hash, number=1000)  # 运行1000次以获得可靠的测量结果
print(f"Average execution time: {execution_time / 1000:.10f} seconds")
# Average execution time: 0.0000000000 seconds

