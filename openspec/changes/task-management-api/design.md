# Design: RESTful 任务管理 API

## 架构概览

```
客户端 (curl / Swagger / pytest)
        │
        ▼
┌───────────────────┐
│   FastAPI 路由层   │  routers/tasks.py — HTTP 入口、查询参数、404 处理
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│   Pydantic 模式层  │  schemas.py — 请求/响应校验（422 由框架自动返回）
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│   SQLAlchemy ORM  │  models.py — Task 实体
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│   SQLite 数据库    │  tasks.db — 本地文件存储
└───────────────────┘
```

## 模块划分

### Module 1: app/main.py

- **职责**: 应用入口，挂载路由，启动/关闭时初始化数据库；`GET /` 重定向到 `/docs`
- **接口**: FastAPI 实例，注册 `tasks` 路由，`RedirectResponse(url="/docs")`

### Module 2: app/database.py

- **职责**: SQLite 引擎、Session 工厂、依赖注入；启动时检测表结构，与模型不一致则重建
- **接口**: `engine`, `SessionLocal`, `get_db()`, `init_db()`

### Module 3: app/models.py

- **职责**: SQLAlchemy ORM 模型
- **接口**: `Task` 表模型

### Module 4: app/schemas.py

- **职责**: Pydantic 请求/响应模型与枚举
- **接口**:
  - `TaskCreate` — 创建请求
  - `TaskUpdate` — 更新请求（字段均可选，只更新提交的字段）
  - `TaskResponse` — 单条任务响应
  - `TaskListResponse` — 列表响应（items + 分页元数据）
- **枚举**:
  - `TaskStatus`: pending / in_progress / done
  - `TaskPriority`: low / medium / high

### Module 5: app/routers/tasks.py

- **职责**: 任务 CRUD 与列表查询
- **接口**:
  - `POST /tasks` — 创建
  - `GET /tasks` — 列表（多条件过滤 + 分页 + 排序）
  - `GET /tasks/{task_id}` — 详情
  - `PUT /tasks/{task_id}` — 更新 title / status / priority
  - `DELETE /tasks/{task_id}` — 删除
- **列表过滤**: 通过 `_apply_list_filters()` 将 status、priority、start_date、end_date 以 **AND** 关系组合到同一 SQL 查询

### Module 6: tests/test_tasks.py

- **职责**: 对照 specs 中 Scenario 编写集成测试
- **工具**: pytest + FastAPI TestClient，测试库使用内存 SQLite

## 数据模型

### Task 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| title | VARCHAR(200) | 标题，**必填** |
| status | VARCHAR(20) | pending / in_progress / done，默认 pending |
| priority | VARCHAR(20) | low / medium / high，**创建时必填** |
| created_at | DATETIME | 创建时间，自动生成 |


### 列表响应结构

```json
{
  "items": [ { "id": 1, "title": "...", "status": "pending", "priority": "high", "created_at": "..." } ],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

## API 设计

| 方法 | 路径 | 说明 | 成功码 |
|------|------|------|--------|
| POST | /tasks | 创建任务 | 201 |
| GET | /tasks | 列表（过滤 / 分页 / 排序） | 200 |
| GET | /tasks/{id} | 查询详情 | 200 |
| PUT | /tasks/{id} | 更新 title、status、priority | 200 |
| DELETE | /tasks/{id} | 删除任务 | 204 |

### POST /tasks 请求体

| 字段 | 必填 | 说明 |
|------|------|------|
| title | 是 | 1~200 字符 |
| priority | 是 | low / medium / high |
| status | 否 | 默认 pending；非法枚举 → 422 |

### PUT /tasks/{id} 请求体

| 字段 | 必填 | 说明 |
|------|------|------|
| title | 否 | 提交则更新 |
| status | 否 | 提交则更新；非法枚举 → 422 |
| priority | 否 | 提交则更新；非法枚举 → 422 |

支持部分更新：仅提交 status、priority 时，title 保持不变（见 specs「仅更新 status 与 priority」）。

### GET /tasks 查询参数

| 参数 | 类型 | 说明 |
|------|------|------|
| status | enum | 按状态过滤 |
| priority | enum | 按优先级过滤 |
| start_date | date | 起始日期（含），格式 `YYYY-MM-DD`，如 `2026-01-01` |
| end_date | date | 结束日期（含），格式 `YYYY-MM-DD`，如 `2026-12-31` |
| page | int | 页码，默认 1，非法值（如 0）→ 422 |
| page_size | int | 每页条数，默认 20，上限 100 |
| sort | asc / desc | 按 created_at 排序，默认 desc；created_at 相同时按 id 升序 |

**时间范围说明**：`start_date` 与 `end_date` 表示从某年某月某日起到某年某月某日止（按任务的 `created_at` 判断）。可只传其一，也可同时传入表示闭区间；例如 `start_date=2026-01-01&end_date=2026-06-30` 表示 2026 年 1 月 1 日至 6 月 30 日之间创建的任务。若同时传入且 `start_date` 晚于 `end_date`，返回 422。

多个过滤参数同时传入时，条件之间为 **AND** 关系（见 specs「多条件组合过滤」）。

## 技术选型说明

| 选型 | 理由 |
|------|------|
| **FastAPI** | 内置 Pydantic 校验与 OpenAPI/Swagger，适合 REST API 课题 |
| **Uvicorn** | ASGI 服务器，用于本地运行 FastAPI 应用 |
| **SQLite** | 零配置，培训环境无需独立数据库服务 |
| **SQLAlchemy 2.0** | 主流 ORM，Session 与依赖注入模式清晰 |
| **pytest + TestClient** | 集成测试，每个 Spec Scenario 可对应一条用例 |

## 错误处理

| 场景 | 实现方式 | HTTP 码 |
|------|----------|---------|
| 请求体/查询参数不合法 | Pydantic / FastAPI `Query` 校验 | 422 |
| 任务 id 不存在 | 路由层 `HTTPException(detail="Task not found")` | 404 |
| 删除成功 | 无响应体 | 204 |

422 场景见 `task-crud`（缺 title/priority、非法 status/priority）与 `task-list`（非法 page 等）；404 场景见 CRUD 查/改/删不存在 id。

## 与 Specs 的对应关系

| Spec 文件 | Design 落点 |
|-----------|-------------|
| task-crud | `routers/tasks.py` CRUD 路由 + `schemas.py` 校验 |
| task-list | `GET /tasks` 查询参数 + `_apply_list_filters()` + 分页/排序 |
