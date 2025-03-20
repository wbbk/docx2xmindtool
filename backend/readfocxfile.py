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
from flask import current_app
from models import db, APIConfig, UserFile

# 定义项目根目录和上传目录的路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOADS_DIR = os.path.join('backend', 'static', 'uploads')

def get_file_model_config(user_id):
    """获取用户配置的文件处理模型配置"""
    with current_app.app_context():
        config = APIConfig.query.filter_by(
            user_id=user_id,
            type='file'
        ).first()
        if not config:
            raise Exception("未找到文件处理模型配置，请先配置模型信息")
        return config

def create_model_client(user_id):
    """创建模型客户端"""
    config = get_file_model_config(user_id)
    return OpenAI(
        api_key=config.api_key,
        base_url=config.api_url
    )

def get_latest_user_file(user_id):
    """获取用户最新上传的文件信息"""
    with current_app.app_context():
        latest_file = UserFile.query.filter_by(user_id=user_id).order_by(UserFile.upload_time.desc()).first()
        if not latest_file:
            raise Exception("未找到用户上传的文件")
        # 将文件路径转换为相对于项目根目录的路径
        relative_path = os.path.join(UPLOADS_DIR, os.path.basename(latest_file.file_path))
        latest_file.file_path = os.path.join(BASE_DIR, relative_path)
        return latest_file

def first_ali_file_agent_handle(user_id):
    # 获取用户最新上传的文件信息
    with current_app.app_context():
        user_file = UserFile.query.filter_by(user_id=user_id).order_by(UserFile.upload_time.desc()).first()
        if not user_file:
            raise Exception("未找到用户上传的文件")
    file_path = user_file.file_path
    client = create_model_client(user_id)
    file_object = client.files.create(file=Path(file_path), purpose="file-extract")
    file_completion = client.chat.completions.create(
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