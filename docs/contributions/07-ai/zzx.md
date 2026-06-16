# AI 智能服务前端贡献说明

姓名：曾昭祥  
学号：2312190219  
日期：2026-06-16

## 我完成的工作

### AI API 封装与类型定义

- [x] 实现 `frontend/src/api/ai.ts`，对接后端 6 个 AI 接口
  - `aiClassify`：批量智能分类
  - `reclassifyTransaction`：单条交易重新分类（支持 `dry_run` 预览）
  - `getAIAdvice`：获取理财建议（超时设为 120s，适配 LLM 生成耗时）
  - `getAIAdviceHistory` / `getAIAdviceDetail`：历史记录与详情
  - `getAIUsage`：用量统计
- [x] 定义 `frontend/src/types/ai.ts`，覆盖分类结果、建议内容、预算 breakdown、历史记录等 TypeScript 类型

### Pinia 状态管理

- [x] 实现 `frontend/src/stores/ai.ts`
  - 建议生成、历史列表分页、详情拉取、用量统计、重新分类等状态与方法
  - `normalizeAdviceDetail`：将历史详情接口的扁平结构规范为页面统一的 `advice` 结构，保证详情抽屉与主页面组件复用一致

### 智能分析主页面（`AIView.vue`）

- [x] 注册路由 `/ai`，侧边栏入口「智能分析」
- [x] **智能建议** Tab：分析周期选择（1/3/6/12 个月）、强制刷新生成、缓存/新生成标签
- [x] 三列等宽等高卡片布局（Grid）：消费亮点 → 优化建议 → 风险提醒
- [x] **下月预算建议**：集成 `AIBudgetChart` 横向柱状图展示分类预算占比
- [x] 完整分析报告折叠面板
- [x] **历史记录** Tab：分页表格 + 详情抽屉，复用 `AIAdviceCard` 展示
- [x] Tab 切换懒加载历史数据，减少无效请求

### 业务组件

- [x] `AIAdviceCard.vue`：亮点 / 建议 / 预警三类卡片，支持空状态与条目计数
- [x] `AIBudgetChart.vue`：基于 ECharts 的动态高度横向柱状图，展示各分类建议金额与占比
- [x] `AIInsightCard.vue`：首页智能洞察摘要卡片（后续按产品需求从仪表盘移除，组件保留供复用）

### AI 能力嵌入现有业务流程

- [x] **微信账单导入**（`WechatImport.vue`）：预览后批量调用 `aiClassify`，分批（每批 20 条）展示进度与成功数
- [x] **交易流水**（`TransactionList.vue` / `TransactionDetail.vue`）：单条「AI 重新分类」，先 `dry_run` 预览再确认应用

### 联调与体验优化（近期迭代）

- [x] 配合后端 `normalize_budget_suggestion`，修复 LLM 返回中文键（`总预算` / `各分类预算`）导致预算图表为空的问题
- [x] 隐藏「用量统计」Tab，简化答辩演示路径
- [x] 从首页仪表盘移除「智能洞察」区块，避免无数据时的冗余展示

## 涉及文件

| 路径 | 说明 |
|------|------|
| `frontend/src/api/ai.ts` | AI 接口封装 |
| `frontend/src/types/ai.ts` | 类型定义 |
| `frontend/src/stores/ai.ts` | Pinia 状态 |
| `frontend/src/views/ai/AIView.vue` | 智能分析主页面 |
| `frontend/src/components/business/AIAdviceCard.vue` | 建议卡片 |
| `frontend/src/components/business/AIBudgetChart.vue` | 预算图表 |
| `frontend/src/components/business/AIInsightCard.vue` | 首页洞察卡片 |
| `frontend/src/views/import/WechatImport.vue` | 导入页智能分类 |
| `frontend/src/views/transaction/TransactionList.vue` | 列表页重新分类 |
| `frontend/src/views/transaction/TransactionDetail.vue` | 详情页重新分类 |
| `frontend/src/router/index.ts` | `/ai` 路由 |

## PR 链接

- PR #30: https://github.com/Ccccwd/personal-financial-management-assistant/pull/30（AI 预算建议归一化与智能分析页优化）
- 早期 AI 前端集成：`fe21e42`、`34f3f5d`（智能分析页、微信导入分类、交易重新分类）

## 遇到的问题和解决

1. **问题**：调用 `getAIAdvice` 时前端默认 30s 超时，LLM 生成较慢导致请求失败  
   **解决**：在 `api/ai.ts` 为建议接口单独设置 `timeout: 120000`

2. **问题**：历史详情接口返回扁平字段（`highlights` 在顶层），与当前建议接口嵌套在 `advice` 下不一致，抽屉渲染异常  
   **解决**：在 `stores/ai.ts` 增加 `normalizeAdviceDetail`，统一转换为 `AIAdviceResponse` 结构

3. **问题**：下月预算图表始终为空，后端 LLM 有时返回 `{ 总预算, 各分类预算 }` 中文键  
   **解决**：与后端同学联调，后端增加 `normalize_budget_suggestion` 归一化；前端 `AIBudgetChart` 消费标准 `{ total, breakdown[] }` 格式

4. **问题**：微信导入智能分类一次提交过多条目，接口耗时长、易超时  
   **解决**：前端按每批 20 条分批调用 `aiClassify`，并展示 `current/total` 进度

5. **问题**：Axios 拦截器已剥离 `res.data`，TypeScript 类型与运行时返回值不一致  
   **解决**：Store 层使用 `as unknown as T` 适配，与项目其他 API 模块保持一致

## 心得体会

AI 功能的前端难点不在页面本身，而在于**长耗时请求**、**非结构化 LLM 响应**与**多入口复用**（分析页、导入页、交易页）。通过独立的 API 超时配置、详情数据归一化、分批调用与 `dry_run` 预览确认，可以在保证体验的同时降低误操作风险。与后端约定稳定的 JSON 契约（尤其是预算建议字段）是图表能否正确展示的关键；Vibe Coding 加快了 UI 搭建，但联调阶段仍需针对 LLM 输出的不确定性做防御性处理。
