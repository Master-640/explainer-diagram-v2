# -*- coding: utf-8 -*-
"""Demo M5/M7: timeline + two-level hierarchy on one canvas.

Run:  python demo_timeline.py
Out:  demo_timeline.png
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from diagram_kit import PALETTE, Canvas

OUT = os.path.join(os.getcwd(), "demo_timeline.png")

c = Canvas()
c.title("进度与归属：一条时间线 + 一张两层树", "explainer-diagram / demo_timeline.py")

# ---------------------------------------------------------------- timeline --
c.box(0.40, 4.55, 14.40, 3.75, "① 时间线：每个里程碑必须带可验收的产出", tint="grey")

c.timeline(
    1.60, 7.00,
    [
        ("2026.01", "基线复现"),
        ("2026.03", "数据管线"),
        ("2026.05", "原型通过"),
        ("2026.08", "调优收敛"),
        ("2026.10", "消融与案例"),
        ("2026.12", "定稿"),
    ],
    span=12.20, color=PALETTE["blue"],
)
c.text(1.60, 5.90, "验收口径写在每一段后面：", size=9.8, color=PALETTE["soft"])
c.text(1.60, 5.55, "「基线复现」= 曲线与论文重合；「原型」= 12 个月 ACC > 0.5；「调优」= 18 个月。",
       size=9.8, color=PALETTE["soft"])
c.text(1.60, 5.05, "红线：定稿之后不再改模型结构，只做分析与写作。", size=9.8,
       color=PALETTE["red"])

# ------------------------------------------------------------------- tree ---
c.box(0.40, 0.95, 9.10, 3.20, "② 归属：一张图看清谁负责什么", tint="blue")
c.tree(4.95, 2.85, "世界模型 f = D·G·E",
       ["编码器 E", "图模块 G", "解码器 D"], color=PALETTE["blue"])
c.text(0.65, 1.40, "读法：上层是整体记号，下层是三个可独立提交、独立测试的模块。", size=9.4,
       color=PALETTE["soft"])

# ---------------------------------------------------------------- legend ---
c.box(9.75, 0.95, 5.05, 3.20, "③ 图例与注意事项", fc="white")
c.legend(10.00, 3.40, [("blue", "预测主线（一阶段）"), ("orange", "发现支线（二阶段）"),
                       ("grey", "流程与里程碑")], dy=0.28)
c.callout(10.00, 1.20, 4.55, 1.30,
          "同一画布放多张图时，每张仍要有\n自己的编号与标题，否则读者\n不知道先看哪一块。",
          color=PALETTE["orange"], fs=9.2)

c.save(OUT)
