# 智能个人财务记账系统

## 团队成员

| 姓名 | 学号 | 分工 | 主要负责模块 |
|------|------|------|-------------|
| 陈伟栋 | 2312190218 | 后端开发 | 1. **数据库设计与迁移**<br>2. **API 接口开发**<br>3. **核心业务逻辑**<br>4. **后端环境与部署** |
| 曾昭祥 | 2312190219 | 前端开发 | 1. **界面 UI 实现与交互** <br>2. **前端架构搭建**<br>3. **数据可视化** <br />4. **前端环境与部署** |

## 项目简介

本项目是一款面向大学生和年轻群体的智能个人财务管理系统，帮助用户便捷记录日常收支、分析消费习惯并制定预算计划。系统支持手动记账与微信账单 CSV 文件导入，并引入大语言模型（LLM）实现两项核心 AI 功能：一是对导入的微信账单条目进行智能语义分类，识别商户名称与消费场景，自动归入餐饮、交通、娱乐等细分类目；二是基于用户的历史账单数据，由 AI 生成个性化消费分析报告与理财建议，帮助用户发现消费规律、优化支出结构。系统同时提供预算设置与超限预警、多账户管理、ECharts 多维度可视化图表及 Excel 报表导出等功能，致力于培养用户良好的理财习惯。

## UI/UX 原型设计

查看我们的高保真原型设计：
- **Figma 链接**: [Finance System Design Prototype](https://www.figma.com/design/C53NmBJvEC8eHJqKqvQyUI/Finance?node-id=0-1&t=BRhUshM7biKi3wvF-1)（由于一开始设计图的制作不在Figma中进行，导入导出的格式有问题，Figma链接中暂时只有设计图图片。）

## 技术栈（初步规划）

- **前端：** Vue 3 + TypeScript、Vue Router 4、Pinia、Element Plus、ECharts 5、Axios、Day.js、Vite
- **后端：** Python FastAPI、SQLAlchemy、JWT 认证（python-jose + passlib）、openpyxl、LLM SDK（DeepSeek / OpenAI）
- **数据库：** MySQL 8.0、Redis（缓存与 Token 管理）

## 快速开始

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

### 后端启动

```bash
cd backend
# 使用 uv 管理依赖和环境
uv sync
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

