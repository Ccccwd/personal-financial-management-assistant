# 后端开发文档

## 目录

- [技术选型](#技术选型)
- [模块功能说明](#模块功能说明)
- [目录结构](#目录结构)
- [数据库设计](#数据库设计)
- [核心 API 接口](#核心-api-接口)
- [运行方式](#运行方式)

---

## 技术选型

| 类别 | 技术 / 库 | 版本建议 | 用途 |
|------|-----------|----------|------|
| Web 框架 | FastAPI | ≥ 0.110 | HTTP 路由、依赖注入、自动文档 |
| ORM | SQLAlchemy | ≥ 2.0 | 数据库映射与查询 |
| 数据库迁移 | Alembic | ≥ 1.13 | 数据库版本管理 |
| 数据验证 | Pydantic v2 | ≥ 2.6 | 请求 / 响应 Schema 校验 |
| 关系型数据库 | MySQL | 8.0 | 主数据存储 |
| 缓存 / Token 存储 | Redis | 7.x | JWT 黑名单、统计缓存 |
| 认证 | python-jose + passlib | — | JWT 生成验证、BCrypt 密码加密 |
| Excel 导出 | openpyxl | ≥ 3.1 | 账单 Excel 报表生成 |
| AI 大模型 | OpenAI SDK / DeepSeek API | — | 微信账单智能分类、理财建议生成 |
| 环境配置 | python-dotenv | — | 读取 `.env` 配置文件 |
| 测试 | pytest + httpx | — | 接口单元测试 |
| 服务器 | Uvicorn | — | ASGI 服务器 |

---

## 模块功能说明

### 1. 用户认证模块（`api/auth.py`）

负责用户注册、登录、登出及 Token 管理。

- **用户注册**：接收邮箱/用户名/密码，BCrypt 加密后入库，返回用户信息。
- **用户登录**：校验密码，签发 Access Token（短效）与 Refresh Token（长效），Refresh Token 存入 Redis。
- **Token 刷新**：使用 Refresh Token 换取新 Access Token。
- **用户登出**：将当前 Access Token 加入 Redis 黑名单，使其立即失效。
- **个人信息编辑**：更新用户名、头像等基本信息。

### 2. 交易记录模块（`api/transactions.py`）

核心记账功能，管理收入、支出、转账三类交易。

- **新增交易**：写入交易记录，同步更新对应账户余额。
- **查询交易列表**：支持多条件筛选（时间范围、分类、账户、收支类型、金额区间、关键词）及分页。
- **编辑 / 删除交易**：修改后自动回滚并重算账户余额。
- **账户转账**：在事务中完成转出账户扣减、转入账户增加、转账记录写入三步操作。
- **交易汇总**：返回指定时段的总收入、总支出、结余。

### 3. 分类管理模块（`api/categories.py`）

管理系统预设分类与用户自定义分类。

- 支持收入 / 支出两类，支持二级分类（`parent_id`）。
- 系统预设分类（`is_system=True`）仅管理员可修改，用户可新增自定义分类。
- 提供分类图标与颜色字段，供前端渲染。

### 4. 账户管理模块（`api/accounts.py`）

管理用户的多个资金账户（现金、银行卡、微信、支付宝等）。

- **账户 CRUD**：新增、编辑、删除账户，支持设置默认账户。
- **余额查询**：返回各账户实时余额及总资产。
- **账户流水**：按账户筛选该账户下的所有交易记录。

### 5. 预算管理模块（`api/budgets.py`）

支持月度总预算与各分类独立预算。

- **设置预算**：按年月为某分类（或全局）设置金额上限及预警阈值（百分比）。
- **预算进度查询**：实时计算当前周期内已用金额及占比。
- **预警判断**：已用金额达到阈值时在响应中标记预警状态（`warning` / `exceeded`）。

### 6. 数据统计模块（`api/statistics.py`）

提供多维度统计数据，驱动前端图表。

- **首页概览**：当月收入、支出、结余及环比变化率。
- **趋势数据**：按日 / 周 / 月聚合的收支趋势，用于折线图。
- **分类占比**：各分类支出金额与百分比，用于饼图。
- **收支对比**：最近 N 个月的月度收支柱状图数据。
- **消费排行**：单笔金额 TOP10、消费频次最高分类。
- **Excel 导出**：生成包含账单明细与统计汇总两个 Sheet 的 `.xlsx` 文件。

### 7. 微信账单导入模块（`api/wechat_bill.py`）

解析用户从微信导出的 CSV 账单文件并批量导入。

- **CSV 解析**：跳过微信账单头部信息，逐行解析交易时间、交易对方、商品名称、收支类型、金额、支付方式等字段。
- **重复检测**：通过 `wechat_transaction_id` 去重，避免重复导入。
- **导入预览**：解析后先返回预览数据，用户确认后再正式写入。
- **批量导入**：支持选择性导入，返回成功数、重复数、失败数统计。
- **导入日志**：每次导入结果写入 `import_logs` 表。

### 8. AI 智能服务模块（`services/ai_service.py`）

接入大语言模型，提供两项核心 AI 能力。

#### 8.1 账单智能分类

- 将微信账单行中的**商户名称**、**商品名称**、**微信原始分类**拼装为结构化 prompt，调用 LLM（DeepSeek-Chat / GPT-4o）返回系统分类名称。
- 内置关键词规则作为前置过滤，命中规则的直接映射，降低 API 调用量。
- LLM 返回结果经 Pydantic 校验后写入 `category_id`，无法识别时降级为"其他"。

**Prompt 示例：**
```
你是一个个人财务分类助手。请根据以下消费信息，将其归类到指定分类之一。

消费信息：
- 商户名称：瑞幸咖啡
- 商品描述：生椰拿铁
- 微信原始分类：餐饮美食

可选分类：餐饮、交通、娱乐、购物、学习、医疗、居住、通讯、社交、美容、运动、宠物、其他

只需返回分类名称，不要附加任何解释。
```

#### 8.2 个性化理财建议

- 汇总用户近 1~3 个月的分类支出数据、预算执行情况、消费趋势作为上下文。
- 调用 LLM 生成结构化分析报告，包含：消费亮点、超支警示、优化建议、下月预算参考。
- 结果以 Markdown 格式返回，前端直接渲染展示。

---

## 目录结构

```
backend/
├── main.py                        # FastAPI 应用入口，注册路由与中间件
├── .env                           # 环境变量（数据库连接、密钥、AI API Key 等）
├── .env.example                   # 环境变量模板
├── requirements.txt               # Python 依赖列表
├── alembic.ini                    # Alembic 迁移配置
├── alembic/                       # 数据库迁移脚本
│   ├── env.py
│   └── versions/
│
├── app/
│   ├── config/                    # 配置层
│   │   ├── __init__.py
│   │   ├── settings.py            # 全局配置（读取 .env）
│   │   ├── database.py            # 数据库引擎与 Session 工厂
│   │   └── redis.py               # Redis 连接配置
│   │
│   ├── api/                       # 路由层（HTTP 接口定义）
│   │   ├── __init__.py
│   │   ├── auth.py                # 注册 / 登录 / 登出 / Token 刷新
│   │   ├── transactions.py        # 交易记录 CRUD、转账、汇总
│   │   ├── categories.py          # 分类管理
│   │   ├── accounts.py            # 账户管理
│   │   ├── budgets.py             # 预算设置与监控
│   │   ├── statistics.py          # 数据统计与报表导出
│   │   └── wechat_bill.py         # 微信账单解析与导入
│   │
│   ├── models/                    # 数据库模型层（SQLAlchemy ORM）
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── transaction.py
│   │   ├── category.py
│   │   ├── account.py
│   │   ├── budget.py
│   │   ├── reminder.py
│   │   └── import_log.py
│   │
│   ├── schemas/                   # 数据校验层（Pydantic Schema）
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── transaction.py
│   │   ├── category.py
│   │   ├── account.py
│   │   ├── budget.py
│   │   └── wechat_bill.py
│   │
│   ├── services/                  # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py        # 注册、登录、Token 管理
│   │   ├── transaction_service.py # 交易增删改、余额联动
│   │   ├── statistics_service.py  # 统计聚合查询
│   │   ├── budget_service.py      # 预算计算与预警
│   │   ├── account_service.py     # 账户余额管理
│   │   ├── wechat_bill_service.py # CSV 解析、重复检测、批量导入
│   │   └── ai_service.py          # LLM 调用：智能分类 & 理财建议
│   │
│   ├── core/                      # 核心基础设施
│   │   ├── __init__.py
│   │   ├── security.py            # JWT 签发与校验、密码哈希
│   │   ├── dependencies.py        # FastAPI 依赖注入（获取当前用户、DB Session）
│   │   └── exceptions.py          # 全局异常处理器
│   │
│   └── utils/                     # 工具函数
│       ├── __init__.py
│       ├── date_utils.py          # 日期范围计算工具
│       └── excel_utils.py         # Excel 报表生成工具
│
└── tests/                         # 测试
    ├── __init__.py
    ├── conftest.py                # 测试夹具（测试 DB、测试客户端）
    ├── test_auth.py
    ├── test_transactions.py
    ├── test_statistics.py
    └── test_ai_service.py
```

---

## 数据库设计

主要数据表及关系如下：

```
users ──┬── accounts          (一对多，user_id)
        ├── transactions       (一对多，user_id)
        ├── budgets            (一对多，user_id)
        ├── reminders          (一对多，user_id)
        └── import_logs        (一对多，user_id)

categories ── transactions    (一对多，category_id)
categories ── budgets         (一对多，category_id)

accounts ── transactions      (一对多，account_id / to_account_id)
```

> 完整建表 SQL 参见 `alembic/versions/` 中的迁移文件。

---

## 核心 API 接口

### 认证

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录，返回 Token |
| POST | `/api/auth/logout` | 用户登出 |
| POST | `/api/auth/refresh-token` | 刷新 Access Token |

### 交易记录

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/transactions` | 获取交易列表（多条件筛选 + 分页） |
| POST | `/api/transactions` | 新增交易 |
| GET | `/api/transactions/{id}` | 获取交易详情 |
| PUT | `/api/transactions/{id}` | 更新交易 |
| DELETE | `/api/transactions/{id}` | 删除交易 |
| POST | `/api/transactions/transfer` | 账户间转账 |
| GET | `/api/transactions/summary` | 获取指定时段汇总 |

### 统计

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/statistics/overview` | 首页概览（收支结余 + 环比） |
| GET | `/api/statistics/trend` | 收支趋势折线图数据 |
| GET | `/api/statistics/category` | 分类占比饼图数据 |
| GET | `/api/statistics/monthly-report` | 月度报表 |
| GET | `/api/statistics/export/excel` | 导出 Excel |

### 预算

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/budgets` | 获取预算列表及执行进度 |
| POST | `/api/budgets` | 新增预算 |
| PUT | `/api/budgets/{id}` | 修改预算 |
| DELETE | `/api/budgets/{id}` | 删除预算 |

### 微信账单导入

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/wechat-bill/parse` | 上传 CSV，返回解析预览数据 |
| POST | `/api/wechat-bill/import` | 确认并批量导入选中记录 |

### AI 智能服务

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/ai/classify` | 对单条或批量账单进行智能分类 |
| GET | `/api/ai/advice` | 生成当月个性化理财建议报告 |

---

## 运行方式

### 环境要求

- Python 3.11+
- MySQL 8.0
- Redis 7.x

### 1. 克隆项目并进入后端目录

```bash
cd backend
```

### 2. 创建并激活虚拟环境

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制模板文件并填写实际配置：

```bash
cp .env.example .env
```

`.env` 配置项说明：

```ini
# 数据库
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/finance_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI 大模型（二选一或同时配置）
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
OPENAI_API_KEY=your_openai_api_key

# 应用
APP_ENV=development
```

### 5. 初始化数据库

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE finance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 执行迁移（初始化表结构）
alembic upgrade head
```

### 6. 启动开发服务器

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后访问：

- **API 文档（Swagger UI）：** http://localhost:8000/docs
- **API 文档（ReDoc）：** http://localhost:8000/redoc

### 7. 运行测试

```bash
pytest tests/ -v
```

