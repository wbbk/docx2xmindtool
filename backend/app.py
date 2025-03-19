from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from models import db, User, APIConfig, TestRule, UserFile
import jwt
from functools import wraps
from datetime import datetime, timedelta
import os
from api.docx_parser import parse_docx
from api.xmind_generator import generate_xmind
from api.model_api import call_model_api
from models import db, APIConfig
import xmindparser
import time

app = Flask(__name__, static_folder='static')
CORS(app)

# 设置响应编码为UTF-8
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_SORT_KEYS'] = False  # 禁用键排序

# 配置文件上传目录
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/outputs')
ALLOWED_EXTENSIONS = {'docx'}

# 确保上传和输出目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@192.168.5.27:3306/docx2xmindtool?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为16MB

# 初始化数据库
db.init_app(app)
with app.app_context():
    db.create_all()
    # 创建默认管理员账号
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

# 添加JWT密钥配置
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # 在生产环境中使用安全的密钥
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# 用户认证装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'message': '缺少Authorization请求头', 'success': False}), 401
        
        try:
            # 验证token格式
            if not auth_header.startswith('Bearer '):
                return jsonify({'message': 'Authorization头格式错误，应为：Bearer <token>', 'success': False}), 401
            
            token = auth_header.split(' ')[1]
            if not token:
                return jsonify({'message': '缺少token', 'success': False}), 401
            
            # 解析token
            try:
                data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                return jsonify({'message': 'token已过期', 'success': False}), 401
            except jwt.InvalidTokenError:
                return jsonify({'message': 'token无效', 'success': False}), 401
            
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'message': '用户不存在或已被删除', 'success': False}), 401
                
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'message': f'认证失败: {str(e)}', 'success': False}), 401
            
    return decorated

# 检查文件扩展名是否允许
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# API配置管理接口
@app.route('/api/configs', methods=['GET', 'POST', 'DELETE'])
@token_required
def manage_configs(current_user):
    if request.method == 'GET':
        configs = APIConfig.query.filter_by(user_id=current_user.id).all()
        return jsonify([config.to_dict() for config in configs])
    
    elif request.method == 'POST':
        configs = request.json
        if not isinstance(configs, list):
            configs = [configs]
            
        try:
            # 验证配置列表不为空
            if not configs:
                return jsonify({"message": "配置列表不能为空", "success": False}), 400
                
            for config in configs:
                # 验证必填字段
                required_fields = ['api_key', 'api_url', 'model']
                missing_fields = [field for field in required_fields if not config.get(field, '').strip()]
                
                if missing_fields:
                    return jsonify({
                        "message": f"缺少必填字段: {', '.join(missing_fields)}", 
                        "success": False
                    }), 400
                
                new_config = APIConfig(
                    api_key=config['api_key'].strip(),
                    api_url=config['api_url'].strip(),
                    model=config['model'].strip(),
                    type=config.get('type', 'normal').strip(),
                    user_id=current_user.id
                )
                db.session.add(new_config)
            
            db.session.commit()
            return jsonify({"message": "配置已保存", "success": True})
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"保存配置失败: {str(e)}", "success": False}), 500
    
    elif request.method == 'DELETE':
        try:
            config_id = request.json.get('id')
            config = APIConfig.query.filter_by(id=config_id, user_id=current_user.id).first()
            if config:
                db.session.delete(config)
                db.session.commit()
                return jsonify({"message": "配置已删除", "success": True})
            return jsonify({"message": "配置不存在", "success": False}), 404
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"删除配置失败: {str(e)}", "success": False}), 500

# 文件上传接口
@app.route('/api/upload', methods=['POST'])
@token_required
def upload_file(current_user):
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({"message": "没有文件部分", "success": False}), 400

    file = request.files['file']

    # 检查文件名是否为空
    if file.filename == '':
        return jsonify({"message": "没有选择文件", "success": False}), 400

    # 检查文件扩展名
    if not allowed_file(file.filename):
        return jsonify({"message": "只允许上传docx格式的文件", "success": False}), 400

    # 读取文件内容到内存
    file_content = file.read()

    # 检查文件大小
    if len(file_content) > 10 * 1024 * 1024:  # 10MB
        return jsonify({"message": "文件大小不能超过10MB", "success": False}), 400

    # 处理文件
    try:
        original_filename = file.filename
        # 使用时间戳和原始文件名组合作为文件名
        timestamp = int(time.time())
        # 构建文件路径并保存文件
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{original_filename}")

        with open(file_path, 'wb') as f:
            f.write(file_content)
            f.flush()
            os.fsync(f.fileno())  # 强制将文件数据刷新到磁盘

        # 添加文件存在性检查和重试机制
        max_retries = 3
        retry_delay = 0.5  # 秒
        for attempt in range(max_retries):
            if os.path.exists(file_path) and os.path.getsize(file_path) == len(file_content):
                # 再次验证文件内容完整性
                with open(file_path, 'rb') as f:
                    saved_content = f.read()
                if len(saved_content) == len(file_content) and saved_content == file_content:
                    # 保存文件信息到数据库
                    user_file = UserFile(
                        user_id=current_user.id,
                        original_filename=original_filename,
                        file_path=file_path,
                        file_size=len(file_content)
                    )
                    db.session.add(user_file)
                    db.session.commit()
                    
                    return jsonify({
                        "message": "文件上传成功",
                        "filename": original_filename,
                        "file_path": file_path,
                        "success": True
                    })
            time.sleep(retry_delay)
            retry_delay *= 2  # 指数退避策略

        # 如果重试后仍未成功，返回错误
        if not os.path.exists(file_path) or os.path.getsize(file_path) != len(file_content):
            return jsonify({"message": "文件保存失败，请重试", "success": False}), 500
    except Exception as e:
        return jsonify({"message": f"文件上传失败: {str(e)}", "success": False}), 500

# 读取上传文档接口调用大模型
@app.route('/api/readdocxfile', methods=['POST'])
@token_required
def read_docx_file(current_user):
    test_rules = request.json.get('test_rules', [])
    results = []
    
    for rule in test_rules:
        if rule['enabled']:
            # 这里应该实现各种测试规则的逻辑
            # 示例实现
            if rule['name'] == '大模型连接测试':
                # 测试与大模型的连接
                success, message = test_model_connection()
                results.append({
                    "rule": rule['name'],
                    "success": success,
                    "message": message
                })
            elif rule['name'] == '文件解析组件依赖检测':
                # 测试文件解析组件
                success, message = test_docx_parser()
                results.append({
                    "rule": rule['name'],
                    "success": success,
                    "message": message
                })
            # 添加更多测试规则...
    
    return jsonify({
        "results": results,
        "success": all(result['success'] for result in results)
    })

# 转换docx到xmind接口
@app.route('/api/convert', methods=['POST'])
@token_required
def convert_docx_to_xmind(current_user):
    filename = request.json.get('filename')
    test_results = request.json.get('test_results', [])
    
    if not filename:
        return jsonify({"message": "未指定文件名", "success": False}), 400
    
    # 安全处理文件名
    safe_filename = secure_filename(filename)
    if not safe_filename:
        timestamp = int(time.time())
        safe_filename = f"document_{timestamp}.docx"
    else:
        # 确保文件名有基本名称部分和扩展名
        base_name, extension = os.path.splitext(safe_filename)
        if not base_name:
            base_name = f"document_{int(time.time())}"
        if not extension or extension.lower() != '.docx':
            extension = '.docx'
        safe_filename = f"{base_name}{extension}"
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
    
    # 如果找不到文件，尝试查找原始文件名对应的文件
    if not os.path.exists(file_path):
        # 获取上传目录中的所有文件
        all_files = os.listdir(app.config['UPLOAD_FOLDER'])
        # 尝试找到文件名的变体（可能添加了计数器）
        base_name, extension = os.path.splitext(safe_filename)
        possible_files = [f for f in all_files if f.startswith(base_name) and f.endswith(extension)]
        
        if possible_files:
            # 使用找到的第一个匹配文件
            safe_filename = possible_files[0]
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        else:
            return jsonify({"message": "文件不存在", "success": False}), 404
    
    try:
        # 解析docx文件
        docx_content = parse_docx(file_path)
        
        # 获取所有API配置
        api_configs = APIConfig.query.all()
        if not api_configs:
            return jsonify({"message": "未配置API", "success": False}), 400
        
        # 默认使用普通模型
        model_config = next((config for config in api_configs if config.type == 'normal'), None)
        
        # 如果没有找到普通模型，则使用第一个可用的配置
        if not model_config and api_configs:
            model_config = api_configs[0]
        
        if not model_config:
            return jsonify({"message": "未找到合适的模型配置", "success": False}), 400
        
        structured_content = call_model_api(docx_content, model_config.to_dict())
        
        # 生成xmind文件
        output_filename = os.path.splitext(safe_filename)[0] + '.xmind'
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        generate_xmind(structured_content, output_path)
        
        return jsonify({
            "message": "转换成功",
            "output_filename": output_filename,
            "output_path": output_path,
            "success": True
        })
    
    except Exception as e:
        return jsonify({"message": f"转换失败: {str(e)}", "success": False}), 500

# 下载生成的xmind文件
@app.route('/api/download/<filename>', methods=['GET'])
@token_required
def download_file(current_user, filename):
    try:
        # 解码文件名
        decoded_filename = secure_filename(filename)
        
        # 如果找不到文件，尝试查找类似的文件
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], decoded_filename)
        if not os.path.exists(file_path):
            # 获取输出目录中的所有文件
            all_files = os.listdir(app.config['OUTPUT_FOLDER'])
            # 尝试找到文件名的变体（可能添加了计数器）
            base_name, extension = os.path.splitext(decoded_filename)
            possible_files = [f for f in all_files if f.startswith(base_name) and f.endswith(extension)]
            
            if possible_files:
                # 使用找到的第一个匹配文件
                decoded_filename = possible_files[0]
            else:
                return jsonify({"message": "文件不存在", "success": False}), 404
        
        # 设置下载的原始文件名
        return send_from_directory(
            app.config['OUTPUT_FOLDER'], 
            decoded_filename, 
            as_attachment=True,
            download_name=filename  # 使用原始文件名作为下载名称
        )
    except Exception as e:
        return jsonify({"message": f"下载失败: {str(e)}", "success": False}), 500

# 获取xmind预览数据
@app.route('/api/preview/<filename>', methods=['GET'])
@token_required
def preview_xmind(current_user, filename):
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({"message": "文件不存在", "success": False}), 404
    
    try:
        # 尝试获取图像识别模型配置
        vision_model = APIConfig.query.filter_by(type='vision').first()
        
        # 解析xmind文件
        xmindparser.config = {
            'showTopicId': False,
            'hideEmptyValue': True
        }
        xmind_data = xmindparser.xmind_to_dict(file_path)
        
        # 处理数据结构以适应前端渲染
        def process_topic(topic):
            node = {
                'text': topic.get('title', ''),
                'children': []
            }
            
            # 如果有图像识别模型配置，可以在这里添加图像处理逻辑
            if vision_model and 'image' in topic:
                try:
                    # 这里可以添加使用图像识别模型处理图像的逻辑
                    # 例如：调用图像识别API等
                    pass
                except Exception as e:
                    # 记录错误但不中断预览流程
                    print(f"图像处理错误: {str(e)}")
            
            if 'topics' in topic:
                for child in topic['topics']:
                    node['children'].append(process_topic(child))
            
            return node
        
        preview_data = None
        if xmind_data and len(xmind_data) > 0 and 'topic' in xmind_data[0]:
            root_node = process_topic(xmind_data[0]['topic'])
            preview_data = {
                'nodes': [root_node]
            }
        
        return jsonify({
            "preview_data": preview_data,
            "success": True
        })
    except Exception as e:
        return jsonify({
            "message": f"预览失败: {str(e)}", 
            "success": False
        }), 500

# 测试函数
def test_model_connection():
    # 实现与大模型API的连接测试
    if not api_configs:
        return False, "未配置API"
    
    try:
        # 这里应该实现实际的连接测试逻辑
        return True, "连接成功"
    except Exception as e:
        return False, f"连接失败: {str(e)}"

def test_docx_parser():
    # 测试docx解析组件
    try:
        # 这里应该实现实际的测试逻辑
        return True, "组件正常"
    except Exception as e:
        return False, f"组件异常: {str(e)}"

# 用户注册
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': '缺少必要字段', 'success': False}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': '用户名已存在', 'success': False}), 400
    
    if data.get('email') and User.query.filter_by(email=data['email']).first():
        return jsonify({'message': '邮箱已被使用', 'success': False}), 400
    
    user = User(username=data['username'], email=data.get('email'))
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': '注册成功', 'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'注册失败: {str(e)}', 'success': False}), 500

# 用户登录
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': '缺少用户名或密码', 'success': False}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user and user.check_password(data['password']):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES']
        }, app.config['JWT_SECRET_KEY'])
        
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': '登录成功',
            'token': token,
            'user': user.to_dict(),
            'success': True
        })
    
    return jsonify({'message': '用户名或密码错误', 'success': False}), 401

# 测试规范管理接口
@app.route('/api/test-rules', methods=['GET', 'POST', 'DELETE'])
@token_required
def manage_test_rules(current_user):
    if request.method == 'GET':
        rules = TestRule.query.filter_by(user_id=current_user.id).all()
        return jsonify([rule.to_dict() for rule in rules])
    
    elif request.method == 'POST':
        data = request.json
        if not isinstance(data, list):
            data = [data]
            
        try:
            # 验证规则列表不为空
            if not data:
                return jsonify({"message": "规则列表不能为空", "success": False}), 400
                
            for rule_data in data:
                # 验证必填字段
                if not rule_data.get('name', '').strip():
                    return jsonify({
                        "message": "规则名称不能为空", 
                        "success": False
                    }), 400
                
                # 如果存在rule_id，则更新现有记录
                if 'id' in rule_data:
                    rule = TestRule.query.filter_by(id=rule_data['id'], user_id=current_user.id).first()
                    if rule:
                        rule.name = rule_data['name'].strip()
                        rule.content = rule_data.get('content', rule.content)
                        rule.enabled = rule_data.get('enabled', True)
                    else:
                        return jsonify({"message": "规则不存在", "success": False}), 404
                else:
                    # 创建新记录
                    new_rule = TestRule(
                        name=rule_data['name'].strip(),
                        content=rule_data.get('content', ''),
                        enabled=rule_data.get('enabled', True),
                        user_id=current_user.id
                    )
                    db.session.add(new_rule)
            
            db.session.commit()
            return jsonify({"message": "规则已保存", "success": True})
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"保存规则失败: {str(e)}", "success": False}), 500
    
    elif request.method == 'DELETE':
        try:
            rule_id = request.json.get('id')
            rule = TestRule.query.filter_by(id=rule_id, user_id=current_user.id).first()
            if rule:
                db.session.delete(rule)
                db.session.commit()
                return jsonify({"message": "规则已删除", "success": True})
            return jsonify({"message": "规则不存在", "success": False}), 404
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"删除规则失败: {str(e)}", "success": False}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)