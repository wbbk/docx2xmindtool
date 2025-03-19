# -*- coding: utf-8 -*-
import re
import json

"""
@author: wubin
@contact: 18050152@qq.com
@file: create_xmind.py
@time: 2025/3/19 21:01
@version: 1.0
@desc: 
"""
# 动态构建XMind结构
def build_topics(parent_topic, data):
    """
    动态构建XMind主题结构，并增强异常处理机制。
    :param parent_topic: 当前父主题
    :param data: 数据结构（字典或列表）
    """
    if not isinstance(data, dict):
        print(f"错误: 数据应为字典类型，但实际类型为 {type(data)}")
        return
    for key, value in data.items():
        try:
            # 创建子主题
            sub_topic = parent_topic.addSubTopic()
            sub_topic.setTitle(key or "未知主题")  # 防止 key 为空
            # 如果值是字典，则递归处理
            if isinstance(value, dict):
                build_topics(sub_topic, value)
            # 如果值是列表，则添加测试用例
            elif isinstance(value, list):
                for i, case in enumerate(value, start=1):
                    try:
                        if not isinstance(case, list) or len(case) < 4:
                            raise ValueError(f"用例格式错误: 预期列表长度至少为4，但实际为 {case}")
                        # 创建用例主题
                        case_topic = sub_topic.addSubTopic()
                        case_title = f"{i}. {case[0]}" if case[0] else f"{i}. 未知用例"
                        case_topic.setTitle(case_title)
                        # 添加步骤和预期结果
                        sub_topic_name = case_topic.addSubTopic()
                        sub_topic_name.setTitle(case[1] or "无步骤描述")
                        steps_topic = sub_topic_name.addSubTopic()
                        steps_topic.setTitle(case[2] or "无步骤内容")
                        expected_topic = steps_topic.addSubTopic()
                        expected_topic.setTitle(case[3] or "无预期结果")
                    except Exception as e:
                        print(f"处理用例时出错 (模块: {key}, 用例编号: {i}): {e}")
            else:
                print(f"错误: 值的类型无效 (模块: {key})，应为字典或列表，但实际类型为 {type(value)}")
        except Exception as e:
            print(f"处理模块时出错 (模块名称: {key}): {e}")

def create_xmind_file(workbook, json_content):
    print("AI🐮🐴正在帮你写入测试用例xmind文件，请稍等…………")
    try:
        json_match = re.search(r'\{(?:[^{}]|\{[^{}]*\})*\}', json_content, re.DOTALL)
        if not json_match:
            print("未找到JSON内容")
            raise ValueError("未找到JSON内容")
        # 验证 JSON 格式
        json_content = json_match.group(0)
        try:
            test_cases = json.loads(json_content)
            print("内容预览～～～\n", json_content)
        except json.JSONDecodeError as e:
            print(f"JSON 格式错误: {e}")
            print(f"尝试解析的 JSON 内容:\n{json_content}")
            return
        # 获取第一个工作表
        sheet = workbook.getPrimarySheet()
        root_topic = sheet.getRootTopic()
        # 构建XMind结构
        build_topics(root_topic, test_cases)
    except Exception as e:
        print(f"写入 XMind 文件时出错: {e}")

    except FileNotFoundError as e:
        print(e)
        return