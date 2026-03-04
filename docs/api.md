# 智能个人财务记账系统 API 设计文档

**版本：** 2.0.0  
**Base URL：** `http://localhost:8000`  
**认证方式：** Bearer Token（JWT）  
**Content-Type：** `application/json`

---

## 目录

1. [通用说明](#通用说明)
2. [认证模块](#一认证模块-prefix-apiauth)
3. [分类管理](#二分类管理-prefix-apicategories)
4. [账户管理](#三账户管理-prefix-apiaccounts)
5. [交易记录](#四交易记录-prefix-apitransactions)
6. [预算管理](#五预算管理-prefix-apibudgets)
7. [统计分析](#六统计分析-prefix-apistatistics)
8. [分析报告](#七分析报告-prefix-apireports)
9. [微信账单导入](#八微信账单导入-prefix-apiwechat)
10. [账户余额历史](#九账户余额历史)
11. [智能提醒](#十智能提醒-prefix-apireminders)
12. [AI 智能服务（新）](#十一ai-智能服务新-prefix-apiai)
13. [数据模型](#数据模型)
14. [错误码说明](#错误码说明)

---

## 通用说明

### 统一响应格式

所有接口均返回以下结构（除文件下载接口）：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | integer | 状态码，200 表示成功 |
| `message` | string | 响应描述 |
| `data` | object/array/null | 业务数据 |

### 认证说明

除注册、登录接口外，所有接口需在请求头中携带 Token：

```
Authorization: Bearer <access_token>
```

### 分页参数（通用）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `page` | integer | 1 | 页码，从 1 开始 |
| `page_size` | integer | 20 | 每页数量，最大 100 |

---

## 一、认证模块 `prefix: /api/auth`

### 1.1 用户注册

```
POST /api/auth/register
```

**请求体：**

```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string"
}
```

**响应示例：**

```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "id": 1,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "created_at": "2026-03-04T10:00:00"
  }
}
```

---

### 1.2 用户登录

```
POST /api/auth/login
```

**请求体：**

```json
{
  "username": "string",
  "password": "string"
}
```

**响应示例：**

```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

---

### 1.3 刷新 Token

```
POST /api/auth/refresh
```

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `refresh_token` | string | 是 | 刷新令牌 |

---

### 1.4 用户登出

```
POST /api/auth/logout
```

**需要认证：** 是

---

### 1.5 获取当前用户信息

```
GET /api/auth/me
```

**需要认证：** 是

**响应示例：**

```json
{
  "code": 200,
  "data": {
    "id": 1,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "avatar": "https://...",
    "created_at": "2026-01-01T00:00:00"
  }
}
```

---

### 1.6 更新当前用户信息

```
PUT /api/auth/me
```

**需要认证：** 是

**请求体（部分更新）：**

```json
{
  "username": "string",
  "avatar": "string"
}
```

---

### 1.7 修改密码

```
POST /api/auth/change-password
```

**需要认证：** 是

**请求体：**

```json
{
  "old_password": "string",
  "new_password": "string"
}
```

---

### 1.8 请求密码重置

```
POST /api/auth/password-reset-request
```

**请求体：**

```json
{
  "email": "user@example.com"
}
```

---

### 1.9 通过 Token 重置密码

```
POST /api/auth/password-reset
```

**请求体：**

```json
{
  "token": "string",
  "new_password": "string"
}
```

---

### 1.10 直接通过邮箱重置密码

```
POST /api/auth/reset-password
```

**请求体：**

```json
{
  "email": "user@example.com",
  "new_password": "string"
}
```

---

### 1.11 验证邮箱是否存在

```
POST /api/auth/verify-email-for-reset
```

**请求体：**

```json
{
  "email": "user@example.com"
}
```

---

## 二、分类管理 `prefix: /api/categories`

分类包括系统预设分类和用户自定义分类，支持二级层级结构。

### 2.1 获取分类列表

```
GET /api/categories
```

**需要认证：** 是

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | string | 否 | 分类类型：`income` / `expense` |
| `include_system` | boolean | 否 | 是否包含系统分类，默认 `true` |
| `parent_id` | integer | 否 | 父分类 ID |

**响应示例：**

```json
{
  "code": 200,
  "data": {
    "categories": [
      {
        "id": 1,
        "name": "餐饮",
        "type": "expense",
        "icon": "🍔",
        "color": "#FF6B6B",
        "parent_id": null,
        "sort_order": 1,
        "is_system": true
      }
    ],
    "total": 20
  }
}
```

---

### 2.2 获取分类树

```
GET /api/categories/tree
```

**需要认证：** 是

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | string | 否 | 分类类型：`income` / `expense` |
| `include_system` | boolean | 否 | 是否包含系统分类，默认 `true` |

返回带有 `children` 字段的树形结构。

---

### 2.3 获取带使用统计的分类列表

```
GET /api/categories/stats
```

**需要认证：** 是

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | string | 否 | 分类类型 |
| `limit` | integer | 否 | 返回数量，默认 20，最大 100 |

---

### 2.4 获取分类详情

```
GET /api/categories/{category_id}
```

**需要认证：** 是

---

### 2.5 创建分类

```
POST /api/categories
```

**需要认证：** 是

**请求体：**

```json
{
  "name": "string",
  "type": "expense",
  "icon": "🍕",
  "color": "#FF6B6B",
  "parent_id": null,
  "sort_order": 0
}
```

---

### 2.6 更新分类

```
PUT /api/categories/{category_id}
```

**需要认证：** 是

**请求体（部分更新，同创建分类）**

---

### 2.7 删除分类

```
DELETE /api/categories/{category_id}
```

**需要认证：** 是

---

## 三、账户管理 `prefix: /api/accounts`

账户类型枚举：`cash`（现金）、`bank`（银行卡）、`wechat`（微信）、`alipay`（支付宝）、`meal_card`（饭卡）、`other`（其他）

### 3.1 获取账户列表

```
GET /api/accounts
```

**需要认证：** 是

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | string | 否 | 账户类型 |
| `is_enabled` | boolean | 否 | 是否启用 |

**响应示例：**

```json
{
  "code": 200,
  "data": {
    "accounts": [
      {
        "id": 1,
        "name": "微信钱包",
        "type": "wechat",
        "balance": 2100.00,
        "initial_balance": 0.00,
        "icon": "💚",
        "color": "#07C160",
        "is_default": true,
        "is_enabled": true,
        "description": "",
        "created_at": "2026-01-01T00:00:00"
      }
    ],
    "total": 4
  }
}
```

---

### 3.2 获取账户统计摘要

```
GET /api/accounts/summary
```

**需要认证：** 是

返回总资产、各账户余额分布等汇总信息。

---

### 3.3 获取默认账户

```
GET /api/accounts/default
```

**需要认证：** 是

---

### 3.4 获取账户详情（含统计）

```
GET /api/accounts/{account_id}
```

**需要认证：** 是

返回账户基本信息及该账户的收支统计。

---

### 3.5 创建账户

```
POST /api/accounts
```

**需要认证：** 是

**请求体：**

```json
{
  "name": "工商银行储蓄卡",
  "type": "bank",
  "initial_balance": 5000.00,
  "icon": "🏦",
  "color": "#4A90E2",
  "is_default": false,
  "description": "日常消费账户"
}
```

---

### 3.6 更新账户

```
PUT /api/accounts/{account_id}
```

**需要认证：** 是

**请求体（部分更新，同创建账户）**

---

### 3.7 删除账户

```
DELETE /api/accounts/{account_id}
```

**需要认证：** 是

> ⚠️ 账户下存在交易记录时不允许删除。

---

### 3.8 账户间转账

```
POST /api/accounts/transfer
```

**需要认证：** 是

**请求体：**

```json
{
  "from_account_id": 1,
  "to_account_id": 2,
  "amount": 500.00,
  "remark": "备用金转账",
  "transaction_date": "2026-03-04T12:00:00"
}
```

**响应：** 返回转出和转入两条交易记录及账户更新后的余额。

---

### 3.9 调整账户余额

```
POST /api/accounts/{account_id}/adjust-balance
```

**需要认证：** 是

**请求体：**

```json
{
  "new_balance": 1500.00,
  "remark": "手动校正余额"
}
```

---

## 四、交易记录 `prefix: /api/transactions`

交易类型枚举：`income`（收入）、`expense`（支出）、`transfer`（转账）

### 4.1 获取交易列表

```
GET /api/transactions
```

**需要认证：** 是

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `page` | integer | 否 | 页码，默认 1 |
| `page_size` | integer | 否 | 每页数量，默认 20 |
| `type` | string | 否 | 交易类型：`income` / `expense` / `transfer` |
| `category_id` | integer | 否 | 分类 ID |
| `account_id` | integer | 否 | 账户 ID |
| `start_date` | string | 否 | 开始日期，ISO 8601 格式 |
| `end_date` | string | 否 | 结束日期，ISO 8601 格式 |
| `keyword` | string | 否 | 备注/商户名关键词搜索 |
| `min_amount` | number | 否 | 最小金额 |
| `max_amount` | number | 否 | 最大金额 |
| `sort_by` | string | 否 | 排序字段 |
| `sort_order` | string | 否 | 排序方向：`asc` / `desc` |

**响应示例：**

```json
{
  "transactions": [
    {
      "id": 1,
      "type": "expense",
      "amount": 35.50,
      "category_id": 1,
      "category_name": "餐饮",
      "category_icon": "🍔",
      "account_id": 2,
      "account_name": "微信钱包",
      "transaction_date": "2026-03-04T12:30:00",
      "remark": "麦当劳午餐",
      "merchant_name": "麦当劳",
      "source": "manual",
      "created_at": "2026-03-04T12:31:00"
    }
  ],
  "total": 156,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

---

### 4.2 获取交易统计摘要

```
GET /api/transactions/summary
GET /api/transactions/statistics
```

**需要认证：** 是

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `start_date` | string | 否 | 开始日期 |
| `end_date` | string | 否 | 结束日期 |
| `type` | string | 否 | 交易类型 |

**响应示例：**

```json
{
  "total_income": 5000.00,
  "total_expense": 3245.00,
  "total_transfer": 500.00,
  "net_income": 1755.00,
  "transaction_count": 156
}
```

---

### 4.3 搜索交易记录

```
GET /api/transactions/search
```

**需要认证：** 是

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `keyword` | string | 是 | 搜索关键词（最少 1 字符） |
| `limit` | integer | 否 | 结果数量，默认 50，最大 100 |

---

### 4.4 获取交易详情

```
GET /api/transactions/{transaction_id}
```

**需要认证：** 是

---

### 4.5 创建交易记录

```
POST /api/transactions
```

**需要认证：** 是

**请求体：**

```json
{
  "type": "expense",
  "amount": 35.50,
  "category_id": 1,
  "account_id": 2,
  "transaction_date": "2026-03-04T12:30:00",
  "remark": "麦当劳午餐",
  "merchant_name": "麦当劳",
  "tags": ["餐饮", "快餐"],
  "location": "北京市朝阳区",
  "images": ["https://..."]
}
```

---

### 4.6 更新交易记录

```
PUT /api/transactions/{transaction_id}
```

**需要认证：** 是

**请求体（部分更新，同创建交易）**

---

### 4.7 删除交易记录

```
DELETE /api/transactions/{transaction_id}
```

**需要认证：** 是

---

### 4.8 标记交易为重复

```
POST /api/transactions/{transaction_id}/mark-repeated
```

**需要认证：** 是

---

## 五、预算管理 `prefix: /api/budgets`

预算周期类型：`monthly`（月度）、`yearly`（年度）

### 5.1 获取预算列表

```
GET /api/budgets
```

**需要认证：** 是

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `year` | integer | 是 | 年份 |
| `month` | integer | 否 | 月份（1-12） |
| `period_type` | string | 否 | 周期类型：`monthly` / `yearly` |

**响应示例：**

```json
{
  "code": 200,
  "data": {
    "year": 2026,
    "month": 3,
    "budgets": [
      {
        "id": 1,
        "category": {
          "id": 1,
          "name": "餐饮",
          "icon": "🍔",
          "color": "#FF6B6B"
        },
        "amount": 1000.00,
        "actual_spending": 856.00,
        "remaining": 144.00,
        "percentage": 85.6,
        "status": "warning",
        "period_type": "monthly",
        "year": 2026,
        "month": 3,
        "alert_threshold": 80,
        "is_enabled": true
      }
    ]
  }
}
```

> `status` 说明：`normal`（正常）、`warning`（预警，已达阈值）、`exceeded`（超支）

---

### 5.2 创建预算

```
POST /api/budgets
```

**需要认证：** 是

**请求体：**

```json
{
  "category_id": 1,
  "amount": 1000.00,
  "period_type": "monthly",
  "year": 2026,
  "month": 3,
  "alert_threshold": 80,
  "is_enabled": true
}
```

> `category_id` 为 `null` 时表示总预算。

---

### 5.3 更新预算

```
PUT /api/budgets/{budget_id}
```

**需要认证：** 是

**请求体（部分更新）：**

```json
{
  "amount": 1200.00,
  "alert_threshold": 90
}
```

---

### 5.4 删除预算

```
DELETE /api/budgets/{budget_id}
```

**需要认证：** 是

---

## 六、统计分析 `prefix: /api/statistics`

### 6.1 获取首页概览

```
GET /api/statistics/overview
```

**需要认证：** 是

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `current_year` | integer | 否 | 年份，默认当前年 |
| `current_month` | integer | 否 | 月份，默认当前月 |

**响应示例：**

```json
{
  "code": 200,
  "data": {
    "period": "2026年3月",
    "monthly_summary": {
      "income": 5000.00,
      "expense": 3245.00,
      "balance": 1755.00,
      "income_growth": 12.5,
      "expense_growth": -5.2
    },
    "total_balance": 12450.00,
    "category_distribution": [
      {
        "name": "餐饮",
        "icon": "🍔",
        "color": "#FF6B6B",
        "amount": 856.00,
        "percentage": 26.37
      }
    ],
    "trend_data": [
      { "date": "2026-02-26", "amount": 120.00 },
      { "date": "2026-02-27", "amount": 85.50 }
    ]
  }
}
```

---

### 6.2 获取趋势数据

```
GET /api/statistics/trend
```

**需要认证：** 是

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `period` | string | 否 | 周期：`daily` / `weekly` / `monthly`（默认）/ `yearly` |
| `start_date` | string | 否 | 开始日期 YYYY-MM-DD，默认近 6 个月 |
| `end_date` | string | 否 | 结束日期 YYYY-MM-DD |

**响应示例：**

```json
{
  "code": 200,
  "data": {
    "period": "monthly",
    "start_date": "2025-09-01",
    "end_date": "2026-03-04",
    "trend": [
      {
        "date": "2025年9月",
        "income": 5000.00,
        "expense": 3100.00,
        "balance": 1900.00
      }
    ]
  }
}
```

---

### 6.3 获取分类统计

```
GET /api/statistics/category
```

**需要认证：** 是

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `transaction_type` | string | 否 | 交易类型：`expense`（默认）/ `income` |
| `period` | string | 否 | 周期：`monthly`（默认）/ `yearly` |
| `year` | integer | 是 | 年份 |
| `month` | integer | 否 | 月份（period 为 monthly 时必需） |

**响应示例：**

```json
{
  "code": 200,
  "data": {
    "transaction_type": "expense",
    "total_amount": 3245.00,
    "categories": [
      {
        "id": 1,
        "name": "餐饮",
        "icon": "🍔",
        "color": "#FF6B6B",
        "amount": 856.00,
        "count": 45,
        "percentage": 26.37
      }
    ]
  }
}
```

---

### 6.4 导出 Excel

```
GET /api/statistics/export/excel
```

**需要认证：** 是

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `transaction_type` | string | 否 | 交易类型：`all`（默认）/ `income` / `expense` |
| `start_date` | string | 是 | 开始日期 YYYY-MM-DD |
| `end_date` | string | 是 | 结束日期 YYYY-MM-DD |

**响应：** 返回导出文件路径和文件名。

---

## 七、分析报告 `prefix: /api/reports`

### 7.1 获取月度报告

```
GET /api/reports/monthly
```

**需要认证：** 是

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `year` | integer | 是 | 年份（2020-2030） |
| `month` | integer | 是 | 月份（1-12） |

---

### 7.2 获取年度报告

```
GET /api/reports/yearly
```

**需要认证：** 是

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `year` | integer | 是 | 年份（2020-2030） |

---

### 7.3 获取分类分析报告

```
GET /api/reports/category/{category_id}
```

**需要认证：** 是

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `days` | integer | 否 | 分析天数，默认 30，最大 365 |

---

### 7.4 生成并发送月度自动报告

```
POST /api/reports/monthly-auto-report
```

**需要认证：** 是

后台任务生成当月报告。

---

## 八、微信账单导入 `prefix: /api/wechat`

支持 CSV 和 XLSX 双格式，提供解析预览、AI 智能分类、重复检测与批量导入功能。

### 8.1 预览账单文件

上传文件后返回解析预览数据，不写入数据库，供用户确认后再导入。

```
POST /api/wechat/preview
```

**需要认证：** 是  
**Content-Type：** `multipart/form-data`

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | file | 是 | 账单文件（`.csv` 或 `.xlsx`） |
| `limit` | integer | 否 | 预览条数，默认 10 |

**响应示例：**

```json
{
  "code": 200,
  "data": {
    "valid": true,
    "detected_format": "微信账单CSV",
    "filename": "微信支付账单.csv",
    "file_size": 24576,
    "summary": {
      "total_records": 120,
      "income_count": 10,
      "expense_count": 110,
      "total_income": 500.00,
      "total_expense": 3245.00,
      "start_date": "2026-01-01",
      "end_date": "2026-02-28",
      "potential_duplicates": 5
    },
    "preview_data": [
      {
        "transaction_date": "2026-01-05 12:30:45",
        "merchant_name": "麦当劳",
        "product_name": "巨无霸套餐",
        "income_expense": "支出",
        "amount": 35.50,
        "payment_method": "零钱",
        "wechat_transaction_id": "420000123456789"
      }
    ]
  }
}
```

---

### 8.2 导入账单（文件上传）

```
POST /api/wechat/import
```

**需要认证：** 是  
**Content-Type：** `multipart/form-data`

**请求参数：**

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `file` | file | 是 | — | 账单文件（`.csv` 或 `.xlsx`） |
| `skip_duplicates` | boolean | 否 | `true` | 是否跳过重复记录 |
| `ai_classify` | boolean | 否 | `true` | 是否启用 AI 智能分类 |
| `default_account_id` | integer | 否 | `null` | 导入时使用的默认账户 ID |

**响应示例：**

```json
{
  "code": 200,
  "message": "导入完成",
  "data": {
    "import_log_id": 42,
    "success_count": 115,
    "fail_count": 2,
    "duplicate_count": 3,
    "ai_classified_count": 28,
    "total_count": 120
  }
}
```

> `ai_classified_count`：其中由 AI 模型完成分类的条目数量。

---

### 8.3 导入账单（Base64 编码）

适用于前端已读取文件内容后直接传递的场景。

```
POST /api/wechat/import-base64
```

**需要认证：** 是

**请求体：**

```json
{
  "file_content": "<base64_encoded_content>",
  "filename": "bill.csv",
  "skip_duplicates": true,
  "ai_classify": true,
  "default_account_id": null
}
```

---

### 8.4 验证文件格式

仅验证文件格式合法性，不做数据解析。

```
POST /api/wechat/validate
```

**需要认证：** 是  
**Content-Type：** `multipart/form-data`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | file | 是 | 待验证文件 |

**响应示例：**

```json
{
  "code": 200,
  "data": {
    "valid": true,
    "detected_format": "微信账单CSV",
    "message": "文件格式正确，包含 120 条记录"
  }
}
```

---

### 8.5 获取导入日志列表

```
GET /api/wechat/import-logs
```

**需要认证：** 是

**Query 参数：** `page`、`page_size`

**响应示例：**

```json
{
  "code": 200,
  "data": {
    "logs": [
      {
        "id": 42,
        "source": "wechat",
        "total_count": 120,
        "success_count": 115,
        "duplicate_count": 3,
        "fail_count": 2,
        "ai_classified_count": 28,
        "import_time": "2026-03-04T10:00:00"
      }
    ],
    "total": 5
  }
}
```

---

### 8.6 获取导入日志详情

```
GET /api/wechat/import-logs/{log_id}
```

**需要认证：** 是

---

### 8.7 下载错误详情

导出本次导入中失败条目的 CSV 文件，包含原始数据及失败原因。

```
GET /api/wechat/import-logs/{log_id}/errors
```

**需要认证：** 是  
**响应：** `text/csv` 文件流

---


## 九、账户余额历史

### 9.1 获取指定账户的余额历史

```
GET /api/accounts/{account_id}/balance-history
```

**需要认证：** 是

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `limit` | integer | 否 | 数量限制，默认 50，最大 100 |
| `offset` | integer | 否 | 偏移量，默认 0 |
| `change_type` | string | 否 | 变化类型过滤 |

**响应示例：**

```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "account_id": 2,
      "transaction_id": 101,
      "change_type": "expense",
      "amount_before": 2135.50,
      "amount_after": 2100.00,
      "change_amount": -35.50,
      "description": "餐饮支出",
      "created_at": "2026-03-04T12:30:00"
    }
  ]
}
```

---

### 9.2 获取所有账户的余额历史

```
GET /api/balance-history
```

**需要认证：** 是

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `limit` | integer | 否 | 数量限制，默认 100，最大 200 |
| `offset` | integer | 否 | 偏移量，默认 0 |
| `change_type` | string | 否 | 变化类型过滤 |

响应中额外包含 `account_name` 字段。

---

## 十、智能提醒 `prefix: /api/reminders`

提醒类型枚举：`daily`（每日记账提醒）、`budget`（预算预警）、`recurring`（周期性提醒）、`report`（报告提醒）

### 10.1 获取提醒列表

```
GET /api/reminders
```

**需要认证：** 是

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `reminder_type` | string | 否 | 提醒类型 |
| `is_enabled` | boolean | 否 | 是否启用 |

**响应示例：**

```json
{
  "code": 200,
  "data": {
    "reminders": [
      {
        "id": 1,
        "type": "daily",
        "title": "每日记账提醒",
        "content": "别忘了记录今天的支出哦！",
        "remind_time": "21:00:00",
        "remind_day": null,
        "category_id": null,
        "amount": null,
        "is_enabled": true,
        "last_reminded_at": "2026-03-03T21:00:00"
      }
    ],
    "total": 3
  }
}
```

---

### 10.2 获取提醒详情

```
GET /api/reminders/{reminder_id}
```

**需要认证：** 是

---

### 10.3 创建提醒

```
POST /api/reminders
```

**需要认证：** 是

**请求体：**

```json
{
  "type": "budget",
  "title": "餐饮预算预警",
  "content": "餐饮预算已使用超过80%",
  "remind_time": "09:00:00",
  "remind_day": null,
  "category_id": 1,
  "amount": null,
  "is_enabled": true
}
```

---

### 10.4 更新提醒

```
PUT /api/reminders/{reminder_id}
```

**需要认证：** 是

**请求体（部分更新，同创建提醒）**

---

### 10.5 删除提醒

```
DELETE /api/reminders/{reminder_id}
```

**需要认证：** 是

---

### 10.6 切换提醒启用状态

```
PATCH /api/reminders/{reminder_id}/toggle
```

**需要认证：** 是

---

### 10.7 检查今日提醒

```
GET /api/reminders/check-today
```

**需要认证：** 是

返回今日需要触发的提醒列表。

---

### 11.8 获取提醒统计

```
GET /api/reminders/statistics
```

**需要认证：** 是

---

## 十一、AI 智能服务（新） `prefix: /api/ai`

本模块调用大语言模型（DeepSeek-Chat / GPT-4o），提供两项核心 AI 能力：**账单智能分类** 与 **个性化理财建议生成**。

---

### 11.1 账单智能分类

对单条或批量账单条目进行语义分类，返回推荐的系统分类。内置规则库优先匹配，无法命中时调用 LLM。

```
POST /api/ai/classify
```

**需要认证：** 是

**请求体：**

```json
{
  "items": [
    {
      "merchant_name": "瑞幸咖啡",
      "product_name": "生椰拿铁",
      "wechat_category": "餐饮美食",
      "amount": 15.90,
      "transaction_type": "expense"
    },
    {
      "merchant_name": "滴滴出行",
      "product_name": "快车",
      "wechat_category": "交通出行",
      "amount": 23.00,
      "transaction_type": "expense"
    }
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `items` | array | 是 | 待分类条目列表，最多 100 条 |
| `items[].merchant_name` | string | 是 | 商户名称 |
| `items[].product_name` | string | 否 | 商品/服务描述 |
| `items[].wechat_category` | string | 否 | 微信原始分类标签（辅助判断） |
| `items[].amount` | number | 否 | 金额（辅助判断） |
| `items[].transaction_type` | string | 否 | `income` / `expense` |

**响应示例：**

```json
{
  "code": 200,
  "data": {
    "results": [
      {
        "index": 0,
        "merchant_name": "瑞幸咖啡",
        "category_id": 1,
        "category_name": "餐饮",
        "confidence": 0.97,
        "matched_by": "rule"
      },
      {
        "index": 1,
        "merchant_name": "滴滴出行",
        "category_id": 2,
        "category_name": "交通",
        "confidence": 0.95,
        "matched_by": "llm"
      }
    ],
    "total": 2,
    "llm_called_count": 1,
    "rule_matched_count": 1
  }
}
```

| 响应字段 | 说明 |
|----------|------|
| `confidence` | 置信度，0-1 |
| `matched_by` | 匹配方式：`rule`（规则库）/ `llm`（大模型） |
| `llm_called_count` | 本次实际调用 LLM 的条目数量 |

---

### 11.2 重新分类单条交易

对已导入的某条交易调用 AI 重新分类，可在用户觉得分类不准确时手动触发。

```
POST /api/ai/reclassify/{transaction_id}
```

**需要认证：** 是

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `dry_run` | boolean | 否 | `true` 时仅返回预览，不修改数据库，默认 `false` |

**响应示例：**

```json
{
  "code": 200,
  "data": {
    "transaction_id": 1234,
    "old_category": { "id": 13, "name": "其他" },
    "new_category": { "id": 1, "name": "餐饮" },
    "confidence": 0.88,
    "applied": true
  }
}
```

---

### 11.3 获取个性化理财建议

基于用户近期消费数据，由 AI 生成结构化理财分析报告，包含消费亮点、超支风险、优化建议和下月预算参考。同一天内重复请求默认复用缓存，不重复调用 LLM。

```
GET /api/ai/advice
```

**需要认证：** 是

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `months` | integer | 否 | 分析的历史月数，默认 3，最大 6 |
| `force_refresh` | boolean | 否 | 强制重新生成（忽略缓存），默认 `false` |

**响应示例：**

```json
{
  "code": 200,
  "data": {
    "generated_at": "2026-03-04T10:00:00",
    "from_cache": false,
    "analysis_period": {
      "start": "2025-12-01",
      "end": "2026-03-04"
    },
    "advice": {
      "highlights": [
        "本月餐饮支出同比下降 12%，节约效果明显。",
        "本月结余率达 35%，高于过去三月均值 22%。"
      ],
      "warnings": [
        "娱乐消费本月达 ¥680，超出预算 36%，已连续两个月超支。",
        "购物支出环比增长 45%，需注意冲动消费趋势。"
      ],
      "suggestions": [
        "建议将娱乐类预算调整至 ¥800，并设置每日上限提醒。",
        "餐饮方面可减少外卖频次，预计每月节省约 ¥200。",
        "建议将每月结余的 50% 固定转入储蓄账户，养成强制储蓄习惯。"
      ],
      "next_month_budget": {
        "total": 3500.00,
        "breakdown": [
          { "category": "餐饮", "suggested_amount": 900.00 },
          { "category": "交通", "suggested_amount": 300.00 },
          { "category": "娱乐", "suggested_amount": 600.00 },
          { "category": "购物", "suggested_amount": 800.00 },
          { "category": "其他", "suggested_amount": 900.00 }
        ]
      },
      "full_report": "## 本月消费总结\n\n### 消费亮点\n..."
    }
  }
}
```

| 响应字段 | 说明 |
|----------|------|
| `from_cache` | 是否来自缓存 |
| `highlights` | 正向消费表现 |
| `warnings` | 需关注的超支或异常 |
| `suggestions` | 具体可执行的优化建议 |
| `next_month_budget.breakdown` | AI 推荐的下月各分类预算金额 |
| `full_report` | Markdown 格式完整报告，供前端渲染 |

---

### 11.4 获取历史建议记录列表

```
GET /api/ai/advice/history
```

**需要认证：** 是

**Query 参数：** `page`、`page_size`

**响应示例：**

```json
{
  "code": 200,
  "data": {
    "records": [
      {
        "id": 5,
        "generated_at": "2026-03-04T10:00:00",
        "analysis_period": { "start": "2025-12-01", "end": "2026-03-04" },
        "summary": "本月结余率 35%，娱乐超支需注意"
      }
    ],
    "total": 5
  }
}
```

---

### 11.5 获取历史建议详情

```
GET /api/ai/advice/history/{record_id}
```

**需要认证：** 是

返回完整的 `advice` 对象（结构同 12.3 响应）。

---

### 11.6 获取 AI 服务用量统计

返回当月 LLM API 调用次数及 Token 消耗，可用于前端展示剩余额度提示。

```
GET /api/ai/usage
```

**需要认证：** 是

**响应示例：**

```json
{
  "code": 200,
  "data": {
    "month": "2026-03",
    "classify_calls": 42,
    "advice_calls": 3,
    "total_tokens_used": 18500,
    "estimated_cost_cny": 0.19
  }
}
```

---

## 数据模型

### Transaction（交易记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 主键 |
| `user_id` | integer | 用户 ID |
| `type` | string | `income` / `expense` / `transfer` |
| `amount` | decimal | 金额（正数） |
| `category_id` | integer | 分类 ID |
| `account_id` | integer | 账户 ID |
| `to_account_id` | integer/null | 转账目标账户 ID |
| `transaction_date` | datetime | 交易时间 |
| `remark` | string | 备注 |
| `merchant_name` | string | 商户名称 |
| `product_name` | string | 商品/服务描述 |
| `source` | string | 来源：`manual` / `wechat` / `alipay` |
| `wechat_transaction_id` | string | 微信交易流水号（去重用） |
| `tags` | array | 标签列表 |
| `location` | string | 地理位置 |
| `images` | array | 票据图片 URL 列表 |
| `ai_classified` | boolean | 是否由 AI 完成分类 |
| `created_at` | datetime | 创建时间 |
| `updated_at` | datetime | 更新时间 |

### AIAdviceRecord（AI 建议记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 主键 |
| `user_id` | integer | 用户 ID |
| `generated_at` | datetime | 生成时间 |
| `analysis_start` | date | 分析起始日期 |
| `analysis_end` | date | 分析截止日期 |
| `summary` | string | 一句话摘要 |
| `full_report` | text | 完整 Markdown 报告 |
| `highlights` | JSON | 消费亮点数组 |
| `warnings` | JSON | 超支警示数组 |
| `suggestions` | JSON | 优化建议数组 |
| `next_month_budget` | JSON | 推荐下月预算 |
| `tokens_used` | integer | 本次调用消耗的 Token 数 |

### Account（账户）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 主键 |
| `user_id` | integer | 用户 ID |
| `name` | string | 账户名称 |
| `type` | string | `cash` / `bank` / `wechat` / `alipay` / `meal_card` / `other` |
| `balance` | decimal | 当前余额 |
| `initial_balance` | decimal | 初始余额 |
| `icon` | string | 图标 |
| `color` | string | 颜色（十六进制） |
| `is_default` | boolean | 是否默认账户 |
| `is_enabled` | boolean | 是否启用 |

### Budget（预算）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 主键 |
| `user_id` | integer | 用户 ID |
| `category_id` | integer/null | 分类 ID（null 为总预算） |
| `amount` | decimal | 预算金额 |
| `period_type` | string | `monthly` / `yearly` |
| `year` | integer | 年份 |
| `month` | integer/null | 月份（月度预算使用） |
| `alert_threshold` | integer | 预警阈值（百分比，默认 80） |
| `is_enabled` | boolean | 是否启用 |

---

## 错误码说明

| HTTP 状态码 | 业务 code | 说明 |
|-------------|-----------|------|
| 200 | 200 | 成功 |
| 400 | 400 | 请求参数错误 / 业务校验失败 |
| 401 | 401 | 未认证或 Token 已过期 |
| 403 | 403 | 无权限访问 |
| 404 | 404 | 资源不存在 |
| 422 | 422 | 请求体格式校验失败（FastAPI 自动返回） |
| 429 | 429 | AI 服务调用频率超限 |
| 500 | 500 | 服务器内部错误 |
| 503 | 503 | AI 服务暂时不可用（上游 LLM API 异常） |

**错误响应格式：**

```json
{
  "code": 400,
  "message": "该分类预算已存在，请编辑现有预算",
  "data": null
}
```
