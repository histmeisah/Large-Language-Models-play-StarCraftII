import requests
import json
import time
import random


class ChatBot_SingleTurn:
    """
    ChatBot类,用于对话
    调用自定义API接口,实现对话
    query方法用于对话
    """

    def __init__(self):
        """
        __init__方法,初始化ChatBot类
        """
        self.base_url = "http://172.18.116.172:8001/v1"
        self.headers = {"Content-Type": "application/json"}
        self.model = "textsc2-7b"
        self.messages = []

    def query(self, user_input, max_retries=5):
        """
        query方法,用于对话
        :param user_input: 用户输入
        :return: 机器人回复
        """
        # 重置 messages 列表
        self.messages = [{"role": "user", "content": user_input}]

        # 构建请求体
        payload = {
            "model": self.model,
            "messages": self.messages
        }

        # 尝试发送请求并获取回复
        for retries in range(max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    data=json.dumps(payload)
                )

                if response.status_code == 200:
                    answer = response.json()['choices'][0]['message']['content']
                    # print("answer:", answer)
                    return answer
                else:
                    print("Error:", response.status_code, response.text)
                    return "There was an error in processing your request."

            except Exception as e:
                # 输出错误信息
                print(f"Error when calling the API: {e}")

                # 如果达到最大尝试次数，返回一个特定的回复
                if retries >= max_retries - 1:
                    print("Maximum number of retries reached. The API is not responding.")
                    return "I'm sorry, but I am unable to provide a response at this time due to technical difficulties."

                # 重试前等待一段时间，使用 exponential backoff 策略
                sleep_time = (2 ** retries) + random.random()
                print(f"Waiting for {sleep_time} seconds before retrying...")
                time.sleep(sleep_time)


if __name__ == "__main__":
    chat_bot = ChatBot_SingleTurn()
    response = chat_bot.query("Hello, how are you?")
    print(response)
