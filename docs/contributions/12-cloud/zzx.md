# 云服务部署贡献说明

姓名：曾昭祥  
学号：2312190219  
日期：2026-06-02

## 我完成的工作

### 1. 平台选择

- 使用平台：`Vercel`（前端部署）
- 说明：后端云部署由陈伟栋同学负责并已实现

### 2. 部署配置

- [x] 配置文件编写（`vercel.json`）
- [x] 环境变量配置方案整理（`VITE_API_BASE_URL`、`NODE_ENV`）
- [x] 自动部署配置说明（GitHub `main` 分支触发 Vercel 自动部署）

### 3. 具体改动

| 文件 | 说明 |
|------|------|
| `vercel.json` | 前端云部署配置：安装/构建命令、产物目录、SPA 路由重写 |
| `docs/deployment.md` | 云部署说明文档（平台选择、环境变量、自动部署、验证清单） |
| `docs/contributions/12-cloud/zzx.md` | 个人贡献说明 |

## 问题解决

- 遇到的问题：前后端分离后，前端线上请求地址不能继续使用本地 `/api` 相对路径  
- 解决方案：在 Vercel 配置 `VITE_API_BASE_URL`，构建时注入后端线上地址

- 遇到的问题：Vue History 路由在云端刷新子路径可能返回 404  
- 解决方案：在 `vercel.json` 添加 `rewrites`，统一回退到 `index.html`

## PR 链接

- PR #24: https://github.com/Ccccwd/personal-financial-management-assistant/pull/24 （`feature/曾昭祥-frontend-doc` → `dev`）
- PR #25: https://github.com/Ccccwd/personal-financial-management-assistant/pull/25 （`dev` → `main`）

## 在线地址

- 前端（Vercel）：（已部署成功，请替换为你的实际 Vercel 线上链接）

## AI 使用情况

- 使用了哪些 Prompt：Vercel 前端部署配置、Vite 环境变量配置、前后端分离部署文档模板
- AI 帮助解决了哪些问题：部署配置项梳理、文档结构整理、校验清单补全

## 心得体会

本次实践明确了前后端分离项目的云部署重点：前端静态资源托管与后端接口地址解耦。通过环境变量注入和自动部署配置，可以在不改业务代码的前提下完成从本地开发到线上发布的流程闭环。
