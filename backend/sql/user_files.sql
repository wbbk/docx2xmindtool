-- 创建用户文件表
CREATE TABLE IF NOT EXISTS user_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    original_filename VARCHAR(255) NOT NULL COMMENT '原始文件名',
    file_path VARCHAR(512) NOT NULL COMMENT '文件路径',
    file_size BIGINT NOT NULL COMMENT '文件大小(字节)',
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户文件表';