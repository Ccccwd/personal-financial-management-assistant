# 监控配置说明

## 1. 日志管理

### 1.1 结构化日志

项目使用自定义 JSON 格式日志，位于 `backend/app/utils/logger.py`。

- **开发环境**：纯文本格式，便于终端阅读
- **生产环境**：JSON 格式，便于日志收集和分析

日志格式示例（JSON 模式）：
```json
{
  "time": "2026-05-30T12:00:00+00:00",
  "level": "INFO",
  "message": "应用启动完成",
  "module": "main",
  "function": "lifespan",
  "line": 48
}
```

日志格式示例（开发模式）：
```
2026-05-30 12:00:00 | INFO     | main:lifespan:48 | 应用启动完成
```

### 1.2 日志级别

| 级别 | 用途 |
|------|------|
| DEBUG | 开发调试（仅 debug=True 时启用） |
| INFO | 常规运行信息（启动、关闭等） |
| WARNING | 警告（数据库连接失败等可恢复问题） |
| ERROR | 错误（未处理异常、关键功能失败） |

### 1.3 配置方式

日志在 `main.py` 启动时初始化：

```python
setup_logging(
    debug=settings.debug,              # DEBUG 级别
    json_output=(settings.app_env == "production"),  # 生产环境用 JSON
)
```

通过环境变量 `APP_ENV=production` 和 `DEBUG=false` 控制日志格式和级别。

## 2. 健康检查端点

### 2.1 端点信息

- **路径**：`GET /api/health`
- **认证**：无需认证

### 2.2 检查项

| 检查项 | 说明 |
|--------|------|
| 应用状态 | 基础存活检查 |
| 数据库连接 | MySQL 连接检测（`SELECT 1`） |
| Redis 连接 | Redis 连接检测（`PING`） |
| 运行时长 | 自应用启动以来的时间 |

### 2.3 响应示例

```json
{
  "code": 200,
  "message": "服务运行正常",
  "data": {
    "status": "healthy",
    "service": "finance-backend",
    "version": "1.0.0",
    "timestamp": "2026-05-30T12:00:00+00:00",
    "uptime": "1h 30m 45s",
    "checks": {
      "database": {"status": "healthy", "type": "MySQL"},
      "redis": {"status": "healthy", "type": "Redis"}
    }
  }
}
```

### 2.4 状态说明

- `healthy`：所有检查通过
- `degraded`：部分服务异常（如 Redis 断连），应用仍可用

## 3. 基础指标收集

### 3.1 指标端点

- **路径**：`GET /api/metrics`
- **认证**：无需认证

### 3.2 收集的指标

| 指标 | 说明 |
|------|------|
| total_requests | 请求总数 |
| total_errors | 错误总数（4xx/5xx） |
| error_rate | 错误率（%） |
| avg_response_time_ms | 平均响应时间（毫秒） |
| top_endpoints | 请求量 Top 10 接口 |

### 3.3 响应示例

```json
{
  "code": 200,
  "message": "指标获取成功",
  "data": {
    "total_requests": 1250,
    "total_errors": 15,
    "error_rate": 1.2,
    "avg_response_time_ms": 85.5,
    "top_endpoints": [
      {"endpoint": "GET /api/transactions", "count": 320},
      {"endpoint": "POST /api/auth/login", "count": 150}
    ]
  }
}
```

### 3.4 响应时间头

每个请求的响应头包含 `X-Response-Time`，记录本次请求处理时间：
```
X-Response-Time: 0.0452s
```

### 3.5 慢请求告警

响应时间超过 2 秒的请求会自动记录 WARNING 级别日志：
```
2026-05-30 12:00:00 | WARNING  | metrics:dispatch:85 | 慢请求: GET /api/statistics (2.35s, 200)
```

## 4. Docker 健康检查

Dockerfile 中配置了 HEALTHCHECK，容器运行时自动检测：

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen(...)"]
```

Railway 平台也会使用此端点进行服务健康检查。

## 5. 文件结构

```
backend/
├── app/
│   ├── api/
│   │   ├── health.py        # 健康检查端点
│   │   └── metrics.py       # 指标查询端点
│   ├── core/
│   │   └── metrics.py       # 指标收集器 + MetricsMiddleware
│   └── utils/
│       └── logger.py        # 结构化日志配置
└── main.py                  # 日志初始化 + 中间件注册
```
