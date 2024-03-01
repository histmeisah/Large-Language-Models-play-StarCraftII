import openai
from typing import List, Dict, Any, Tuple
import os
import time
import random


# os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
# os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

class ChatBot_MultiTurn:
    """
    ChatBot类,用于对话
    调用openai的ChatCompletion接口,实现对话
    query方法用于对话
    """

    def __init__(self, model_name, api_key, api_base, temperature, system_prompt, example):
        """
        __init__方法,初始化ChatBot类
        :param model_name: 模型名称
        :param key: openai的api_key
        :param system_prompt: 系统提示语
        :param example: 例子,用于初始化对话,格式为[用户输入,机器人回复]

        """
        self.model_name = model_name
        self.temperature = temperature
        openai.api_key = api_key
        openai.api_base = api_base
        self.messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": example[0]},
            {"role": "assistant", "content": example[1]},
        ]

    def query(self, user_input):
        """
        query方法,用于对话
        :param user_input: 用户输入
        :return: 机器人回复


        """
        self.messages.append({"role": "user", "content": user_input})
        output = openai.ChatCompletion.create(
            model=self.model_name,
            messages=self.messages,
            temperature=self.temperature,
        )
        total_tokens = output["usage"]["total_tokens"]
        # 获取对话的总token数,用于判断对话是否结束
        if total_tokens > 4000:
            # Reset the conversation when the token limit is near.
            self.messages = self.messages[:3]
            return "Sorry, the conversation was too long and has been reset."
            # 当对话token数超过4000时,重置对话
        answer = output["choices"][0]["message"]["content"]
        # 获取机器人回复
        self.messages.append({"role": "assistant", "content": answer})
        # 将机器人回复添加到对话中
        return answer


class ChatBot_SingleTurn:
    """
    ChatBot类,用于对话
    调用openai的ChatCompletion接口,实现对话
    query方法用于对话
    """

    def __init__(self, model_name, api_key, api_base, system_prompt, example_prompt, temperature):
        """
        __init__方法,初始化ChatBot类
        :param model_name: 模型名称
        :param key: openai的api_key
        :param system_prompt: 系统提示语
        :param example: 例子,用于初始化对话,格式为[用户输入,机器人回复]

        """
        self.model_name = model_name
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.example = example_prompt

        openai.api_key = api_key
        openai.api_base = api_base
        self.messages = []

    def query(self, user_input, max_retries=5):
        """
        query方法,用于对话
        :param user_input: 用户输入
        :return: 机器人回复
        """

        # 重置 messages 列表
        self.messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.example[0]},
            {"role": "assistant", "content": self.example[1]},
        ]
        self.messages.append({"role": "user", "content": user_input})

        # 尝试发送请求并获取回复
        for retries in range(max_retries):
            try:
                output = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=self.messages,
                    temperature=self.temperature
                )
                answer = output["choices"][0]["message"]["content"]
                return answer
            except Exception as e:
                # 输出错误信息
                print(f"Error when calling the OpenAI API: {e}")

                # 如果达到最大尝试次数，返回一个特定的回复
                if retries >= max_retries - 1:
                    print("Maximum number of retries reached. The OpenAI API is not responding.")
                    return "I'm sorry, but I am unable to provide a response at this time due to technical difficulties."

                # 重试前等待一段时间，使用 exponential backoff 策略
                sleep_time = (2 ** retries) + random.random()
                print(f"Waiting for {sleep_time} seconds before retrying...")
                time.sleep(sleep_time)


if __name__ == '__main__':
    system_prompt = "You are a helpful assistant"
    example_prompt = ["Hello, who are you?", "I am a helpful assistant"]
    chat_bot = ChatBot_SingleTurn(model_name="gpt-4", api_key="Your-key",
                                  api_base="Your-api-base", system_prompt=system_prompt,
                                  example_prompt=example_prompt, temperature=0.1)
    print(chat_bot.query("What is your name?"))
