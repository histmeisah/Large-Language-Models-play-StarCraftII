from sc2_rl_agent.starcraftenv_test.prompt.level_one_prompt import system_prompt, example_input_prompt_1, \
    example_output_prompt_1
from sc2_rl_agent.starcraftenv_test.LLM.gpt_test import ChatBot_SingleTurn


class L1_LLM_version:
    def __init__(self, api_key, api_base, temperture):
        self.system_prompt = system_prompt
        self.example_input_prompt = example_input_prompt_1
        self.example_output_prompt = example_output_prompt_1
        self.example_prompt = [self.example_input_prompt, self.example_output_prompt]
        self.LLM_model_name = "gpt-3.5-turbo-16k"
        self.LLM_temperature = 0.1
        self.chatbot = ChatBot_SingleTurn(model_name=self.LLM_model_name, api_key=api_key, api_base=api_base,
                                          system_prompt=system_prompt, example_prompt=self.example_prompt,
                                          temperature=temperture)

    def query(self, user_input):
        return self.chatbot.query(user_input)