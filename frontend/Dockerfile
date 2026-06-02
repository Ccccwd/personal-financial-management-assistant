# =============================================================================
# Stage: development — 开发环境（热重载，配合 compose volume 挂载）
# 构建：docker build --target development -t finance-frontend:dev ./frontend
# =============================================================================
FROM node:20-bookworm-slim AS development

WORKDIR /app

# 国内网络：使用 npmmirror，并增加拉包重试
ENV NPM_CONFIG_REGISTRY=https://registry.npmmirror.com \
    NPM_CONFIG_FETCH_RETRIES=5 \
    NPM_CONFIG_FETCH_RETRY_MINTIMEOUT=20000 \
    NPM_CONFIG_FETCH_RETRY_MAXTIMEOUT=120000

COPY package.json package-lock.json ./
# npm ci 在容器内常漏装 Rollup 平台包，需与 lock 中 rollup 版本一致显式安装
RUN npm ci \
    && npm install @rollup/rollup-linux-x64-gnu@4.60.0 --no-save

COPY . .

RUN apt-get update && apt-get install -y --no-install-recommends wget \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD wget -qO- http://127.0.0.1:3000/ || exit 1

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]

# =============================================================================
# Stage: builder — 构建静态资源（Debian glibc）
# =============================================================================
FROM node:20-bookworm-slim AS builder

WORKDIR /app

ENV NPM_CONFIG_REGISTRY=https://registry.npmmirror.com \
    NPM_CONFIG_FETCH_RETRIES=5 \
    NPM_CONFIG_FETCH_RETRY_MINTIMEOUT=20000 \
    NPM_CONFIG_FETCH_RETRY_MAXTIMEOUT=120000

COPY package.json package-lock.json ./
RUN npm ci \
    && npm install @rollup/rollup-linux-x64-gnu@4.60.0 --no-save

COPY . .

# 生产构建使用相对路径 /api，由 Nginx 反向代理至后端
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build

# =============================================================================
# Stage: production — Nginx 托管静态文件（默认目标，镜像 < 50MB）
# 构建：docker build -t finance-frontend:prod ./frontend
# =============================================================================
FROM nginxinc/nginx-unprivileged:1.27-alpine AS production

# 非 root 镜像（nginx 用户，监听 8080）
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://127.0.0.1:8080/health || exit 1
