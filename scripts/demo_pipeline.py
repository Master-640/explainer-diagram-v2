# -*- coding: utf-8 -*-
"""Demo: the four-part layout (3 steps + product grid) built from diagram_kit.

Run:  python demo_pipeline.py
Out:  demo_pipeline.png
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from diagram_kit import PALETTE, Canvas

OUT = os.path.join(os.getcwd(), "demo_pipeline.png")

c = Canvas()
c.title("三步流水线 → 一个批次张量", "explainer-diagram / demo_pipeline.py")

# ---------------------------------------------------------------- ① input --
c.box(0.2, 4.70, 3.35, 3.50, "① 输入：逐行记录")
c.footnote(0.45, 7.10, [
    "# raw.txt",
    "0 1",
    "1 2",
    "2 2      ← 自环",
    "0 1      ← 重复",
], fs=10.2, dy=0.42, color=PALETTE["ink2"])
c.footnote(0.45, 4.95, ["每行一条边；注释与空行跳过"], fs=9.2)

# ------------------------------------------------------------ ② normalise --
c.box(3.75, 4.70, 3.65, 3.50, "② 规范化：去自环 / 去重 / 重编号")
c.footnote(4.00, 7.05, [
    "drop self-loop      → 删 (2,2)",
    "collapse duplicate  → 保留一条 (0,1)",
    "relabel 0..n-1      → 节点 0,1,2,3",
], fs=9.4, dy=0.42, color=PALETTE["ink2"])
c.text(4.00, 5.55, "结果：n=4，m=3", size=10.5, color=PALETTE["blue"])
c.footnote(4.00, 5.20, ["边集合不再是文件里的行，", "而是去重后的无序对。"], fs=9.2)

# ------------------------------------------------------- ③ symmetrise+pack --
c.box(7.60, 4.70, 3.55, 3.50, "③ 对称化 + 打包")
c.footnote(7.85, 7.05, [
    "us += [u, v]",
    "vs += [v, u]",
], fs=9.6, dy=0.34, color=PALETTE["orange"])
c.text(7.85, 6.05, "无向边 → 两条有向边", size=9.8, color=PALETTE["soft"])
c.text(7.85, 5.70, "3 条 → 6 条", size=11, color=PALETTE["orange"])
c.footnote(7.85, 5.30, ["COO 里没有「一条边」，", "只有 src→dst 的有向对。"], fs=9.2)

# ----------------------------------------------------------------- ④ note --
c.box(11.35, 4.70, 3.65, 3.50, "④ 产物：BatchedGraph")
c.kv_lines(11.58, 7.05, [
    "num_nodes = 4",
    "edge_weight = None",
    "batch = [0,0,0,0]",
    "ptr   = [0, 4]",
    "x     = None",
], fs=9.8, dy=0.42)
c.text(11.58, 4.95, "这一步不造节点特征", size=9.4, color=PALETTE["red"])

# ------------------------------------------------------------- bottom grid --
c.box(0.2, 0.30, 14.80, 4.10, "产物：edge_index（COO）", fc="white", ec="#9FB0BF")
c.text(0.42, 3.84, "edge_index  shape [2, E] = [2, 6]  int64", size=11, mono=True,
       color=PALETTE["ink2"])
c.text(5.60, 3.84, "列 = 一条有向边；每对正反向各一列", size=9.4, color=PALETTE["grey"])

gw, gh = c.tensor_grid(
    1.35, 3.00,
    [[0, 1, 1, 2, 2, 3], [1, 0, 2, 1, 3, 2]],
    row_labels=["src", "dst"],
)
c.bracket(1.35 - 0.02, 1.35 + gw - 0.07, 2.05, "6 条有向边 = 3 条无向边 × 2", PALETTE["blue"])
c.kv_lines(0.42, 1.35, [
    "batch [N] = [0, 0, 0, 0]      ptr [B+1] = [0, 4]      num_nodes = 4",
], fs=10.2, dy=0.3)
c.footnote(0.42, 1.00, [
    "为什么还要 batch / ptr：单图时它们退化成一个零向量和一个前缀和，"
    "但拼批后正是这两条向量告诉 scatter「第 k 个节点属于哪张图」。",
    "自检：src/dst 两行长度相同、下标连续；有向边数 = 2 × 无向边数。",
], fs=9.6, dy=0.34)

c.save(OUT)
