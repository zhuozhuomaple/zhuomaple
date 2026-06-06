## ADDED Requirements

### Requirement: 创建任务
The system SHALL 支持通过 POST /tasks 创建新任务

#### Scenario: 创建成功
- GIVEN POST 请求体包含有效的 title、priority
- WHEN 客户端 POST /tasks
- THEN 返回 HTTP 201
- AND 响应体包含自动生成的 id、status 与 created_at
- AND 数据库中存在该任务记录

#### Scenario: 缺少必填字段
- GIVEN 请求体缺少 title 或 priority
- WHEN 客户端 POST /tasks
- THEN 返回 HTTP 422
- AND 响应体包含字段校验错误详情

#### Scenario: priority 值非法
- GIVEN 请求体中 priority 不在允许枚举值内（low / medium / high）
- WHEN 客户端 POST /tasks
- THEN 返回 HTTP 422

#### Scenario: status 值非法
- GIVEN 请求体中 status 不在允许枚举值内（pending / in_progress / done）
- WHEN 客户端 POST /tasks
- THEN 返回 HTTP 422

### Requirement: 查询任务详情
The system SHALL 支持通过 GET /tasks/{id} 查询单个任务

#### Scenario: 查询成功
- GIVEN 数据库中存在 id 为 1 的任务
- WHEN 客户端 GET /tasks/1
- THEN 返回 HTTP 200
- AND 响应体包含完整任务信息（含 title、status、priority、created_at）

#### Scenario: 任务不存在
- GIVEN 数据库中不存在 id 为 999 的任务
- WHEN 客户端 GET /tasks/999
- THEN 返回 HTTP 404
- AND 响应体包含 "Task not found" 错误信息

### Requirement: 更新任务
The system SHALL 支持通过 PUT /tasks/{id} 更新任务的 title、status、priority

#### Scenario: 更新 title、status、priority 成功
- GIVEN 数据库中存在 id 为 1 的任务，当前 status 为 pending，priority 为 medium
- WHEN 客户端 PUT /tasks/1 并提交新的 title、status 为 in_progress、priority 为 high
- THEN 返回 HTTP 200
- AND 响应体中 title、status、priority 均已更新

#### Scenario: 仅更新 status 与 priority
- GIVEN 数据库中存在 id 为 1 的任务
- WHEN 客户端 PUT /tasks/1 并仅提交 status 为 done、priority 为 low
- THEN 返回 HTTP 200
- AND 响应体中 status 为 done
- AND 响应体中 priority 为 low
- AND title 保持不变

#### Scenario: 更新时 status 值非法
- GIVEN 数据库中存在 id 为 1 的任务
- WHEN 客户端 PUT /tasks/1 并提交非法 status 值
- THEN 返回 HTTP 422

#### Scenario: 更新时 priority 值非法
- GIVEN 数据库中存在 id 为 1 的任务
- WHEN 客户端 PUT /tasks/1 并提交非法 priority 值
- THEN 返回 HTTP 422

#### Scenario: 更新不存在的任务
- GIVEN 数据库中不存在 id 为 999 的任务
- WHEN 客户端 PUT /tasks/999
- THEN 返回 HTTP 404

### Requirement: 删除任务
The system SHALL 支持通过 DELETE /tasks/{id} 删除任务

#### Scenario: 删除成功
- GIVEN 数据库中存在 id 为 1 的任务
- WHEN 客户端 DELETE /tasks/1
- THEN 返回 HTTP 204
- AND 再次 GET /tasks/1 返回 404

#### Scenario: 删除不存在的任务
- GIVEN 数据库中不存在 id 为 999 的任务
- WHEN 客户端 DELETE /tasks/999
- THEN 返回 HTTP 404
