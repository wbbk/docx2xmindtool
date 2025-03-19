import requests
import json
import time

def call_model_api(docx_content, api_config):
    """
    调用大模型API，将docx内容转换为结构化数据
    
    Args:
        docx_content: 解析后的docx内容
        api_config: API配置信息，包含api_key和api_url
        
    Returns:
        dict: 结构化后的内容，适合生成xmind
    """
    try:
        api_key = api_config.get('api_key')
        api_url = api_config.get('api_url')
        
        if not api_key or not api_url:
            raise ValueError("API配置不完整")
        
        # 构建请求数据
        prompt = generate_prompt(docx_content)
        
        # 构建请求头
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        # 构建请求体
        # 注意：这里的请求体结构可能需要根据实际使用的大模型API进行调整
        payload = {
            'model': 'gpt-3.5-turbo',  # 或其他模型
            'messages': [
                {
                    'role': 'system',
                    'content': '你是一个专业的文档结构分析助手，擅长将文档内容转换为思维导图结构。'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.7,
            'max_tokens': 4000
        }
        
        # 发送请求
        start_time = time.time()
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        end_time = time.time()
        
        # 检查响应状态
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        
        # 提取模型返回的内容
        # 注意：这里的提取逻辑可能需要根据实际使用的大模型API进行调整
        model_response = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        # 解析模型返回的内容为结构化数据
        structured_content = parse_model_response(model_response)
        
        # 添加调用信息
        structured_content['_meta'] = {
            'api_call_time': f"{end_time - start_time:.2f}秒",
            'model': payload['model'],
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return structured_content
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"API请求失败: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("API响应解析失败")
    except Exception as e:
        raise Exception(f"调用大模型API失败: {str(e)}")

def generate_prompt(docx_content):
    """
    根据docx内容生成提示词
    
    Args:
        docx_content: 解析后的docx内容
        
    Returns:
        str: 提示词
    """
    title = docx_content.get('title', '未命名文档')
    content_items = docx_content.get('content', [])
    tables = docx_content.get('tables', [])
    
    # 构建提示词
    prompt = f"""请将以下文档内容转换为思维导图结构。文档标题是：{title}

文档内容：
"""
    
    # 添加段落内容
    for item in content_items:
        prefix = "#" * item['level'] if item['is_heading'] and item['level'] > 0 else ""
        prompt += f"{prefix} {item['text']}\n"
    
    # 添加表格内容
    if tables:
        prompt += "\n文档中的表格：\n"
        for i, table in enumerate(tables):
            prompt += f"表格{i+1}:\n"
            for row in table:
                prompt += " | ".join(row) + "\n"
            prompt += "\n"
    
    # 添加输出格式要求
    prompt += """
请将文档内容转换为JSON格式的思维导图结构，格式如下：
{
  "root": {
    "text": "中心主题",
    "children": [
      {
        "text": "一级主题1",
        "children": [
          { "text": "二级主题1.1" },
          { "text": "二级主题1.2" }
        ]
      },
      {
        "text": "一级主题2",
        "children": [...]
      }
    ]
  }
}

请确保：
1. 保留文档的层级结构
2. 提取关键信息，避免冗余
3. 合理组织主题间的关系
4. 返回的JSON必须是有效的，可以直接解析
"""
    
    return prompt

def parse_model_response(response_text):
    """
    解析模型返回的文本为结构化数据
    
    Args:
        response_text: 模型返回的文本
        
    Returns:
        dict: 结构化数据
    """
    try:
        # 尝试从返回文本中提取JSON部分
        json_start = response_text.find('{')
        json_end = response_text.rfind('}')
        
        if json_start >= 0 and json_end >= 0:
            json_str = response_text[json_start:json_end+1]
            structured_data = json.loads(json_str)
            return structured_data
        else:
            # 如果没有找到JSON，尝试解析整个响应
            return json.loads(response_text)
            
    except json.JSONDecodeError:
        # 如果JSON解析失败，返回简单结构
        return {
            "root": {
                "text": "解析失败",
                "children": [
                    {"text": "无法从模型响应中提取有效的思维导图结构"}
                ]
            }
        }