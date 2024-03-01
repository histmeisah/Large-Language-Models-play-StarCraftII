
import anthropic
import os
import time
import random




class ChatBot_SingleTurn:
    """
    ，用于对话。
    调用 claude2  API 实现对话。
    query 方法用于对话。
    """

    def __init__(self, model_name, api_key, api_base, system_prompt, example_prompt, temperature):
        """
        初始化 Claude2ChatBot 类。
        :param model_name: claude 模型名称。
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
        self.model = anthropic.Anthropic(api_key="Your-api-key")
        self.temperature = temperature

    def configure_api(self, api_key, proxy):
        """
        配置 API 密钥和代理。
        """
        os.environ["HTTP_PROXY"] = proxy["http"]
        os.environ["HTTPS_PROXY"] = proxy["https"]

    def query(self, user_input, max_retries=5):
        """
        发送查询并获取回复。
        :param user_input: 用户输入。
        :return: Claude2 模型的回复。
        """
        # 重置 messages 列表
        messages = [
            {'role': 'user', 'content': self.system_prompt + self.example_prompt[0]},
            {'role': 'assistant', 'content': self.example_prompt[1]},
            {'role': 'user', 'content': user_input},
        ]

        # 尝试发送请求并获取回复
        for retries in range(max_retries):
            try:
                response = self.model.beta.messages.create(model="claude-2.1", max_tokens=1024, messages=messages,temperature=self.temperature)
                answer = response.content[0].text
                return answer
            except Exception as e:
                # 输出错误信息
                print(f"Error when calling the Claude2 API: {e}")

                # 如果达到最大尝试次数，返回一个特定的回复
                if retries >= max_retries - 1:
                    print("Maximum number of retries reached. The Claude2 API is not responding.")
                    return "I'm sorry, but I am unable to provide a response at this time due to technical difficulties."

                # 重试前等待一段时间，使用 exponential backoff 策略
                sleep_time = (2 ** retries) + random.random()
                print(f"Waiting for {sleep_time} seconds before retrying...")
                time.sleep(sleep_time)


# 使用示例
if __name__ == '__main__':
    api_key = "n"
    model_name = ''
    system_prompt = "请按照我们需要的格式输出动作的格式"
    example_prompt = ["A kill B", "A,B,<KILL>"]
    api_base = ""
    temperature = 0.1
    claude2_bot = ChatBot_SingleTurn(model_name, api_key, api_base, system_prompt, example_prompt, temperature)

    # 进行对话查询
    user_input = "A 打 B 吃 C"
    response = claude2_bot.query(user_input)
    print(response)
