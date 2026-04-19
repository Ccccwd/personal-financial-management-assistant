# AI 智能服务功能说明

## 使用模型

| 配置项 | 值 |
|--------|------|
| 模型名称 | GLM-5.1（智谱 AI） |
| API 地址 | `https://open.bigmodel.cn/api/paas/v4` |
| 调用方式 | OpenAI SDK 兼容格式（openai 库） |
| 配置文件 | `backend/.env`（AI_API_KEY / AI_BASE_URL / AI_MODEL） |

## 实现功能

### 1. 账单智能分类（`POST /api/ai/classify`）

**功能描述：** 接收一批交易记录，自动将其归类到对应的消费分类中。

**实现策略：** 两级分类机制，优先规则匹配，降低 LLM 调用成本。

| 级别 | 方式 | 说明 |
|------|------|------|
| 第一级 | 规则匹配 | 根据商户名关键词（如"瑞幸"→餐饮、"滴滴"→交通）匹配，置信度 0.9 |
| 第二级 | LLM 分类 | 规则未匹配的记录调用 GLM 模型分类，返回置信度和分类 ID |

**规则覆盖的分类：** 餐饮、交通、购物、娱乐、医疗、教育、住房、通讯、金融（共 9 类，约 80 个关键词）

**请求示例：**
```json
{
  "items": [
    {"merchant_name": "瑞幸咖啡", "amount": 15.9, "transaction_type": "expense"},
    {"merchant_name": "未知商店", "amount": 100.0, "transaction_type": "expense"}
  ]
}
```

**响应示例：**
```json
{
  "code": 200,
  "data": {
    "results": [
      {"index": 0, "category_name": "餐饮", "confidence": 0.9, "matched_by": "rule"},
      {"index": 1, "category_name": "其他", "confidence": 0.7, "matched_by": "llm"}
    ],
    "total": 2,
    "llm_called_count": 1,
    "rule_matched_count": 1
  }
}
```

### 2. 重新分类（`POST /api/ai/reclassify/{transaction_id}`）

**功能描述：** 对单条交易记录重新进行智能分类，支持预览模式（dry_run）。

| 参数 | 说明 |
|------|------|
| `transaction_id` | 待重新分类的交易 ID |
| `dry_run=true` | 仅预览分类结果，不修改数据 |
| `dry_run=false` | 实际更新交易的 category_id 和 ai_classified 字段 |

### 3. 个性化理财建议（`GET /api/ai/advice`）

**功能描述：** 基于用户最近 N 个月的消费数据，调用 GLM 生成个性化理财建议。

**生成流程：**
1. 查询用户最近 N 个月的交易记录
2. 按分类汇总支出数据
3. 构建 Prompt 发送给 GLM
4. 解析返回的 JSON 结果并保存到数据库

**建议内容包含：**
- `highlights`：消费亮点（肯定良好消费习惯）
- `warnings`：预警信息（指出消费问题）
- `suggestions`：改进建议
- `next_month_budget`：下月预算建议（总额 + 分类预算）
- `full_report`：完整理财报告文本

**缓存机制：** 同一分析周期内的建议会被缓存，避免重复调用 LLM。`force_refresh=true` 可强制重新生成。

### 4. 历史建议记录（`GET /api/ai/advice/history`）

**功能描述：** 分页查询用户的历史理财建议记录，包含生成时间、分析周期、Token 消耗等信息。

### 5. 建议详情（`GET /api/ai/advice/history/{record_id}`）

**功能描述：** 查看某条建议记录的完整内容，包括完整报告和预算建议。

### 6. 用量统计（`GET /api/ai/usage`）

**功能描述：** 统计指定月份的 AI 服务使用情况。

**返回数据：**
- `classify_calls`：分类调用次数
- `advice_calls`：建议生成次数
- `total_tokens_used`：总消耗 Token 数

## 技术架构

```
用户请求 → API 层 (ai.py) → 服务层 (ai_service.py) → GLM API
                                    ↓
                              规则分类器（本地）
                                    ↓
                            数据库 (AIAdviceRecord)
```

**关键设计决策：**
- 使用 OpenAI SDK 兼容格式调用 GLM，便于后续切换模型
- 两级分类策略：规则优先，LLM 补充，降低成本
- LLM 调用失败时降级返回"其他"分类，保证服务可用性
- 建议结果持久化存储，支持历史查询和缓存复用
