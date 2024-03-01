from sc2_rl_agent.starcraftenv_test.agent.chatgpt_agent import ChatGPTAgent
from sc2_rl_agent.starcraftenv_test.agent.random_agent import RandomAgent
from sc2_rl_agent.starcraftenv_test.agent.llama2_agent import Llama2Agent
from sc2_rl_agent.starcraftenv_test.agent.glm2_agent import Glm2Agent

# Agent type to class mapping
AGENT_TYPE_TO_CLASS = {
    "gpt": ChatGPTAgent,
    "random": RandomAgent,
    "llama2": Llama2Agent,
    "glm2": Glm2Agent
}

# Agent config: set the agent parameters here
AGENT_CONFIG = {
    "llama2": {
        "LLM_model_name": "llama2",
        "project": "TextStarCraft2",
        "LLM_api_key ": "sk-kgD6PtwccvSxXAoH1aF84a227a9848348bC6C26eA5A9F827",
        "LLM_api_base": "https://api.wzunjh.top/v1",
        "LLM_temperature": 0,
        "action_interval": 10,
        "request_delay": 0.2,
        "chunk_window": 5,
        "action_window": 10,
        "action_mix_rate": 0.5,
        "last_k": 5
    },
    "glm2": {
        "LLM_model_name": "llama2",
        "project": "glm2_TextStarCraft2",
        "LLM_api_key ": "sk-kgD6PtwccvSxXAoH1aF84a227a9848348bC6C26eA5A9F827",
        "LLM_api_base": "https://api.wzunjh.top/v1",
        "LLM_temperature": 0,
        "action_interval": 10,
        "request_delay": 0.2,
        "chunk_window": 5,
        "action_window": 10,
        "action_mix_rate": 0.5,
        "last_k": 5
    },
    "gpt": {
        "LLM_model_name": "gpt-3.5-turbo-16k",  # gpt-3.5-turbo-16k,gpt-4
        "project": "TextStarCraft2",
        "LLM_api_key": "sk-kgD6PtwccvSxXAoH1aF84a227a9848348bC6C26eA5A9F827",
        "LLM_api_base": "https://api.wzunjh.top/v1",
        "LLM_temperature": 0,
        "action_interval": 10,
        "request_delay": 0.2,
        "chunk_window": 5,
        "action_window": 10,
        "action_mix_rate": 0.5,
        "last_k": 5
    },
    "random": {
        "LLM_model_name": "gpt-3.5-turbo",  # random just copy the gpt
        "project": "TextStarCraft2",
        "LLM_api_key ": "sk-kgD6PtwccvSxXAoH1aF84a227a9848348bC6C26eA5A9F827",
        "LLM_api_base": "https://api.wzunjh.top/v1",
        "LLM_temperature": 0,
        "action_interval": 10,
        "request_delay": 0.2,
        "chunk_window": 5,
        "action_window": 10,
        "action_mix_rate": 0.5,
        "last_k": 5
    },
}
