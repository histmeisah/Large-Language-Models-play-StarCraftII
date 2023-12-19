from env.starcraft_env import StarCraftEnvSelector
from utils.action_info import ActionDescriptions
from prompt.prompt import StarCraftIIPrompt_V4
from agent.random_agent import RandomAgent
from agent.chatgpt_agent import ChatGPTAgent
import wandb


def random_worker(input_args):
    """
    为多进程定义的工作函数
    """
    # 使用args中的设置创建环境
    args = input_args

    selector = StarCraftEnvSelector(args)
    env = selector.create_env()

    action_description = ActionDescriptions(env.player_race)
    action_dict = action_description.action_descriptions

    # 假设这些参数和设置对于random agent仍然有用
    sc2prompt = StarCraftIIPrompt_V4(race=args.player_race, K="5", action_dict=action_dict, game_style=args.game_style)
    system_prompt, example_input_prompt, example_output_prompt = sc2prompt.generate_prompts()
    example_prompt = [example_input_prompt, example_output_prompt]

    # 创建并测试random agent
    random_agent = RandomAgent(model_name=args.LLM_model_name, api_key=args.LLM_api_key,
                               api_base=args.LLM_api_base, system_prompt=system_prompt,
                               temperature=args.LLM_temperature, example_prompt=example_prompt,
                               args=args, action_description=action_description)
    random_agent_test(random_agent, env)


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


def gpt_worker(input_args):
    """
    为多进程定义的工作函数
    """
    # 使用args中的设置创建环境
    args = input_args

    selector = StarCraftEnvSelector(args)
    env = selector.create_env()

    action_description = ActionDescriptions(env.player_race)
    action_dict = action_description.action_descriptions

    # 假设这些参数和设置对于random agent仍然有用
    sc2prompt = StarCraftIIPrompt_V4(race=args.player_race, K="5", action_dict=action_dict, game_style=args.game_style)
    system_prompt, example_input_prompt, example_output_prompt = sc2prompt.generate_prompts()
    example_input_prompt.format(K_1=4)
    example_prompt = [example_input_prompt, example_output_prompt]

    # 创建并测试random agent
    gpt_agent = ChatGPTAgent(model_name=args.LLM_model_name, api_key=args.LLM_api_key,
                             api_base=args.LLM_api_base, system_prompt=system_prompt,
                             temperature=args.LLM_temperature, example_prompt=example_prompt,
                             args=args, action_description=action_description)
    gpt_agent_test(gpt_agent, env, args=args)


def gpt_agent_test(agent, env, args):
    wandb.login(key='a51e8268ce285c7e63ccc7a6d685e6ea85c48101')
    config = {
        "LLM_model_name": "gpt-3.5-turbo-16k",
        "LLM_temperature": 0,
        "action_interval": 10,
        "request_delay": 0.2,
        "chunk_window": 5,
        "action_window": 10,
        "action_mix_rate": 0.5,
        "last_k": 5,
        "game_style": args.game_style,
    }
    process_id = args.process_id
    wandb.init(project=f"TextStarCraft2_{process_id}_{args.game_style}", config=config)
    observation, _ = env.reset()  # Get initial L1_observation
    done = False

    while not done:
        action = agent.action(observation)
        observation, reward, done, result, info = env.step(action)

        if done:
            break
