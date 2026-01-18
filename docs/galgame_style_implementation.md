# Galgame 风格实现指南 (Implementation Guide)

本指南基于 [web_magical_girl_witch_trials_text_box](https://github.com/entropy622/web_magical_girl_witch_trials_text_box) 的视觉风格，将其 Canvas 实现转换为适用于 AstrBot 的 HTML/CSS 实现。

## 1. 核心视觉元素

参考项目通过 Canvas 层叠实现画面，我们将使用 CSS `z-index` 和 `absolute` 定位复刻此逻辑：

1.  **Background (底层)**: 场景背景图。
2.  **Character (中层)**: 角色立绘，位于背景之上，文本框之下。
3.  **Frame/TextBox (上层)**: 包含九宫格边框的文本容器。
4.  **Text (顶层)**: 动态文本内容。

## 2. 关键技术实现

### 2.1 自适应文本框 (Nine-Slice Scaling)

Canvas 实现通常需要手动切片，而 CSS 提供了原生支持 `border-image`，可以完美实现“九宫格”拉伸，无论文本多长，边框都不变形。

**CSS 方案**:
```css
.text-box {
  /* 定义边框厚度 */
  border: 20px solid transparent; 
  /* 引用边框素材，slice参数(20)对应九宫格切割位置 */
  border-image: url('../assets/themes/galgame/assets/textbox_border.png') 20 fill stretch;
  /* 确保文字不压边框 */
  padding: 10px; 
}
```

### 2.2 角色立绘叠加 (Character Overlay)

参考 `TextBoxLayer.tsx`:
```tsx
<URLImage src={bgPath} ... />
<URLImage src={charPath} x={0} y={134} />
```

**HTML/CSS 方案**:
```html
<div class="scene">
  <img class="bg" src="background.jpg">
  <!-- 角色层：通过 filter 处理 Vibe/Ick 效果 -->
  <img class="char" src="character.png" style="filter: contrast(1.2) brightness(0.9);">
  <div class="text-box-container">
      <div class="text-box">
          {{ analysis_text }}
      </div>
  </div>
</div>
```

### 2.3 字体与排版

参考项目使用了自定义字体 `MagicalFont`。我们需要：
1.  下载同款或类似的像素/魔女风格字体 (e.g. `FZPixel12`).
2.  在 CSS 中定义 `@font-face`。

```css
@font-face {
    font-family: 'MagicalFont';
    src: url('../fonts/MagicalFont.ttf');
}
body {
    font-family: 'MagicalFont', sans-serif;
    color: white;
    text-shadow: 2px 2px 0px #000; /* 描边效果增强可读性 */
}
```

## 3. 动态效果映射 (Logic Mapping)

| 恋爱指标 (Metric) | 视觉表现 (Visual Ref) | CSS 实现 |
| :--- | :--- | :--- |
| **Simp Rate (沸羊羊)** | 角色缩小/边缘化 | `transform: scale(0.8); right: 10%;` |
| **High Vibe (高情商)** | 角色发光/过曝 | `filter: drop-shadow(0 0 10px gold) brightness(1.2);` |
| **High Ick (下头)** | 角色阴暗/紫调 | `filter: grayscale(0.5) hue-rotate(270deg) contrast(1.5);` |
| **Msg Count** | 文本框高度 | 自动撑开 (`height: auto`) |

## 4. 资源需求清单

*   **Backgrounds**: 从参考仓库 `public/assets/backgrounds` 提取或生成类似风格背景。
*   **Characters**: 提取或生成通用的一套 "Silhouette" 或 "Default Anime" 立绘。
*   **Fonts**: 获取授权字体。
*   **TextBox Border (关键)**: 制作一张支持九宫格拉伸的透明 PNG 素材。

## 5. 结论

使用 HTML/CSS 复刻该风格不仅可行，而且在文本排版（自动换行、行高控制）上比 Canvas 更具优势，完全符合 AstrBot 插件的技术栈。
