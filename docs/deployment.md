# 部署说明文档

## 1. 部署架构

```
用户浏览器
  ├── 前端页面 → Vercel / 本地 Docker
  └── API 请求 → Railway（后端 + MySQL + Redis）
```

| 服务 | 平台 | 说明 |
|------|------|------|
| 后端 API | Railway | FastAPI + Dockerfile 部署 |
| MySQL | Railway | 内置 MySQL 服务 |
| Redis | Railway | 内置 Redis 服务 |
| 前端 | Vercel / 本地 | Vue 3 静态构建 |

## 2. 后端部署（Railway）

### 2.1 创建项目

1. 登录 [railway.app](https://railway.app)，使用 GitHub 账号
2. **New Project** → **Deploy from GitHub repo** → 选择仓库
3. 进入服务 → **Settings** → **Root Directory** 设为 `backend`

### 2.2 添加数据库服务

在项目中添加：
- **+ New** → **Database** → **MySQL**（自动创建）
- **+ New** → **Database** → **Redis**（自动创建）

### 2.3 环境变量配置

在 backend 服务的 **Variables** 中配置：

```bash
# 数据库（使用 Railway 变量引用，注意协议头是 mysql+pymysql）
DATABASE_URL=mysql+pymysql://${{MySQL.MYSQL_USER}}:${{MySQL.MYSQL_PASSWORD}}@${{MySQL.MYSQL_HOST}}:${{MySQL.MYSQL_PORT}}/${{MySQL.MYSQL_DATABASE}}

# Redis
REDIS_URL=${{Redis.REDIS_URL}}

# JWT 密钥（生成方式：python -c "import secrets; print(secrets.token_urlsafe(32))"）
SECRET_KEY=<随机强密钥>

# AI 配置
AI_API_KEY=<智谱AI API Key>
AI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
AI_MODEL=glm-5.1

# 应用环境
APP_ENV=production
DEBUG=false
```

### 2.4 部署配置文件

项目已包含以下配置文件：

| 文件 | 说明 |
|------|------|
| `backend/Dockerfile` | 多阶段构建，uv 安装依赖，非 root 用户 |
| `backend/railway.toml` | Railway 专用配置，指定 Dockerfile 构建和启动命令 |
| `backend/.dockerignore` | 排除无关文件 |

### 2.5 自动部署

Railway 已连接 GitHub 仓库，推送到 `main` 分支会自动触发重新部署。

### 2.6 验证

部署成功后访问：
- 健康检查：`https://<你的域名>.up.railway.app/api/health`
- API 文档：`https://<你的域名>.up.railway.app/redoc`

## 3. 前端部署（Vercel）

### 3.1 创建项目

1. 登录 [vercel.com](https://vercel.com)，使用 GitHub 账号
2. **Import Project** → 选择仓库
3. 配置：
   - **Framework Preset**: Vue.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 3.2 环境变量

在 Vercel 项目设置 → **Environment Variables** 中添加：

```bash
VITE_API_BASE_URL=https://<你的Railway后端域名>.up.railway.app/api
```

> **注意**：`VITE_API_BASE_URL` 必须是完整的后端 API 地址，以 `/api` 结尾。

### 3.3 自动部署

Vercel 已连接 GitHub，推送到 `main` 分支自动部署。

## 4. 本地 Docker 部署

### 4.1 开发环境

```bash
# 一键启动（后端 + MySQL + Redis）
docker compose up -d --build

# 查看服务状态
docker compose ps

# 前端单独启动
cd frontend && npm run dev
```

服务地址：
- 后端 API：http://localhost:8000
- MySQL：localhost:3307
- Redis：localhost:6379
- 前端：http://localhost:3000

### 4.2 生产环境

```bash
# 创建 secrets
mkdir -p secrets
echo "强密码" > secrets/db_password.txt

# 启动生产配置
docker compose -f compose.prod.yaml up -d --build
```

## 5. CORS 配置

后端默认允许所有来源（`allow_origins=["*"]`），生产环境建议限制为前端域名。

修改 `backend/main.py`：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://你的前端域名.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 6. 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 健康检查失败 | `$PORT` 未展开 | railway.toml 使用 `sh -c` 包裹启动命令 |
| 数据库连接失败 | URL 格式错误 | 确保用 `mysql+pymysql://` 不是 `mysql://` |
| 前端 API 404 | 环境变量未设 | Vercel 设置 `VITE_API_BASE_URL` |
| Swagger UI 空白 | CDN 被墙 | 改用 `/redoc` 或使用 VPN |

## 7. 在线地址

- 后端 API：[Railway 部署后填写]
- 前端页面：[Vercel 部署后填写]
- API 文档：[后端地址]/redoc
