# Large Language Models Play StarCraft II: Benchmarks and A Chain of Summarization Approach
![VYY 5IX JX3 H)`N$_B}@L](https://github.com/histmeisah/Large-Language-Models-play-StarCraftII/assets/49554454/59a941fa-bd71-4145-b99e-3a971aa93790)
StarCraft II is a challenging benchmark for AI agents due to  micro-level operations and macro-awareness. Previous works,  such as Alphastar and SCC, achieve impressive performance on tackling StarCraft
II , however, still exhibit deficiencies in long-term strategic planning and strategy interpretability. Emerging large language model (LLM) agents, presents the immense potential in solving intricate tasks. 

Motivated by this, we aim to validate the capabilities of LLMs on StarCraft II.  We first develop textual StratCraft II environment, called TextStarCraft II. Secondly, we propose a Chain of Summarization
method, including single-frame summarization for processing raw observations and multi-frame summarization for analyzing game information, providing command recommendations, and generating strategic decisions. Our experiment demonstrates that LLM agents are capable of defeating the built-in AI at the Harder(Lv5) difficulty level. 


|  Work        |         AlphaStar     | SCC          | HierNet-SC2         |AlphaStar Unplugged |  ROA-Star|Ours |
|-----------------------|--------------|-----------------|---------------------|---------------|-------------|--------------|
|Method                 |SL+RL+self-play  | SL+RL+self-play  | data-mining + RL|offline RL |  SL+RL+self-play   |prompt + Rule base script|     
| Compute resource      | 12000 CPU cores, 384 TPUs| Linear     | 4 GPUs,48 CPU cores|not clear|2x 64 v100 |1 gpu,1 cpu(home computer)|
|Required replay        |971,000 | 4,638     |608|20,000,000(20m)| 120938 |0 |
|Best result(The greatest opponent ever to win)|Serral(One of the best progamer in the world)|Time(IEM2023 Champion)|build-in ai lv-10|AlphaStar BC agent|hero(GSL Champion)|build-in ai lv-5| 
|Strategy Interpretability|&#x2716;|&#x2716;|&#x2716;|&#x2716;|&#x2716;|&#x2714;|
|Expansibility(adapt to latest game version and other race ) |&#x2716;|&#x2716;|&#x2716;|&#x2716;|&#x2716;|&#x2714;|

Our paper: 

Large Language Models Play StarCraft II: Benchmarks and A Chain of Summarization Approach 
[https://arxiv.org/abs/2312.11865](https://arxiv.org/abs/2312.11865)

Our website:

[Large Language Models Play StarCraft II: Benchmarks and A Chain of Summarization Approach 
](https://sites.google.com/view/textstarcraft2/%E9%A6%96%E9%A1%B5)

Our demo video:

[Large Language Models Play StarCraft II: Benchmarks and A Chain of Summarization Approach 
](https://www.youtube.com/watch?v=Iz6Hd917eME&list=PL2vvP3CXffZxrjxSjVAL7QXNFqNq96mcy)

## Install StarCraft II and setup maps

### Install StarCraft II
StatCraft II is a classic game developed by BLZ, and has some professional leagues such as IEM, WTL....You can download Battle.net from:https://us.shop.battle.net/en-us, or here:https://www.blizzard.com/zh-tw/

If you are Chinese, due to the Bobby Kotick, CN play cant own their sever again. So we must download StarCraft II by this video :[video](https://www.bilibili.com/video/BV1As4y147NP/?buvid=XY6E01868C47C929FEFCE4A6DBF0A4ECFFB64&is_story_h5=false&mid=y0%2Bkb3rZVEwQ9j34NFXkLA%3D%3D&p=1&plat_id=114&share_from=ugc&share_medium=android&share_plat=android&share_session_id=2e6181cb-fa27-4ce1-9b2e-f126f39267d5&share_source=COPY&share_tag=s_i&timestamp=1674580642&unique_k=rPeGgmE&up_id=149681985&vd_source=0553fe84b5ad759606360b9f2e687a01)
or you can search in the internet.

### Download maps
First , we should use StarCraft II Editor.exe to download the newest ladder map
![217539085-d14f0177-33a4-42f1-ac7d-ac9f61ad29f2](https://github.com/histmeisah/Large-Language-Models-play-StarCraftII/assets/49554454/095023ec-497b-4510-889e-6166f6cfb57d)

when we open this, please log in your blz account and search the map which you want.
![217540537-db80aca9-aec7-4d30-b4f9-f4dc818a1697](https://github.com/histmeisah/Large-Language-Models-play-StarCraftII/assets/49554454/8f68af70-d877-47cc-8d36-8240c7645900)
Then you should put maps to your StarCrafrt2 file  in StarCraft II\Maps(If the 'Maps' file dont exist, please create it).

Or you can download maps in here:
![image](https://github.com/histmeisah/Large-Language-Models-play-StarCraftII/assets/49554454/630c1f87-6762-4f23-be90-bd57238187ed)



## Setup environment

### Create environment

- `python`: python 3.10.
- `cuda`: cuda 12.1.
- `torch`: 2.1.0
- `openai`: 0.27.9, very important. This is crucial as versions above 0.28 have altered API functionalities.
Install all necessary packages with `pip install -r requirements.txt`.


### Tips
- `burnysc2`: This is our core package, offering an easy-to-use API for project development. Find more information here:[Python-sc2](https://github.com/BurnySc2/python-sc2)
- `chromadb`: We utilize the Chroma vector database. Due to package conflicts, **install Chromadb first, followed by burnysc2.**
- `Huggingface` and `sentence-transformers`: we used the embedding model  `sentence-transformers/all-mpnet-base-v2`, in our github version, it will automatically download. We also provide the `release` zip, you can just download and unzip that(with embedding model). 

## Run demo

### Single process
You can run `test_the_env.py` to try our agent. Here is some parameters you need to set.

- `player_race`: Currently, only `Protoss` is supported. `Zerg` and `Terran` are under development.
- `opposite_race`: Typically set to `Zerg`, but `Terran` and `Protoss` are also compatible.
- `difficulty`: We offer 10 difficulty levels, ranging from Level 1 (`VeryEasy`) to Level 10 (`CheatInsane`). Note that these names differ from those in the StarCraft2 client, but the AI difficulty remains unchanged.

|       Level   |         1     | 2          | 3         |4 |  5|6 |7|8|9|10|
|       ------   |    -------   |-------  | -------  |------ | -------|--------|-----|-----|-------|-----------|
|  BLZ difficulty|     VeryEasy  | Easy | Medium|Hard|Harder|Very Hard |Elite|CheatVision|CheatMoney|CheatInsane|
| python-sc2 difficulty|    VeryEasy   |Easy | Medium  |MediumHard | Hard|Harder|VeryHard|CheatVision|CheatMoney|CheatInsane|

- `replay_folder`: Specify the folder for saving demo replays.
- `LLM_model_name`: We used `gpt-3.5-turbo-16k` in our experiments.
- `LLM_temperature`: Set between 0 and 1 as per your preference.
- `LLM_api_key`: Your API key.
- `LLM_api_base`: Your API base URL.

Note: Using LLM to play StarCraft2 can take approximately 7 hours for a single game.

### Multi process
To save time, you can run multiple demos simultaneously using `multiprocess_test.py`. Configure the following parameter:
- `num_processes`: The number of processes to spawn.

Other parameters are the same as in the Single Process setup.

### Other settings
In our experiments, we have added some more settings, but due to several reasons these settings will coming soon.

- `num_agents` : This environment will support `LLM agent` vs `LLM agent` or `RL agent`.
- `env_type`: This environment will support Text or MultiModal
- 'player_race': This environment will support Zerg and Terran
- `opposite_type`: This env will support some human designed botai.



## Create your LLM Agent
If you want to use other llm to create your own llm agent, the following things you should to know.

### Component of LLM Agent
- `LLM`: In our repo, you should request llm from `ChatBot_SingleTurn` function in `TextStarCraft2_2/LLM/gpt_test` 
- 'L1_summarize': Our level-1 summarization method is here: `generate_summarize_L1` in `TextStarCraft2_2/summarize/L1_summarize.py` 
- `L2_summarize`: Our level-2 summarization method is here : `L2_summary` in `TextStarCraft2_2/summarize/gpt_test/L2_summarize.py`
- `action dict`: The actions that llm agent can use. Here we can set `TextStarCraft2_2/utils/action_info.py` . You can add more actions for llm agent. 
- `action extractor` : We can extract decisions by `TextStarCraft2_2/utils/action_extractor.py`

### Env
The core of our TextStarCraft II env is `TextStarCraft2_2/env/bot`. Here you can add more settings for environment. So if you want to realise Terran and Zerg bot, you can modify our code about this dictionary.

- `State`: In `Protoss_bot.py`, the State of Env is generate from `get_information` function. This is what we said `Obs to Text adaptor`
- `Action`: In `Protoss_bot.py`, the Action space of Agent is designed by these `handle_action` function. This is what we said `Text to Action adaptor`.

 





