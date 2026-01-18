# AstrBot 持久化机制调研报告

## 1. 调研结论 (Executive Summary)

经过对 AstrBot 核心代码 (`astrbot/core/\*`) 的深度审查，得出以下结论：

1.  **现有机制存在但未自动启用**: AstrBot 定义了 `PlatformMessageHistory` 表和 `PlatformMessageHistoryManager` 管理器，但核心管道 (`Pipeline`) 均**未发现自动写入**该表的逻辑。这意味着对于 NapCat/OneBot 来源的消息，数据库中默认**是空的**。
2.  **Schema 不够专用**: `PlatformMessageHistory` 表的设计主要用于存储原始消息链 (`content: JSON`)，对于“恋爱成分分析”所需的结构化指标（如 `poke_count`, `reaction_count`）查询效率低下，且无法索引。
3.  **不建议直接复用**: 直接复用 AstrBot 的 `PlatformMessageHistoryManager` 需要插件自行调用 `insert`，且查询时仍需解析 JSON。

**最终建议**: 利用 AstrBot 已经集成的 `SQLModel` (基于 SQLAlchemy)，为插件**设计独立的 SQLite 数据表**。这既符合 AstrBot 的技术栈，又能获得最佳的性能和开发体验。

## 2. 详细分析 (Detailed Analysis)

### 2.1. AstrBot 内置持久化现状
*   **Table**: `PlatformMessageHistory` (in `astrbot/core/db/po.py`)
*   **Manager**: `PlatformMessageHistoryManager` (in `astrbot/core/platform_message_history_mgr.py`)
*   **Context**: 插件可以通过 `self.context.message_history_manager` 访问。
*   **问题**: 全局搜索 `insert_platform_message_history` 未发现任何调用点（除了定义处）。这表明该功能可能尚处于半成品状态，或仅供特定平台（如 WebChat）内部使用。

### 2.2. 为什么需要自定义表？
我们需要存储的是**高度结构化**的统计数据，而不是原始消息日志。

*   **Love Formula 需求**:
    *   Need `UPDATE` operations (e.g., increment `poke_count` for User A in Group B).
    *   Need `SUM` aggregations (e.g., total `simp_score` for today).
*   **Generic Log 缺陷**:
    *   如果只存原始 Log，每次分析都需要 `SELECT * FROM logs WHERE date=today` 然后在 Python 内存中遍历计算，随着消息量增加，性能会急剧下降。
    *   无法简单处理 "撤回" (Recall) 逻辑（需要物理删除或标记）。

## 3. 架构调整建议 (Architecture Update)

在 `src/models` 中定义插件专用的 `SQLModel`：

### 3.1. 表结构设计

我们设计两张表：一张存每日汇总指标（读多写多），一张存原始交互日志（用于溯源和审计，可选）。

#### Table 1: `LoveDailyRef` (每日指标快照)
*   **Primary Key**: `id`
*   **Indices**: `date`, `group_id`, `user_id`
*   **Fields**:
    *   `date`: Date (YYYY-MM-DD)
    *   `group_id`: str
    *   `user_id`: str
    *   `msg_count`: int
    *   `reply_received`: int
    *   `poke_sent`: int
    *   `poke_received`: int
    *   `reaction_sent`: int
    *   `reaction_received`: int
    *   `recall_count`: int

#### Table 2: `MessageOwnerIndex` (用于 Reaction 溯源)
*   **Primary Key**: `message_id`
*   **Fields**:
    *   `user_id`: str (Sender)
    *   `group_id`: str
    *   `timestamp`: int (TTL cleanup based on this)

### 3.2. 实现方式
插件初始化时，利用 AstrBot 的 DB 引擎创建表：

```python
from sqlmodel import SQLModel
from astrbot.core.db import BaseDatabase

# 在插件 __init__ 中
async def init_db(self):
   async with self.context.db.engine.begin() as conn:
       await conn.run_sync(SQLModel.metadata.create_all)
```

## 4. 总结
不要试图“搭便车”使用 AstrBot 的 `PlatformMessageHistory`。它就像一辆没油的公交车（代码在并未运行）。应该自己造一辆精密的赛车（自定义 SQLModel 表），直接跑在 AstrBot 提供的赛道（DB Engine）上。
