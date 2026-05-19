# Docker 部署贡献说明

姓名：曾昭祥  
学号：2312190219  
日期：2026-05-19

## 我完成的工作

### 1. Dockerfile 编写

- [x] 前端 Dockerfile（多阶段构建）
- [ ] 后端 Dockerfile（多阶段构建，由陈伟栋完成）
- [x] `.dockerignore` 文件

**Dockerfile 要点：**

| 构建目标 | 说明 |
|---------|------|
| `development` | Node 20 Alpine，`npm ci` + Vite 热重载，暴露 `3000` |
| `builder` | 编译 Vue 静态资源，构建时注入 `VITE_API_BASE_URL=/api` |
| `production`（默认） | `nginxinc/nginx-unprivileged` 托管 `dist/`，**非 root** 用户，监听 **8080** |

- 多阶段构建：构建依赖不进入最终镜像，目标体积 **< 50MB**
- 生产镜像内置 `HEALTHCHECK`，检测 `/health` 端点
- Nginx 将 `/api/` 反向代理至 Compose 网络内 `backend:8000`

### 2. Compose 配置

- [ ] 开发环境 `compose.yaml`（由后端同学维护，见下方集成说明）
- [ ] 生产环境 `compose.prod.yaml`
- [x] 前端服务健康检查配置（`frontend/Dockerfile` + `nginx/default.conf`）

### 3. 自动化部署

- 选择了选项 A / B：**前端镜像构建命令已就绪**；GHCR 推送与工作流扩展需团队在后端 `.github/workflows/docker.yml` 中增加 `frontend` job（本次仅修改 `frontend/` 目录）

## 文件清单

| 文件 | 说明 |
|------|------|
| `frontend/Dockerfile` | 三阶段：`development` / `builder` / `production` |
| `frontend/.dockerignore` | 排除 `node_modules`、测试、`.env` 等 |
| `frontend/nginx/default.conf` | SPA 路由、`/health`、`/api` 反向代理 |
| `frontend/.env.example` | `VITE_API_BASE_URL`、`VITE_PROXY_TARGET` 模板 |
| `frontend/vite.config.ts` | `VITE_PROXY_TARGET` 支持，容器内 `host: true` |
| `frontend/src/env.d.ts` | Vite 环境变量类型声明 |
| `frontend/src/api/request.ts` | `baseURL` 读取 `VITE_API_BASE_URL`，默认 `/api` |

## 本地验证命令

```bash
# 生产镜像构建（默认 production 阶段）
docker build -t finance-frontend:prod ./frontend

# 开发镜像构建（热重载）
docker build --target development -t finance-frontend:dev ./frontend

# 查看镜像体积（应明显小于 50MB 的 Node 全量镜像）
docker images finance-frontend:prod

# 单独运行生产前端（需后端在同一 Docker 网络，且服务名为 backend）
docker network create finance-network 2>/dev/null || true
docker run -d --name finance-frontend -p 3000:8080 --network finance-network finance-frontend:prod

# 健康检查与静态页
docker inspect --format='{{.State.Health.Status}}' finance-frontend
curl http://localhost:3000/health
curl -I http://localhost:3000/
```

## 与 Compose 集成说明（供团队合并）

当前根目录 `compose.yaml` 由后端同学配置。前端服务可按下列片段加入（**需后端同学在 PR 中合并**）：

**开发环境 `compose.yaml` 追加：**

```yaml
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: development
    container_name: finance-frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_PROXY_TARGET=http://backend:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      backend:
        condition: service_started
    networks:
      - finance-network
```

**生产环境 `compose.prod.yaml` 追加：**

```yaml
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: production
    container_name: finance-frontend-prod
    restart: unless-stopped
    ports:
      - "80:8080"
    depends_on:
      backend:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://127.0.0.1:8080/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 128M
    networks:
      - finance-network
```

浏览器访问：`http://localhost:3000`（开发）或 `http://localhost`（生产映射 80 端口时）。

## PR 链接

- PR #20: https://github.com/Ccccwd/personal-financial-management-assistant/pull/20 （`feature/曾昭祥-frontend-doc` → `dev`，前端 Docker 容器化）
- PR #21: https://github.com/Ccccwd/personal-financial-management-assistant/pull/21 （`dev` → `main`，同步至主分支）

## 遇到的问题和解决

1. **问题**：原 `frontend/Dockerfile` 为单阶段 Node 镜像，仅适合 `npm run dev`，不符合「多阶段构建 + 镜像体积 < 50MB」要求。  
   **解决**：拆分为 `development`（Node 热重载）+ `builder`（编译）+ `production`（Nginx 非特权镜像托管静态资源）。

2. **问题**：生产环境 Axios 的 `baseURL` 需与 Nginx 代理路径一致。  
   **解决**：构建参数 `VITE_API_BASE_URL=/api`，与 `nginx/default.conf` 中 `location /api/` 及 `request.ts` 默认值对齐。

3. **问题**：开发容器内 Vite 代理仍指向 `127.0.0.1:8000`，无法访问 Compose 中的 `backend` 服务。  
   **解决**：`vite.config.ts` 增加 `VITE_PROXY_TARGET` 环境变量，容器内设为 `http://backend:8000`。

4. **问题**：`npm run build`（含 `vue-tsc`）在 Docker 构建阶段失败。  
   **解决**：补齐测试 mock 的 `account_id` 字段，并修正 `AccountDetail.vue` 模板中的类型索引写法，保证 `builder` 阶段可通过类型检查。

## AI 使用情况

- 使用了哪些 Prompt：Docker 前端多阶段构建、nginx-unprivileged 非 root 部署、Vite 环境变量与 Nginx 反向代理配置  
- AI 帮助解决了哪些问题：三阶段 Dockerfile 结构、健康检查端点设计、Compose 集成片段编写  

## 心得体会

本次实践明确了前端容器化的两条路径：开发阶段用 Node + Vite 热重载保证体验，生产阶段用 Nginx 托管构建产物以缩小镜像并提升安全性。通过构建时注入 `VITE_API_BASE_URL` 与运行时 Nginx 反向代理的配合，实现了「浏览器只访问同源 `/api`」的部署模式，避免硬编码后端地址，便于与后端 Docker 网络协同。
