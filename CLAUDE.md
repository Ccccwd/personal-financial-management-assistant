# 智能个人财务记账系统 - 项目规则

## 1. 项目概述

本项目是一个智能个人财务记账系统，旨在帮助用户进行日常收支记录、预算管理、数据统计和 AI 智能理财建议。系统采用前后端分离架构，支持微信账单导入和智能分类。

---

## 2. 技术栈

### 2.1 前端技术栈

| 类别 | 技术/库 | 版本 | 用途 |
|------|---------|------|------|
| 核心框架 | Vue 3 | ^3.4.0 | 构建用户界面的渐进式框架 |
| 构建工具 | Vite | ^5.0.0 | 快速冷启动与模块热替换 |
| 编程语言 | TypeScript | ~5.3.0 | 类型安全的 JavaScript 超集 |
| 路由管理 | Vue Router | ^4.2.0 | 单页面应用路由管理 |
| 状态管理 | Pinia | ^2.1.0 | 新一代 Vue 状态管理库 |
| UI 组件库 (移动端) | Vant | ^4.8.0 | 轻量级移动端 Vue 组件库 |
| UI 组件库 (桌面端) | Element Plus | ^2.4.0 | 基于 Vue 3 的组件库 |
| HTTP 客户端 | Axios | ^1.6.0 | 处理 API 请求与响应 |
| 图表库 | ECharts | ^5.4.0 | 数据可视化图表绘制 |
| 实用工具 | VueUse | ^10.7.0 | Vue 组合式 API 工具集 |
| 日期处理 | Day.js | ^1.11.0 | 轻量级日期时间处理库 |

### 2.2 后端技术栈

| 类别 | 技术/库 | 版本 | 用途 |
|------|---------|------|------|
| Web 框架 | FastAPI | ≥ 0.110 | HTTP 路由、依赖注入、自动文档 |
| ORM | SQLAlchemy | ≥ 2.0 | 数据库映射与查询 |
| 数据库迁移 | Alembic | ≥ 1.13 | 数据库版本管理 |
| 数据验证 | Pydantic v2 | ≥ 2.6 | 请求/响应 Schema 校验 |
| 关系型数据库 | MySQL | 8.0 | 主数据存储 |
| 缓存/Token 存储 | Redis | 7.x | JWT 黑名单、统计缓存 |
| 认证 | python-jose + passlib | — | JWT 生成验证、BCrypt 密码加密 |
| Excel 导出 | openpyxl | ≥ 3.1 | 账单 Excel 报表生成 |
| AI 大模型 | OpenAI SDK / DeepSeek API | — | 微信账单智能分类、理财建议生成 |
| 环境配置 | python-dotenv | — | 读取 `.env` 配置文件 |
| 测试 | pytest + httpx | — | 接口单元测试 |
| 服务器 | Uvicorn | — | ASGI 服务器 |

### 2.3 虚拟环境管理

| 工具 | 说明 |
|------|------|
| **uv** | Python 虚拟环境和依赖管理工具（项目统一使用） |

> **重要**：本项目后端统一使用 **uv** 创建和管理虚拟环境，不使用 `venv`、`virtualenv` 或 `conda`。

---

## 3. 目录结构

### 3.1 项目根目录

```
personal-financial-management-assistant/
├── frontend/                # 前端项目
├── backend/                 # 后端项目
├── docs/                    # 项目文档
│   ├── api.md              # API 接口设计文档
│   ├── architecture.md     # 架构设计文档
│   ├── backend.md          # 后端开发文档
│   ├── database.md         # 数据库设计文档
│   ├── design-spec.md      # 设计说明文档
│   ├── frontend.md         # 前端开发文档
│   └── design/             # 设计资源目录
│       └── contributions/  # 贡献记录
├── CLAUDE.md               # 项目规则文档（本文件）
└── README.md               # 项目说明
```

### 3.2 前端目录结构

```
frontend/
├── index.html                   # 应用入口 HTML
├── package.json                 # 项目依赖配置
├── tsconfig.json                # TypeScript 配置
├── vite.config.ts               # Vite 构建配置
├── public/                      # 静态资源目录
│
└── src/                         # 源代码目录
    ├── main.ts                  # 应用入口文件
    ├── App.vue                  # 根组件
    ├── env.d.ts                 # 类型声明文件
    │
    ├── api/                     # API 接口封装
    │   ├── account.ts           # 账户相关接口
    │   ├── auth.ts              # 认证相关接口
    │   ├── budget.ts            # 预算相关接口
    │   ├── transaction.ts       # 交易相关接口
    │   └── ...
    │
    ├── components/              # 公共组件
    │   └── ...
    │
    ├── layouts/                 # 页面布局组件
    │   └── ...
    │
    ├── router/                  # 路由配置
    │   └── index.ts
    │
    ├── stores/                  # Pinia 状态管理
    │   ├── user.ts              # 用户状态
    │   └── ...
    │
    ├── utils/                   # 工具函数
    │   ├── request.ts           # Axios 封装与拦截器
    │   ├── format.ts            # 格式化工具
    │   └── ...
    │
    ├── views/                   # 页面视图组件
    │   ├── auth/                # 认证页面
    │   ├── dashboard/           # 仪表盘
    │   ├── transaction/         # 交易页面
    │   ├── account/             # 账户页面
    │   ├── statistics/          # 统计页面
    │   ├── budget/              # 预算页面
    │   ├── import/              # 导入页面
    │   └── settings/            # 设置页面
    │
    └── styles/                  # 全局样式
        └── ...
```

### 3.3 后端目录结构

```
backend/
├── main.py                        # FastAPI 应用入口
├── .env                           # 环境变量配置
├── .env.example                   # 环境变量模板
├── pyproject.toml                 # 项目配置（uv 使用）
├── uv.lock                        # 依赖锁定文件
├── alembic.ini                    # Alembic 迁移配置
├── alembic/                       # 数据库迁移脚本
│   ├── env.py
│   └── versions/
│
└── app/
    ├── config/                    # 配置层
    │   ├── __init__.py
    │   ├── settings.py            # 全局配置
    │   ├── database.py            # 数据库引擎与 Session 工厂
    │   └── redis.py               # Redis 连接配置
    │
    ├── api/                       # 路由层（HTTP 接口定义）
    │   ├── __init__.py
    │   ├── auth.py                # 注册/登录/登出/Token 刷新
    │   ├── transactions.py        # 交易记录 CRUD、转账、汇总
    │   ├── categories.py          # 分类管理
    │   ├── accounts.py            # 账户管理
    │   ├── budgets.py             # 预算设置与监控
    │   ├── statistics.py          # 数据统计与报表导出
    │   └── wechat_bill.py         # 微信账单解析与导入
    │
    ├── models/                    # 数据库模型层（SQLAlchemy ORM）
    │   ├── __init__.py
    │   ├── user.py
    │   ├── transaction.py
    │   ├── category.py
    │   ├── account.py
    │   ├── budget.py
    │   ├── reminder.py
    │   └── import_log.py
    │
    ├── schemas/                   # 数据校验层（Pydantic Schema）
    │   ├── __init__.py
    │   ├── user.py
    │   ├── transaction.py
    │   ├── category.py
    │   ├── account.py
    │   ├── budget.py
    │   └── wechat_bill.py
    │
    ├── services/                  # 业务逻辑层
    │   ├── __init__.py
    │   ├── auth_service.py        # 注册，登录、Token 管理
    │   ├── transaction_service.py # 交易增删改、余额联动
    │   ├── statistics_service.py  # 统计聚合查询
    │   ├── budget_service.py      # 预算计算与预警
    │   ├── account_service.py     # 账户余额管理
    │   ├── wechat_bill_service.py # CSV 解析、重复检测、批量导入
    │   └── ai_service.py          # LLM 调用：智能分类 & 理财建议
    │
    ├── core/                      # 核心基础设施
    │   ├── __init__.py
    │   ├── security.py            # JWT 签发与校验、密码哈希
    │   ├── dependencies.py        # FastAPI 依赖注入
    │   └── exceptions.py          # 全局异常处理器
    │
    └── utils/                     # 工具函数
        ├── __init__.py
        ├── date_utils.py          # 日期范围计算工具
        └── excel_utils.py         # Excel 报表生成工具
```

---

## 4. 代码规范

### 4.1 通用规范

- **命名规范**
  - 文件名：小写字母，单词间用下划线分隔（snake_case）
  - 类名：大驼峰命名法（PascalCase）
  - 函数/方法名：小写字母，单词间用下划线分隔（snake_case）
  - 常量：全大写，单词间用下划线分隔（UPPER_SNAKE_CASE）
  - 变量：小写字母，单词间用下划线分隔（snake_case）

- **注释规范**
  - 所有公共函数必须添加文档字符串（docstring）
  - 复杂逻辑必须添加行内注释说明
  - 使用中文注释，保持清晰易懂

- **代码格式化**
  - 前端：ESLint + Prettier
  - 后端：Black + isort
  - 缩进：4 空格（Python）/ 2 空格（TypeScript/Vue）

### 4.2 前端代码规范

- **Vue 组件规范**
  - 使用 `<script setup>` 语法糖
  - 组件命名：大驼峰命名法（PascalCase）
  - Props 必须定义类型
  - 使用 TypeScript 类型注解

- **TypeScript 规范**
  - 禁止使用 `any` 类型，必须明确类型定义
  - 接口命名以 `I` 开头（如 `IUser`）
  - 类型别名使用大驼峰命名

- **API 调用规范**
  - 所有 API 调用统一放在 `src/api/` 目录
  - 使用 Axios 拦截器统一处理请求/响应
  - 错误处理统一使用 try-catch

### 4.3 后端代码规范

- **Python 代码规范**
  - 遵循 PEP 8 编码规范
  - 使用类型注解（Type Hints）
  - 函数最大长度：50 行
  - 类最大长度：300 行

- **FastAPI 规范**
  - 所有路由必须定义响应模型
  - 使用依赖注入获取数据库会话和当前用户
  - 异常统一使用 `HTTPException`

- **SQLAlchemy 规范**
  - 模型类必须继承 `Base`
  - 表名使用小写字母 + 下划线
  - 外键关系必须明确定义

### 4.4 数据库规范

- **表命名**：小写字母，单词间用下划线分隔，使用复数形式（如 `users`、`transactions`）
- **字段命名**：小写字母，单词间用下划线分隔
- **主键**：使用自增整数 `id`
- **外键**：使用 `{表名单数}_id` 格式（如 `user_id`、`category_id`）
- **时间字段**：使用 `created_at`、`updated_at` 命名
- **软删除**：使用 `is_deleted` 布尔字段

---

## 5. API 设计规范

### 5.1 RESTful API 规范

- **HTTP 方法语义**
  - `GET`：查询资源
  - `POST`：创建资源
  - `PUT`：完整更新资源
  - `PATCH`：部分更新资源
  - `DELETE`：删除资源

- **URL 规范**
  - 使用小写字母
  - 单词间用连字符分隔
  - 使用名词复数形式
  - 避免深层嵌套（最多 2 层）

- **统一响应格式**
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {}
  }
  ```

### 5.2 认证规范

- 使用 JWT Bearer Token 认证
- Access Token 有效期：30 分钟
- Refresh Token 有效期：7 天
- Token 黑名单存储在 Redis

### 5.3 分页规范

- 分页参数：`page`（页码，从 1 开始）、`page_size`（每页数量）
- 默认每页：20 条
- 最大每页：100 条

---

## 6. 禁止事项

### 6.1 安全禁止事项

- **禁止**在代码中硬编码敏感信息（密码、API Key、密钥等）
- **禁止**在日志中输出用户密码、Token 等敏感信息
- **禁止**在前端存储敏感信息（除必要的 Token）
- **禁止**使用明文存储用户密码（必须使用 BCrypt 加密）
- **禁止**绕过认证机制直接访问受保护资源
- **禁止**在 SQL 查询中拼接用户输入（防止 SQL 注入）
- **禁止**直接输出用户输入到页面（防止 XSS）

### 6.2 代码禁止事项

- **禁止**使用 `eval()`、`exec()` 等动态执行代码
- **禁止**在循环中进行数据库查询
- **禁止**提交未使用的代码和注释掉的代码
- **禁止**在业务代码中使用 `print()` 调试（使用 logging）
- **禁止**忽略异常处理
- **禁止**使用魔法数字（必须定义常量）

### 6.3 数据库禁止事项

- **禁止**在生产环境直接执行 DDL 操作
- **禁止**删除含有外键关联的数据
- **禁止**在没有事务的情况下执行多表操作
- **禁止**使用 `SELECT *` 查询（必须明确字段）

### 6.4 Git 禁止事项

- **禁止**直接提交到 `main` 分支（必须通过 PR 合并）
- **禁止**提交 `.env` 文件和敏感配置
- **禁止**提交大型二进制文件
- **禁止**使用 `--force` 推送到共享分支
- **禁止**提交未测试的代码

### 6.5 虚拟环境禁止事项

- **禁止**使用 `venv`、`virtualenv`、`conda` 创建虚拟环境
- **禁止**直接使用系统 Python 环境
- **禁止**提交 `.venv/` 虚拟环境目录到 Git

---

## 7. 虚拟环境管理规范（uv）

### 7.1 uv 环境初始化

```bash
# 进入后端目录
cd backend

# 使用 uv 初始化项目（如果尚未初始化）
uv init

# 创建虚拟环境
uv venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 7.2 依赖管理

```bash
# 安装所有依赖
uv sync

# 添加新依赖
uv add <package_name>

# 添加开发依赖
uv add --dev <package_name>

# 移除依赖
uv remove <package_name>

# 更新依赖
uv lock --upgrade
```

### 7.3 运行项目

```bash
# 使用 uv 运行脚本
uv run python main.py

# 使用 uv 运行 uvicorn
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 运行测试
uv run pytest tests/ -v
```

---

## 8. Git 工作流规范

### 8.1 分支命名

- `main`：主分支，生产环境代码
- `dev`：开发分支
- `feature/{功能名}`：功能开发分支
- `bugfix/{bug描述}`：Bug 修复分支
- `hotfix/{紧急修复描述}`：紧急修复分支

### 8.2 Commit 规范

使用约定式提交（Conventional Commits）：

- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `style:` 代码格式调整（不影响功能）
- `refactor:` 代码重构
- `perf:` 性能优化
- `test:` 测试相关
- `chore:` 构建配置等

示例：
```
feat: 添加微信账单导入功能
fix: 修复预算计算错误的 bug
docs: 更新 API 文档
```

---

## 9. 测试规范

### 9.1 单元测试

- 测试文件命名：`test_{模块名}.py`
- 测试函数命名：`test_{功能描述}`
- 覆盖率要求：核心业务逻辑 ≥ 80%

### 9.2 测试范围

- 所有 API 接口必须有测试用例
- 所有业务服务层方法必须有测试用例
- 复杂的数据处理逻辑必须有测试用例

---

## 10. 部署规范

### 10.1 环境配置

- 开发环境：`development`
- 测试环境：`staging`
- 生产环境：`production`

### 10.2 环境变量

所有环境变量必须在 `.env.example` 中列出并添加说明。

---

## 11. 文档规范

- 所有 API 接口必须更新 `docs/api.md`
- 所有架构变更必须更新 `docs/architecture.md`
- 所有数据库变更必须更新 `docs/database.md`
- 代码变更涉及设计规范时更新 `docs/design-spec.md`

---

## 12. 开发流程

1. 从 `dev` 分支创建功能分支
2. 使用 `uv venv` 创建虚拟环境并激活
3. 使用 `uv sync` 安装依赖
4. 编写代码和测试用例
5. 运行测试确保通过（`uv run pytest`）
6. 更新相关文档
7. 提交 PR 并等待 Code Review
8. Review 通过后合并到 `dev` 分支
9. 定期将 `dev` 合并到 `main` 进行发布
