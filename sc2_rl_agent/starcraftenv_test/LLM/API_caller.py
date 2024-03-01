import openai
import os
import time

openai.api_base = "http://172.18.116.172:8000/v1"
openai.api_key = "none"

# 如果需要代理，可以取消下面两行的注释
# os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
# os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

def test_local_llm():
    def query(prompt):
        content = prompt
        output = openai.ChatCompletion.create(model="qwen_textsc2",
                                              messages=[{"role": "user", "content": content}])["choices"][0]["message"]["content"]
        return output

    a = """
    ....
    """

    total_time = 0
    num_calls = 100

    for _ in range(num_calls):
        start_time = time.time()
        query(a)
        end_time = time.time()
        total_time += (end_time - start_time)

    average_time = total_time / num_calls
    print("Average time per call: {:.2f} seconds".format(average_time))

def test_glm4():
    from zhipuai import ZhipuAI
    client = ZhipuAI(api_key="Your-API-KEY")  # 填写您自己的APIKey
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "我是人工智能助手"},
            {"role": "user", "content": "你叫什么名字"},
            {"role": "assistant", "content": "我叫chatGLM"},
            {"role": "user", "content": "你都可以做些什么事"}
        ],
    )
    print(response.choices[0].message.content)

test_glm4()
