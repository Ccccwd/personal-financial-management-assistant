# AI 智能服务前端贡献说明

姓名：曾昭祥  
学号：2312190219  
日期：2026-06-27（更新：对齐最终代码）

## 我完成的工作

### 1. AI API 封装与类型定义

- [x] `frontend/src/api/ai.ts`：理财建议相关接口（**不含** classify/reclassify）
  - `getAIAdvice`：获取理财建议（超时 120s）
  - `getAIAdviceHistory` / `getAIAdviceDetail`：历史记录
  - `getAIUsage`：用量统计
- [x] `frontend/src/types/ai.ts`：建议内容、预算 breakdown、历史记录等类型

### 2. Pinia 状态管理

- [x] `frontend/src/stores/ai.ts`：建议生成、历史分页、详情、用量
- [x] `normalizeAdviceDetail`：统一历史详情与实时建议的数据结构

### 3. 智能分析主页面

- [x] `frontend/src/views/ai/AIView.vue`，路由 `/ai`，侧边栏「智能分析」
- [x] 智能建议 Tab：分析周期、强制刷新、缓存/新生成标签
- [x] 三列卡片：消费亮点 → 优化建议 → 风险提醒
- [x] 下月预算建议：`AIBudgetChart` 横向柱状图
- [x] 历史记录 Tab：分页表格 + 详情抽屉

### 4. 业务组件

- [x] `AIAdviceCard.vue`、`AIBudgetChart.vue`、`AIInsightCard.vue`

### 5. 交易分类（非 AI 按钮）

- [x] **微信导入**（`WechatImport.vue`）：导入设置可选默认分类；导入完成后由**后端** `_auto_classify_imported` 自动分类（前端仅展示 `classified_count` 统计）
- [x] **交易列表/详情**：未分类条目可**手动选择**分类保存（无「AI 识别」按钮）

### 6. 已移除（PR #37）

- ~~`POST /api/ai/classify`、`/api/ai/reclassify`~~
- ~~导入结果页/交易页的「智能分类」「AI 识别」按钮~~
- ~~`aiClassify`、`reclassifyTransaction` 等前端 API~~

## 涉及文件

| 路径 | 说明 |
|------|------|
| `frontend/src/api/ai.ts` | 理财建议接口 |
| `frontend/src/types/ai.ts` | 类型定义 |
| `frontend/src/stores/ai.ts` | Pinia 状态 |
| `frontend/src/views/ai/AIView.vue` | 智能分析页 |
| `frontend/src/views/import/WechatImport.vue` | 导入（展示自动分类条数） |
| `frontend/src/views/transaction/TransactionList.vue` | 手动快速分类 |
| `frontend/src/views/transaction/TransactionDetail.vue` | 手动修改分类 |

## PR 链接

- PR #37: https://github.com/Ccccwd/personal-financial-management-assistant/pull/37

## 截图占位（学习通 / 答辩）

1. 「智能分析」页生成理财建议完整界面
2. 微信导入结果页显示「AI 分类 N 条」
3. 交易列表中导入记录已带分类（无 AI 按钮）

## 心得体会

最终版将 AI 能力收敛为「导入后后端自动分类 + 前端理财建议展示」两条主线，降低答辩复杂度，同时与 `docs/ai-features.md`、后端 `wechat_bill_service.py` 保持一致。
