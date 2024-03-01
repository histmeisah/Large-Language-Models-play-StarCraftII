import re
import openai
from sc2_rl_agent.starcraftenv_test.LLM.claude2_test import ChatBot_SingleTurn
import json
from sc2_rl_agent.starcraftenv_test.template.template import Template



class L2_summary:
    """
    L2_summary类

    """

    def __init__(self, LLMapi_base, LLMapi_key, model_name, temperature, system_prompt, example_prompt, chunk_window,prompt_type):
        """
        初始化
        :param LLMapi_base:
        :param LLMapi_key:
        :param model_name:
        :param temperature:
        :param system_prompt:
        :param example_prompt:
        :param chunk_window: # 摘要的窗口大小
        """
        self.api_base = LLMapi_base
        self.api_key = LLMapi_key
        self.model_name = model_name
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.example_prompt = example_prompt
        self.chunk_window = chunk_window
        self.chatbot = ChatBot_SingleTurn(api_base=self.api_base, api_key=self.api_key, model_name=self.model_name,
                                          temperature=self.temperature, system_prompt=self.system_prompt,
                                          example_prompt=self.example_prompt)
        self.template = Template()
        self.prompt_type = prompt_type

    def split_into_chunks(self, L1_summaries):
        """
        将L1_summaries依照self.chunk_window的大小拆分成一些chunk

        :param L1_summaries:
        :return:
        """
        if not isinstance(L1_summaries, list):
            raise TypeError("Input must be a list of L1 summaries.")
        self.L1_summaries = L1_summaries
        return [self.L1_summaries[i:i + self.chunk_window] for i in range(0, len(self.L1_summaries), self.chunk_window)]

    def get_latest_k_messages(self, chunks, k):
        """
        获取最新的K个信息

        :param chunks:
        :param k:
        :return:
        """
        if not chunks:
            raise ValueError("Input must be a non-empty list of chunks.")
        if not all(isinstance(chunk, list) for chunk in chunks):
            raise TypeError("Input must be a list of chunks.")
        if not isinstance(k, int) or k <= 0:
            raise ValueError("k must be a positive integer.")

        latest_k_messages = []
        for chunk in chunks:
            # 从每个块中选择最新的k条信息
            latest_messages = chunk[-k:]
            latest_k_messages.append(latest_messages)
        return latest_k_messages

    def query(self, inputs):
        """
        进行L2summary的请求

        先进行检查,判断是否为空
        再检查是否为[[],[]],即chunks的列表
        经过检查之后,每一个chunk会由LLM进行总结
        总结过后的L2_summary会被添加到一个list中
        最终返回这个L2_summaries的list

        :param chunks:
        :return:
        """
        chunks = inputs['L1_summaries']
        executed_actions = inputs['executed_actions']
        failed_actions = inputs['failed_actions']
        # print("chunks_type", type(chunks))
        # print("type_executed_actions", type(executed_actions))
        if executed_actions:
            pass
            # print("type_executed_actions[0]", type(executed_actions[0]))
        else:
            pass
            # print("executed_actions is empty!")
        if failed_actions:
            # print("type_failed_actions[0]", type(failed_actions[0]))
            pass
        else:
            pass
            # print("failed_actions is empty!")
        # print("type_failed_actions", type(failed_actions))
        if not chunks:
            raise ValueError("Input must be a non-empty list of chunks.")
        if not all(isinstance(chunk, list) for chunk in chunks):
            raise TypeError("Input must be a list of chunks.")

        L2_summaries = []

        if self.prompt_type == "v1":
            for chunk in chunks:
                # 根据模板填充内容
                chunks_str = "\n".join(f"chunk{i}: {item}" for i, item in enumerate(chunk))
                # 使用模板填充
                formatted_input = self.template.input_template_v1.format(
                    num_rounds=len(chunks),
                    chunks_str=chunks_str,
                )
                # 使用填充好的模板进行查询
                L2_summary = self.chatbot.query(formatted_input)
                L2_summaries.append(L2_summary)
        elif self.prompt_type == "v2":
            for chunk in chunks:
                # 根据模板填充内容
                chunks_str = "\n".join(f"chunk{i}: {item}" for i, item in enumerate(chunk))
                # 对于 executed_actions 和 failed_actions, 我们需要特别处理嵌套的列表结构
                executed_actions_str = "\n".join(
                    " ".join(str(sub_action) for sub_action in action) for action in executed_actions)

                failed_actions_str = "\n".join(
                    " ".join(str(sub_action) for sub_action in action) for action in failed_actions)

                # 使用模板填充
                formatted_input = self.template.input_template_v2.format(
                    num_rounds=len(chunks),
                    chunks_str=chunks_str,
                    executed_actions_str=executed_actions_str,
                    failed_actions_str=failed_actions_str
                )

                # 使用填充好的模板进行查询
                L2_summary = self.chatbot.query(formatted_input)
                L2_summaries.append(L2_summary)
        elif self.prompt_type=="v3":
            for chunk in chunks:
                # 根据模板填充内容
                chunks_str = "\n".join(f"chunk{i}: {item}" for i, item in enumerate(chunk))
                # 使用模板填充
                formatted_input = self.template.input_template_v3.format(
                    num_rounds=len(chunks),
                    chunks_str=chunks_str,
                )
                # 使用填充好的模板进行查询
                L2_summary = self.chatbot.query(formatted_input)
                L2_summaries.append(L2_summary)
        elif self.prompt_type=="v4":
            for chunk in chunks:
                # 根据模板填充内容
                chunks_str = "\n".join(f"chunk{i}: {item}" for i, item in enumerate(chunk))
                L2_summary = self.chatbot.query(chunks_str)
                L2_summaries.append(L2_summary)
        return L2_summaries
