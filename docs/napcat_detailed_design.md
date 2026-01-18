# NapCat API 精细化对接设计 (Advanced Integration Design)

> ⚠️ **警告**：本文档基于 NapCat (OneBot V11) 官方能力进行深度定制，旨在挖掘常规消息之外的“潜意识”恋爱指标。

## 1. 数据源全景图 (Data Source Panorama)

为了保证“恋爱成分分析”的准确性与趣味性，我们将数据采集范围从单一的“文本消息”扩展到以下维度：

| 数据维度 | 对应 OneBot 事件/API | 恋爱隐喻 (Love Metaphor) |
| :--- | :--- | :--- |
| **显性交流** | `message.group` | 正式对话，表白与争吵 |
| **肢体接触** | `notice.notify.poke` (戳一戳) | 调情，引起注意，试探 |
| **情绪反馈** | `notice.group_msg_emoji_like` (贴贴) | 认可，好感，心动信号 |
| **犹豫后悔** | `notice.group_recall` (撤回) | 下头瞬间，欲言又止，掩饰 |
| **物料投喂** | `notice.group_upload` (文件) | 上交工资卡，分享资源 |
| **特殊关注** | `message` (at, reply) | 眼里只有你 |

## 2. 详细事件监听设计 (Detailed Event Listeners)

### 2.1. 戳一戳 (The Poke) - 主动试探

戳一戳是计算 **Simp (舔狗值)** 和 **Vibe (双向奔赴)** 的重要隐藏指标。

*   **Event Path**: `post_type=notice` & `sub_type=poke`
*   **关键字段解析**:
    *   `sender_id`: 发起戳一戳的人 (Source)
    *   `target_id`: 被戳的人 (Target)
    *   `group_id`: 所在群
*   **恋爱逻辑**:
    *   **Simp++**: 你戳了别人，但别人没戳回你。
    *   **Vibe++**: 互戳 (A戳B，B戳A)。
    *   **Ick++**: 连续戳同一个人超过 5 次且无回应（骚扰）。

```json
/* Poke Event Sample */
{
    "post_type": "notice",
    "notice_type": "notify",
    "sub_type": "poke",
    "group_id": 123456,
    "user_id": 11111,       // Sender
    "target_id": 22222,     // Target
    "time": 1678888888
}
```

### 2.2. 表情回应 (The Reaction) - 情绪价值

NapCat 支持 NTQQ 的表情回应（贴贴），这是计算 **Vibe (魅力值)** 的黄金指标。仅仅发消息是不够的，被贴贴才是“被爱”的证明。

*   **Event Path**: `post_type=notice` & `notice_type=group_msg_emoji_like`
*   **关键字段解析**:
    *   `user_id`: 点赞的人 (Giver)
    *   `operator_id`: 同 `user_id`
    *   `message_id`: 被点赞的消息 ID
    *   `likes`: 具体的表情代码（虽然很难解析具体含义，但有动作即为正向）
*   **恋爱逻辑**:
    *   **Vibe++**: `received_reaction_count` (你被贴贴了)。
    *   **Simp++**: `sent_reaction_count` (你到处给别人贴贴)。
    *   **Vibe+++**: 你的单条消息获得了 >5 个贴贴（万人迷）。

```json
/* Reaction Event Sample */
{
    "post_type": "notice",
    "notice_type": "group_msg_emoji_like",
    "group_id": 123456,
    "user_id": 33333,       // Who reacted
    "message_id": "123456"  // Which message
}
```

### 2.3. 消息撤回 (The Recall) - 减分项

撤回往往代表着失言、情绪失控或过度谨慎。

*   **Event Path**: `post_type=notice` & `notice_type=group_recall`
*   **关键字段解析**:
    *   `user_id`: 撤回者
    *   `operator_id`: 操作者（如果是管理员撤回，则是“被制裁”）
    *   `message_id`: 原消息 ID
*   **恋爱逻辑**:
    *   **Ick++**: 自己撤回（Self-Recall）。根据频率判断，偶尔一次是“羞涩”，多次是“戏精”。
    *   **Ick+++ (Critical)**: 被管理员撤回（Admin-Recall）。说明说了让人下头的话。

### 2.4. 特殊消息节点 (Special Message Segments)

在常规 `message.group` 中，除了 Text 和 Image，还需解析以下节点：

*   **Reply (`[CQ:reply,id=...]`)**:
    *   **逻辑**: 如果一条消息包含 Reply 节点，提取 `id`。
    *   **API调用**: 调用 `get_msg(id)` 获取原消息的 `sender_id`。
    *   **判定**: 如果 `sender_id` != `user_id`，则是一次**Interaction**。
*   **RedBag (`[CQ:redbag]`)** (部分实现支持):
    *   **Simp++**: 发红包是极其强力的付出信号。
    *   **Vibe++**: 大家都在抢你的红包。
*   **Record (`[CQ:record]`)** (语音):
    *   **Ick+**: 长时间语音（>60s）通常被认为是社交压力。

## 3. 指标量化公式 (Quantifiable Metrics)

基于上述丰富的数据源，重新定义 $J_{love}$ 的构成：

### 3.1. Simp (付出值 / 舔狗指数)
$$ S = w_1 \cdot N_{msg} + w_2 \cdot N_{poke\_sent} + w_3 \cdot N_{react\_sent} + w_4 \cdot \text{AvgLen} $$
*   *数据来源*: `message.group` (count), `notice.poke` (sender), `notice.reaction` (sender)

### 3.2. Vibe (魅力值 / 氛围感)
$$ V = w_5 \cdot N_{reply\_recv} + w_6 \cdot N_{react\_recv} + w_7 \cdot N_{poke\_recv} $$
*   *数据来源*: `message` (CQ:reply target), `notice.reaction` (target implicit in msg_id), `notice.poke` (target)
*   *难点*: `reaction` 事件只给 `message_id`，需要插件端维护 `{message_id: sender_id}` 的 LRU 缓存，才能知道是谁收到了赞。

### 3.3. Ick (下头值)
$$ I = w_8 \cdot N_{recall\_self} + w_9 \cdot N_{recall\_admin} \cdot 5 + w_{10} \cdot N_{spam} $$
*   *数据来源*: `notice.group_recall`

## 4. 实现侧缓存策略 (Implementation Strategy: Local Cache)

由于 `notice` 事件通常只包含 ID 引用（如点赞了某条消息），而不包含原消息内容或原发送者，插件必须在内存中维护轻量级映射：

```python
# LRU Cache Structure
message_owner_cache = {
    "msg_id_1001": "user_id_A",
    "msg_id_1002": "user_id_B",
    ...
}
```
*   **写入时机**: 收到 `message.group` 时，记录 `{message_id: user_id}`。
*   **读取时机**: 收到 `notice.group_msg_emoji_like` 时，查表得知是谁的消息被点赞了，给该用户 Vibe++。
*   **持久化**: 建议使用 `sqlite` 或 `json` 定时 dump，防止重启丢失当日数据。

## 5. 总结

本设计方案将 NapCat 的能力利用到了极致，不再局限于简单的文本统计，而是通过 **Action (Poke)**, **Reaction (Emoji)**, **Retraction (Recall)** 三个维度，构建了一个立体、鲜活的群聊“恋爱”评价体系。
