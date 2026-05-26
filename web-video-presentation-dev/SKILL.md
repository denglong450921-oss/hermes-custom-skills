---
name: web-video-presentation-dev
description: Engineering companion for web-video-presentation. Captures build-time patterns, parser pitfalls, and layout rules discovered during implementation. Adds oxc parser conflict fix, within-step content rule, layout checklist items, and keyboard sub-navigation pattern.
---

# Web Video Presentation — Dev Companion

Companion to the `web-video-presentation` skill. Covers engineering patterns, parser pitfalls, and design rules **not** in the main skill's CHAPTER-CRAFT.md.

Load alongside `web-video-presentation` when building chapters.

---

## 1. Within-step 内容全量显示规则

逐步揭示是**步与步之间**的责任。一旦进入该 step，该 step 要呈现的**所有**内容必须全部可见。

**禁止：** 用 CSS visible 条件（`i <= N`）在 step 内部做截断。

```
// ❌ 错误：step 内部截断
className={`item${i <= 2 ? " visible" : ""}`}

// ✅ 正确：step 内所有内容一次展示
className="item visible"
```

如果一口播节拍下内容太多，说明步太胖了 → 拆成多个 step，不要在 step 内再分页。

---

## 2. oxc 解析器坑：JSX 嵌套箭头函数块体

Vite 8.x 的 oxc 解析器在 JSX 表达式内遇到嵌套的箭头函数块体（`{ ... return ... }`）时，会将内层花括号误解析为 JSX 表达式分隔符，报 `PARSE_ERROR`。

```
// ❌ 错误（块体会导致 oxc PARSE_ERROR）
{rows.map((row, ri) => row.items.map((item, ci) => {
  const cx = ...;
  return (<g>...</g>);
}))}
```

**两种修复方案：**

**方案 A — flatMap + 对象表达式（推荐）：**

```tsx
{rows.flatMap((row, ri) => row.items.map((item, ci) => ({
  item, cx: ..., key: `n-${ri}-${ci}`,
}))).map(({ item, cx, key }) => (
  <g key={key}>{item}</g>
))}
```

**方案 B — 预计算平面数组：**

```tsx
const nodes = rows.flatMap((row, ri) =>
  row.items.map((item, ci) => ({ item, cx: ..., key: `n-${ri}-${ci}` }))
);
// 在 JSX 中：
{nodes.map(({ item, cx, key }) => <g key={key}>{item}</g>)}
```

**规则：** 不要在 JSX 表达式 `{ }` 内嵌带块体 `{ }` 的箭头函数。

---

## 3. 单 step 内子翻页模式（Keyboard-driven）

当一个 step 包含多个子页面（如阶段总览需要翻 6 页），用内部 `useState` + 键盘事件处理，**不要**用全局 step 计数或点击。

**模式：**

```tsx
function PhaseBrowser() {
  const [subIdx, setSubIdx] = useState(0);
  const idxRef = useRef(subIdx);
  idxRef.current = subIdx;

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" || e.key === " ") {
        if (idxRef.current < MAX_PAGES - 1) {
          e.preventDefault();
          e.stopPropagation();
          setSubIdx(i => i + 1);
        }
      }
    };
    window.addEventListener("keydown", handler, true);
    return () => window.removeEventListener("keydown", handler, true);
  }, []);

  return <div className="co-scene">{/* render current sub-page */}</div>;
}
```

**规则：** 子页内不能有进度点、页码或其他 UI "chrome"。用户通过 → 键自然翻页，不需要 UI 提示。

---

## 4. 视觉设计验收清单

- [ ] SVG/ 图中文字全部水平放置，无旋转 90° 文字
- [ ] 标题至少 80px，正文至少 18px，SVG 内文字至少 14px，标签至少 12px
- [ ] 无突兀的独立色——全部走主题 token 调色板
- [ ] 不欠内容——每个 step 该显示什么全部显示，不截断
- [ ] 布局美观——不填满，有呼吸感。必要时重做整页布局

---

## 5. 参考

- `web-video-presentation` — 主 Skill（设计方法论 + 协作流程）
- `references/CHAPTER-CRAFT.md` — 章节开发主要指引
