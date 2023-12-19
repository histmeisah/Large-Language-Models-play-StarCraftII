import openai
import os

openai.api_key = "sk-8p38chfjXbbL1RT943B051229a224a8cBdE1B53b5e2c04E2"
openai.api_base = "https://api.ai-yyds.com/v1"


# os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
# os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

def query(prompt, inputs):
    content = prompt + inputs
    output = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                          messages=[{"role": "user", "content": content}])["choices"][0]["message"][
        "content"]
    return output


a = 'daadaadada'
b = 'dasdadadad'

print(query(a, b))
