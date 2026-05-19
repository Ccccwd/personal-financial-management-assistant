# Docker 部署贡献说明

姓名：陈伟栋
学号：2312190218
日期：2026-05-13

## 我完成的工作

### 1. Dockerfile 编写

- [x] 后端 Dockerfile（多阶段构建）
- [x] .dockerignore 文件

**Dockerfile 要点：**
- 使用 `python:3.12-slim` 基础镜像，减小镜像体积
- 多阶段构建：Stage 1（builder）使用 uv 安装依赖，Stage 2（runtime）仅复制虚拟环境
- 非 root 用户 `appuser` 运行容器
- 内置 HEALTHCHECK，检测 `/api/health` 端点
- 使用 `uv sync --frozen` 保证依赖一致性

### 2. Compose 配置

- [x] 开发环境 compose.yaml
- [x] 生产环境 compose.prod.yaml
- [x] 健康检查配置

**compose.yaml（开发）：** backend + MySQL 8.0 + Redis 7，volume 挂载支持热重载，services 间 healthcheck 依赖管理

**compose.prod.yaml（生产）：** 资源限制（backend 512M/1CPU, MySQL 512M, Redis 128M）、Docker secrets 管理数据库密码、json-file 日志轮转（10m × 3）、restart: unless-stopped

### 3. 自动化部署

选择了选项 A + B：

- **选项 A**：`.github/workflows/docker.yml` — 推送到 main 分支时自动构建镜像并推送到 GHCR，集成 Trivy 安全扫描（CRITICAL/HIGH 级别），使用 GHA cache 加速构建
- **选项 B**：`deploy.sh` — 一键本地部署脚本，支持 `dev` / `prod` 两种模式，自动创建 secrets 和 .env，内置健康检查验证

## 文件清单

| 文件 | 说明 |
|------|------|
| `backend/Dockerfile` | 多阶段构建，uv 安装依赖，非 root 运行 |
| `backend/.dockerignore` | 排除 .venv、tests、.env 等 |
| `compose.yaml` | 开发环境（backend + MySQL + Redis） |
| `compose.prod.yaml` | 生产环境（资源限制 + secrets + 日志轮转） |
| `deploy.sh` | 一键部署脚本 |
| `.github/workflows/docker.yml` | CI 构建 + Trivy 扫描 |

## 遇到的问题和解决

1. **问题**：项目使用 uv 管理依赖而非 pip，传统 Dockerfile 的 `pip install -r requirements.txt` 不适用
   **解决**：使用 `COPY --from=ghcr.io/astral-sh/uv:latest` 拷贝 uv 二进制，再用 `uv sync --frozen --no-dev` 安装依赖到虚拟环境

2. **问题**：开发环境需要代码热重载
   **解决**：compose.yaml 中使用 `volumes: ./backend:/app` 挂载源码目录，配合 uvicorn 的 `--reload` 参数

3. **问题**：生产环境需要安全的密码管理
   **解决**：使用 Docker Secrets（`MYSQL_ROOT_PASSWORD_FILE`）+ `.env` 文件，secrets/db_password.txt 首次自动生成随机密码

## AI 使用情况

- 使用了哪些 Prompt：Docker 多阶段构建、uv 集成到 Dockerfile、Docker Compose 健康检查与依赖管理
- AI 帮助解决了哪些问题：uv 与 Docker 的集成方式、多阶段构建优化、Compose V2 语法

## 心得体会

通过本次 Docker 容器化实践，掌握了多阶段构建减小镜像体积的技巧，理解了 Docker Compose 的服务编排与健康检查机制，以及 GitHub Actions 自动化构建 CI/CD 流程的搭建方法。
