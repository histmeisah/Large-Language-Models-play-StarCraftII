import openai
import os


def test1():
    openai.api_key = "EMPTY"
    openai.base_url = "http://172.18.116.172:8001/v1"

    # model = "textsc2-7b"
    model = "qwen_textsc2-7b"
    prompt = "Once upon a time"

    # 创建一个completion
    print("start")
    # 创建一个聊天completion
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": "Hello! What is your name?"}]
    )
    # 打印这个completion
    print(completion.choices[0].message.content)


import requests
import json


def test_chat_completion():
    url = "http://172.18.116.170:8000/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "APU-0-25",
        "messages": [{"role": "user", "content": "Hello! What is your name?"}]
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print(response.json()['choices'][0]['message']['content'])
    else:
        print("Error:", response.status_code, response.text)


def test_text_completion():
    url = "http://172.18.116.170:8000/v1/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "APU-0-25",
        "prompt": "Once upon a time",
        "max_tokens": 41,
        "temperature": 0.5
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print(response.json()['choices'][0]['text'])
    else:
        print("Error:", response.status_code, response.text)


# 运行测试
test_chat_completion()
# test_text_completion()
