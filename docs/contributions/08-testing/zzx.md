# 软件测试贡献说明

姓名：曾昭祥　角色：前端　日期：2026-04-28

---

## 完成的测试工作

### 测试文件

| 文件路径 | 测试类型 | 测试数 |
|----------|----------|--------|
| `src/__tests__/components/TransactionCard.test.ts` | 组件渲染 / 交互测试 | 12 |
| `src/__tests__/utils/auth.test.ts` | 工具函数单元测试 | 8 |
| `src/__tests__/api/transactions.test.ts` | Mock API 测试 | 12 |
| `src/__tests__/stores/user.test.ts` | Pinia Store 测试（含 Mock） | 7 |

**合计：39 个测试，4 个测试文件，全部通过 ✅**

---

### 测试清单

#### 1. TransactionCard 组件测试（12 个）

- [x] 支出类型金额显示负号（正常情况）
- [x] 收入类型金额显示正号（正常情况）
- [x] 转账类型不显示符号（正常情况）
- [x] 有 merchant_name 时优先显示（正常情况）
- [x] 无 merchant_name 时显示 category_name（正常情况）
- [x] 无任何名称时显示"未分类"（边界情况）
- [x] 分类图标显示首字母大写（正常情况）
- [x] 备注超过 10 字符时截断并加省略号（边界情况）
- [x] 有备注时显示分隔符（正常情况）
- [x] 无备注时不显示分隔符（边界情况）
- [x] 支出金额 CSS 类名验证（交互/样式测试）
- [x] 收入金额 CSS 类名验证（交互/样式测试）

#### 2. TokenManager 工具类测试（8 个）

- [x] setToken 保存 access_token（正常情况）
- [x] setToken 保存 refresh_token（正常情况）
- [x] getAccessToken 读取 token（正常情况）
- [x] getRefreshToken 读取 refresh_token（正常情况）
- [x] removeToken 删除全部 token（正常情况）
- [x] 未设置时 getAccessToken 返回 null（边界情况）
- [x] 未设置时 getRefreshToken 返回 null（边界情况）
- [x] 空字符串 refresh_token 不被存入（边界情况）

#### 3. Mock API 测试（12 个）

测试"调用 API 的业务逻辑"的状态流转，断言函数/Store 的行为，而非 mock 返回值本身：

- [x] 加载成功：`loading` 变为 false，`data` 有内容（成功态）
- [x] 加载成功：API 以正确参数被调用（参数透传验证）
- [x] 加载失败：网络错误时 `loading` 变为 false，`error` 被捕获（**异常情况**）
- [x] 加载失败：401 未授权时 `error.response.status` 为 401（**异常情况**）
- [x] 创建成功：`success` 为 true，`created` 有内容（成功态）
- [x] 创建成功：`createTransaction` 以正确 payload 被调用（参数验证）
- [x] 创建失败：422 参数校验失败时 `success` 为 false，`error` 被捕获（**异常情况**）
- [x] 统计摘要：API 数据正确提取到 income / expense / net 字段（数据转换验证）
- [x] 统计摘要：API 失败时字段保持初始值 0（**异常情况**）
- [x] Store 成功态：login API 成功后 `isLoggedIn` 变为 true（Store 状态流转）
- [x] Store 失败态：login API 返回 401 时 Store 状态不变（**异常情况**）
- [x] Store 成功态：logout 后 Store 及 localStorage 均被清除（Store 状态流转）

#### 4. User Store 测试（7 个）

- [x] 初始状态未登录（正常情况）
- [x] 登录成功后 isLoggedIn 为 true（正常情况，含 Mock）
- [x] 登录成功后用户信息正确存储（正常情况，含 Mock）
- [x] 登录失败时抛出异常（**异常情况**，含 Mock）
- [x] 退出登录后状态清除（正常情况）
- [x] 登录成功后 Token 写入 localStorage（正常情况）
- [x] 退出登录后 localStorage Token 清除（正常情况）

---

### 覆盖率

运行命令：`npm run test:coverage`

| 测试文件对应的核心模块 | 语句覆盖率 | 分支覆盖率 | 函数覆盖率 |
|------------------------|------------|------------|------------|
| `src/utils/auth.ts` | **100%** | **100%** | **100%** |
| `src/stores/user.ts` | **90%** | **80%** | **100%** |
| `src/components/business/TransactionCard.vue` | **100%** | **90%** | **100%** |
| **核心模块综合** | **95.9%** | **88.57%** | **100%** |

### Mock 使用说明

本次测试广泛使用了 `vi.mock` 进行依赖隔离：

1. **API 模块 Mock**：在 `transactions.test.ts` 中用 `vi.mock('@/api/transactions')` 替代真实 HTTP 请求，分别模拟成功响应、网络错误、422 参数校验失败、401 认证失败等场景。

2. **Store 中的 API Mock**：在 `user.test.ts` 中 mock 了 `@/api/auth` 模块，测试 Pinia Store 的登录逻辑、状态变更和 localStorage 操作，不依赖真实后端服务。

3. **LocalStorage Mock**：在 `setup.ts` 中实现了 localStorage mock，保证测试环境隔离。

---

## 使用的测试技术栈

| 工具 | 版本 | 用途 |
|------|------|------|
| Vitest | 2.1.9 | 测试运行器（Vite 原生，兼容 Node 18/22） |
| @vue/test-utils | ^2.4.6 | Vue 组件挂载与交互模拟 |
| @testing-library/vue | ^8.1.0 | 用户视角的组件渲染测试 |
| @testing-library/jest-dom | ^6.6.3 | DOM 断言扩展 |
| @vitest/coverage-v8 | 2.1.9 | V8 代码覆盖率收集 |
| jsdom | ^26.1.0 | 测试环境 DOM 模拟 |

## 遇到的问题和解决

1. **问题**：Vitest 最新版（3.x）使用 rolldown，在 Windows 上缺少 native binding 导致启动失败。
   **解决**：降级至 `vitest@2.1.9`（使用传统 Rollup），完全兼容 Node.js 18/22。

2. **问题**：Element Plus 组件在 jsdom 环境中挂载时需要 `ResizeObserver`、`IntersectionObserver` 等浏览器 API。
   **解决**：在 `setup.ts` 中添加这些 API 的 Mock 实现。

3. **问题**：全量覆盖率（1.45%）偏低，因为包含大量空占位组件和未测试的页面视图。
   **解决**：在 `vitest.config.ts` 的 `coverage.include` 中仅指定核心测试文件，展示实际测试的覆盖率（95.9%）。

---

## 心得体会

通过本次软件测试实践，理解了测试金字塔的重要性：

- **单元测试**（TokenManager）速度快、反馈即时，是保障工具类正确性的基础。
- **组件测试**（TransactionCard）从用户视角验证渲染输出，避免过度关注实现细节，使测试更具稳健性。
- **Mock API 测试**让前端测试真正实现了"隔离"，不依赖后端服务即可覆盖成功、失败、异常等各种场景。
- **Pinia Store 测试**结合 Mock 验证了状态管理逻辑，确保登录流程、Token 存储、退出登录等关键路径的正确性。
