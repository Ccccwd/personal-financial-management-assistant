# 监控配置贡献说明

姓名：曾昭祥  
学号：2312190219  
日期：2026-06-16

## 我完成的工作

### 1. 日志配置

- [x] 后端已实现结构化日志（`backend/app/utils/logger.py`，由陈伟栋同学完成）
- [x] 前端通过系统监控页展示后端可观测性入口说明

### 2. 健康检查

- [x] 前端对接 `GET /api/health` 端点
- [x] 展示服务版本、运行时长、MySQL / Redis 检查状态
- [x] 健康 / 降级状态标签可视化

### 3. 指标收集

- [x] 前端对接 `GET /api/metrics` 端点
- [x] 展示请求总数、错误率、平均响应时间
- [x] Top 10 接口请求量表格
- [x] 支持手动刷新与 30 秒自动刷新

### 4. 具体改动

| 文件 | 说明 |
|------|------|
| `frontend/src/api/monitoring.ts` | 健康检查与指标 API 封装 |
| `frontend/src/types/monitoring.ts` | 监控相关 TypeScript 类型 |
| `frontend/src/views/monitoring/MonitoringView.vue` | 系统监控页面 |
| `frontend/src/router/index.ts` | 注册 `/monitoring` 路由 |
| `frontend/src/components/common/AppSidebar.vue` | 侧边栏添加入口 |

## 遇到的问题和解决

1. **问题**：作业要求健康检查与指标可查，但前端缺少对应展示页面  
   **解决**：新增「系统监控」页面，对接后端已有 `/api/health` 与 `/api/metrics` 接口

2. **问题**：监控数据需要定期更新  
   **解决**：增加自动刷新开关，默认每 30 秒拉取一次

## 心得体会

监控不仅是后端打日志和暴露端点，前端也需要把可观测性信息可视化，方便开发与答辩演示时快速确认服务状态。本次实践将后端已有的三支柱（日志、健康检查、指标）通过前端页面串联起来，形成完整的可观测性体验。
