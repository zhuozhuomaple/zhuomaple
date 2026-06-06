## ADDED Requirements

### Requirement: 任务列表分页
The system SHALL 支持通过 GET /tasks 分页返回任务列表

#### Scenario: 默认分页
- GIVEN 数据库中存在 25 条任务
- WHEN 客户端 GET /tasks（不传分页参数）
- THEN 返回 HTTP 200
- AND 响应体 items 长度为 20（默认 page_size）
- AND 响应体 total 为 25

#### Scenario: 自定义分页
- GIVEN 数据库中存在 25 条任务
- WHEN 客户端 GET /tasks?page=2&page_size=10
- THEN 返回 HTTP 200
- AND 响应体 items 长度为 10
- AND 响应体 page 为 2

#### Scenario: 页码非法
- GIVEN 任意数据库状态
- WHEN 客户端 GET /tasks?page=0
- THEN 返回 HTTP 422

### Requirement: 按状态过滤
The system SHALL 支持按 status 过滤任务列表

#### Scenario: 过滤 pending 状态
- GIVEN 数据库中存在 status 分别为 pending 和 done 的任务
- WHEN 客户端 GET /tasks?status=pending
- THEN 返回 HTTP 200
- AND 响应体 items 中每条任务的 status 均为 pending

#### Scenario: 过滤结果为空
- GIVEN 数据库中不存在 status 为 in_progress 的任务
- WHEN 客户端 GET /tasks?status=in_progress
- THEN 返回 HTTP 200
- AND 响应体 items 为空数组
- AND total 为 0

### Requirement: 按优先级过滤
The system SHALL 支持按 priority 过滤任务列表

#### Scenario: 过滤 high 优先级
- GIVEN 数据库中存在 priority 分别为 high 和 low 的任务
- WHEN 客户端 GET /tasks?priority=high
- THEN 返回 HTTP 200
- AND 响应体 items 中每条任务的 priority 均为 high

#### Scenario: 过滤结果为空
- GIVEN 数据库中不存在 priority 为 high 的任务
- WHEN 客户端 GET /tasks?priority=high
- THEN 返回 HTTP 200
- AND 响应体 items 为空数组
- AND total 为 0

### Requirement: 按创建日期过滤
The system SHALL 支持按 created_at 的日期范围过滤任务列表（从某年某月某日到某年某月某日）

#### Scenario: 指定起始日期
- GIVEN 数据库中存在创建于 2026-01-01 与 2026-06-01 的任务
- WHEN 客户端 GET /tasks?start_date=2026-05-01
- THEN 返回 HTTP 200
- AND items 中每条任务的 created_at 日期均 >= 2026-05-01

#### Scenario: 指定结束日期
- GIVEN 数据库中存在不同 created_at 日期的任务
- WHEN 客户端 GET /tasks?end_date=2026-03-31
- THEN 返回 HTTP 200
- AND items 中每条任务的 created_at 日期均 <= 2026-03-31

#### Scenario: 指定起止日期
- GIVEN 数据库中存在 2026-01-01、2026-06-01、2026-12-01 创建的任务
- WHEN 客户端 GET /tasks?start_date=2026-01-01&end_date=2026-06-30
- THEN 返回 HTTP 200
- AND items 中每条任务的 created_at 日期均在 2026-01-01 至 2026-06-30 之间（含首尾）

#### Scenario: 日期范围内无匹配
- GIVEN 所有任务创建于 2026-06-01
- WHEN 客户端 GET /tasks?start_date=2026-12-01&end_date=2026-12-31
- THEN 返回 HTTP 200
- AND items 为空数组
- AND total 为 0

### Requirement: 多条件组合过滤
The system SHALL 支持同时使用多个查询条件过滤任务列表，条件之间为 AND 关系

#### Scenario: 组合过滤 status 与 priority
- GIVEN 数据库中存在 (pending, high)、(pending, low)、(done, high) 任务
- WHEN 客户端 GET /tasks?status=pending&priority=high
- THEN 返回 HTTP 200
- AND 响应体 items 中每条任务 status 均为 pending 且 priority 均为 high
- AND total 为 1

#### Scenario: 组合过滤 status 与日期范围
- GIVEN 数据库中存在 pending 任务 A（创建于 2026-06-01）与 pending 任务 B（创建于 2026-01-01）
- WHEN 客户端 GET /tasks?status=pending&start_date=2026-05-01
- THEN 返回 HTTP 200
- AND 响应体 items 中每条任务 status 均为 pending
- AND 响应体 items 中每条任务 created_at 日期均 >= 2026-05-01
- AND total 为 1

#### Scenario: 组合过滤 priority 与日期范围
- GIVEN 数据库中存在 high 任务 A（创建于 2026-06-01）与 high 任务 B（创建于 2026-01-01）
- WHEN 客户端 GET /tasks?priority=high&end_date=2026-03-31
- THEN 返回 HTTP 200
- AND 响应体 items 中每条任务 priority 均为 high
- AND 响应体 items 中每条任务 created_at 日期均 <= 2026-03-31
- AND total 为 1

#### Scenario: 组合过滤 status、priority 与日期范围
- GIVEN 数据库中存在 (pending, high, 2026-06-01)、(pending, high, 2026-01-01)、(pending, low, 2026-06-01) 任务
- WHEN 客户端 GET /tasks?status=pending&priority=high&start_date=2026-05-01&end_date=2026-12-31
- THEN 返回 HTTP 200
- AND 响应体 items 中每条任务 status 均为 pending 且 priority 均为 high
- AND 响应体 items 中每条任务 created_at 均在指定时间范围内
- AND total 为 1

#### Scenario: 多条件组合过滤结果为空
- GIVEN 数据库中不存在同时满足 status=pending 且 priority=high 的任务
- WHEN 客户端 GET /tasks?status=pending&priority=high
- THEN 返回 HTTP 200
- AND 响应体 items 为空数组
- AND total 为 0

#### Scenario: 多条件组合过滤与分页、排序
- GIVEN 数据库中存在 5 条 status 为 pending 且 priority 为 high 的任务
- WHEN 客户端 GET /tasks?status=pending&priority=high&page=1&page_size=2&sort=asc
- THEN 返回 HTTP 200
- AND 响应体 items 长度为 2
- AND total 为 5
- AND items 按 created_at 从旧到新排列

### Requirement: 列表排序
The system SHALL 支持按 created_at 排序

#### Scenario: 按创建时间降序（默认）
- GIVEN 数据库中存在多条不同 created_at 的任务
- WHEN 客户端 GET /tasks
- THEN 返回 HTTP 200
- AND items 按 created_at 从新到旧排列

#### Scenario: 按创建时间升序
- GIVEN 数据库中存在多条不同 created_at 的任务
- WHEN 客户端 GET /tasks?sort=asc
- THEN 返回 HTTP 200
- AND items 按 created_at 从旧到新排列
