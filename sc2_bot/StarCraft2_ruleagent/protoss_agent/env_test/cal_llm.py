import time
import random
import time
import json
import websocket


class ChatBot_SingleTurn:
    """
    ChatBot类,用于对话
    调用openai的ChatCompletion接口,实现对话
    query方法用于对话
    """

    def __init__(self, model_name,  system_prompt, temperature, port=1111,
                 host='172.18.116.172'):
        """
        __init__方法,初始化ChatBot类
        :param model_name: 模型名称
        :param system_prompt: 系统提示语
        :param temperature: 控制生成文本的随机性的参数
        :param host: 服务器地址
        :param port: 服务器端口
        """
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.ipaddress = host + ":" + str(port)
        self.ws = websocket.create_connection("ws://" + self.ipaddress)

    def query(self, user_input, max_retries=5):
        """
        query方法,用于对话
        :param user_input: 用户输入
        :return: 机器人回复
        """

        # 构造instruction部分
        instruction = f"{self.system_prompt}"

        # 构造发送的消息
        state = {"instruction": instruction, "input": user_input}
        send_data = json.dumps(state, ensure_ascii=False)

        # 尝试发送请求并获取回复
        for retries in range(max_retries):
            try:
                self.ws.send(send_data)
                msg = self.ws.recv()

                # 根据你的服务器响应格式提取答案
                # 如果需要更复杂的处理，请根据实际响应格式修改以下代码
                answer = msg

                return answer

            except Exception as e:
                # 输出错误信息
                print(f"Error when calling the server: {e}")

                # 如果达到最大尝试次数，返回一个特定的回复
                if retries >= max_retries - 1:
                    print("Maximum number of retries reached. The server is not responding.")
                    return "I'm sorry, but I am unable to provide a response at this time due to technical difficulties."

                # 重试前等待一段时间，使用 exponential backoff 策略
                sleep_time = (2 ** retries) + random.random()
                print(f"Waiting for {sleep_time} seconds before retrying...")
                time.sleep(sleep_time)
