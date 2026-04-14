# 后端开发贡献说明

姓名：陈伟东
学号：XXXXXX
日期：2026-04-11

## 我完成的工作

### API 实现

- [x] 用户认证 API（注册 / 登录 / 获取当前用户信息）
- [x] 分类管理 CRUD：列表查询（支持类型过滤、系统分类）、树形结构、带统计分类、详情、创建、更新、删除（7 个端点）
- [x] 账户管理 CRUD：列表查询、统计摘要、默认账户、详情（含收支统计）、创建、更新、删除、账户间转账、余额调整（9 个端点）
- [x] 交易记录 CRUD：分页列表（支持多条件筛选排序）、统计摘要、关键词搜索、详情、创建（自动更新余额）、更新（回退+重算余额）、删除（回退余额）、标记重复（8 个端点）
- [x] 预算管理 CRUD：列表（含实时进度计算）、创建（唯一性校验）、详情（含进度）、更新、删除（5 个端点）
- [x] 统计分析 API：首页概览（月度汇总、增长率、分类分布、趋势）、趋势分析（日/周/月/年）、分类统计、Excel 导出（4 个端点）
- [x] 健康检查 API
- [x] 统一错误响应格式（全局异常处理器处理 Pydantic 校验错误、数据库错误、通用异常）

### 数据验证（Pydantic Schema）

- [x] 通用响应 Schema（Response、PaginatedResponse）
- [x] 用户 Schema（UserCreate、UserLogin、UserResponse、TokenResponse）
- [x] 分类 Schema（CategoryCreate、CategoryUpdate、CategoryResponse、CategoryTreeResponse）
- [x] 账户 Schema（AccountCreate、AccountUpdate、AccountResponse、TransferRequest、BalanceAdjustRequest）
- [x] 交易 Schema（TransactionCreate、TransactionUpdate、TransactionResponse、TransactionSummaryResponse）
- [x] 预算 Schema（BudgetCreate、BudgetUpdate、BudgetResponse、BudgetWithProgress）
- [x] 统计 Schema（MonthlySummary、CategoryDistribution、TrendDataPoint 等）

### 数据库

- [x] 数据模型定义（User、Transaction、Category、Account、Budget、ImportLog）
- [x] ORM 配置（SQLAlchemy 引擎、Session 工厂、声明式基类）
- [x] 数据库迁移配置（Alembic）

### 测试

- [x] pytest 测试框架搭建（SQLite 内存数据库 + TestClient）
- [x] 认证测试（注册、登录、Token 验证）
- [x] 分类管理测试（20 个用例：创建/查询/树形/统计/更新/删除/权限校验）
- [x] 账户管理测试（26 个用例：创建/列表/摘要/默认账户/详情/更新/转账/余额调整/删除）
- [x] 全部 46 个测试用例通过

### Postman 测试集合

- [x] 覆盖全部 API 的 Postman 测试集合（33 个测试用例）
- [x] 包含认证、分类、账户、交易、预算、统计、健康检查 7 大模块
- [x] 环境变量自动传递（Token、ID 等在请求间自动传递）

### 文档

- [x] OpenAPI 3.0 规范文档（docs/api.yaml）
- [x] Postman 导入文件（docs/postman_collection.json + postman_environment.json）

## PR 链接

- PR #X: https://github.com/Ccccwd/personal-financial-management-assistant/pull/X（待提交）

## 遇到的问题和解决

1. **问题**：bcrypt/passlib 版本不兼容，密码验证报 ValueError "password cannot be longer than 72 bytes"
   **解决**：弃用 passlib，直接使用 bcrypt 库的 `hashpw` 和 `checkpw` 方法

2. **问题**：JWT 的 sub 字段必须为字符串，传入整数导致 JWTClaimsError
   **解决**：在创建 Token 时将 `user.id` 转为字符串 `str(user.id)`，解析时再 `int()` 转回

3. **问题**：测试中余额断言失败，API 返回 `"1000.00"` 字符串与预期 `1000` 不匹配
   **解决**：统一使用 `float()` 转换后进行数值比较

4. **问题**：test_user fixture 在重复运行时注册失败（用户已存在）
   **解决**：改为先尝试注册（忽略已存在错误），再登录获取用户信息

## 心得体会

在本次后端开发中，我完整实现了基于 FastAPI + SQLAlchemy 的 RESTful API 体系，涵盖了认证、分类、账户、交易、预算、统计六大业务模块，共计 34 个 API 端点。过程中深入理解了 JWT 认证机制、Pydantic 数据校验、ORM 模型设计以及依赖注入模式。测试方面，通过 pytest + SQLite 内存数据库实现了 46 个自动化测试用例，确保了接口的正确性。同时编写了覆盖全部 API 的 Postman 测试集合，方便团队进行手动验证。
