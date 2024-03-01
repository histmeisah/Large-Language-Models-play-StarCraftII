from zhipuai import ZhipuAI
import os
import time
import random


class ChatBot_SingleTurn:
    """
    GeminiChatBot类，用于对话。
    调用 Google Gemini API 实现对话。
    query 方法用于对话。
    """

    def __init__(self, model_name, api_key, api_base, system_prompt, example_prompt, temperature):
        """
        初始化 GeminiChatBot 类。
        :param model_name: Gemini 模型名称。
        :param api_key: Google API 密钥。
        :param system_prompt: 系统提示。
        :param example_prompt: 例子，用于初始化对话，格式为[用户输入,机器人回复]。
        """
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.example_prompt = example_prompt
        self.client = self.apply_client()
        self.temperature = temperature

    def apply_client(self):
        client = ZhipuAI(api_key="Your-key")  # 填写您自己的APIKey
        return client

    def query(self, user_input, max_retries=5):
        """
        发送查询并获取回复。
        :param user_input: 用户输入。
        :return: Gemini 模型的回复。
        """
        # 重置 messages 列表

        # 尝试发送请求并获取回复
        for retries in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="glm-4",  # 填写需要调用的模型名称
                    messages=[
                        {'role': 'user', 'content': self.system_prompt + self.example_prompt[0]},
                        {'role': 'assistant', 'content': self.example_prompt[1]},
                        {'role': 'user', 'content': user_input}
                    ],
                    temperature=self.temperature
                )

                answer = response.choices[0].message.content
                return answer
            except Exception as e:
                # 输出错误信息
                print(f"Error when calling the GLM4 API: {e}")

                # 如果达到最大尝试次数，返回一个特定的回复
                if retries >= max_retries - 1:
                    print("Maximum number of retries reached. The Gemini API is not responding.")
                    return "I'm sorry, but I am unable to provide a response at this time due to technical difficulties."

                # 重试前等待一段时间，使用 exponential backoff 策略
                sleep_time = (2 ** retries) + random.random()
                print(f"Waiting for {sleep_time} seconds before retrying...")
                time.sleep(sleep_time)


if __name__ == '__main__':
    api_key = ""
    model_name = 'glm-4'
    system_prompt = "请按照我们需要的格式输出动作的格式"
    example_prompt = ["A kill B", "A,B,<KILL>"]
    api_base = ""
    temperature = 0.2
    gemini_bot = ChatBot_SingleTurn(model_name, api_key, api_base, system_prompt, example_prompt, temperature)

    # 进行对话查询
    user_input = "A hit B"
    response = gemini_bot.query(user_input)
    print(response)
