# AI 智能服务开发贡献说明

姓名：陈伟栋
学号：2312190218
日期：2026-04-18

## 我完成的工作

### AI 配置

- [x] 统一 AI 模型配置（`AI_API_KEY` / `AI_BASE_URL` / `AI_MODEL`）
- [x] 配置 GLM-5.1（智谱 AI）作为默认模型
- [x] 使用 OpenAI SDK 兼容格式调用，便于后续切换模型
- [x] 更新 `.env` 和 `.env.example` 配置模板

### AI 服务层

- [x] 实现 `AIService` 类（`app/services/ai_service.py`，601 行）
- [x] 规则分类器：9 大分类、约 80 个关键词覆盖常见商户
- [x] LLM 分类：通过 Prompt 引导模型返回 JSON 格式分类结果
- [x] 两级分类策略：规则匹配优先，未命中再调用 LLM，降低成本
- [x] 理财建议生成：汇总消费数据 → 构建 Prompt → 调用 LLM → 解析并存储
- [x] 缓存机制：相同分析周期的建议自动缓存，避免重复调用
- [x] 降级策略：LLM 调用失败时返回默认分类，保证服务可用性

### AI API 接口（6 个端点）

- [x] `POST /api/ai/classify` - 账单智能分类（支持批量，最多 100 条）
- [x] `POST /api/ai/reclassify/{transaction_id}` - 重新分类单条交易（支持 dry_run 预览）
- [x] `GET /api/ai/advice` - 获取个性化理财建议（支持缓存和强制刷新）
- [x] `GET /api/ai/advice/history` - 获取历史建议列表（分页）
- [x] `GET /api/ai/advice/history/{record_id}` - 获取建议详情
- [x] `GET /api/ai/usage` - 获取 AI 服务用量统计

### 数据模型

- [x] `AIAdviceRecord` 模型（`app/models/ai_advice_record.py`）
  - 存储生成的理财建议：亮点、预警、建议、预算方案、完整报告
  - 记录 Token 消耗和缓存状态

### 数据校验 Schema

- [x] `ClassifyItem` / `ClassifyRequest` - 分类请求
- [x] `ClassifyResultItem` / `ClassifyResponse` - 分类结果
- [x] `AdviceResponse` - 理财建议响应
- [x] `AIUsageResponse` - 用量统计响应

### Postman 测试集合

- [x] 新增"11. AI 智能服务"文件夹（7 个测试请求）
- [x] 覆盖智能分类、重新分类（预览+执行）、理财建议、历史记录、建议详情、用量统计
- [x] 环境变量自动传递（advice_record_id）

## PR 链接

- PR #X: https://github.com/Ccccwd/personal-financial-management-assistant/pull/X（待提交）

## 遇到的问题和解决

1. **问题**：GLM API 使用 OpenAI SDK 兼容格式，需要确认 `base_url` 和 `response_format` 的兼容性
   **解决**：使用 `openai` 库，设置 `base_url` 为智谱 API 地址，`response_format={"type": "json_object"}` 确保 LLM 返回有效 JSON

2. **问题**：LLM 返回的 JSON 格式不固定，有时包含 `{"results": [...]}` 包装，有时直接是数组
   **解决**：在解析逻辑中同时处理两种格式：`if isinstance(result, dict) and "results" in result`

3. **问题**：每次分类都调用 LLM 成本较高
   **解决**：实现两级分类策略，规则匹配覆盖常见商户（餐饮、交通等），仅对规则未命中的记录调用 LLM

4. **问题**：LLM 调用可能因网络或配额问题失败
   **解决**：使用 try-except 包裹所有 LLM 调用，失败时降级返回默认分类或提示信息，保证 API 不会 500 报错

## 心得体会

本次 AI 服务开发让我深入理解了 LLM 应用的工程化实践。核心收获包括：如何设计有效的 Prompt 引导模型返回结构化 JSON 数据；如何通过规则 + LLM 的混合策略平衡准确性和成本；以及如何实现降级策略确保服务稳定性。使用 OpenAI SDK 兼容格式调用 GLM 模型的经验也让我理解了 AI API 的标准化趋势，后续切换模型只需修改配置即可。
