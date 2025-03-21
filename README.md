### 仍在开发中，页面已搭好，正在逐步完善请求逻辑。

# Docx 转 XMind 工具

基于大模型的 docx 文档转 xmind 思维导图工具，实现文档结构智能解析与思维导图生成。本工具可以帮助用户快速将Word文档转换为结构化的思维导图，提高文档阅读和理解效率。

## 项目预览

![文档上传界面](iShot_2025-03-19_22.55.27.png)

![思维导图预览](iShot_2025-03-19_22.55.49.png)

## 功能特点

- **智能解析**：利用大模型分析文档结构，提取关键信息
- **文件上传**：支持拖拽或点击上传docx文件
- **API配置管理**：可添加多个大模型API配置，灵活切换
- **测试规则**：支持多种测试规则，确保转换质量
- **实时日志**：显示转换过程中的详细日志
- **预览功能**：转换完成后可预览思维导图结构
- **下载功能**：支持下载生成的xmind文件
- **在线编辑**：支持对生成的思维导图进行在线编辑（开发中）

## 项目结构

```
├── backend/                   # 后端Flask应用
│   ├── api/                   # API核心功能模块
│   │   ├── docx_parser.py     # Word文档解析器：负责解析docx文件结构
│   │   ├── model_api.py       # 大模型API接口：处理与AI模型的交互
│   │   └── xmind_generator.py # XMind生成器：构建思维导图结构
│   ├── app.py                 # Flask应用入口：配置路由和中间件
│   ├── models.py              # 数据模型：定义数据库结构
│   ├── create_xmind.py        # XMind创建工具：封装XMind文件操作
│   ├── readfocxfile.py        # Docx读取工具：处理文档读取逻辑
│   ├── requirements.txt       # 项目依赖清单
│   ├── static/                # 静态资源目录
│   │   ├── outputs/           # XMind文件输出目录
│   │   └── uploads/           # 文档上传临时存储目录
│   └── utils/                 # 通用工具函数库
└── frontend/                  # 前端Vue.js应用
    ├── public/                # 静态公共资源
    │   └── index.html         # 应用入口HTML文件
    ├── src/                   # 源代码目录
    │   ├── assets/            # 项目资源文件
    │   ├── components/        # 可复用的Vue组件
    │   ├── router/            # 前端路由配置
    │   ├── views/             # 页面视图组件
    │   ├── App.vue            # 根组件
    │   └── main.js            # 应用入口文件
    ├── babel.config.js        # Babel配置文件
    └── package.json           # 前端依赖配置
```

### 核心目录说明

- **backend/api/**: 包含核心业务逻辑，负责文档解析、AI处理和XMind生成
- **backend/static/**: 管理文件上传和导出，确保数据安全存储
- **frontend/src/**: 实现用户界面，提供直观的操作体验
- **frontend/components/**: 存放可复用的UI组件，保证界面统一性

## 环境要求

### 后端环境
- Python 3.6+
- Flask 3.1.0
- Flask-Cors 3.1.0
- Flask-SQLAlchemy 3.1.1
- python-docx 1.1.2
- Requests 2.32.3
- XMind 1.2.0

### 前端环境
- Node.js 12+
- Vue 3.2.0+
- Element Plus 2.3.0+
- axios 0.21.1
- vue-router 4.0.0+

## 安装与运行

### 后端安装

```bash
# 克隆项目
git clone https://github.com/wbbk/docx2xmindtool.git
cd docx2xmindtool/backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动后端服务
python backend/app.py
```

### 前端安装

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run serve

# 构建生产版本
npm run build
```

## 使用指南

### 1. API配置
1. 点击左上角"编辑"按钮
2. 在弹出的配置面板中添加大模型API信息：
   - API Key
   - API URL
   - 其他相关配置
3. 保存配置

### 2. 文档转换
1. 将Word文档拖拽到上传区域或点击选择文件
2. 选择合适的测试规则
3. 点击"开始转换"按钮
4. 在右侧日志区域查看转换进度
5. 转换完成后预览思维导图
6. 下载生成的xmind文件或进行在线编辑

## 使用限制

- 仅支持.docx格式文件
- 单个文件大小限制为16MB
- 需要正确配置大模型API才能使用转换功能
- 转换质量取决于文档结构和大模型的能力

## 开发计划

- [ ] 转换接口
- [ ] 文档解析
- [ ] 模型调用
- [ ] 规范存储
- [ ] 预览内容
- [ ] 文档下载
- [ ] 失败重试
- [ ] xmind在线编辑

## 贡献
欢迎贡献代码和建议！请在GitHub上fork本项目，然后提交pull request。

## 许可证
本项目采用MIT许可证。


```
echo "# demo" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/wbbk/docx2xmindtool.git
git push -u origin main
```