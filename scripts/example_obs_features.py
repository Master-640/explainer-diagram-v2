# -*- coding: utf-8 -*-
"""造特征：BatchedGraph + state -> 每步观测 x[N,3]（GRACO 的 DismantlingEnv）。

Run:  python draw_obs_features.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from matplotlib.patches import FancyBboxPatch

from diagram_kit import PALETTE, Canvas

OUT = os.path.join(os.getcwd(), "graco_obs_features.png")
BLUE, ORANGE, GREY, RED = (PALETTE["blue"], PALETTE["orange"], PALETTE["grey"],
                           PALETTE["red"])

c = Canvas()
c.title("造特征：BatchedGraph + state  →  每步观测 x[N, 3]",
        "graco/envs/dismantling.py : obs_graph() / node_features()")

# ------------------------------------------------------------------ ① 输入 --
c.box(0.20, 4.70, 3.95, 3.50, "① 两个输入")
pos = [(0.55, 1.30), (1.85, 1.30), (1.85, 0.30), (0.55, 0.30)]
c.node_graph(0.55, 6.15, pos, [(0, 1), (1, 2), (2, 3), (3, 0)],
             ["0", "1", "2", "3"], BLUE)
c.text(1.05, 6.02, "图 G：n=4，4 条无向边", size=9.4, color=BLUE)

c.text(0.42, 5.62, "状态（每步循环）", size=9.6, color=PALETTE["ink"])
c.text(0.42, 5.32, "t=0  selected = [0,0,0,0]", size=9.0, mono=True, color=GREY)
c.text(0.42, 5.02, "t=1  selected = [0,0,1,0]", size=9.0, mono=True, color=ORANGE)
c.text(0.42, 4.88, "下面两表取 t=1 的这组", size=9.0, color=RED)

# -------------------------------------------------------------- ② 三列公式 --
c.box(4.40, 4.70, 4.45, 3.50, "② 三列怎么算（每个节点一行）")
c.text(4.60, 7.44, "第 1 列  是否已移除", size=9.6, color=PALETTE["ink"])
c.text(4.60, 7.16, "removed.float()", size=9.0, mono=True, color=BLUE)

c.text(4.60, 6.72, "第 2 列  活跃度 / 原度", size=9.6, color=PALETTE["ink"])
c.text(4.60, 6.44, "scatter_sum(active[src] & active[dst], src)", size=9.0, mono=True,
       color=BLUE)
c.text(4.60, 6.16, "/ max(deg, 1)", size=9.0, mono=True, color=BLUE)

c.text(4.60, 5.74, "第 3 列  是否仍活跃", size=9.6, color=PALETTE["ink"])
c.text(4.60, 5.46, "1 - removed", size=9.0, mono=True, color=BLUE)

c.text(4.60, 5.08, "三列按最后一维拼起来，就是节点输入 x", size=9.4, color=PALETTE["soft"])
c.text(4.60, 4.86, "x = cat([...], dim=-1)  ->  [N, 3]", size=9.0, mono=True, color=ORANGE)

# ----------------------------------------------------------------- ③ 边筛选 --
c.box(9.10, 4.70, 3.00, 3.50, "③ 边同步裁剪")
c.text(9.26, 7.42, "emask = active[src] & active[dst]", size=8.6, mono=True, color=BLUE)
c.text(9.26, 7.08, "edge_index[:, emask]", size=8.8, mono=True, color=BLUE)
c.text(9.26, 6.55, "被移除节点连着的边\n一起从图里消失", size=9.2, color=PALETTE["soft"],
       linespacing=1.5)
c.text(9.26, 5.86, "E: 8 -> 4", size=11.5, mono=True, color=ORANGE)
c.text(9.26, 5.44, "顺带：valid_mask 会把\n没有活跃邻居的节点\n排除出可选动作",
       size=9.0, color=GREY, linespacing=1.5)

# ----------------------------------------------------------------- ④ 产物 --
c.box(12.35, 4.70, 2.65, 3.50, "④ 产物：一次观测")
c.kv_lines(12.52, 7.40, [
    "obs = BatchedGraph(",
    "  x          = [4,3]",
    "  edge_index = [2,4]",
    "  num_nodes  = 4",
], fs=8.2, dy=0.32)
c.text(12.52, 5.86, "直接喂 encoder\n（GraphSAGE，K 层）", size=9.2,
       color=PALETTE["soft"], linespacing=1.5)
c.text(12.52, 5.10, "batch / ptr 不变", size=9.0, color=GREY)

# ------------------------------------------------------------- 底部：两表 --
c.box(0.20, 0.30, 14.80, 4.05, "同一个图，两个时刻的 x（这就是「每步重算」）",
      fc="white", ec="#9FB0BF")

HEADERS = ["removed", "活跃度 / 度", "active"]
ROWS_T0 = [[0, 1.0, 1]] * 4
ROWS_T1 = [[0, 1.0, 1], [0, 0.5, 1], [1, 0.0, 0], [0, 0.5, 1]]
LABELS = ["节点 0", "节点 1", "节点 2", "节点 3"]

CW, CH = 1.05, 0.45


def table(x0, y0, rows, title, sub):
    c.text(x0 - 0.02, 3.86, title, size=10.2, color=PALETTE["ink"])
    c.text(x0 + 1.60, 3.86, sub, size=9.6, mono=True, color=GREY)
    for i, h in enumerate(HEADERS):
        c.text(x0 + (i + 0.5) * CW, 3.55, h, size=9.0, color=GREY, ha="center")
    c.tensor_grid(x0, y0, rows, row_labels=LABELS, group_sizes=[1, 1, 1],
                  group_colors=[ORANGE, BLUE, BLUE], cw=CW, ch=CH, fs=9.6, label_fs=9.2)


table(1.55, 3.02, ROWS_T0, "t = 0：什么都没移除", "E=8")
table(8.60, 3.02, ROWS_T1, "t = 1：移除节点 2", "E=4")

# 高亮 t=1 里发生变化的格子
for (col, row) in [(0, 2), (1, 1), (1, 3)]:
    x = 8.60 + col * CW
    y = 3.02 - row * CH
    c.ax.add_patch(FancyBboxPatch((x - 0.02, y - 0.02), CW - 0.03, CH - 0.03,
                                  boxstyle="round,pad=0.02,rounding_size=0.04",
                                  fc="none", ec=RED, lw=1.6, ls=(0, (3, 2)), zorder=5))

# 中间箭头
c.ax.annotate("", xy=(8.30, 2.45), xytext=(5.05, 2.45),
              arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.8, mutation_scale=16))
c.text(6.02, 2.62, "移除节点 2", size=9.6, color=RED)
c.text(6.02, 2.22, "removed 翻 1 / 邻居活跃度减半", size=9.0, color=RED)

# 右侧 obs 汇总
c.text(11.95, 3.90, "读法", size=9.6, color=PALETTE["ink"])
c.text(11.95, 3.58, "第 2 列 = 该节点还剩", size=9.0, color=PALETTE["soft"])
c.text(11.95, 3.32, "多少比例的活跃邻居", size=9.0, color=PALETTE["soft"])
c.text(11.95, 2.86, "它区分「度」与「还有", size=9.0, color=PALETTE["soft"])
c.text(11.95, 2.60, "多少度没被切断」", size=9.0, color=PALETTE["soft"])

c.footnote(0.42, 1.32, [
    "为什么每步重算：状态一变，模型看到的图就变了。把「移除进度」编码进输入，等价于给 GNN 一个随步变化的上下文；"
    "否则 T 步都喂同一张图，模型无法知道已经拆到哪一步。",
    "特征可以更省：FINDER 基线直接用 ones[n,2] 常量输入，靠 encoder 的 aggr=sum 让聚合值隐式等于度"
    "（见 configs/finder.yaml）；三列版本是把这一步显式化。",
    "自检：x 行数 = num_nodes；removed + active = 1；edge_index 列数 = 2 × 活跃无向边数；"
    "孤立节点会被 valid_mask 排除。",
], fs=9.2, dy=0.30)

c.save(OUT)
