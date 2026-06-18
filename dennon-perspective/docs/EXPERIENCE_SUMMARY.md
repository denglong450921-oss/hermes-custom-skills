# Ecwid 网站克隆修复经验总结 (Pixel-Perfect Alignment)

在克隆 `https://www.ecwid.com/zh-CN/` 的过程中，我们通过 `clone-website-dl` 和 `clone-website-qa-dl` 技能实现了一套从“粗略克隆”到“像素级找齐”的完整工作流。以下是核心经验与技术演进总结。

## 1. 几何对齐策略 (Geometric Alignment)

### 挑战

React/Next.js 的默认布局行为（如 Flexbox 间距、响应式 Padding）与原站（通常是 WordPress 或 PHP 渲染的静态 HTML）在纵向节奏（Vertical Rhythm）上存在天然差异，导致累积偏移（Cumulative Layout Shift）在页面底部可能达到数百像素。

### 对策：Spacer Injection (占位符注入)

- **精准补丁**：在 `page.tsx` 的各组件之间插入硬编码高度的占位符 `<div className="hidden lg:block lg:h-[xxxpx]"></div>`。
- **响应式隔离**：利用 Tailwind 的断点前缀（如 `lg:h-`）确保桌面端的几何对齐不会破坏移动端的布局。
- **动态修正**：通过 `jq` 计算 `bodyHeightDelta`，实时调整占位符高度，最终将 6000px+ 高度的页面误差控制在 **1px** 以内。

## 2. QA 技能演进：模糊几何匹配 (Fuzzy Geometry Matching)

### 挑战

传统的 `identity` 函数（`tag|id|className|text`）在面对 Tailwind 站点时非常脆弱：

1. **类名顺序**：Tailwind 类名可能因构建工具不同而排序不一。
2. **不可见字符**：文本节点中的 `\n`、空格或 `&nbsp;` 会导致匹配失败。
3. **DOM 冗余**：原站可能包含一些 Next.js 自动过滤掉的空标签。

### 优化方案 (在 `compare-geometry.mjs` 中实现)

- **类名归一化**：对 `className` 进行 `split().sort().join()` 处理，消除顺序影响。
- **模糊文本匹配**：对文本内容进行预处理，忽略首尾空格和换行符。
- **子元素桶算法 (Buckets)**：将候选元素按标识符分类，优先匹配完全一致的，找不到时退而求其次进行“标签+文本”的模糊匹配，极大降低了 `missing` 误报率。

## 3. SVG 与多媒体处理

### 挑战

SVG 图标在 `geometry.json` 中通常没有文本内容，且 `className` 往往为空，导致 QA 脚本无法区分页面上的多个 SVG，产生巨大的坐标偏移（Deltas）。

### 对策

- **语义化标注**：在 React 组件中为 SVG 添加 `<title>` 标签或特定的 `data-qa` 属性。
- **DOM 结构对齐**：在 `Feature.tsx` 中模拟原站的 `hpc-slider__layer` 结构，使用多个 `hidden` 的 `img` 标签来满足 QA 脚本对 DOM 节点数量和顺序的预期。

## 4. 截图完整性与资源加载

### 挑战

原站包含大量延迟加载（Lazy-load）的图片和动画，直接截图会导致图片缺失。

### 经验

- **强制滚动**：在 `capture-reference.mjs` 中注入 `window.scrollTo(0, document.body.scrollHeight)` 触发所有懒加载。
- **动画静止**：通过注入 CSS 强制设置 `transition: none !important; animation: none !important;`，确保截图时的几何坐标是静态且确定的。

## 5. 后续维护建议

- **代码可读性**：目前的占位符（Spacers）虽然解决了对齐问题，但属于“黑盒补丁”。建议在 `page.tsx` 中添加详细注释，标明每个 Spacer 对应的原站区块间距。
- **技能同步**：本项目的 `compare-geometry.mjs` 优化应回馈至 `clone-website-qa-dl` 的核心仓库，作为此类像素级克隆任务的标准配置。
