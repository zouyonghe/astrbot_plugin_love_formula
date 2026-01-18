# NapCat API 调研与群聊数据源说明

## 1. 简介 (Introduction)

[NapCatQQ](https://github.com/NapNeko/NapCatQQ) 是基于 NTQQ 的 OneBot V11 协议实现。对于 `astrbot_plugin_love_formula` 插件而言，NapCat 提供了底层的群聊消息监听与主动查询能力。由于它遵循 OneBot V11 标准，我们可以利用标准的 OneBot 事件和 API 来获取所需的数据。

## 2. 核心数据源：消息事件 (Message Events)

插件的实时分析主要依赖于 NapCat 上报的 **群消息事件 (`message.group`)**。每当群内有人发言，NapCat 会推送一个 JSON 事件，包含以下核心字段，这些是我们计算“恋爱成分”的基础。

### 2.1. 事件结构 (Event Structure)

```json
{
  "time": 1678888888,          // [时间戳] 用于计算消息频率、回复延迟 (Simp值)
  "self_id": 123456789,        // [Bot QQ] 接收消息的 Bot 账号
  "post_type": "message",
  "message_type": "group",
  "sub_type": "normal",
  "message_id": "1234",        // [消息ID] 唯一标识 (NapCat 推荐使用 String 类型)
  "group_id": 987654321,       // [群号] 区分不同的“恋爱对象”
  "user_id": 111222333,        // [发送者QQ] 分析的主体
  "anonymous": null,
  "message": [                 // [消息链] 核心内容，用于分析 Vibe 和 Nostalgia
    {
      "type": "text",
      "data": {
        "text": "今天群里好冷清啊"
      }
    },
    {
      "type": "image",
      "data": {
        "file": "https://example.com/meme.jpg",
        "url": "https://example.com/meme.jpg"
      }
    }
  ],
  "raw_message": "今天群里好冷清啊[图片]", // [原始消息] 用于正则匹配或快速文本分析
  "font": 0,
  "sender": {                  // [发送者信息] 用于展示和辅助判断
    "user_id": 111222333,
    "nickname": "某群友",
    "card": "群名片-某群友",   // 优先展示群名片
    "sex": "male",
    "age": 18,
    "area": "",
    "level": "10",
    "role": "member",          // owner/admin/member
    "title": ""
  }
}
```

### 2.2. 数据映射 (Mapping to Love Formula)

| NapCat 字段 | 恋爱公式变量 | 用途说明 |
| :--- | :--- | :--- |
| `time` | $t$ (时间), $r$ (衰减) | 计算消息的时间分布，判断是“秒回”还是“轮回”。时间越近权重越高。 |
| `user_id` | $Identity$ | 区分不同的“追求者”。每个 user_id 对应一份独立的恋爱报告。 |
| `message` (Text) | $Simp$ (舔狗值) | 文本长度、关键词（如“早安”、“在吗”）。 |
| `message` (Image) | $Nostalgia$ (记忆) | 表情包、图片分享。高频发老图可能增加“白月光”指数或“下头”指数。 |
| `message` (Reply) | $Vibe$ (氛围) | 如果消息中包含 `reply` 节点，说明是一次互动。指向该用户的回复越多，Vibe 越高。 |
| `sender.card` | Display | 报告生成时，用于在仪表盘上显示用户的称呼。 |

## 3. 辅助数据源：API 主动查询 (API Calls)

除了被动接收消息，插件还可以通过调用 NapCat (OneBot V11) 的 API 主动获取补充信息。

### 3.1. 获取群成员列表 (`get_group_member_list`)
*   **用途**：获取全员基础信息，用于计算 user 在群内的相对活跃度排名（Rank）。
*   **参数**：`group_id`
*   **返回**：List of Member Info。

### 3.2. 获取单条消息详情 (`get_msg`)
*   **用途**：如果分析中检测到回复消息（Reply），但缺少被回复消息的原文，可调用此 API 溯源。
*   **参数**：`message_id`
*   **注意**：NapCat 的消息缓存可能有限，过久的消息可能无法获取。

### 3.3. 获取历史消息 (`get_group_msg_history`)
*   **用途**：插件冷启动时，可能需要回溯过去 24 小时的数据进行“补课”。
*   **兼容性提示**：标准 OneBot V11 并不强制包含此 API，但在 NapCat/Go-CQHTTP 中通常支持。如果不支持，需要插件自行维护本地数据库（如 SQLite）来记录消息。

## 4. 获取数据的限制 (Limitations)

1.  **历史回溯**：如果 NapCat 重启，内存中的上下文可能丢失。因此架构设计中建议**本地持久化**（SQLite/JSON）今日的消息记录，确保服务重启后“恋爱进度”不丢失。
2.  **ID 类型**：NapCat 强调 ID 可能为 String 类型（防止 JS 精度丢失），Python 插件端处理 ID 时最好统一转为 `str` 或使用 `int` 但注意溢出风险（Python 自动处理大整数，所以 Python 端问题不大，但跨语言交互需注意）。
3.  **媒体文件**：获取图片/语音通常为 URL。如果需要 OCR 或深度分析，需要下载文件流。本项目 V1.0 暂仅根据 `type=image` 计数，不进行图像内容识别。

## 5. 总结 (Conclusion)

NapCat 提供的 OneBot V11 接口完全满足 `astrbot_plugin_love_formula` 的需求。
*   **实时流** (`message.group`) 是主要养料。
*   **API 查询** 是补充手段。
*   我们将在 `src/provider/message_fetcher.py` 中封装这些调用，向业务层屏蔽底层的协议细节。
