# 云服务部署贡献说明

姓名：陈伟栋
学号：2312190218
日期：2026-05-30

## 我完成的工作

### 1. 平台选择

- 使用平台：**Railway**（后端 + MySQL + Redis）
- 前端推荐部署平台：**Vercel**

### 2. 部署配置

- [x] 配置文件编写（Dockerfile、railway.toml、.dockerignore）
- [x] 环境变量配置（DATABASE_URL、REDIS_URL、SECRET_KEY、AI_API_KEY 等）
- [x] 自动部署配置（Railway 连接 GitHub，推送 main 自动部署）
- [x] 健康检查配置（/api/health 端点）

### 3. 部署文件清单

| 文件 | 说明 |
|------|------|
| `backend/Dockerfile` | 多阶段构建，uv 管理依赖，非 root 用户运行 |
| `backend/railway.toml` | Railway 配置，Dockerfile 构建模式，动态 PORT |
| `backend/.dockerignore` | 排除 .venv、tests、.env 等 |
| `compose.yaml` | 开发环境 Docker Compose（backend + MySQL + Redis） |
| `compose.prod.yaml` | 生产环境配置（资源限制 + secrets + 日志轮转） |
| `deploy.sh` | 本地一键部署脚本 |
| `docs/deployment.md` | 部署说明文档 |

### 4. 问题解决

1. **问题**：Railway 使用 Railpack 构建器无法识别项目
   **解决**：设置 Root Directory 为 `backend`，创建 `railway.toml` 指定 Dockerfile 构建模式

2. **问题**：`$PORT` 环境变量未被展开，uvicorn 报错 `'$PORT' is not a valid integer`
   **解决**：`railway.toml` 的 startCommand 用 `sh -c` 包裹，使 shell 正确展开 `$PORT`

3. **问题**：Docker Compose 开发环境 volume 挂载覆盖容器内 .venv
   **解决**：添加匿名卷 `/app/.venv` 保留容器内构建的虚拟环境

4. **问题**：GitHub Actions 构建推送镜像失败（cache export 不支持）
   **解决**：添加 `docker/setup-buildx-action@v3` 设置 buildx builder

5. **问题**：Trivy 扫描失败，镜像名包含大写字母
   **解决**：使用 `tr '[:upper:]' '[:lower:]'` 将镜像名强制转小写

## PR 链接

- PR 链接待合并后填写

## 在线地址

- 后端 API：待 Railway 部署成功后填写
- 前端页面：待 Vercel 部署后填写

## 心得体会

通过本次云服务部署实践，掌握了以下技能：
- Railway 平台的 Dockerfile 部署方式，理解了 Root Directory、环境变量引用语法 `${{Service.VAR}}` 的使用
- Docker 容器化部署中端口动态分配（`$PORT`）的处理方式
- 前后端分离架构的云端部署：后端部署在 Railway，前端部署在 Vercel，通过 API 地址连接
- GitHub Actions CI/CD 流程中 Docker 镜像构建、推送和 Trivy 安全扫描的集成
