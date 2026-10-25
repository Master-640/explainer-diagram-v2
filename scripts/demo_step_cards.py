# -*- coding: utf-8 -*-
"""M11 步骤卡：每个框自带「输入 / 输出 + 代码 + 一个算得出来的例子」。

这是可直接抄改的模板：把 STEPS（4 个）和 PRODUCTS（右下）换成你的内容即可。
约定：
  - 每个框四段：中文一句话（干什么）、in/out（形状或值）、代码 2 行、示例 1–2 行；
  - 示例必须是能算对的真实数字（m=5、LCC=3、r=-3/25），算出来的值标「示例」；
  - in 用蓝、out 用绿、代码用墨色、示例用橙——同一颜色只承担一个语义；
  - 底部通栏放"产物"，并用 callout 写口径/偏差。
Run:  python demo_step_cards.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from matplotlib.patches import Circle  # noqa: E402

from diagram_kit import PALETTE, Canvas  # noqa: E402

BLUE, ORANGE, RED, SOFT = PALETTE["blue"], PALETTE["orange"], PALETTE["red"], PALETTE["soft"]
GREEN, INK = PALETTE["green"], PALETTE["ink"]
OUT = os.path.join(os.getcwd(), "demo_step_cards.png")

# ---------------------------------------------------------------- 要改的部分 --
STEPS = [
    dict(title="1. 取数据", tint="blue",
         cn=["每轮现采 256 张小图，", "拼成一个大 batch。"],
         i=("in", "none (resampled each iter)"),
         o=("out", "x [10240, 2]"),
         code=["x = ones(N, 2)   # all ones", "N = 256 x 40 = 10,240"],
         ex=["ex: n=5  x = [[1,1]] x 5"]),
    dict(title="2. 编码", tint="blue",
         cn=["K 层聚合邻居，把每个点", "K 跳内的形状压成 64 维。"],
         i=("in", "x [10240,2] + edge_index"),
         o=("out", "h [10240, 64]   L2"),
         code=["for l in range(K):", "    h = layer[l](h, edge_index)"],
         ex=["ex: n=5, K=3  -> h [5, 64]", "receptive field = 3 hops"]),
    dict(title="3. 打分", tint="blue",
         cn=["整图向量做门控，拼上 4 维", "全局特征，给每个点打分。"],
         i=("in", "h + aux [256, 4]"),
         o=("out", "q [10240]"),
         code=["y = sum_pool(h); s = w_cross(y)", "q = h2(cat(h1(h*s), aux))"],
         ex=["ex: q = [-.28 -.11 -.35 -.08 -.44]", "argmax = 1  -> remove node 1"]),
    dict(title="4. 执行", tint="green",
         cn=["删掉它，重算最大连通块，把", "余量记成负奖励。"],
         i=("in", "q + mask (legal nodes)"),
         o=("out", "r [256] + new selected"),
         code=["a = argmax(q)   # a = 1", "r = -LCC / n^2"],
         ex=["ex: remove 1 -> LCC 5 -> 3", "r = -3/25 = -0.12"]),
]

# 底部通栏：左列两段说明，右列三条产物
LEFT = [
    ("钩子 A：局末 after_episode()", "一局拆完再回填，摊成 5 步回报：",
     ["buf.add(s_t, a_t, sum(r_t .. r_{t+4}), s_{t+5})", "n_step = 5,  gamma = 1"],
     "-> 46.4 steps/epi, ~12k transitions / iter"),
    ("钩子 B：步内 after_step()", "每 2 个环境步就更新一次，不等局末：",
     ["if _env_steps % 2 == 0:  _learn()", "learn_freq = 2"],
     "-> 625 iter = ~7,000 updates only"),
]
RIGHT_KV = [("s_t", "[0,0,0,0,0]"), ("a_t", "1"), ("r_t", "-0.12"),
            ("s_{t+5}", "[0,1,0,0,1]"), ("R_t", "-0.37   (5-step sum)")]
RIGHT_CODE = ["sample 64;  target = r + gamma^5 * Q(s_next)",
              "loss = smooth_l1(Q, target) + alpha * recon",
              "obs = f(static graph, selected)   # pure fn"]
RIGHT_NOTE = "alpha = 1e-4;  lr = 1e-4;  target sync / 1000"
CAVEAT = ("口径/偏差：alpha 1e-4（论文 1e-3）· buffer=nstep（论文 PER alpha=0.6）"
          "· 特征 ones[N,2]（论文加权是 [c(v), 1]）")
# ----------------------------------------------------------------------------

c = Canvas(w=15.2, h=9.2)
c.title("M11 步骤卡：每一步的输入、输出与代码",
        "每个框写清 in / out / 代码 / 一个算得出来的例子；示例数值标「示例」，其余来自源码或日志")

Y, H, W = 5.45, 2.78, 3.55
XS = [0.35, 4.10, 7.85, 11.60]

for x, s in zip(XS, STEPS):
    c.box(x, Y, W, H, s["title"], tint=s["tint"])
    for i, line in enumerate(s["cn"]):
        c.text(x + 0.14, Y + H - 0.60 - i * 0.27, line, size=9.0, color=SOFT)
    c.text(x + 0.14, Y + H - 1.20, s["i"][0], size=8.4, mono=True, color=BLUE)
    c.text(x + 0.56, Y + H - 1.20, s["i"][1], size=8.4, mono=True, color=BLUE)
    c.text(x + 0.14, Y + H - 1.46, s["o"][0], size=8.4, mono=True, color=GREEN)
    c.text(x + 0.56, Y + H - 1.46, s["o"][1], size=8.4, mono=True, color=GREEN)
    for i, line in enumerate(s["code"]):
        c.text(x + 0.14, Y + 1.05 - i * 0.25, line, size=8.2, mono=True, color=INK)
    for i, line in enumerate(s["ex"]):
        c.text(x + 0.14, Y + 0.58 - i * 0.25, line, size=8.2, mono=True, color=ORANGE)

for i in range(len(XS) - 1):
    c.arrow(XS[i] + W + 0.01, Y + H - 1.35, XS[i + 1] - 0.02, Y + H - 1.35, color=SOFT)

# ------------------------------------------------------------------ 底部通栏 --
c.box(0.35, 0.90, 14.65, 4.35, "学习钩子在哪、产物是什么", fc="white", ec="#9FB0BF")

yy = 4.78
for title, desc, code, note in LEFT:
    c.text(0.55, yy, title, size=10.2, color=RED, weight="bold")
    c.text(0.55, yy - 0.30, desc, size=9.0, color=SOFT)
    for i, line in enumerate(code):
        c.text(0.72, yy - 0.62 - i * 0.24, line, size=8.4, mono=True, color=BLUE)
    c.text(0.72, yy - 0.62 - len(code) * 0.24, note, size=8.4, mono=True, color=ORANGE)
    yy -= 1.75

c.text(6.35, 4.78, "示例：删节点 1 前后", size=10.2, color=INK, weight="bold")
POS = [(0.00, 0.42), (0.46, 0.42), (0.92, 0.42), (0.92, 0.00), (0.46, 0.00)]
EDGES = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 1)]


def draw_graph(ox, oy, removed=None, s=0.72):
    for u, v in EDGES:
        if removed in (u, v):
            continue
        c.ax.plot([ox + POS[u][0] * s, ox + POS[v][0] * s],
                  [oy + POS[u][1] * s, oy + POS[v][1] * s],
                  color=PALETTE["wire"], lw=1.5, zorder=1)
    for i, (px, py) in enumerate(POS):
        gone = i == removed
        c.ax.add_patch(Circle((ox + px * s, oy + py * s), 0.135,
                              fc="white" if gone else BLUE,
                              ec=RED if gone else "white",
                              lw=1.4 if gone else 1.2,
                              ls="--" if gone else "-", zorder=3))
        c.ax.text(ox + px * s, oy + py * s, str(i), color=RED if gone else "white",
                  fontsize=8.0, ha="center", va="center", zorder=4, weight="bold")


draw_graph(6.45, 3.55)
c.text(6.45, 3.20, "t: LCC = 5,  m = 5", size=8.4, mono=True, color=SOFT)
draw_graph(6.45, 1.95, removed=1)
c.text(6.45, 1.60, "after removing 1: LCC = 3, node 0 isolated", size=8.4, mono=True, color=RED)
c.text(6.45, 1.30, "r = -3/25 = -0.12", size=9.0, mono=True, color=ORANGE)

c.text(9.55, 4.78, "产物 1：一条 n-step 转移（示例）", size=10.2, color=INK, weight="bold")
for i, (k, v) in enumerate(RIGHT_KV):
    c.text(9.55, 4.42 - i * 0.27, k, size=8.4, mono=True, color=SOFT)
    c.text(10.45, 4.42 - i * 0.27, v, size=8.4, mono=True, color=ORANGE)

c.text(9.55, 2.88, "产物 2：一次梯度更新", size=10.2, color=INK, weight="bold")
for i, line in enumerate(RIGHT_CODE):
    c.text(9.70, 2.56 - i * 0.24, line, size=8.4, mono=True, color=BLUE)
c.text(9.70, 2.56 - len(RIGHT_CODE) * 0.24, RIGHT_NOTE, size=8.4, mono=True, color=ORANGE)
c.text(9.55, 1.36, "产物 3：best.pt —— 每 50 iter 贪心跑 100 张验证图，按 -ANC 取最优",
       size=8.8, color=SOFT)

c.callout(0.35, 0.22, 14.65, 0.52, CAVEAT, color=RED, fs=8.4)

c.save(OUT)
