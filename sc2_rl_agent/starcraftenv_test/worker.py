from sc2_rl_agent.starcraftenv_test.env.starcraft_env import StarCraftEnvSelector
from sc2_rl_agent.starcraftenv_test.utils.action_info import ActionDescriptions
from sc2_rl_agent.starcraftenv_test.prompt.prompt import *
from sc2_rl_agent.starcraftenv_test.agent.random_agent import RandomAgent
from sc2_rl_agent.starcraftenv_test.agent.chatgpt_agent import ChatGPTAgent
from sc2_rl_agent.starcraftenv_test.agent.prompt1_agent import Prompt1_Agent
from sc2_rl_agent.starcraftenv_test.agent.gemini_agent import GeminiAgent
# from sc2_rl_agent.starcraftenv_test.agent.glm4_agent import Glm4Agent
from sc2_rl_agent.starcraftenv_test.agent.claude2_agent import Claude2Agent
from sc2_rl_agent.starcraftenv_test.agent.qwen_7b_agent import Qwen7bAgent
from sc2_rl_agent.starcraftenv_test.agent.llama2_agent import Llama2_Agent
from sc2_rl_agent.starcraftenv_test.agent.APU_agent import APUAgent

def agent_test(agent, env, args=None):
    """
    通用的代理测试函数
    """
    # 如果args中包含特定于代理的设置或参数，可以在这里使用
    if args is not None:
        process_id = args.process_id
        # 如果需要，可以在这里使用process_id

    observation, _ = env.reset()  # 获取初始观察
    done = False

    while not done:
        action = agent.action(observation)
        observation, reward, done, result, info = env.step(action)

        if done:
            break


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
    sc2prompt = StarCraftIIPrompt_V4(race=args.player_race, K="5", action_dict=action_dict)
    system_prompt, example_input_prompt, example_output_prompt = sc2prompt.generate_prompts()
    example_prompt = [example_input_prompt, example_output_prompt]

    # 创建并测试random agent
    random_agent = RandomAgent(model_name=args.LLM_model_name, api_key=args.LLM_api_key,
                               api_base=args.LLM_api_base, system_prompt=system_prompt,
                               temperature=args.LLM_temperature, example_prompt=example_prompt,
                               args=args, action_description=action_description)
    agent_test(random_agent, env)




def chatgpt_worker(input_args):
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
    # sc2prompt = StarCraftIIPrompt_old(race=args.player_race, K="5", action_dict=action_dict)# prompt version old 旧版prompt
    sc2prompt = StarCraftIIPrompt_V4(race=args.player_race, K="5", action_dict=action_dict)# prompt version 4
    system_prompt, example_input_prompt, example_output_prompt = sc2prompt.generate_prompts()
    example_input_prompt.format(K_1=4)
    example_prompt = [example_input_prompt, example_output_prompt]

    # 创建并测试chatgpt agent
    gpt_agent = ChatGPTAgent(model_name=args.LLM_model_name, api_key=args.LLM_api_key,
                             api_base=args.LLM_api_base, system_prompt=system_prompt,
                             temperature=args.LLM_temperature, example_prompt=example_prompt,
                             args=args, action_description=action_description)
    agent_test(gpt_agent, env, args=args)



def prompt1_worker(input_args):
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
    sc2prompt = StarCraftIIPrompt_old(race=args.player_race, K="5", action_dict=action_dict)  # old prompt

    system_prompt, example_input_prompt, example_output_prompt = sc2prompt.generate_prompts()
    example_input_prompt.format(K_1=4)
    example_prompt = [example_input_prompt, example_output_prompt]

    # 创建并测试random agent
    gpt_agent = Prompt1_Agent(model_name=args.LLM_model_name, api_key=args.LLM_api_key,
                              api_base=args.LLM_api_base, system_prompt=system_prompt,
                              temperature=args.LLM_temperature, example_prompt=example_prompt,
                              args=args, action_description=action_description)
    agent_test(gpt_agent, env, args=args)


def gemini_worker(input_args):
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
    sc2prompt = StarCraftIIPrompt_V4(race=args.player_race, K="5", action_dict=action_dict)  # prompt v4


    system_prompt, example_input_prompt, example_output_prompt = sc2prompt.generate_prompts()
    example_input_prompt.format(K_1=4)
    example_prompt = [example_input_prompt, example_output_prompt]

    # 创建并测试random agent
    gemini_agent = GeminiAgent(model_name=args.LLM_model_name, api_key=args.LLM_api_key,
                             api_base=args.LLM_api_base, system_prompt=system_prompt,
                             temperature=args.LLM_temperature, example_prompt=example_prompt,
                             args=args, action_description=action_description)
    agent_test(gemini_agent, env, args=args)

"""
Due to package version issues, the following agents are not available for testing.
"""
# def glm4_worker(input_args):
#     """
#     为多进程定义的工作函数
#     """
#     # 使用args中的设置创建环境
#     args = input_args
#
#     selector = StarCraftEnvSelector(args)
#     env = selector.create_env()
#
#     action_description = ActionDescriptions(env.player_race)
#     action_dict = action_description.action_descriptions
#
#     # 假设这些参数和设置对于random agent仍然有用
#     sc2prompt = StarCraftIIPrompt_V4(race=args.player_race, K="5", action_dict=action_dict)  # prompt v4
#
#
#     system_prompt, example_input_prompt, example_output_prompt = sc2prompt.generate_prompts()
#     example_input_prompt.format(K_1=4)
#     example_prompt = [example_input_prompt, example_output_prompt]
#
#     # 创建并测试random agent
#     glm4_agent = Glm4Agent(model_name=args.LLM_model_name, api_key=args.LLM_api_key,
#                              api_base=args.LLM_api_base, system_prompt=system_prompt,
#                              temperature=args.LLM_temperature, example_prompt=example_prompt,
#                              args=args, action_description=action_description)
#     agent_test(glm4_agent, env, args=args)


def claude2_worker(input_args):
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
    sc2prompt = StarCraftIIPrompt_V4(race=args.player_race, K="5", action_dict=action_dict)  # prompt v4


    system_prompt, example_input_prompt, example_output_prompt = sc2prompt.generate_prompts()
    example_input_prompt.format(K_1=4)
    example_prompt = [example_input_prompt, example_output_prompt]

    # 创建并测试random agent
    claude2_agent = Claude2Agent(model_name=args.LLM_model_name, api_key=args.LLM_api_key,
                             api_base=args.LLM_api_base, system_prompt=system_prompt,
                             temperature=args.LLM_temperature, example_prompt=example_prompt,
                             args=args, action_description=action_description)
    agent_test(claude2_agent, env, args=args)

def qwen7b_worker(input_args):
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
    sc2prompt = StarCraftIIPrompt_V4(race=args.player_race, K="5", action_dict=action_dict)  # prompt v4


    system_prompt, example_input_prompt, example_output_prompt = sc2prompt.generate_prompts()
    example_input_prompt.format(K_1=4)
    example_prompt = [example_input_prompt, example_output_prompt]

    # 创建并测试random agent
    qwen7b_agent = Qwen7bAgent(model_name=args.LLM_model_name, api_key=args.LLM_api_key,
                             api_base=args.LLM_api_base, system_prompt=system_prompt,
                             temperature=args.LLM_temperature, example_prompt=example_prompt,
                             args=args, action_description=action_description)
    agent_test(qwen7b_agent, env, args=args)

def llama2_7b_worker(input_args):
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
    sc2prompt = StarCraftIIPrompt_V4(race=args.player_race, K="5", action_dict=action_dict)  # prompt v4


    system_prompt, example_input_prompt, example_output_prompt = sc2prompt.generate_prompts()
    example_input_prompt.format(K_1=4)
    example_prompt = [example_input_prompt, example_output_prompt]

    # 创建并测试random agent
    llama2_agent = Llama2_Agent(model_name=args.LLM_model_name, api_key=args.LLM_api_key,
                             api_base=args.LLM_api_base, system_prompt=system_prompt,
                             temperature=args.LLM_temperature, example_prompt=example_prompt,
                             args=args, action_description=action_description)
    agent_test(llama2_agent, env, args=args)


def APU_worker(input_args):
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
    sc2prompt = StarCraftIIPrompt_V4(race=args.player_race, K="5", action_dict=action_dict)  # prompt v4


    system_prompt, example_input_prompt, example_output_prompt = sc2prompt.generate_prompts()
    example_input_prompt.format(K_1=4)
    example_prompt = [example_input_prompt, example_output_prompt]

    # 创建并测试random agent
    apu_agent = APUAgent(model_name=args.LLM_model_name, api_key=args.LLM_api_key,
                             api_base=args.LLM_api_base, system_prompt=system_prompt,
                             temperature=args.LLM_temperature, example_prompt=example_prompt,
                             args=args, action_description=action_description)
    agent_test(apu_agent, env, args=args)