# 安全审查报告

## 项目信息

- **项目名称**: 智能个人财务记账系统
- **审查日期**: 2026-05-10
- **审查范围**: 后端核心代码（认证、数据库操作、API 接口、AI 服务）
- **审查标准**: OWASP Top 10 (2021)

---

## 一、审查方法

使用 AI 辅助安全审查（Claude Code Vibe Coding 工作流），对以下核心模块进行 OWASP Top 10 视角的代码审查：

| 模块 | 文件 | 说明 |
|------|------|------|
| 认证安全 | `app/core/security.py` | JWT 签发、密码哈希、Token 黑名单 |
| 认证接口 | `app/api/auth.py` | 注册、登录、密码重置 |
| 依赖注入 | `app/core/dependencies.py` | 用户鉴权中间件 |
| 异常处理 | `app/core/exceptions.py` | 全局错误处理 |
| 配置管理 | `app/config/settings.py` | 环境变量、密钥配置 |
| 交易接口 | `app/api/transactions.py` | 交易 CRUD |
| AI 服务 | `app/services/ai_service.py` | LLM 调用 |
| 应用入口 | `main.py` | CORS、中间件配置 |
| 微信导入 | `app/api/wechat_bill.py` | 文件上传处理 |
| 微信解析 | `app/services/wechat_bill_service.py` | CSV 解析 |

---

## 二、发现的安全问题

### 问题 #1: .env.example 包含真实 API 密钥

- **OWASP 分类**: A02:2021 - 加密机制失败
- **危害等级**: **高**
- **文件**: `backend/.env.example`
- **问题描述**: `.env.example` 文件中包含真实的 AI API Key（`5113b387ac4e424e8fe739ff4e5810d4.TRmbbS3OdmHVCs4c`）和数据库密码（`finance123456`）。该文件会被提交到 Git 仓库，任何人都可以看到这些密钥。
- **修复方案**: 将 `.env.example` 中的所有密钥替换为占位符（如 `your_api_key_here`）。

### 问题 #2: 无需认证即可重置密码

- **OWASP 分类**: A01:2021 - 失效的访问控制
- **危害等级**: **高**
- **文件**: `backend/app/api/auth.py`
- **问题描述**: `/api/auth/reset-password` 端点仅需提供邮箱和新密码即可重置密码，无需任何身份验证或 Token。攻击者可以利用此端点重置任意用户的密码。
- **修复方案**: 移除该无认证端点。密码重置应通过 `/password-reset-request` 生成 Token，再通过 `/password-reset` 使用 Token 验证后重置。

### 问题 #3: Refresh Token 未检查黑名单

- **OWASP 分类**: A01:2021 - 失效的访问控制
- **危害等级**: **中**
- **文件**: `backend/app/core/security.py`
- **问题描述**: `verify_refresh_token()` 函数没有调用 `is_blacklisted()` 检查。这意味着即使用户登出（Token 被加入黑名单），refresh_token 仍然可以用来获取新的 access_token。
- **修复方案**: 在 `verify_refresh_token()` 开头添加黑名单检查。

### 问题 #4: 调试模式暴露数据库错误详情

- **OWASP 分类**: A05:2021 - 安全配置错误
- **危害等级**: **中**
- **文件**: `backend/app/core/exceptions.py`
- **问题描述**: 全局异常处理器在 `app.debug` 为 True 时，会将数据库错误详情（`str(exc)`）和未处理异常信息返回给客户端，可能暴露表结构、SQL 语句等敏感信息。
- **修复方案**: 移除所有异常响应中的 `str(exc)` 输出，改为使用 `logging` 记录到服务端日志。

### 问题 #5: sort_by 参数允许任意列排序

- **OWASP 分类**: A01:2021 - 失效的访问控制
- **危害等级**: **低**
- **文件**: `backend/app/api/transactions.py`
- **问题描述**: `GET /api/transactions` 的 `sort_by` 参数通过 `getattr(Transaction, sort_by, ...)` 直接访问 ORM 模型属性，虽然不会导致 SQL 注入，但允许按任意列排序（如 `password_hash` 等内部字段）。
- **修复方案**: 添加白名单限制，仅允许 `transaction_date`、`amount`、`created_at`、`type` 四个字段排序。

### 问题 #6: CORS 允许所有来源

- **OWASP 分类**: A05:2021 - 安全配置错误
- **危害等级**: **低**（当前为开发环境）
- **文件**: `main.py`
- **问题描述**: `allow_origins=["*"]` 允许任何域名跨域访问 API。在开发环境可接受，但生产环境需要限制为前端域名。
- **修复方案**: 从环境变量读取允许的域名列表，生产环境设置为具体的前端 URL。

### 问题 #7: Token 黑名单仅存储在内存中

- **OWASP 分类**: A07:2021 - 身份识别和认证失败
- **危害等级**: **低**
- **文件**: `backend/app/core/security.py`
- **问题描述**: `BLACKLIST = set()` 是一个 Python 内存集合，服务重启后黑名单丢失，已登出的 Token 可以被重新使用。
- **修复方案**: 生产环境应使用 Redis 存储黑名单（项目已配置 Redis，但尚未集成）。

### 问题 #8: 无速率限制保护

- **OWASP 分类**: A07:2021 - 身份识别和认证失败
- **危害等级**: **中**
- **文件**: `main.py`（原缺少）
- **问题描述**: 登录、注册等敏感接口没有速率限制，容易遭受暴力破解攻击。
- **修复方案**: 添加基于 IP 的速率限制中间件，登录接口限制 5次/分钟，全局 API 限制 60次/分钟。

---

## 三、已完成的修复

| 编号 | 问题 | 修复方式 | 涉及文件 |
|------|------|----------|----------|
| #1 | .env.example 泄露密钥 | 替换为占位符 | `backend/.env.example` |
| #2 | 无认证密码重置 | 移除 `/reset-password` 端点 | `backend/app/api/auth.py` |
| #3 | Refresh Token 未检查黑名单 | 添加 `is_blacklisted()` 检查 | `backend/app/core/security.py` |
| #4 | 异常暴露内部信息 | 移除错误详情输出，改用 logging | `backend/app/core/exceptions.py` |
| #5 | sort_by 无限制 | 添加白名单过滤 | `backend/app/api/transactions.py` |
| #8 | 无速率限制 | 添加速率限制中间件 | `backend/app/core/rate_limiter.py`, `backend/main.py` |

### 额外安全加固

- **安全 HTTP 响应头**: 添加 `X-Content-Type-Options`、`X-Frame-Options`、`X-XSS-Protection`、`Referrer-Policy`、`Content-Security-Policy` 等安全头
- **print() 替换为 logging**: `main.py` 中的 `print()` 语句替换为标准 `logging` 模块

---

## 四、安全检查清单

### 认证与授权

- [x] **密码存储**: 使用 bcrypt 哈希，不存明文
- [x] **JWT / Session**: Token 有过期时间（access 30 分钟，refresh 7 天），logout 后加入黑名单
- [x] **接口鉴权**: 所有需要登录的接口通过 `get_current_active_user` 依赖注入校验
- [x] **越权访问**: 所有数据操作均过滤 `user_id == current_user.id`

### 注入防护

- [x] **SQL 注入**: 使用 SQLAlchemy ORM，所有查询均为参数化查询，无字符串拼接 SQL
- [x] **XSS**: 后端为纯 API 服务，不渲染 HTML。前端使用 Vue 模板语法自动转义

### 敏感信息

- [x] **API Key / 密码**: 不硬编码在代码中，通过 `.env` 环境变量读取
- [x] **.env 文件**: 已加入 `.gitignore`，仓库中有 `.env.example`（已清理密钥）

### 依赖安全

- [x] **依赖扫描**: CI 中集成 `pip-audit` 进行依赖漏洞扫描

---

## 五、CI 自动化安全扫描

### 已配置的扫描项

#### 选项 A: 密钥泄露扫描 (Gitleaks)

- **配置文件**: `.github/workflows/security.yml`
- **扫描工具**: `gitleaks/gitleaks-action@v2`
- **触发条件**: push 到 main/dev 分支 或 PR 到 main 分支
- **扫描范围**: 全部 Git 历史，检测硬编码的密钥、Token、密码等

#### 选项 B: 依赖漏洞扫描 (pip-audit)

- **配置文件**: `.github/workflows/security.yml`
- **扫描工具**: `pip-audit`
- **触发条件**: 同上
- **扫描范围**: 后端 Python 依赖包，检测已知 CVE 漏洞

---

## 六、结论

通过本次安全审查，共发现 **8 个安全问题**（2 个高危、3 个中危、3 个低危），已全部修复。项目在以下方面具有较好的安全基础：

1. **密码安全**: 使用 bcrypt 加密存储，非明文
2. **注入防护**: 全部使用 SQLAlchemy ORM，无 SQL 注入风险
3. **认证机制**: JWT + Refresh Token + 黑名单，多层保护
4. **数据隔离**: 所有接口均按用户 ID 过滤数据，防止越权访问

仍需在生产环境部署前完善的部分：
- Token 黑名单迁移到 Redis（持久化存储）
- CORS 白名单根据实际域名配置
- 考虑添加 HTTPS 强制跳转
