-- 初始化数据库字符集
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- 确保数据库存在
CREATE DATABASE IF NOT EXISTS finance_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE finance_db;

-- 授予所有权限（如需创建其他用户可在此添加）
-- CREATE USER IF NOT EXISTS 'finance_user'@'%' IDENTIFIED BY 'your_password';
-- GRANT ALL PRIVILEGES ON finance_db.* TO 'finance_user'@'%';
-- FLUSH PRIVILEGES;
