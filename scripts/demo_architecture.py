# -*- coding: utf-8 -*-
"""Demo M2: system architecture — swimlanes, boxes, routed arrows, legend.

Run:  python demo_architecture.py
Out:  demo_architecture.png
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from diagram_kit import PALETTE, Canvas

OUT = os.path.join(os.getcwd(), "demo_architecture.png")

c = Canvas()
c.title("请求链路：客户端 → 网关 → 查询服务 → 存储", "explainer-diagram / demo_architecture.py")

# ---------------------------------------------------------------- lanes ----
c.lane(0.4, 7.02, 10.9, 1.32, "接入层", tint="blue")
c.lane(0.4, 4.65, 10.9, 1.75, "服务层", tint="grey")
c.lane(0.4, 1.55, 10.9, 1.85, "数据层", tint="green")

# ---------------------------------------------------------------- boxes ----
c.box(0.85, 7.18, 3.30, 0.98, "客户端")
c.text(1.05, 7.48, "GET /api/v1/query?q=...", size=9.4, mono=True, color=PALETTE["ink2"])

c.box(4.85, 7.18, 3.30, 0.98, "网关")
c.text(5.05, 7.48, "鉴权 · 限流 · 路由", size=9.6, color=PALETTE["ink2"])

c.box(0.85, 4.90, 3.70, 1.20, "查询服务")
c.text(1.05, 5.50, "parse -> plan -> exec", size=9.4, mono=True, color=PALETTE["ink2"])
c.text(1.05, 5.10, "超时 3 s，失败重试 1 次", size=9.2, color=PALETTE["grey"])

c.box(5.25, 4.90, 3.70, 1.20, "缓存（旁路）")
c.text(5.45, 5.50, "key = hash(query)", size=9.4, mono=True, color=PALETTE["ink2"])
c.text(5.45, 5.10, "命中即返回，不回源", size=9.2, color=PALETTE["grey"])

c.box(0.85, 1.80, 3.70, 1.30, "向量库")
c.text(1.05, 2.50, "top-k = 20 / cosine", size=9.4, mono=True, color=PALETTE["ink2"])

c.box(5.25, 1.80, 3.70, 1.30, "对象存储")
c.text(5.45, 2.50, "s3://bucket/chunks/", size=9.4, mono=True, color=PALETTE["ink2"])

# ---------------------------------------------------------------- arrows ----
c.arrow(4.20, 7.67, 4.80, 7.67)                      # client -> gateway
c.elbow([(6.50, 7.15), (6.50, 6.55), (2.70, 6.55), (2.70, 6.15)])   # gateway -> query
c.arrow(4.60, 5.50, 5.20, 5.50)                      # query -> cache
c.elbow([(7.10, 4.85), (7.10, 4.10), (2.70, 4.10), (2.70, 3.15)])   # cache -> vector db
c.arrow(4.60, 2.45, 5.20, 2.45)                      # vector db -> object store

# ---------------------------------------------------------------- right ----
c.legend(11.65, 8.20, [("blue", "接入层组件"), ("grey", "服务层组件"), ("green", "数据层组件")])

c.callout(11.65, 5.55, 3.30, 1.90,
          "注意：缓存是旁路，\n不是必经环节。\n缓存故障必须回源，\n不能返回空结果。",
          color=PALETTE["red"], fs=9.4)

c.box(11.65, 1.80, 3.30, 2.30, "关键约束", fc="white")
c.kv_lines(11.85, 3.30, ["网关 5 万 QPS", "查询 P99 < 800 ms", "缓存 TTL = 60 s"], fs=9.6, dy=0.40)

c.why(0.45, 1.05, "读这张图的方式：先看三个泳道（谁负责），再顺着箭头看一次请求经过谁，最后看右下角的约束。", fs=10.2)

c.save(OUT)
