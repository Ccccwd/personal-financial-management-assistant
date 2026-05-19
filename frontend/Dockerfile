# =============================================================================
# Stage: development — 开发环境（热重载，配合 compose volume 挂载）
# 构建：docker build --target development -t finance-frontend:dev ./frontend
# =============================================================================
FROM node:20-alpine AS development

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD wget -qO- http://127.0.0.1:3000/ || exit 1

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]

# =============================================================================
# Stage: builder — 构建静态资源
# =============================================================================
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

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
