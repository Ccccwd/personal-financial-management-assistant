# CI/CD 配置贡献说明

姓名：曾昭祥　学号：2312190219　角色：前端　日期：2026-04-29

---

## 完成的工作

### 工作流相关

- [x] 参与编写 `.github/workflows/ci.yml`（前端 job 部分主导，后端 job 协同）
- [x] 配置 Codecov 覆盖率上传（`frontend` flag）
- [x] 添加 README 状态徽章（CI 徽章 + 前端/后端覆盖率徽章）

### 代码适配

- [x] 本地测试命令与 CI 一致：将 `test` 脚本更新为 `vitest run --coverage`，CI 环境直接运行即可生成 `lcov.info`
- [x] 代码通过 Lint 检查（ESLint）：新增 `lint` 脚本 `eslint src/ --ext .vue,.ts,.tsx --max-warnings 0`
- [x] 核心覆盖率达标（`src/utils/auth.ts` + `src/stores/user.ts` + `TransactionCard.vue` 综合覆盖率 95.9% > 60%）

### 可选项

- [ ] 配置 Dependabot 自动更新依赖
- [ ] 集成 CodeRabbit AI 代码审查
- [ ] 使用 act 本地验证工作流

---

## 关键实现说明

### 1. CI 工作流设计（`.github/workflows/ci.yml`）

工作流在 `push` 到 `main`/`dev` 分支以及 PR 到 `main` 时自动触发，**前端与后端 job 并行运行**：

**前端 job 步骤：**

| 步骤 | 命令 | 说明 |
|------|------|------|
| 检出代码 | `actions/checkout@v4` | 拉取最新代码 |
| 配置 Node 20 | `actions/setup-node@v4` | 使用 npm 缓存加速 |
| 安装依赖 | `npm ci --prefix frontend` | 严格锁版本安装 |
| Lint 检查 | `npm run lint --prefix frontend` | ESLint 零警告 |
| 运行测试 | `npm test --prefix frontend` | Vitest 运行 + 生成 lcov.info |
| 上传覆盖率 | `codecov/codecov-action@v4` | 上传 `frontend/coverage/lcov.info` |

**后端 job 步骤：**

| 步骤 | 命令 | 说明 |
|------|------|------|
| 检出代码 | `actions/checkout@v4` | 拉取最新代码 |
| 安装 uv | `astral-sh/setup-uv@v3` | 项目使用 uv 管理依赖 |
| 配置 Python 3.12 | `actions/setup-python@v5` | — |
| 安装依赖 | `uv sync` | 从 uv.lock 严格安装 |
| Lint 检查 | `uv run ruff check .` | Ruff 零警告 |
| 运行测试 | `uv run coverage run -m pytest tests/` | SQLite in-memory 模拟数据库 |
| 上传覆盖率 | `codecov/codecov-action@v4` | 上传 `backend/coverage.xml` |

### 2. 前端 CI 适配要点

- **使用 `happy-dom` 替代 `jsdom`**：避免了 `@exodus/bytes` ESM 兼容性错误（`jsdom` 依赖的 `html-encoding-sniffer` 无法 `require()` ESM 模块），CI 环境下无需额外配置即可正常运行
- **`npm ci` 而非 `npm install`**：`npm ci` 严格按 `package-lock.json` 安装，保证 CI 与本地依赖完全一致
- **注入 `VITE_API_URL`**：测试中所有 API 调用均已 mock，该环境变量仅为占位，避免 Vite 构建时因缺少变量而警告
- **`--prefix frontend`**：在项目根目录运行前端命令，无需 `cd frontend`，与 CI 工作目录保持一致

### 3. README 徽章

在 `README.md` 顶部添加了三个徽章：

```markdown
[![CI](https://github.com/Ccccwd/personal-financial-management-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/Ccccwd/personal-financial-management-assistant/actions)
[![Frontend Coverage](https://codecov.io/gh/Ccccwd/personal-financial-management-assistant/branch/main/graph/badge.svg?flag=frontend)](https://codecov.io/gh/Ccccwd/personal-financial-management-assistant)
[![Backend Coverage](https://codecov.io/gh/Ccccwd/personal-financial-management-assistant/branch/main/graph/badge.svg?flag=backend)](https://codecov.io/gh/Ccccwd/personal-financial-management-assistant)
```

---

## PR 链接

（提交后补充）

---

## CI 运行链接

（CI 运行成功后补充）

---

## 遇到的问题和解决

1. **问题**：`jsdom` 依赖的 `@exodus/bytes` 在 CI 环境因 ESM/CJS 兼容性问题导致所有测试报 `ERR_REQUIRE_ESM`，`no tests` 执行。
   **解决**：将 `vitest.config.ts` 的 `environment` 从 `jsdom` 改为 `happy-dom`，彻底绕开该依赖链，CI 无需任何额外配置。

2. **问题**：原 `lint` 脚本带 `--fix` 参数，会在 CI 中自动修改代码但无法提交，且没有 `--max-warnings 0` 保证零警告门禁。
   **解决**：新增独立的 `lint` 脚本（`eslint src/ --ext .vue,.ts,.tsx --max-warnings 0`），保留原脚本重命名为 `lint:fix` 供本地使用。

3. **问题**：后端项目使用 `uv` 而非 `pip + requirements.txt`，作业模板中的后端 CI 步骤无法直接使用。
   **解决**：将后端 job 中的安装步骤替换为 `astral-sh/setup-uv@v3` + `uv sync`，保持与项目实际技术栈一致。

---

## 心得体会

通过本次 CI/CD 配置实践，深刻体会到了持续集成的核心价值：

- **消除"本地能跑"的问题**：`happy-dom` 替换 `jsdom` 的经历正是 CI 价值的最好体现——依赖版本的细微差异在 CI 统一环境下被立即暴露，而不是等到上线才发现。
- **`npm ci` vs `npm install`**：在 CI 中使用 `npm ci` 而非 `npm install` 是关键细节，前者严格按锁文件安装、速度更快，后者可能因语义化版本范围安装到不同版本。
- **并行 job 设计**：前后端并行运行让 CI 总耗时从串行的 N 分钟缩短至最长单个 job 的时间，是 GitHub Actions 中最实用的优化手段之一。
- **Codecov flag 隔离**：通过 `flag=frontend` 和 `flag=backend` 分别上传覆盖率，可以在 Codecov 面板上单独查看前后端的覆盖趋势，避免后端测试覆盖率低拖累前端指标的显示。
