# AI 智能服务前端贡献说明

姓名：曾昭祥  
学号：2312190219  
日期：2026-06-17（更新：移除智能分类功能）

## 我完成的工作

### AI API 封装与类型定义

- [x] 实现 `frontend/src/api/ai.ts`，对接后端理财建议相关接口
  - `getAIAdvice`：获取理财建议（超时设为 120s，适配 LLM 生成耗时）
  - `getAIAdviceHistory` / `getAIAdviceDetail`：历史记录与详情
  - `getAIUsage`：用量统计
- [x] 定义 `frontend/src/types/ai.ts`，覆盖建议内容、预算 breakdown、历史记录等 TypeScript 类型

### Pinia 状态管理

- [x] 实现 `frontend/src/stores/ai.ts`
  - 建议生成、历史列表分页、详情拉取、用量统计
  - `normalizeAdviceDetail`：将历史详情接口的扁平结构规范为页面统一的 `advice` 结构

### 智能分析主页面（`AIView.vue`）

- [x] 注册路由 `/ai`，侧边栏入口「智能分析」
- [x] **智能建议** Tab：分析周期选择、强制刷新生成、缓存/新生成标签
- [x] 三列卡片布局：消费亮点 → 优化建议 → 风险提醒
- [x] **下月预算建议**：`AIBudgetChart` 横向柱状图
- [x] **历史记录** Tab：分页表格 + 详情抽屉

### 业务组件

- [x] `AIAdviceCard.vue`、`AIBudgetChart.vue`、`AIInsightCard.vue`

### 交易分类（手动）

- [x] **交易流水**（`TransactionList.vue`）：未分类条目「待分类」入口，弹窗手动选择分类保存
- [x] **微信账单导入**（`WechatImport.vue`）：导入设置可选默认分类；导入结果页仅展示统计与跳转

### 已移除（2026-06-17）

- ~~批量/单条 AI 智能分类（`aiClassify`、`reclassifyTransaction`）~~
- ~~导入结果页「智能分类」按钮、交易详情/列表「AI 识别」~~

## 涉及文件

| 路径 | 说明 |
|------|------|
| `frontend/src/api/ai.ts` | AI 接口封装（仅理财建议） |
| `frontend/src/types/ai.ts` | 类型定义 |
| `frontend/src/stores/ai.ts` | Pinia 状态 |
| `frontend/src/views/ai/AIView.vue` | 智能分析主页面 |
| `frontend/src/views/transaction/TransactionList.vue` | 手动快速分类 |
| `frontend/src/views/import/WechatImport.vue` | 账单导入 |

## 心得体会

当前 AI 能力聚焦**理财建议**单一主线，降低答辩演示与维护复杂度。交易分类由用户手动完成，与导入时可选默认分类配合，仍能满足记账场景需求。
