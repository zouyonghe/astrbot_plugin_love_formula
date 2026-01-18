# AstrBot Plugin: Love Formula - 最终架构设计方案

## 1. 设计概述 (Overview)

本插件旨在实现基于**OneBot V11 (NapCat)** 协议的群聊“恋爱成分分析”。通过实时监听群内包含显性（消息）与隐性（戳一戳、贴贴、撤回）在内的全维度交互数据，利用“恋爱动力学”数学模型计算用户当日在群聊中的“恋爱状态”，并结合 **LLM (大语言模型)** 生成趣味毒舌点评，最终以 Y2K Galgame 风格的视觉报告呈现。

**核心设计理念**：
1.  **全维度捕捉**: 不止于文本，更关注动作 (Action) 和情绪 (Reaction)。
2.  **数据私有化**: 使用插件独立的 SQLite 表存储当日高频交互数据，不依赖宿主 log。
3.  **计算即时性**: 所有指标（Simp, Vibe 等）均为当日累计，每日零点重置（逻辑上）。
4.  **视觉可扩展**: 引入**主题引擎**，支持多风格切换。
5.  **智能点评**: 引入 LLM 对分析结果进行二次解读，增加娱乐性。

## 2. 系统架构 (System Architecture)

### 2.1 目录结构 (Directory Structure)

```text
astrbot_plugin_love_formula/
├── assets/
│   └── themes/                 # 主题目录
│       ├── galgame/            # 核心主题：魔法少女裁判风格
│       │   ├── config.yaml     # 主题配置
│       │   ├── template.html   # HTML 模板 (含 KaTeX)
│       │   └── assets/         # 局部素材
│       └── y2k_pixel/          # 备用主题
├── src/
│   ├── analysis/               # [核心] 业务逻辑层
│   │   ├── calculator.py       # 公式计算引擎 (LoveCalculator)
│   │   ├── classifier.py       # 人格判定逻辑 (ArchetypeClassifier)
│   │   └── llm_analyzer.py     # [NEW] LLM 点评生成器
│   ├── models/                 # [核心] 数据模型层
│   │   ├── events.py           # 内部事件结构定义
│   │   └── tables.py           # SQLModel 数据库表定义
│   ├── persistence/            # [核心] 数据持久层
│   │   ├── database.py         # DB 初始化与 Session 管理
│   │   └── repo.py             # 数据访问对象 (LoveRepo)
│   ├── handlers/               # [核心] 交互层
│   │   ├── message_handler.py  # 消息/Command 监听
│   │   └── notice_handler.py   # 通知(Poke/Reaction/Recall) 监听
│   ├── visual/                 # [辅助] 视觉层
│   │   ├── theme_manager.py    # 主题管理器
│   │   └── renderer.py         # 模板渲染与图片生成
│   └── utils/                  # 工具类
├── main.py                     # 插件入口
├── metadata.yaml               # 插件元数据
└── requirements.txt            # 依赖声明
```

### 2.2 数据流 (Data Flow)

1.  **Event Source**: NapCat 推送事件。
2.  **Ingestion**: Handlers 解析并存入 SQLite (`LoveDailyRef`).
3.  **Query**: 用户触发 `/今日人设`。
4.  **Calculation**: `LoveCalculator` 计算 S/V/I 指数，`Classifier` 判定人格。
5.  **LLM Analysis**:
    *   将分数与人格输入 LLM。
    *   生成一段结合公式变量（如 "E", "W"）的趣味/毒舌点评。
6.  **Rendering**:
    *   `ThemeManager` 加载模板。
    *   注入数据、LLM 点评。
    *   **KaTeX** 渲染数学公式。
    *   生成图片。
7.  **Response**: 发送图片。

## 3. 详细模块设计 (Detailed Design)

### 3.1 数据库设计 (Database Schema)

*   **`LoveDailyRef`**: 存储当日每位用户在每个群的累计互动数据 (msg_sent, poke_sent, reply_received, etc.)。
*   **`MessageOwnerIndex`**: 存储消息 ID 与发送者的映射，用于归属 Reaction。

### 3.2 业务逻辑层 (Business Logic)

#### `LoveCalculator`
实现简化的微分方程离散模型计算 Simp Score (S), Vibe Score (V), Ick Score (I)。

#### `LLMAnalyzer` (New)
*   **功能**: 调用 AstrBot `llm_generate` 接口。
*   **Prompt**: "你在扮演一个 Galgame 中的毒舌裁判。根据以下数据（S=80, V=20, 人格=沸羊羊），用中二病的语气点评用户，并引用公式 $S = \int ...$ 来解释为什么他得分这么高。"

### 3.3 交互层 (Handlers)
*   `NoticeHandler`: 处理 Poke, Reaction, Recall。
*   `MessageHandler`: 处理文本消息与指令。

### 3.4 视觉渲染 (Visual)

#### Theme Support
引入 `ThemeManager` 支持多主题。
详细实现细节请参考文档：[galgame_style_implementation.md](docs/galgame_style_implementation.md)。

#### LaTeX Rendering
为了在 HTML 中完美呈现数学公式，模板中需引入 **KaTeX**：
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script>
    renderMathInElement(document.body);
</script>
```

## 4. 总结
本设计统一了 API 接入、自定义持久化、LLM 增强分析以及多风格视觉渲染的所有需求，是最终的实施蓝图。
