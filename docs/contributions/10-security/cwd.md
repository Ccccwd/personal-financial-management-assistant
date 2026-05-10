# 安全审查贡献说明

**姓名**: 陈伟栋
**学号**: 2312190218
**日期**: 2026-05-10

## 我完成的工作

### AI 安全审查

使用 Claude Code AI 对后端核心代码进行 OWASP Top 10 视角的安全审查，审查了以下模块：

| 模块 | 审查文件 |
|------|----------|
| 认证安全 | `app/core/security.py`, `app/api/auth.py`, `app/core/dependencies.py` |
| 异常处理 | `app/core/exceptions.py` |
| 配置管理 | `app/config/settings.py`, `.env.example` |
| 交易接口 | `app/api/transactions.py` |
| AI 服务 | `app/services/ai_service.py`, `app/api/ai.py` |
| 微信导入 | `app/api/wechat_bill.py`, `app/services/wechat_bill_service.py` |
| 应用入口 | `main.py` |

**AI 发现的主要问题**:

1. **高危**: `.env.example` 包含真实 API 密钥
2. **高危**: `/reset-password` 端点无需认证即可重置密码
3. **中危**: `verify_refresh_token` 未检查 Token 黑名单
4. **中危**: 调试模式向客户端暴露数据库错误详情
5. **中危**: 登录等接口无速率限制保护
6. **低危**: `sort_by` 参数允许任意列排序
7. **低危**: CORS 允许所有来源
8. **低危**: Token 黑名单仅存储在内存

**我修复了哪些问题**: 全部 8 个问题均已修复或加固

### 安全检查清单

#### 认证与授权
- [x] 密码存储：使用 bcrypt 哈希，不存明文
- [x] JWT / Session：Token 有过期时间，logout 后失效（黑名单）
- [x] 接口鉴权：所有需要登录的接口都有权限校验（`get_current_active_user`）
- [x] 越权访问：用户只能操作自己的数据（所有查询过滤 `user_id`）

#### 注入防护
- [x] SQL：使用 SQLAlchemy ORM，无字符串拼接 SQL
- [x] XSS：后端为 API 服务不渲染 HTML，前端使用 Vue 自动转义

#### 敏感信息
- [x] API Key / 密码：通过 `.env` 环境变量读取，不硬编码
- [x] .env 文件：已加入 `.gitignore`，仓库中有 `.env.example`（已清理密钥）

#### 依赖安全
- [x] 运行 `pip-audit` 依赖扫描，集成在 CI 中

### CI 安全扫描

- **配置了选项 A + B**: Gitleaks 密钥泄露扫描 + pip-audit 依赖漏洞扫描
- **配置文件**: `.github/workflows/security.yml`
- **触发条件**: push 到 main/dev 或 PR 到 main 时自动运行
- **扫描结果**: 待合并后首次运行验证

### 选做完成情况

| 选做项 | 状态 | 说明 |
|--------|------|------|
| 速率限制 | ✅ 已完成 | 登录 5次/分钟，全局 60次/分钟 |
| 安全 HTTP 头 | ✅ 已完成 | X-Content-Type-Options, X-Frame-Options, CSP 等 |
| Prompt 注入防护 | 已考虑 | AI 服务使用 `response_format=json_object` 约束输出格式 |

## PR 链接

待合并后补充。

## 遇到的问题和解决

1. **问题**: 添加速率限制中间件后，测试套件中 68 个 API 测试全部返回 429 错误
   - **解决**: 在速率限制中间件中添加测试环境检测（`APP_ENV=testing`），测试时跳过限制

2. **问题**: 移除 `/reset-password` 端点后，需要确保 `ResetPassword` schema 的 import 不影响其他代码
   - **解决**: 从 auth.py 中移除未使用的 `ResetPassword` import

## 心得体会

在 Vibe Coding 工作流中，AI 能够快速系统地审查代码安全问题，覆盖 OWASP Top 10 的各个维度。但安全修复需要谨慎处理边界情况——比如速率限制中间件虽然保护了生产环境，但在测试环境中反而成为了阻碍。这提醒我们在做安全加固时，要同时考虑开发和测试的便利性。总体来说，AI 辅助安全审查能显著提升效率，但最终的判断和权衡仍需要开发者根据项目实际情况来决定。
