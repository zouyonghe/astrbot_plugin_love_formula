# 基于“恋爱动力学”的群聊·今日恋爱成分分析 (Daily Cyber-Love Diagnosis)

## 1. 核心概念 (Concept)

**“假如这个群是你的恋人，你今天表现得怎么样？”**

我们不分析长期的固化人格，而是分析**你今天的“恋爱状态”**。
利用动态优化公式，计算你今天在“群聊这段关系”中的投入、回报与沉没成本。

**Slogan**: "Every message is a flirt. (每一条消息都是一次调情)"

---

## 2. 公式的“恋爱脑”映射

$$ J_{love} = \int_{today} \underbrace{e^{-rt}}_{\text{新鲜感衰减}} \cdot \left[ \underbrace{\text{Vibe}}_{\text{存在感}} + \beta \underbrace{\text{Nostalgia}}_{\text{旧情}} - \lambda \underbrace{\text{Ick}}_{\text{败犬值}} - c \cdot \underbrace{\text{Simp}}_{\text{纯爱值}} \right] dt $$

| 变量 | 原含义 | **💕 赛博恋爱映射** | **📊 数据指标 (Daily)** |
| :--- | :--- | :--- | :--- |
| **Simp ($E$)** | 投入成本 | **纯爱值**：你今天主动发了多少消息试图引起注意？秒回了吗？ | `msg_sent`, `reply_delay` (平均回复延迟) |
| **Vibe ($W \cdot A$)** | 匹配度 | **存在感**：群友宠你吗？你的爱得到回应了吗？ | `reply_received` (被回率), `reaction_count` (被贴贴) |
| **Nostalgia ($M$)** | 记忆资产 | **白月光指数**：你是在吃老本（玩烂梗），还是创造新回忆？ | `meme_sent` includes 'old_meme', `topic_initiation` |
| **Ick ($R$)** | 无聊惩罚 | **败犬值**：你有没有发长语音、刷屏、或讲冷笑话让人“下头”？ | `long_voice_count`, `repeat_count`, `cold_joke_score` |
| **$J_{love}$** | 总效用 | **群聊好感度**：你今天和群聊是在热恋期，还是冷战期？ | 综合得分 |

---

## 3. 今日恋爱成分 (Archetypes)

采用更具“网感”和“攻击性”的恋爱标签，通过反差萌制造话题。

### **类型一：付出型 (High Simp)**
*   **高 Simp + 低 Vibe** $\rightarrow$ **🥵 沸羊羊 (The Simp)**
    *   *描述*：推了一天的塔，结果不仅没偷到家，连高地都没上去。感动了自己，尴尬了群友。
    *   *诊断*：“检测到今日发送100条消息，被回复率0.5%。建议停止自我感动。”
*   **高 Simp + 高 Vibe** $\rightarrow$ **🐶 黏人修勾 (Golden Retriever)**
    *   *描述*：全群的开心果，只要你在，空气都是甜的。大家都很宠你，但可能只是因为你看起来很好撸。
    *   *诊断*：“恋爱脑晚期，但群友很受用。”

### **类型二：技巧型 (High Vibe)**
*   **低 Simp + 高 Vibe** $\rightarrow$ **🎣 顶级海王 (The Player)**
    *   *描述*：仅仅说了三句话，就有十个人出来附和。时间管理大师，精准拿捏了每一条消息的边际效用。
    *   *诊断*：“你不是爱这个群，你只是享受被众星捧月的感觉。”
*   **中 Simp + 极高 Vibe** $\rightarrow$ **🦊 纯欲天花板 (The Charmer)**
    *   *描述*：既不清高也不卑微，尺码拿捏得死死的。
    *   *诊断*：“教科书级别的赛博推拉技术。”

### **类型三：特殊型**
*   **高 Simp + 高 Ick** $\rightarrow$ **🤡 下头男/女 (The Ick)**
    *   *描述*：很努力想融入，但总是用力过猛。刷屏、复读、发不知所云的表情包。
    *   *诊断*：“你的爱太沉重了，建议让群友喘口气。”
*   **极低 Simp + 高 Nostalgia** $\rightarrow$ **🌙 白月光 (The Ex)**
    *   *描述*：虽然你今天不在江湖，但江湖到处是你的传说。
    *   *诊断*：“得不到的永远在骚动。”
*   **高 Ick + 高 Vibe (???)** $\rightarrow$ **🤪 笨蛋美人 (The Bimbo/Himbo)**
    *   *描述*：虽然经常说蠢话让人下头，但大家莫名其妙还是很原谅你。
    *   *诊断*：“颜值（头像）即正义？”

---

## 4. 视觉展示方案 (Visuals)

**风格：Y2K 复古恋爱游戏 (Galgame) 界面**

*   **背景**：粉色/像素风/爱心气泡。
*   **主图**：将用户头像放在一个像素爱心框里。
*   **雷达图**：此时名为 **“恋爱六维图”** (付出、魅力、持久、甚至“变态”指数)。
*   **进度条**：
    *   `Love Meter`: ❤️❤️❤️💔🤍 (今日好感度)
    *   `Simp Meter`: 🟩🟩🟩🟩🟥 (舔狗值爆表预警)
*   **底部对话框**：
    *   AstrBot (NPC): "Senpai! Based on the calculated differential equation, your love is too heavy today!"

---

## 5. 实现路径

1.  **数据获取**: 复用 `analyze_group_daily` 的数据，但需要时间范围为 `today`。
2.  **指标计算**:
    *   `simp_score`: Normalize(msg_count * 0.7 + avg_len * 0.3)
    *   `charm_score`: Normalize(reply_count / msg_count)
    *   `ick_score`: 此时需要简单的 heuristic (e.g. 连续发图 > 5, 文本长度 > 200, 复读 > 3)
3.  **模板制作**: 这是难点，需要一套精美的 image template (HTML/CSS)。建议复用 `scrapbook` 的布局逻辑，但换肤。

---

## 6. 交互指令

*   `/今日人设`: 生成你的单人恋爱诊断卡。
*   `/测CP @user`: (进阶) 将两个人的 $m_1(t)$ 和 $m_2(t)$ 放在一起做卷积，看波形是否同步。
