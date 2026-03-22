# 个人贡献记录（03-架构）

## 本次贡献概述

- **贡献人：** 陈伟栋 (Cccccwd)
- **日期：** 2026-03-21 ~ 2026-03-22
- **任务来源：** 后端项目架构搭建、数据库设计、Docker 容器化部署支持

---

## 贡献一：后端项目架构与数据库设计（2026-03-21）

**Commit:** `072f029` - feat: add database design documentation for personal finance tracking system

### 1) 后端项目结构搭建

创建了完整的 FastAPI 后端项目结构：

```
backend/
├── main.py                    # FastAPI 应用入口
├── pyproject.toml             # uv 依赖管理配置
├── .env.example               # 环境变量模板
└── app/
    ├── config/                # 配置层（数据库、Redis、全局设置）
    ├── api/                   # 路由层（auth、health 等接口）
    ├── models/                # ORM 模型（user、account、transaction、budget、category）
    ├── schemas/               # Pydantic 数据校验
    ├── core/                  # 核心基础设施（安全、依赖注入、异常处理）
    └── services/              # 业务逻辑层（预留）
```

### 2) 数据库设计文档

完成 `docs/database.md` 和 `docs/architecture.md`：

- **ER 图设计**：用户、账户、交易记录、分类、预算五大核心实体
- **表结构定义**：字段类型、约束、索引策略
- **数据字典**：完整的字段说明文档
- **SQL 初始化脚本**：建表语句与初始分类数据

### 3) 核心模块实现

- **认证模块**：JWT Token 生成与校验、BCrypt 密码加密
- **数据库配置**：SQLAlchemy 异步连接池
- **Redis 配置**：Token 黑名单存储支持
- **全局异常处理**：统一错误响应格式

---

## 贡献二：Docker 容器化部署支持（2026-03-22）

**Commit:** `72f4e1a` - feat: 添加 Docker 支持和初始化数据库脚本

### 1) Docker Compose 配置

创建 `docker-compose.yml`：

- **MySQL 8.0**：字符集 utf8mb4、持久化存储、健康检查
- **Redis 7**：AOF 持久化、健康检查
- **网络隔离**：独立 bridge 网络 finance-network

### 2) 数据库初始化脚本

创建 `mysql/init/01-init.sql`：

- 自动创建数据库 `finance_db`
- 设置字符集和排序规则
- 支持 Docker 容器启动时自动执行

### 3) 环境变量配置

创建 `.env.docker`：

- MySQL root 密码配置
- 应用连接字符串参考

---

## 输出成果

| 文件 | 说明 |
|------|------|
| `docker-compose.yml` | Docker 容器编排配置 |
| `.env.docker` | Docker 环境变量模板 |
| `mysql/init/01-init.sql` | 数据库初始化脚本 |
| `docs/database.md` | 数据库设计文档 |
| `docs/architecture.md` | 系统架构文档 |
| `backend/` | 完整后端项目结构 |

---

## 自评

- 后端架构遵循分层设计原则，配置、路由、模型、服务职责清晰分离
- Docker 容器化支持一键启动开发环境，降低团队协作门槛
- 数据库设计文档完整，包含 ER 图、表结构、索引策略，为后续开发提供清晰参考
