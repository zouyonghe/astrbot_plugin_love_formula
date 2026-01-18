中文

# 恋爱公式插件实现方案

## 目标描述
实现 `astrbot_plugin_love_formula` 插件，通过“恋爱公式”分析日常群聊互动，并以 Y2K/Galgame 视觉风格呈现结果。

## 拟议变更

### 配置文件和模型
#### [NEW] [models/tables.py](file:///c:/Helianthus/astrpro/AstrBot-master/data/plugins/astrbot_plugin_love_formula/src/models/tables.py)
-   定义用于存储每日互动指标的 LoveDailyRef SQLModel。
-   定义用于跟踪消息所有权的 MessageOwnerIndex SQLModel。

#### [NEW] [models/events.py](file:///c:/Helianthus/astrpro/AstrBot-master/data/plugins/astrbot_plugin_love_formula/src/models/events.py)
-   定义内部事件结构（如果需要）。

### 持久层
#### [NEW] [persistence/repo.py](file:///c:/Helianthus/astrpro/AstrBot-master/data/plugins/astrbot_plugin_love_formula/src/persistence/repo.py)
-   实现 LoveRepo 类来处理数据库操作（upsert 每日统计数据，查询范围）。

#### [NEW] [persistence/database.py](file:///c:/Helianthus/astrpro/AstrBot-master/data/plugins/astrbot_plugin_love_formula/src/persistence/database.py)
-   使用 AstrBot 的引擎处理数据库 schema 创建。

### 核心逻辑（分析）
#### [NEW] [analysis/calculator.py](file:///c:/Helianthus/astrpro/AstrBot-master/data/plugins/astrbot_plugin_love_formula/src/analysis/calculator.py)
-   实现 LoveCalculator 类，包含恋爱公式逻辑（Simp、Vibe、Ick 分数）。

#### [NEW] [analysis/classifier.py](file:///c:/Helianthus/astrpro/AstrBot-master/data/plugins/astrbot_plugin_love_formula/src/analysis/classifier.py)
-   实现 ArchetypeClassifier 类，根据分数确定用户画像。

#### [NEW] [analysis/llm_analyzer.py](file:///c:/Helianthus/astrpro/AstrBot-master/data/plugins/astrbot_plugin_love_formula/src/analysis/llm_analyzer.py)
-   实现 LLMAnalyzer 类，生成趣味/毒舌点评。
-   调用 `self.context.llm_generate` 接口。

### Handlers (Data Ingestion)
#### [NEW] [handlers/message_handler.py](file:///c:/Helianthus/astrpro/AstrBot-master/data/plugins/astrbot_plugin_love_formula/src/handlers/message_handler.py)
-   监听 message.group 事件。
-   触发 LoveRepo 更新文本统计数据。

#### [NEW] [handlers/notice_handler.py](file:///c:/Helianthus/astrpro/AstrBot-master/data/plugins/astrbot_plugin_love_formula/src/handlers/notice_handler.py)
-   监听 notice.poke、notice.group_msg_emoji_like、notice.group_recall 事件。
-   触发 LoveRepo 更新互动统计数据。

### Visual Layer
#### [NEW] [visual/theme_manager.py](file:///c:/Helianthus/astrpro/AstrBot-master/data/plugins/astrbot_plugin_love_formula/src/visual/theme_manager.py)
-   从 assets/themes/ 加载主题配置。

#### [NEW] [visual/renderer.py](file:///c:/Helianthus/astrpro/AstrBot-master/data/plugins/astrbot_plugin_love_formula/src/visual/renderer.py)
-   使用 Jinja2 和主题资源实现 HTML 渲染。
-   注入 **KaTeX** 脚本以渲染数学公式。
-   调用 html_renderer.render 生成图片。

#### [NEW] [assets/themes/galgame/](file:///c:/Helianthus/astrpro/AstrBot-master/data/plugins/astrbot_plugin_love_formula/assets/themes/galgame/)
-   创建默认主题结构（css、html 模板）。

### Main Entry
#### [NEW] [main.py](file:///c:/Helianthus/astrpro/AstrBot-master/data/plugins/astrbot_plugin_love_formula/main.py)
-   初始化所有组件。
-   注册 handlers 和 commands (`/今日人设`)。

## 验证计划

### 自动化测试
-   本阶段不计划自动化测试（插件逻辑严重依赖运行时数据库和通用事件）。

### 手动验证
1.  **数据库创建**: 验证插件加载时表是否已创建。
2.  **数据摄入**:
    - 发送消息 -> 检查 `LoveDailyRef` `msg_sent`。
    - 戳用户 -> 检查 `LoveDailyRef` `poke_sent`/`poke_received`。
    - 反应消息 -> 检查 `LoveDailyRef` `reaction_sent`/`reaction_received`。
3.  **命令**:
    - 运行 `/今日人设` -> 验证图片生成和正确的 archetype。
    - 测试主题切换（如果在本轮实现）。
