import google.generativeai as genai
import os
import time
import json
import random


class GeminiChatBot:
    """
    GeminiChatBot类，用于对话。
    调用 Google Gemini API 实现对话。
    query 方法用于对话。
    """

    def __init__(self, model_name, api_key, api_base, system_prompt, example_prompt, temperature, game_folder=None):
        """
        初始化 GeminiChatBot 类。
        :param model_name: Gemini 模型名称。
        :param api_key: Google API 密钥。
        :param proxy: 代理设置。
        :param system_prompt: 系统提示。
        :param example_prompt: 例子，用于初始化对话，格式为[用户输入,机器人回复]。
        """
        self.model_name = model_name
        self.proxy = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
        self.configure_api(api_key, self.proxy)
        self.system_prompt = system_prompt
        self.example_prompt = example_prompt
        self.model = genai.GenerativeModel(model_name)
        self.temperature = temperature
        self.game_folder = game_folder


    def configure_api(self, api_key, proxy):
        """
        配置 API 密钥和代理。
        """
        os.environ["HTTP_PROXY"] = proxy["http"]
        os.environ["HTTPS_PROXY"] = proxy["https"]
        genai.configure(api_key="your-api-key")

    def _LLM_log_to_file(self, messages, response):
        """
        保存日志信息到文件，包括发送给LLM的信息和LLM的回复。
        :param messages: 发送给LLM的消息列表。
        :param response: LLM的回复。
        :return: None
        """
        if self.game_folder is not None:
            log_data = {
                "messages": messages,
                "response": response
            }
            filename = "gemini_pro_log.jsonl"
            full_path = os.path.join(self.game_folder, filename)
            with open(full_path, "a", encoding='utf-8') as file:
                # 使用 ensure_ascii=False 来保存可读的文本
                json.dump(log_data, file, ensure_ascii=False)
                file.write("\n")

    def query(self, user_input, max_retries=5):
        """
        发送查询并获取回复。
        :param user_input: 用户输入。
        :param max_retries: 最大重试次数。
        :return: Gemini 模型的回复。
        """
        messages = [
            {'role': 'user', 'parts': [self.system_prompt + self.example_prompt[0]]},
            {'role': 'model', 'parts': [self.example_prompt[1]]},
            {'role': 'user', 'parts': [user_input]}
        ]

        print("User input:", user_input)
        for retries in range(max_retries):
            try:
                response = self.model.generate_content(messages, generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature)
                                                       )
                answer = response.text

                # 更新日志保存逻辑，包括完整的对话上下文和LLM的回复
                self._LLM_log_to_file(messages, {"text": answer})

                return answer
            except Exception as e:
                print(f"Error when calling the Gemini API: {e}")
                if retries >= max_retries - 1:
                    print("Maximum number of retries reached. The Gemini API is not responding.")
                    return "I'm sorry, but I am unable to provide a response at this time due to technical difficulties."
                sleep_time = (2 ** retries) + random.random()
                print(f"Waiting for {sleep_time} seconds before retrying...")
                time.sleep(sleep_time)


# 使用示例
if __name__ == '__main__':
    api_key = "Your-api-key"
    model_name = 'gemini-pro'
    system_prompt = "请按照我们需要的格式输出动作的格式"
    example_prompt = ["A kill B", "A,B,<KILL>"]
    api_base = ""
    temperature = 1.0
    game_folder = None
    gemini_bot = GeminiChatBot(model_name, api_key, api_base, system_prompt, example_prompt, temperature, game_folder)

    # 进行对话查询
    user_input = "A hit B"
    response = gemini_bot.query(user_input)
    print(response)

