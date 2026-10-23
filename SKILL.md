---
name: explainer-diagram-v2
description: >-
  Turn any explanation into ONE annotated figure: data/tensor layout, system architecture,
  pipeline with artifacts, A/B comparison, timeline, state machine, hierarchy, before/after,
  causal loop, or an annotated chart. Ships a measured-QA renderer (overlap / missing-glyph /
  off-canvas detection) plus 10 layout archetypes so the figure is legible at a glance —
  exact shapes, real values, and a "why this step" line on the image itself.
  Use when the user asks 画张图解释一下 / 画个示意图 / 出一张图说明这个流程 / 做个架构图 /
  对比图 / 时间线, or when a text answer about code paths, modules, batching, state, or a
  multi-stage pipeline would be clearer as one PNG.
whenToUse: >-
  Trigger on: 画图解释, 示意图, 流程图, 架构图, 对比图, 时间线, 状态机, 层次图, 数据流,
  张量形状/布局, COO/CSR, batch/ptr, 数据管线, 模块接线, before/after, 因果环; or
  "explain X with a diagram", "draw this flow", "make an architecture sketch".
  Not for numeric data charts (use a normal plot) and not for slide decks (use a pptx skill).
metadata:
  version: 2
  supersedes: explainer-diagram
  locale: zh-CN
  requires: python3, matplotlib>=3.4, a CJK font (Microsoft YaHei / SimHei / Noto Sans CJK)
  related_skills:
    - office-docx
    - academic-ppt
---

# 解释图 v2 —— 任何"讲清一件事"的标注图

一张图讲清一件事：**输入长什么样 → 中间怎么变 → 输出是什么、值是多少**。
不是插画，是"带标注的技术图"：每个框有名，每个箭头有因，每个量写出真实数值。

与 v1 的区别：不再只服务"数据流/张量布局"，而是 **10 种图型可选**，并且渲染器自带
**可测量的版式自检**（文字重叠、缺字、越界），改坐标有了客观依据，不靠眼睛猜。

---

## 0. 先决条件（一次性）

需要 matplotlib（>=3.4）和一个中文字体（Microsoft YaHei / SimHei / Noto Sans CJK 任一）。
渲染器不联网、不依赖任何第三方包。

```bash
python -c "import matplotlib, sys; print(sys.executable, matplotlib.__version__)"
```

找不到支持中文的 matplotlib 环境时先探测，不要盲目 pip：

```bash
py -3 -c "import matplotlib, sys; print(sys.executable, matplotlib.__version__)"
```

Windows 上也可以用装了 matplotlib 的独立环境（例如 `C:\Python37\python.exe`）。

---

## 1. 先选图型（10 种，别硬套流水线）

| # | 图型 | 什么时候用 | 主构件 |
|---|---|---|---|
| M1 | 数据流 / 张量布局 | 输入经过若干变换成为一个张量；要写出 shape 与真实索引 | `box` `tensor_grid` `bracket` |
| M2 | 系统架构 / 模块接线 | 有分层、有部署边界、有调用关系 | `lane` `box` `arrow` `elbow` |
| M3 | 流水线（阶段 + 产物） | 每步都有落盘产物，关心"产出物是什么" | `box` + 底部产物带 |
| M4 | A / B 对比 | 论文 vs 代码、before vs after、方案一 vs 方案二 | 两个 `box` + 对称 `tensor_grid` + `callout` |
| M5 | 时间线 / 里程碑 | 排期、事件沿时间推进，每点可验收 | `timeline` |
| M6 | 状态机 / 决策树 | 有限状态、转移条件、分支判定 | `node_graph(directed=True)` `arrow` |
| M7 | 层次 / 分类树 | 一层总、下层分；词表、模块归属 | `tree` |
| M8 | 单点放大 | 讲清"这一格/这一行是怎么来的" | `box` + `annotate` 引出线 + 放大框 |
| M9 | 因果环 / 反馈回路 | 有正负反馈、闭环（如 Bjerknes、控制环） | `node_graph` 环形布局 + 正负号标签 |
| M10 | 带标注的图（annotated chart） | 结论来自真实曲线/柱状，需要把关键点标在图上 | 原生 matplotlib 图 + `callout` 标注 |

判据（一句话）：**看的是"怎么变形"→ M1/M3；"谁连谁"→ M2；"差在哪"→ M4；
"什么时候"→ M5；"下一步能去哪"→ M6；"包含什么"→ M7；"这一处细节"→ M8；
"为什么绕回来"→ M9；"数值怎么说"→ M10。**

> 一张图只讲一件事。步骤 > 4 或并列对象 > 2 → **拆图**，不要塞。

---

## 2. 工作流（5 步，第 2 步不许跳）

1. **定题**：一句话写出 `标题 = <动作>：<输入> → <输出>`；副标题写来源（`file.py:func` / 数据口径）。
2. **写 spec（先进对话、再进代码）**：6 行之内交代清
   - 图型（M1–M10）与画布尺寸；
   - 3–4 个面板各自的一句标题；
   - 底部"硬信息"是什么（shape / 真实数字 / 索引 / 约束）；
   - 唯一的"为什么这一句"写什么；
   - 颜色语义（哪种色代表哪一组）。
3. **实现**：`copy` 一份 kit 到工作区或直接 `sys.path.insert` 指向 skill 的 `scripts/`，
   用 §3 的构件画；坐标以 inch 为单位。
4. **渲染 + 自检**：`c.save(path)` 会自动跑 `qa()`；`QA: NEEDS FIX` 时按报告挪坐标，
   直到 `QA: PASS`，再 `read_image` 人工看一遍（§5）。
5. **交付**：PNG 落到工作区根目录，`snake_case` 命名；回复里内嵌图 + 一句话说"图在说什么"。

---

## 3. 构件速查

| 要画什么 | 调用 |
|---|---|
| 标题 / 副标题 | `c.title(main, sub)` |
| 圆角箱（可带底色语义） | `c.box(x, y, w, h, title, tint="blue"/"orange"/"grey")` |
| 泳道（分层的背景带） | `c.lane(x, y, w, h, label, tint="blue")` |
| 小标签块 | `c.chip(x, y, text, tint)` |
| 直箭头 / 折线连接 | `c.arrow(x1, y1, x2, y2)`；`c.elbow([(x, y), …])` |
| 数字网格（张量 / 表格） | `c.tensor_grid(x0, y0, rows, row_labels=…, tints=[…], header=[…])` |
| 分组括号 | `c.bracket(x1, x2, y, label, color)` |
| 时间线 | `c.timeline(x0, y, [(label, detail), …], span=…)` |
| 两层树 | `c.tree(cx, y, root, [children])` |
| 节点-边小图 | `c.node_graph(ox, oy, pos, edges, labels, color, directed=True)` |
| 图例 | `c.legend(x, y, [(tint, label), …])` |
| 警示框（虚线） | `c.callout(x, y, w, h, text, color)` |
| 键值块 / 脚注 | `c.kv_lines(…)`；`c.footnote(…)` |
| **"为什么"那一句** | `c.why(x, y, text)` —— 全图最值钱的一行 |

完整签名与参数见 `scripts/diagram_kit.py` 的 docstring；版式细则见 `references/style-spec.md`；
每种图型的排布配方见 `references/archetypes.md`。

---

## 4. 六条硬规则（IRON RULE，违反即重画）

1. **必须有真实数值**：`shape [2, 12]`、具体索引、`ptr=[0,4,7]`、真实权重值。
   只有方框和箭头 = 流程图，不是解释图。
2. **一句"为什么"**：把"为什么需要这一步"写在图上；读者不看正文也能懂。
3. **CJK 与 monospace 必须分开调用**：`text(mono=True)` 遇中文会抛错（v2 主动拦），
   拆成两次 `text()`。
4. **缺字必须替换**：`₁ ⚠ Σ ∘ ̂` 等 YaHei 没有 → 用 `G1 / 注意 / sum / D·G·E / X_hat`。
5. **不许靠猜坐标**：渲染后必须 `QA: PASS` + `read_image` 复核（§5）。
6. **数据必须可溯源**：图上的每个数字都要能在源码/output 里指到出处；推断的量标注
   `估计` 或 `目标`，不要与实测混排。

---

## 5. 自检（脚本 + 人工两道）

```python
c.save("out.png")          # 自动打印 QA: PASS / NEEDS FIX
ok = c.report()            # 也可手动再跑一次
```

`qa()` 检查三件事（都是可测量，不靠目测）：

| 检查 | 判定 | 修法 |
|---|---|---|
| 文字重叠 | 任意两段文字包围盒相交 | 挪 0.1–0.3 inch；或缩小字号/改换行 |
| 越界 | 文字跑到画布外 | 调 x/y 或加宽画布 |
| 缺字 | 字体拿不到字形 | 换成 ASCII 写法（规则 4） |

人工再过 5 条（`read_image` 看）：

- [ ] 一眼能读出"输入 → 输出"，不需要正文解释
- [ ] 每个框的标题没压到内容（标题占约 0.28 inch 高）
- [ ] 同一颜色在同一图里只有一个语义
- [ ] 底部没有大片空白（把"为什么"或约束填进去）
- [ ] 缩写首次出现写全（例：`LCC（最大连通片）`）

详见 `references/qa-checklist.md`。

---

## 6. 脚本与示例

| 文件 | 用途 |
|---|---|
| `scripts/diagram_kit.py` | 渲染器 + 构件 + QA（本 skill 的核心） |
| `scripts/demo_pipeline.py` | M1/M3：三步流水线 + COO 产物网格 |
| `scripts/demo_architecture.py` | M2：三泳道架构 + 折线路由 + 图例 |
| `scripts/demo_compare.py` | M4：论文 vs 代码的 A/B 对比 + 结论三行 |
| `scripts/demo_timeline.py` | M5/M7：时间线 + 两层树 + 图例 |
| `scripts/example_obs_features.py` | M1 变体：`BatchedGraph + state → x[N,3]` 每步观测 |

跑一张看效果（输出到当前目录）：

```bash
python scripts/demo_compare.py
```

---

## 7. 交付

- PNG 存工作区根目录，命名 `snake_case`（`graco_coo_batch.png`、`consistency_loss_ab.png`）。
- 回复里用 `![说明](绝对路径)` 内嵌；正文只写"图在说什么 / 怎么读"，不逐字复述图上已有的字。
- 若一次要出多张，先出 1 张给用户确认图型，再批量——图型选错的返工最贵。
