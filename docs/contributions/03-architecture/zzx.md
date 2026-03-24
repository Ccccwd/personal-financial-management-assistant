# 个人贡献记录（03-架构）

## 本次贡献概述

- **贡献人：** 曾昭祥 
- **日期：** 2026-03-24
- **任务来源：** 前端技术选型、开发环境搭建、工程化配置与基础架构铺设

---

## 贡献一：前端开发环境搭建与工程化配置

### 1) 技术栈选型与环境初始化

基于 **Vue 3 + TypeScript + Vite** 构建高性能前端开发环境，确保代码规范与类型安全：

- **构建工具配置**：配置 `vite.config.ts`，集成 `@vitejs/plugin-vue` 插件与 `unplugin-auto-import` 等工程化工具；设置路径别名（Alias）优化模块导入路径；配置开发服务器代理（Proxy）解决跨域问题。
- **TypeScript 环境修复与优化**：创建并配置 `tsconfig.json`；针对项目启动初期遇到的 `@tsconfig/node20` 解析错误，手动优化 `tsconfig.node.json`，将编译器选项内联，确保 Vite 配置文件能被正确编译。
- **核心依赖管理**：通过 `package.json` 管理项目依赖，确立 Vue Router 4 (路由), Pinia (状态), Element Plus (UI), Axios (HTTP), ECharts (图表) 等技术栈版本。

### 2) 项目目录结构与脚手架搭建

建立了标准化的企业级前端项目结构，为后续功能开发提供稳固基础：

```
frontend/
├── public/                      # 静态资源入口
├── src/
│   ├── api/                     # API 接口统一管理 (RESTful 风格)
│   ├── assets/                  # 静态资源 (图片、图标)
│   ├── components/              # 全局公共组件
│   ├── layouts/                 # 布局组件 (MainLayout)
│   ├── router/                  # 路由配置与权限守卫
│   ├── stores/                  # Pinia 状态管理模块
│   ├── styles/                  # 全局样式与主题变量
│   ├── types/                   # TypeScript 类型定义
│   ├── utils/                   # 工具函数库
│   └── views/                   # 页面视图代码
├── env.d.ts                     # 环境变量类型声明
├── vite.config.ts               # Vite 构建配置
└── tsconfig.json                # TypeScript配置
```

### 3) 核心基础设施代码实现

- **网络请求层封装 (`src/utils/request.ts`)**：
  - 封装全局 Axios 实例，配置超时与 Base URL。
  - **请求拦截器**：实现 JWT Token 的自动注入。
  - **响应拦截器**：统一处理 HTTP 状态码，对 401 未授权自动登出，并对网络异常进行全局提示。

- **路由与权限控制系统 (`src/router/index.ts`)**：
  - 搭建 Vue Router 实例，定义路由表。
  - 实现**全局路由守卫**：基于 `meta.requiresAuth` 字段鉴权，拦截未登录访问。

- **状态管理初始化 (`src/stores/user.ts`)**：
  - 使用 Pinia 定义 `useUserStore`，管理 Token 存储与用户信息状态同步。
  - 实现 `login` / `logout` 等核心 Action。

---

## 输出成果

| 类别 | 文件/模块 | 说明 |
|------|-----------|------|
| **环境配置** | `vite.config.ts` | 别名配置、Plugins集成、Server设置 |
|  | `tsconfig.node.json` | 修复 TypeScript 配置文件解析错误 |
| **基础架构** | `src/utils/request.ts` | Axios 二次封装，统一拦截器处理 |
|  | `src/router/index.ts` | 路由配置与全局权限守卫逻辑 |
|  | `src/utils/auth.ts` | Token 本地存储 (LocalStorage) 管理工具 |
|  | `src/api/*` | 统一的 API 接口定义层 |
| **依赖管理** | `package.json` | 完整依赖树定义与启动脚本 |

