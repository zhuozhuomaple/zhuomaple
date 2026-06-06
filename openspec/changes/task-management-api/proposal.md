# Proposal: RESTful 任务管理 API (SD-01)

## Why

团队日常需要一个简单的任务管理工具来跟踪待办事项。本项目通过实现一个轻量级 RESTful API，练习 OpenSpec 规范驱动开发（SDD）的完整流程：从需求分析、规格编写到编码实现与验收测试。

## What Changes

实现一个基于 FastAPI 的任务管理 REST API，具体包括：

- 任务的增删改查（CRUD）
- 任务列表的多条件过滤（状态、优先级、创建时间范围）
- 分页与按 `created_at` 排序
- 请求参数校验与统一错误处理（422 / 404，在 task-crud / task-list 规格中分别定义）
- 自动生成的 OpenAPI / Swagger 文档
- pytest 集成测试，覆盖 Specs 中的主要场景

## 范围

### 包含

- 任务 CRUD：`POST /tasks`、`GET /tasks/{id}`、`PUT /tasks/{id}`、`DELETE /tasks/{id}`
- 任务列表：`GET /tasks`，响应含 `id`、`title` 等字段；支持 `status`、`priority`、`start_date` / `end_date`（YYYY-MM-DD）过滤
- 分页参数：`page`、`page_size`；排序参数：`sort`（asc / desc）
- Pydantic 请求/响应校验
- SQLite 持久化存储
- Swagger 文档（`/docs`）

### 不包含

- 用户认证与权限控制
- 前端 Web 页面
- 多用户 / 多租户
- 分布式部署、消息队列、缓存
- 任务附件、评论、标签等扩展功能

## Capabilities

### New Capabilities

- `task-crud`: 对于任务的增删改查及 422/404 错误处理
- `task-list`: 对于任务的分页筛选（状态、优先级、时间）、排序及查询参数校验

### Modified Capabilities

无

## Impact

- **代码**: 新增/修改 `app/` 下路由、模型、Schema 及 `tests/` 集成测试
- **API**: 对外提供 RESTful 任务管理接口（`/tasks`、`/tasks/{id}`）
- **依赖**: Python 3.9+、FastAPI、Uvicorn、SQLAlchemy、pytest
- **数据**: 使用 SQLite 持久化，运行后生成 `tasks.db`
- **文档**: 需同步更新 OpenSpec 下 `specs/`、`design.md`、`tasks.md` 及项目 `README.md`

## 技术栈

- **语言**: Python 3.9+
- **主要依赖**: FastAPI、Uvicorn、SQLAlchemy、Pydantic、pytest
- **运行环境**: 纯软件（本地 SQLite，无需独立数据库服务）

## 验收标准

- [x] 所有 CRUD 接口可用，符合 RESTful 约定
- [x] 列表接口支持 status / priority / `start_date` / `end_date` 过滤、分页、`created_at` 排序
- [x] 非法参数返回 422，资源不存在返回 404
- [x] Swagger 文档可访问（`/docs`）
- [x] pytest 测试通过率 ≥ 80%（当前 33/33 通过）
