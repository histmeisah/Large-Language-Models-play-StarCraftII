# Large Language Models Play StarCraft II: Benchmarks and A Chain of Summarization Approach
![VYY 5IX JX3 H)`N$_B}@L](https://github.com/histmeisah/Large-Language-Models-play-StarCraftII/assets/49554454/59a941fa-bd71-4145-b99e-3a971aa93790)

## Install StarCraft II and setup maps

### Install StarCraft II
StatCraft II is a classic game developed by BLZ, and has some professional leagues such as IEM, WTL....You can download Battle.net from:https://us.shop.battle.net/en-us, or here:https://www.blizzard.com/zh-tw/

If you are Chinese, due to the Bobby Kotick, CN play cant own their sever again. So we must download StarCraft II by this video :https://www.bilibili.com/video/BV1As4y147NP/?buvid=XY6E01868C47C929FEFCE4A6DBF0A4ECFFB64&is_story_h5=false&mid=y0%2Bkb3rZVEwQ9j34NFXkLA%3D%3D&p=1&plat_id=114&share_from=ugc&share_medium=android&share_plat=android&share_session_id=2e6181cb-fa27-4ce1-9b2e-f126f39267d5&share_source=COPY&share_tag=s_i&timestamp=1674580642&unique_k=rPeGgmE&up_id=149681985&vd_source=0553fe84b5ad759606360b9f2e687a01
or you can search in the internet.

### Download maps
First , we should use StarCraft II Editor.exe to download the newest ladder map
![217539085-d14f0177-33a4-42f1-ac7d-ac9f61ad29f2](https://github.com/histmeisah/Large-Language-Models-play-StarCraftII/assets/49554454/095023ec-497b-4510-889e-6166f6cfb57d)

when we open this, please log in your blz account and search the map which you want.
![217540537-db80aca9-aec7-4d30-b4f9-f4dc818a1697](https://github.com/histmeisah/Large-Language-Models-play-StarCraftII/assets/49554454/8f68af70-d877-47cc-8d36-8240c7645900)
Then you should put maps to your StarCrafrt2 file  in StarCraft II\Maps(If the 'Maps' file dont exist, please create it).

Or you can download maps in here:
![1703001254300](https://github.com/histmeisah/Large-Language-Models-play-StarCraftII/assets/49554454/69f89739-6bfe-417b-96df-afcb7f7756f3)


## Setup environment

### Create environment

- `python`: python 3.10.
- `cuda`: cuda 12.1.
- `torch`: 2.1.0
- `openai`: 0.27.9, very important. The openai version must <= 0.28(they change the api port)
- pip install -r requirements.txt

### Tips
- `burnysc2`:This is our core package that provide an easy api for use to create this project. Here is: https://github.com/BurnySc2/python-sc2
- `chromadb`:We used the vector datavase chroma.Due to the package conflict, **you must install Chromadb first, then install burnysc2.**
- `Huggingface` and `sentence-transformers`:we used the embedding model  `sentence-transformers/all-mpnet-base-v2`, in our github version, it will automatically download.We also provide the `release` zip, you can just download and unzip that(with embedding model). 

## Run demo
TODO

