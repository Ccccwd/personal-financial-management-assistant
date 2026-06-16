# 安全审查贡献说明

姓名：曾昭祥  
学号：2312190219  
日期：2026-06-16

## 我完成的工作

### AI 安全审查

- 审查范围：参考 `docs/security-review.md`（由陈伟栋同学主导完成 OWASP Top 10 审查）
- 本人在本次迭代中重点复核：AI 相关配置与前端监控页新增代码未引入新的安全风险

### 安全检查清单（复核状态）

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 密码 bcrypt 哈希 | ✅ | 后端 `app/core/security.py` |
| JWT 过期与 logout 黑名单 | ✅ | Refresh Token 已检查黑名单 |
| 接口鉴权 | ✅ | 业务接口需 Bearer Token；health/metrics 为公开监控端点 |
| 越权访问防护 | ✅ | 交易、分类等按 `user_id` 过滤 |
| SQL 参数化 / ORM | ✅ | SQLAlchemy ORM，无字符串拼接 |
| API Key 环境变量 | ✅ | `backend/.env` 不入库，`.env.example` 为占位符 |
| 依赖漏洞扫描 | ✅ | `.github/workflows/security.yml` 集成 gitleaks + pip-audit |

### CI 安全扫描

- 配置选项：**A（Gitleaks）+ B（pip-audit）**
- 配置文件：`.github/workflows/security.yml`
- 本次修改后复核：未在代码中硬编码密钥，未新增无鉴权敏感接口

### 本次变更安全自查

| 变更 | 安全评估 |
|------|----------|
| `normalize_budget_suggestion` | 仅做数据结构转换，无用户输入拼接 |
| 前端监控页 | 只读展示公开 health/metrics，无 XSS 风险（无 innerHTML） |
| AI API Key 配置 | 仍通过 `.env` 管理，未提交到 Git |

## 遇到的问题和解决

1. **问题**：修改 `.env` 后需确保密钥不进入版本库  
   **解决**：确认 `.gitignore` 已忽略 `.env`，仅更新本地配置

2. **问题**：Docker 重建容器后环境变量未生效  
   **解决**：使用 `docker compose up -d --force-recreate backend` 重新加载 `env_file`

## 心得体会

安全审查不是一次性任务。每次新增功能（如 AI 集成、监控页面）都应复核是否引入密钥泄露、越权或注入风险。Vibe Coding 提升效率的同时，需要用检查清单和 CI 扫描守住底线。
