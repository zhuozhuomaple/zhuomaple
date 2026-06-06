# Task Management API

RESTful 任务管理 API。

## 功能

- 任务 CRUD（创建、查询、更新、删除）
- 列表：按 `status`、`priority`、`start_date` / `end_date` 过滤，分页、按 `created_at` 排序
- 参数校验与统一错误响应（422 / 404）
- Swagger 自动文档

## 技术栈

- Python 3.9+
- FastAPI + Uvicorn + SQLAlchemy
- SQLite
- pytest
- OpenSpec（SDD 规范驱动）

## SDD 文档（OpenSpec）

所有 SDD 文档位于 `openspec/changes/task-management-api/`：

| 文档 | 路径 |
|------|------|
| Proposal | [openspec/changes/task-management-api/proposal.md](openspec/changes/task-management-api/proposal.md) |
| Specs | [openspec/changes/task-management-api/specs/](openspec/changes/task-management-api/specs/) |
| Design | [openspec/changes/task-management-api/design.md](openspec/changes/task-management-api/design.md) |
| Tasks | [openspec/changes/task-management-api/tasks.md](openspec/changes/task-management-api/tasks.md) |

```bash
# 查看 SDD 进度
openspec status --change task-management-api

# 查看某阶段编写指引
openspec instructions proposal --change task-management-api

# 校验文档格式
openspec validate task-management-api
```

## 环境要求

- Python 3.9+
- Node.js 20+（OpenSpec CLI）

## 安装

FastAPI 本身只是 Web 框架，**不能直接当服务器跑**。本地开发需要 ASGI 服务器 **Uvicorn**（已在 `requirements.txt` 中），先安装全部依赖：

```powershell
cd D:\task-api
py -m pip install -r requirements.txt
```

## 启动服务

用 Uvicorn 加载 FastAPI 应用并监听 HTTP 请求：

```powershell
cd D:\task-api
py -m uvicorn app.main:app --reload
```

| 参数 | 含义 |
|------|------|
| `app.main:app` | 模块路径 `app/main.py` 中的 FastAPI 实例 `app` |
| `--reload` | 代码改动后自动重启（开发时用） |

等价写法（依赖已安装且 `Scripts` 在 PATH 中时）：

```powershell
uvicorn app.main:app --reload
```

- 默认地址：<http://127.0.0.1:8000>
- Swagger 文档：<http://127.0.0.1:8000/docs>

若提示 `No module named uvicorn`，说明尚未执行上面的 `pip install`。

## 运行测试

```powershell
cd D:\task-api
py -m pytest -v
```

## API 示例

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"学习 FastAPI\", \"priority\": \"high\"}"

curl "http://127.0.0.1:8000/tasks?status=pending&priority=high&page=1&page_size=10"
curl "http://127.0.0.1:8000/tasks?start_date=2026-01-01&end_date=2026-12-31"
```

## 测试结果

运行 `py -m pytest -v` 后，将终端截图保存为 `docs/pytest-result.png`：

```powershell
cd D:\task-api
py -m pytest -v
```

![pytest 测试通过](docs/pytest-result.png)

## 项目结构

```
task-api/
├── openspec/changes/task-management-api/   # SDD 文档（OpenSpec）
│   ├── proposal.md
│   ├── design.md
│   ├── tasks.md
│   └── specs/
├── app/                                    # 应用代码
├── tests/                                  # 测试
└── docs/                                   # 截图等资源
```

## 作者

校招 AI Coding 培训 — 软件开发工程师
