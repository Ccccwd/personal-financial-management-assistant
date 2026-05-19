#!/bin/bash
set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 智能个人财务记账系统 - 开始部署...${NC}"

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误：Docker 未安装，请先安装 Docker${NC}"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}错误：Docker Compose V2 未安装${NC}"
    exit 1
fi

# 创建 secrets 目录（生产环境）
if [ ! -d "secrets" ]; then
    mkdir -p secrets
    echo -e "${YELLOW}⚠ 已创建 secrets 目录，请填写 secrets/db_password.txt${NC}"
fi

if [ ! -f "secrets/db_password.txt" ]; then
    echo "finance_prod_$(openssl rand -hex 16)" > secrets/db_password.txt
    echo -e "${GREEN}✓ 已生成随机数据库密码${NC}"
fi

# 检查 .env 文件
if [ ! -f "backend/.env" ]; then
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo -e "${YELLOW}⚠ 已从 .env.example 复制 .env，请根据实际情况修改配置${NC}"
    else
        echo -e "${RED}错误：找不到 backend/.env 配置文件${NC}"
        exit 1
    fi
fi

# 选择部署模式
MODE=${1:-dev}

if [ "$MODE" = "prod" ]; then
    echo -e "${GREEN}📦 生产模式部署${NC}"
    docker compose -f compose.prod.yaml down || true
    docker compose -f compose.prod.yaml up -d --build
    echo -e "${YELLOW}⏳ 等待服务就绪...${NC}"
    sleep 15
    echo ""
    echo -e "${GREEN}服务状态：${NC}"
    docker compose -f compose.prod.yaml ps
else
    echo -e "${GREEN}📦 开发模式部署${NC}"
    docker compose down || true
    docker compose up -d --build
    echo -e "${YELLOW}⏳ 等待服务就绪...${NC}"
    sleep 15
    echo ""
    echo -e "${GREEN}服务状态：${NC}"
    docker compose ps
fi

# 健康检查
echo ""
echo -e "${YELLOW}🔍 健康检查...${NC}"
HEALTH_URL="http://localhost:8000/api/health"
for i in $(seq 1 10); do
    if curl -sf "$HEALTH_URL" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 后端服务健康检查通过${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ 后端服务健康检查超时${NC}"
    fi
    sleep 3
done

echo ""
echo -e "${GREEN}✅ 部署完成！${NC}"
echo -e "  后端地址：http://localhost:8000"
echo -e "  API 文档：http://localhost:8000/docs"
echo -e "  MySQL 端口：3307"
echo -e "  Redis 端口：6379"
