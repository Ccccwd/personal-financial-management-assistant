# AI 智能服务功能说明

## 使用模型

| 配置项 | 值 |
|--------|------|
| 模型名称 | DeepSeek Chat（`deepseek-chat`） |
| API 地址 | `https://api.deepseek.com` |
| 调用方式 | OpenAI SDK 兼容格式（openai 库） |
| 配置文件 | `backend/.env`（`AI_API_KEY` / `AI_BASE_URL` / `AI_MODEL`） |

## 实现功能

### 1. 微信账单导入自动分类（后端内部）

**触发时机：** 用户通过微信账单导入接口完成批量入账后，由 `WechatBillService._auto_classify_imported` 自动执行。

**适用范围：** 仅对本次导入且**未在导入设置中指定 `category_id`** 的交易记录。

**分类策略：**

| 级别 | 方式 | 说明 |
|------|------|------|
| 第一级 | 规则匹配 | 根据商户名关键词匹配，置信度高、无 Token 消耗 |
| 第二级 | LLM 分类 | 规则未命中时调用 DeepSeek |
| 第三级 | 默认分类 | 仍无法识别时归入用户默认/「其他」分类 |

导入完成后，`import_summary` 与响应字段 `classified_count` 会体现 AI 分类条数。

> 不提供独立的「智能分类」前端按钮或 `POST /api/ai/classify`、`/api/ai/reclassify` 对外接口；交易列表/详情页通过手动选择分类。

### 2. 个性化理财建议（`GET /api/ai/advice`）

基于用户最近 N 个月的消费数据，调用 DeepSeek 生成个性化理财建议（亮点、预警、建议、下月预算、完整报告）。支持缓存与 `force_refresh`。

### 3. 历史建议（`GET /api/ai/advice/history`、`/history/{id}`）

分页查询与查看历史理财建议记录。

### 4. 用量统计（`GET /api/ai/usage`）

统计指定月份的 AI 建议调用次数与 Token 消耗（`classify_calls` 字段保留兼容，导入内部分类不计入对外展示时可置 0）。

## 技术架构

```
微信导入 → WechatBillService.import_transactions → _auto_classify_imported → AIService
用户请求 → API 层 (ai.py) → ai_service.generate_advice → DeepSeek API
```
