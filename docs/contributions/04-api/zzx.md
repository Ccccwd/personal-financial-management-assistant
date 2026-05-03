# API 设计与实现贡献说明

姓名：曾昭祥
学号：2312190219
日期：2026-03-31

## 我完成的工作

### 1. API 设计
- 用户认证 API（已有实现，前端对接完成）
- 交易记录 API（8 个端点）
- 预算管理 API（4 个端点）
- 统计分析 API（4 个端点）
- 分析报告 API（4 个端点）
- 微信账单导入 API（7 个端点）
- 智能提醒 API（8 个端点）
- AI 智能服务 API（6 个端点）
- 账户余额历史 API（2 个端点）

### 2. 文档编写
- API 使用说明（`docs/api.md`）
- 个人贡献说明

### 3. 前端实现
- HTTP 客户端配置（`frontend/src/utils/request.ts`）
  - Axios 实例创建，baseURL 配置
  - 请求拦截器：自动注入 JWT Bearer Token
  - 响应拦截器：统一解包 `{ code, message, data }` 格式，自动处理错误提示
- Token 管理工具（`frontend/src/utils/auth.ts`）
  - `TokenManager` 类：封装 LocalStorage 的 Token 存取与清除
- API 调用函数封装（共 11 个模块，覆盖 `api.md` 全部端点）：
  - `frontend/src/api/auth.ts` — 认证模块（11 个函数：注册、登录、刷新 Token、登出、获取/更新用户信息、修改密码、密码重置等）
  - `frontend/src/api/categories.ts` — 分类管理（7 个函数）
  - `frontend/src/api/accounts.ts` — 账户管理（9 个函数，含转账、余额调整、余额历史）
  - `frontend/src/api/transactions.ts` — 交易记录（8 个函数）
  - `frontend/src/api/budgets.ts` — 预算管理（4 个函数）
  - `frontend/src/api/statistics.ts` — 统计分析（4 个函数）
  - `frontend/src/api/reports.ts` — 分析报告（4 个函数）
  - `frontend/src/api/wechat.ts` — 微信账单导入（7 个函数，含文件上传与 Base64 方式）
  - `frontend/src/api/reminders.ts` — 智能提醒（8 个函数）
  - `frontend/src/api/ai.ts` — AI 智能服务（6 个函数）
- TypeScript 类型定义（`frontend/src/types/` 目录，共 12 个类型文件）：
  - `index.ts`、`common.ts`、`user.ts`、`category.ts`、`account.ts`、`transaction.ts`
  - `budget.ts`、`statistics.ts`、`report.ts`、`wechat.ts`、`reminder.ts`、`ai.ts`
- Pinia Store（`frontend/src/stores/user.ts`）
  - 用户登录/登出状态管理
  - Token 持久化与自动获取用户信息
- 页面视图组件：
  - `frontend/src/views/auth/Login.vue` — 登录页面（表单校验 + API 调用 + 路由跳转）
  - `frontend/src/views/auth/Register.vue` — 注册页面（表单校验 + API 调用 + 成功后跳转登录）
- 路由配置（`frontend/src/router/index.ts`）
  - 路由守卫：未登录重定向到登录页，已登录阻止访问 guest 页面
  - 路由注册：`/login`、`/register`、`/dashboard`

### 4. 后端实现
- 无

### 5. 测试
- Apifox 测试集合


## 遇到的问题和解决

### 问题 1：模块导出名不匹配导致白屏
**问题**：`stores/user.ts` 中导入了 `getUserInfo`，但 `api/auth.ts` 导出的函数名是 `getCurrentUser`，导致浏览器报 `SyntaxError: does not provide an export named 'getUserInfo'`，页面一片空白。

**解决**：将导入语句修正为实际的导出名称：
```typescript
// 修正前
import { login as loginApi, getUserInfo as getUserInfoApi } from '@/api/auth'
// 修正后
import { login as loginApi, getCurrentUser as getUserInfoApi } from '@/api/auth'
```

### 问题 2：IPv4/IPv6 代理不匹配导致 500 错误
**问题**：Vite 代理配置中 `target: 'http://localhost:8000'`，在 Windows 上 Node.js 解析 `localhost` 优先使用 IPv6 地址 `::1`，而后端 uvicorn 绑定的是 IPv4 `127.0.0.1`，导致代理连接被拒绝，前端请求全部返回 500。

**解决**：将 `vite.config.ts` 中的代理目标从 `localhost` 改为 `127.0.0.1`：
```typescript
proxy: {
  '/api': {
    target: 'http://127.0.0.1:8000',  // 强制使用 IPv4
    changeOrigin: true
  }
}
```

### 问题 3：JWT sub 字段类型错误导致 401
**问题**：后端创建 Token 时 `create_access_token(data={"sub": user.id})` 传入了整数类型的 `user.id`，但 JWT 规范要求 `sub` 必须是字符串，`python-jose` 解码时校验失败 `JWTClaimsError: Subject must be a string`，导致 `/auth/me` 接口始终返回 401。

**解决**：
- 创建 Token 时将 `user.id` 转为字符串：`{"sub": str(user.id)}`
- 解码时将字符串转回整数：`user_id = int(payload.get("sub"))`

### 问题 4：bcrypt/passlib 版本冲突导致注册 500 错误
**问题**：`passlib` 库与最新版 `bcrypt 5.0.0` 存在 API 不兼容，调用密码哈希函数时报 `AttributeError: module 'bcrypt' has no attribute '__about__'`。

**解决**：将 `bcrypt` 降级至兼容版本 `3.2.0`：
```bash
uv add bcrypt==3.2.0
```

## 心得体会

### 1. 前端 API 层架构设计
通过本次实践，建立了清晰的三层架构：
- **Types 层**（`src/types/`）：定义所有数据模型的 TypeScript 接口，作为前后端的契约
- **API 层**（`src/api/`）：每个模块对应一个文件，封装 HTTP 请求，统一返回类型
- **Utils 层**（`src/utils/`）：Axios 拦截器统一处理认证 Token 注入和响应解包

这种分层设计使得 API 调用方只需关注业务逻辑，不需要关心 Token 管理和响应格式解析。

### 2. Axios 拦截器的重要性
请求拦截器自动注入 JWT Token，响应拦截器统一解包后端的 `{ code, message, data }` 格式并处理错误提示，大幅减少了业务层的重复代码。

### 3. TypeScript 类型安全
为所有 API 请求和响应定义了强类型接口，在编码阶段就能发现参数类型不匹配、属性拼写错误等问题，显著提高了开发效率和代码可靠性。

### 4. 前后端联调的关键细节
- IPv4/IPv6 差异在 Windows 环境下容易被忽视，但会导致代理完全失效
- JWT 规范对字段类型有严格要求，后端传参类型不正确会导致 Token 创建成功但验证失败
- 前端导入导出名称必须精确匹配，否则 ES Module 直接报语法错误
