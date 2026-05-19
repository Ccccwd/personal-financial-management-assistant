# CI/CD 配置贡献说明

姓名：陈伟栋  学号：2312190218  角色：后端  日期：2026-05-03

## 完成的工作

### 工作流相关

- [x] 在已有 `.github/workflows/ci.yml` 中添加后端 backend job（与前端 frontend 并行运行）
- [x] 配置 Codecov 覆盖率上传（backend flag）
- [x] README.md 状态徽章已存在（CI + Backend Coverage + Frontend Coverage）

### 后端 CI Job 配置

```yaml
backend:
  runs-on: ubuntu-latest
  steps:
    - 设置 Python 3.12
    - 安装 uv（astral-sh/setup-uv@v4）
    - uv sync 安装依赖
    - ruff check app/ 进行 Lint 检查
    - pytest --cov=app --cov-report=xml 运行测试+覆盖率
    - codecov/codecov-action@v4 上传覆盖率（flag: backend）
  env:
    DATABASE_URL: sqlite:///./test.db  # CI 使用 SQLite 替代 MySQL
```

### 代码适配

- [x] pyproject.toml 添加 `[tool.pytest.ini_options]`、`[tool.coverage.run]`、`[tool.ruff]` 配置
- [x] ruff lint 零警告（89 个错误全部修复）
  - 77 个自动修复（未使用的导入、`== True/False` 比较）
  - 12 个手动修复（`__init__.py` re-export 使用 `as` 别名）
- [x] 本地测试命令与 CI 一致：`uv run pytest tests/ -v --cov=app`
- [x] 核心覆盖率 **68%**（98 个测试用例全部通过）

### 覆盖率报告本地验证

```bash
cd backend
uv run pytest tests/ -v --cov=app --cov-report=xml
# 结果：98 passed, 68% coverage
# 生成 coverage.xml 供 Codecov 上传
```

### 可选项

- [x] 使用 uv 替代 pip 管理依赖（CI 中使用 astral-sh/setup-uv@v4）
- [ ] 配置 Dependabot 自动更新依赖
- [ ] 集成 CodeRabbit AI 代码审查

## PR 链接

- PR #X: https://github.com/Ccccwd/personal-financial-management-assistant/pull/X（待提交）

## CI 运行链接

- https://github.com/Ccccwd/personal-financial-management-assistant/actions（合并到 main 后触发）

## 遇到的问题和解决

1. **问题**：ruff 检查报 89 个错误（56 个未使用导入、27 个 `== True/False` 比较、6 个未使用变量）
   **解决**：使用 `ruff check --fix --unsafe-fixes` 自动修复 77 个，手动修复 `__init__.py` 中的 re-export 导入（添加 `as` 别名保持包导出功能）

2. **问题**：CI 环境没有 MySQL 数据库，后端测试需要数据库连接
   **解决**：在 CI workflow 中设置 `DATABASE_URL: sqlite:///./test.db`，pytest 的 conftest.py 已使用 SQLite 内存数据库，无需额外配置

3. **问题**：pyproject.toml 缺少 pytest/coverage/ruff 配置段
   **解决**：添加 `[tool.pytest.ini_options]`、`[tool.coverage.run]`、`[tool.ruff]` 配置，确保 CI 命令与本地一致

## 心得体会

本次 CI/CD 配置让我理解了持续集成的工作流程：代码提交后自动运行 lint 检查和测试，确保代码质量。ruff 的使用让我注意到之前忽略的代码规范问题（未使用的导入、布尔值比较方式），通过自动修复大大提升了代码整洁度。将覆盖率报告上传到 Codecov 可以直观地追踪测试覆盖情况，有助于持续改进测试质量。
