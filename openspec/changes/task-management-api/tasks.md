# Tasks: RESTful 任务管理 API

## 1. 基础架构
- [x] 1.1 初始化 FastAPI 项目结构（`app/main.py`、`requirements.txt`）
- [x] 1.2 配置 SQLite 引擎与 Session 依赖注入（`app/database.py`：`engine`、`SessionLocal`、`get_db()`、`init_db()`）
- [x] 1.3 定义 Task ORM 模型（`app/models.py`：id、title、status、priority、created_at；无 description / updated_at）
- [x] 1.4 定义 Pydantic Schema 与枚举（`app/schemas.py`：`TaskStatus`、`TaskPriority`、`TaskCreate`、`TaskUpdate`、`TaskResponse`、`TaskListResponse`）
- [x] 1.5 在 `main.py` 挂载 tasks 路由，启动/关闭时调用 `init_db()`；确认 `/docs` 可访问

## 2. task-crud 实现

- [x] 2.1 实现 POST /tasks：title、priority 必填，status 可选默认 pending，成功返回 201（对照「创建成功」「缺少必填字段」）
- [x] 2.2 实现 POST /tasks 枚举校验：非法 status / priority 返回 422（对照「priority 值非法」「status 值非法」）
- [x] 2.3 实现 GET /tasks/{id}：存在返回 200 含完整字段，不存在返回 404 且 detail 为 "Task not found"
- [x] 2.4 实现 PUT /tasks/{id}：支持更新 title、status、priority；部分更新时 title 保持不变（对照「仅更新 status 与 priority」）
- [x] 2.5 实现 PUT /tasks/{id} 校验与 404：非法 status / priority 返回 422，id 不存在返回 404
- [x] 2.6 实现 DELETE /tasks/{id}：成功返回 204，再次 GET 同 id 返回 404；id 不存在返回 404

## 3. task-list 实现

- [x] 3.1 实现 GET /tasks 默认分页（page=1、page_size=20），响应含 items、total、page、page_size；page=0 等非法值返回 422
- [x] 3.2 实现按 status 过滤，支持空结果（items=[]、total=0）
- [x] 3.3 实现按 priority 过滤
- [x] 3.4 实现按创建日期过滤：查询参数 `start_date` / `end_date`（YYYY-MM-DD），支持单边界与闭区间；无匹配时返回空列表；`start_date` 晚于 `end_date` 返回 422
- [x] 3.5 实现 `_apply_list_filters()`：status、priority、start_date、end_date 以 AND 组合（对照「多条件组合过滤」全部 Scenario）
- [x] 3.6 实现按 created_at 排序：默认 desc（新→旧），`sort=asc` 为旧→新；created_at 相同时按 id 升序；组合过滤与分页、排序可同时生效

## 4. 测试与验收

- [x] 4.1 编写 task-crud 集成测试（`tests/test_tasks.py`：创建/422/详情/更新/部分更新/删除/404）
- [x] 4.2 编写 task-list 集成测试（分页、单条件过滤、start_date/end_date、多条件 AND、排序、空结果）
- [x] 4.3 运行 `pytest`，通过率 ≥ 80%，对照 specs 中主要 Scenario 全部通过
- [x] 4.4 更新 README：接口说明、本地运行步骤
