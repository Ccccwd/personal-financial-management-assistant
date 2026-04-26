# 软件测试贡献说明

姓名：陈伟栋  学号：2312190218  角色：后端  日期：2026-04-25

## 完成的测试工作

### 测试文件

- `tests/test_services.py` - 业务逻辑单元测试（Mock 隔离外部依赖）
- `tests/test_reminders.py` - 提醒管理 API 接口测试
- `tests/test_reports.py` - 分析报告 API 接口测试
- `tests/test_ai_api.py` - AI 智能服务 API 接口测试（Mock LLM 调用）
- `tests/test_ai.py` - 余额历史 API 接口测试
- `tests/test_accounts.py` - 账户管理 API 接口测试（已有）
- `tests/test_categories.py` - 分类管理 API 接口测试（已有）
- `tests/conftest.py` - 测试 fixtures 配置

### 测试清单

- [x] 正常情况测试（72 个）
  - 认证：注册、登录、获取用户信息、重复注册、错误密码
  - 分类：CRUD、列表过滤、树形结构、统计
  - 账户：CRUD、列表、摘要、默认账户、转账、余额调整
  - 提醒：CRUD、列表过滤、统计、今日提醒、切换状态
  - 报告：月度报告、年度报告、分类分析、自动报告生成
  - AI：智能分类、重新分类、理财建议、历史记录、用量统计
  - 余额历史：全局历史、账户历史、类型过滤、分页

- [x] 边界 / 异常情况测试（18 个）
  - 重复注册返回 400
  - 错误密码返回 401
  - 未认证访问返回 401
  - 无效 Token 验证返回 None
  - 过期 Token 验证返回 None
  - 同名账户返回 400
  - 不存在的资源返回 404
  - 无效时间格式返回 400
  - 余额不足转账返回 400
  - 向同一账户转账返回 400
  - 无交易数据时 AI 建议返回默认提示
  - LLM 调用失败时降级返回默认分类
  - 空商户名规则匹配返回 None
  - 不存在的分类分析返回 404
  - 不存在的建议记录返回 404
  - 缺少必填参数返回 422
  - 空余额历史返回空列表
  - 相同密码生成不同哈希

- [x] Mock 使用（8 处）
  - `@patch.object(AIService, 'classify_by_llm')` - Mock LLM 分类调用
  - `@patch.object(AIService, '_find_category_by_name')` - Mock 数据库分类查询
  - `@patch('app.services.ai_service.OpenAI')` - Mock OpenAI 客户端
  - `@patch('app.services.ai_service.AIService.generate_advice')` - Mock 建议生成
  - `@patch('app.services.ai_service.AIService.reclassify_transaction')` - Mock 重新分类
  - `@patch('app.services.ai_service.AIService.classify_items')` - Mock 批量分类

### 覆盖率

- 总覆盖率：**68%**（1940 行代码，628 行未覆盖）
- 核心模块覆盖率：
  - `app/core/security.py`：**100%**
  - `app/api/reports.py`：**100%**
  - `app/api/accounts.py`：**93%**
  - `app/api/categories.py`：**94%**
  - `app/api/balance_history.py`：**97%**
  - `app/models/*`：**92%-97%**
  - `app/schemas/*`：**100%**（除未使用的 balance_history）
  - `app/services/ai_service.py`：**71%**

### AI 辅助

- 使用工具：Claude Code（AI 编程助手）
- AI 辅助生成的测试：约 60 个（API 测试 + Mock 测试框架搭建）
- 人工修改的测试：约 38 个（修复断言、调整 Mock 返回值、修复 Schema 兼容性问题）

## PR 链接

- PR #X: https://github.com/Ccccwd/personal-financial-management-assistant/pull/X（待提交）

## 遇到的问题和解决

1. **问题**：Reminder 模型的 `remind_time` 字段使用 SQLAlchemy `Time` 类型，Pydantic 的 `from_attributes` 将其映射为 `datetime.time` 对象而非 Schema 定义的 `str`，导致序列化时 ValidationError
   **解决**：将 Schema 的 `remind_time` 类型改为 `Optional[Union[str, time]]`，兼容两种类型

2. **问题**：AI 建议接口的 Mock 返回值使用字符串日期，但 API 代码调用 `.isoformat()` 方法导致 AttributeError
   **解决**：Mock 返回值中使用 `datetime` 对象而非字符串，与实际代码行为一致

3. **问题**：`reports.py` 被误覆盖为分类管理的旧代码，导致报告相关测试全部返回 404
   **解决**：重新写入正确的报告 API 实现，确认所有 4 个端点（月度/年度/分类分析/自动报告）正常工作

4. **问题**：SQLite 不支持某些 MySQL 特有的 SQL 语法（如 `Time` 类型的某些操作）
   **解决**：在 Schema 层面做类型转换，确保与 SQLite 测试数据库兼容

## 心得体会

本次测试工作让我深入理解了测试金字塔的实践：单元测试覆盖核心业务逻辑（密码加密、JWT Token、AI 规则匹配），API 测试验证接口的正确性和异常处理。Mock 的使用让我学会了如何隔离外部依赖（LLM API、数据库查询），使测试更快速、更稳定。覆盖率 68% 说明还有优化空间，核心模块（认证、分类、账户、报告、安全）均达到 86%-100%，符合质量要求。
