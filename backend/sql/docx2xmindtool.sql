-- 创建数据库
CREATE DATABASE IF NOT EXISTS docx2xmindtool DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE docx2xmindtool;

-- 创建API配置表
CREATE TABLE IF NOT EXISTS api_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    api_key VARCHAR(255) NOT NULL COMMENT 'API密钥',
    api_url VARCHAR(255) NOT NULL COMMENT 'API请求地址',
    model VARCHAR(50) NOT NULL COMMENT '模型名称',
    type VARCHAR(20) DEFAULT 'normal' COMMENT '模型类型：normal-普通模型，vision-图像识别模型',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='API配置表';

-- 创建用户并授权
CREATE USER IF NOT EXISTS 'docx2xmindtool'@'%' IDENTIFIED BY 'bNRM2rB8Ccjm6tAK';
GRANT ALL PRIVILEGES ON docx2xmindtool.* TO 'docx2xmindtool'@'%';
FLUSH PRIVILEGES;