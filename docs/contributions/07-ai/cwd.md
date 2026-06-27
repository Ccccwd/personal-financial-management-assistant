# AI 智能服务开发贡献说明

姓名：陈伟栋
学号：2312190218
日期：2026-06-17（更新：移除智能分类 API）

## 我完成的工作

### AI 配置

- [x] 统一 AI 模型配置（`AI_API_KEY` / `AI_BASE_URL` / `AI_MODEL`）
- [x] 使用 DeepSeek Chat（`deepseek-chat`）作为默认模型
- [x] 使用 OpenAI SDK 兼容格式调用

### AI 服务层

- [x] 实现 `AIService` 类（`app/services/ai_service.py`）
- [x] 理财建议生成：汇总消费数据 → 构建 Prompt → 调用 LLM → 解析并存储
- [x] 缓存机制：相同分析周期的建议自动缓存
- [x] 降级策略：LLM 调用失败时返回友好默认建议

> **已移除**：`POST /api/ai/classify`、`POST /api/ai/reclassify/{id}` 及微信导入自动 AI 分类。`ai_service.py` 内规则/分类相关代码保留供维护脚本使用，不再对外暴露。

### AI API 接口（当前 4 个端点）

- [x] `GET /api/ai/advice` - 获取个性化理财建议
- [x] `GET /api/ai/advice/history` - 历史建议列表（分页）
- [x] `GET /api/ai/advice/history/{record_id}` - 建议详情
- [x] `GET /api/ai/usage` - 用量统计

### 数据模型

- [x] `AIAdviceRecord` 模型（`app/models/ai_advice_record.py`）

### Postman 测试集合

- [x] 「11. AI智能服务」文件夹：理财建议、历史、详情、用量（4 项）

## 心得体会

产品侧去掉智能分类后，AI 模块职责更清晰：专注理财建议与可解释的财务分析，减少 LLM 在批量导入链路上的不确定性与成本。
