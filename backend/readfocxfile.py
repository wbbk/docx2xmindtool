# -*- coding: utf-8 -*-

"""
@author: wubin
@contact: 18050152@qq.com
@file: agentForTodo.py
@time: 2025/2/24 19:01
@version: 1.0
@desc:
"""

import os
import sys
from pathlib import Path
from openai import OpenAI

client_ali = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",key的获取地址如下
    # https://bailian.console.aliyun.com/?spm=5176.29619931.J__Z58Z6CX7MY__Ll8p1ZOR.1.540959fcDn6UTO#/model-market/detail/qwen2.5-72b-instruct?tabKey=sdk
    api_key="sk-624a75f0a67d4a5f80d26032fc2c7c01",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 读取该项目根目录下的文件路径
path = os.path.dirname(sys.argv[0])
def first_ali_file_agent_handle(filename):
    file_path = os.path.join(path, filename)
    file_object = client_ali.files.create(file=Path(file_path), purpose="file-extract")
    file_completion = client_ali.chat.completions.create(
        model="qwen-long",
        messages=[
            {'role': 'system', 'content': f'fileid://{file_object.id}'},
            {'role': 'user',
             'content': '根据上述文档，对功能需求部分的内容进行 整理，大标题按照一、二……罗列，小点按点1、2……罗列，仅返回响应内容，不需要使用json格式，无需格外描述'}
        ],
        stream=True,
        temperature=0.9
    )
    full_content = ""
    print("文件处理的流式输出内容为：")
    for chunk in file_completion:
        if chunk.choices and chunk.choices[0].delta.content:
            full_content += chunk.choices[0].delta.content
            print(chunk.choices[0].delta.content)
    print("文件处理的输出内容为：", full_content)
    return full_content