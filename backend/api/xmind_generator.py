import xmind
import os
import json

def generate_xmind(structured_content, output_path):
    """
    根据结构化内容生成xmind文件
    
    Args:
        structured_content: 结构化的内容数据，通常是从大模型API返回并解析后的数据
        output_path: 输出的xmind文件路径
        
    Returns:
        str: 生成的xmind文件路径
    """
    try:
        # 创建xmind工作簿和工作表
        workbook = xmind.load(output_path) if os.path.exists(output_path) else xmind.load()
        sheet = workbook.getPrimarySheet()
        sheet.setTitle(structured_content.get('root', {}).get('text', '思维导图'))
        
        # 获取根节点
        root_topic = sheet.getRootTopic()
        root_topic.setTitle(structured_content.get('root', {}).get('text', '中心主题'))
        
        # 递归构建思维导图结构
        build_topics(root_topic, structured_content.get('root', {}).get('children', []))
        
        # 保存xmind文件
        xmind.save(workbook, path=output_path)
        
        return output_path
        
    except Exception as e:
        raise Exception(f"生成xmind文件失败: {str(e)}")

def build_topics(parent_topic, children):
    """
    递归构建xmind主题结构
    
    Args:
        parent_topic: 父主题
        children: 子主题列表
    """
    for child_data in children:
        # 创建子主题
        child_topic = parent_topic.addSubTopic()
        child_topic.setTitle(child_data.get('text', ''))
        
        # 如果有子主题，递归处理
        if 'children' in child_data and child_data['children']:
            build_topics(child_topic, child_data['children'])

def read_xmind_preview(file_path):
    """
    读取xmind文件，返回预览数据
    
    Args:
        file_path: xmind文件路径
        
    Returns:
        dict: 预览数据
    """
    try:
        # 加载xmind文件
        workbook = xmind.load(file_path)
        sheet = workbook.getPrimarySheet()
        root_topic = sheet.getRootTopic()
        
        # 构建预览数据
        preview_data = {
            'nodes': [extract_topic_data(root_topic)]
        }
        
        return preview_data
        
    except Exception as e:
        raise Exception(f"读取xmind文件失败: {str(e)}")

def extract_topic_data(topic):
    """
    提取主题数据
    
    Args:
        topic: xmind主题对象
        
    Returns:
        dict: 主题数据
    """
    # 获取主题标题
    title = topic.getTitle()
    
    # 获取子主题
    children = []
    for sub_topic in topic.getSubTopics() or []:
        children.append(extract_topic_data(sub_topic))
    
    # 构建主题数据
    topic_data = {
        'id': topic.getID(),
        'name': title,
        'children': children
    }
    
    return topic_data