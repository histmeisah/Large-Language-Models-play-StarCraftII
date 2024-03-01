from sc2_rl_agent.starcraftenv_test.env.single_agent import Text_Starcraftenv_Rule_Bot as SingleTextRule
from sc2_rl_agent.starcraftenv_test.env.single_agent import Text_Starcraftenv_Build_In_Bot as SingleTextBuildIn
from sc2_rl_agent.starcraftenv_test.env.single_agent import Text_Starcraftenv_VS_Human as SingleTextHuman

from sc2_rl_agent.starcraftenv_test.env.Agent_vs_Agent_Env import Agent_vs_Agent_Env as TwoText
from gym.vector import make


class StarCraftEnvSelector:
    """
    星际争霸2环境选择器
    SingleTextRule: 单个agent,规则对手, 文本环境,
    SingleTextBuildIn: 单个agent,内置AI对手,文本环境
    TwoText: 两个agent, 文本环境
    """

    def __init__(self, args):
        self.num_agents = args.num_agents
        self.env_type = args.env_type.lower()
        self.args = args

    def create_env(self, ):
        if self.num_agents == 'single':
            if self.env_type == 'text':
                if self.args.opposite_type == 'rule':
                    return SingleTextRule(self.args)
                elif self.args.opposite_type == 'build_in':
                    return SingleTextBuildIn(self.args)
                else:
                    raise ValueError('Invalid opposite type. Only "rule" and "build_in" are supported.')
            else:
                raise ValueError('Invalid environment type. Only "text" are supported.')
        elif self.num_agents == 'two':
            if self.env_type == 'text':
                print("test for two agent")
                return TwoText(self.args)

            else:
                raise ValueError('Invalid environment type. Only "text" are supported.')
        elif self.num_agents =="Human":
            if self.env_type == 'text':
                return SingleTextHuman(self.args)

        else:
            raise ValueError('Invalid number of agents. Only "single" and "two" are supported.')
