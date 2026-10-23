# -*- coding: utf-8 -*-
"""Demo M4: A / B comparison — two numeric grids, a verdict line, a red caveat.

Run:  python demo_compare.py
Out:  demo_compare.png
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from diagram_kit import PALETTE, Canvas

OUT = os.path.join(os.getcwd(), "demo_compare.png")

c = Canvas()
c.title("同一句损失，两种口径：论文写法 vs 代码默认", "explainer-diagram / demo_compare.py")

# ------------------------------------------------------------ left panel ---
c.box(0.40, 3.90, 6.55, 3.95, "A｜论文 Methods Eq.(9)", tint="blue")
c.text(0.62, 7.28, "L_field = lam1 * mse(X, X_hat)", size=9.6, mono=True,
       color=PALETTE["ink2"])
c.tensor_grid(
    1.35, 6.50,
    [["SST", "τx", "τy", "hT", "T300"]],
    row_labels=["被监督"],
    tints=["blue"] * 5,
)
c.bracket(1.33, 1.35 + 5 * 0.80 - 0.07, 6.18, "5 个变量全部进入损失", PALETTE["blue"])
c.text(0.62, 5.55, "结论：τ 有损失，说「不进入任何损失」是错的。", size=10.2,
       color=PALETTE["blue"], weight="bold")
c.text(0.62, 5.10, "但它按通道相加，通道之间没有任何耦合项。", size=9.6,
       color=PALETTE["soft"])

# ----------------------------------------------------------- right panel ---
c.box(7.25, 3.90, 7.55, 3.95, "B｜开源默认 config：loss_all = 0", tint="orange")
c.text(7.47, 7.28, "loss = mean((pred[:,:,0] - target[:,:,0])**2)", size=9.6, mono=True,
       color=PALETTE["ink2"])
c.tensor_grid(
    8.20, 6.50,
    [["SST", "τx", "τy", "hT", "T300"]],
    row_labels=["被监督"],
    tints=["orange", "grey", "grey", "grey", "grey"],
)
c.bracket(8.18, 8.20 + 5 * 0.80 - 0.07, 6.18, "只有通道 0 有梯度，其余 4 个为 0", PALETTE["orange"])
c.text(7.47, 5.55, "结论：默认跑出来的模型，τ 的预测值没有任何监督。", size=10.2,
       color=PALETTE["orange"], weight="bold")
c.text(7.47, 5.10, "而且 τ 的预测质量从未被独立评估。", size=9.6, color=PALETTE["soft"])

# -------------------------------------------------------------- verdict ---
c.arrow(6.98, 5.40, 7.22, 5.40, color=PALETTE["red"], lw=2.0, ms=16)

c.box(0.40, 0.85, 14.40, 2.80, "三句话合起来才是完整的说法", fc="white", ec="#9FB0BF")
c.why(0.65, 3.12, "① 论文层面：主损失覆盖 5 个变量，τ 有损失 —— 这一点必须承认。", fs=10.4)
c.why(0.65, 2.72, "② 结构层面：损失按通道可加，没有跨通道项 —— 这才是真正可批评处。", fs=10.4)
c.why(0.65, 2.32, "③ 代码层面：默认只算通道 0，τ 实际未受监督 —— 引用时必须带「默认配置下」。", fs=10.4)
c.text(0.65, 1.75, "反例（别这么写）：τ 虽由模型生成却不进入任何损失。"
                   "   ← 忽略 ①，一句话就能被打回。", size=9.8, color=PALETTE["red"])
c.text(0.65, 1.25, "推荐写法：论文以覆盖 5 个变量的重构损失训练；但该损失按通道可分离、无跨通道项；"
                   "且开源默认配置下场级损失只取 SST 通道。", size=9.8, color=PALETTE["soft"])

c.save(OUT)
