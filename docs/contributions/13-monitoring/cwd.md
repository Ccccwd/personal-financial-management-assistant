# 监控配置贡献说明

姓名：陈伟栋
学号：2312190218
日期：2026-05-30

## 我完成的工作

### 1. 日志配置

- [x] 结构化日志格式（JSON 格式化器 + 纯文本格式化器）
- [x] 日志级别配置（开发环境 INFO，生产环境 JSON 输出）
- [x] 第三方库日志降噪（uvicorn、SQLAlchemy 降为 WARNING）

实现文件：`backend/app/utils/logger.py`

- `JsonFormatter`：生产环境使用，输出包含 time/level/message/module/function/line 的 JSON
- `PlainFormatter`：开发环境使用，输出人类可读的文本格式
- `setup_logging()`：根据 `APP_ENV` 和 `DEBUG` 自动选择格式和级别

### 2. 健康检查

- [x] `/api/health` 端点实现
- [x] 数据库连接检查（MySQL SELECT 1）
- [x] Redis 连接检查（PING）
- [x] 运行时长计算
- [x] 版本号和时间戳输出
- [x] 降级状态（degraded）支持

实现文件：`backend/app/api/health.py`

### 3. 指标收集

- [x] 请求计数（按接口路径统计）
- [x] 响应时间（平均值 + 慢请求告警）
- [x] 错误率（4xx/5xx 统计）
- [x] Top 10 接口排行
- [x] `X-Response-Time` 响应头

实现文件：
- `backend/app/core/metrics.py` — MetricsCollector 收集器 + MetricsMiddleware 中间件
- `backend/app/api/metrics.py` — `/api/metrics` 查询端点

### 4. 文件清单

| 文件 | 说明 |
|------|------|
| `backend/app/utils/logger.py` | 结构化日志配置（JSON + 纯文本双模式） |
| `backend/app/api/health.py` | 健康检查端点（DB + Redis + uptime） |
| `backend/app/core/metrics.py` | 指标收集器 + MetricsMiddleware |
| `backend/app/api/metrics.py` | 指标查询端点 |
| `backend/main.py` | 日志初始化 + 中间件注册 |
| `docs/monitoring.md` | 监控配置说明文档 |

## PR 链接

- PR 链接待合并后填写

## 遇到的问题和解决

1. **问题**：健康检查端点过于简单，无法判断依赖服务状态
   **解决**：增加 MySQL（`SELECT 1`）和 Redis（`PING`）连接检查，引入 `degraded` 状态表示部分异常

2. **问题**：日志格式不统一，生产环境不便于日志收集
   **解决**：实现 `JsonFormatter`，通过 `APP_ENV=production` 自动切换 JSON 输出

3. **问题**：无法观测接口性能和错误率
   **解决**：实现 `MetricsMiddleware` 收集每个请求的计数和响应时间，暴露 `/api/metrics` 端点查询

## 心得体会

通过本次监控配置实践，理解了可观测性的三个支柱（日志、指标、健康检查）在实际项目中的应用方式。结构化日志让生产环境的问题排查更高效，指标收集中间件能帮助发现性能瓶颈和异常接口。
