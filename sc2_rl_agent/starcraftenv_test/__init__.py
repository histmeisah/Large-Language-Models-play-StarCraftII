from gym.envs.registration import register
register(
    id='StarCraftSingleTextRule-v0',
    entry_point='sc2_rl_agent.starcraftenv_test.env.single_agent:Text_Starcraftenv_Rule_Bot',
)

register(
    id='StarCraftSingleTextBuildIn-v0',
    entry_point='sc2_rl_agent.starcraftenv_test.env.single_agent:Text_Starcraftenv_Build_In_Bot',
)

register(
    id='StarCraftTwoText-v0',
    entry_point='sc2_rl_agent.starcraftenv_test.env.two_agents:Text_STARCRAFTENV_2',
)


