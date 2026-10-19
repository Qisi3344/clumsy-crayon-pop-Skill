#!/usr/bin/env python3
"""四格波普猫 —— clumsy-crayon-pop 范例。
Warhol 式 2x2 重复：同一只猫头，四种底色轮换。配色取自「迷幻六十年代」。
注意：crayon_lib 的绘图函数都返回新图，必须 img = C.crayon(img, ...) 这样接住。
跑：python3 pop_cat_4panel.py → pop_cat_4panel.png（约几秒）
"""
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "crayon"))
import crayon_lib as C
from PIL import Image

random.seed(7)

def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

BLACK = (20, 20, 20)
PINK = hx("#FF2E88")

# 面板：(底色, 猫色)
PANELS = [
    (hx("#FF7B00"), hx("#FFF3D6")),   # 橘子汽水底 → 奶油猫
    (hx("#E5007D"), hx("#B8D800")),   # 品红底 → 酸性柠檬猫
    (hx("#B8D800"), hx("#7B2FF7")),   # 酸性柠檬底 → 电紫猫
    (hx("#7B2FF7"), hx("#FF7B00")),   # 电紫底 → 橘子汽水猫
]

W, H = 1000, 1150
C.set_size(W, H)
img = Image.new("RGBA", (W, H), C.PAPER + (255,))

def fill_poly(base, pts, color, alpha=(170, 250), feather=3, grow=2, n=5200):
    m = C.soft_mask(pts, feather=feather, grow=grow)
    return C.crayon(base, m, color, direction=0, spread=8, n=n,
                    length=(14, 40), dot=(1.2, 2.4), alpha=alpha, jitter=14)

def outline(base, pts, color=BLACK, width=(2.6, 4.0)):
    closed = pts + [pts[0]]
    return C.crayon_line(base, closed, color, width=width, alpha=(200, 255), wobble=1.2)

def draw_cat(base, ox, oy, fur):
    cx, cy = ox + 250, oy + 275
    # 耳朵
    ear_l = [(cx-118, cy-55), (cx-140, cy-175), (cx-35, cy-105)]
    ear_r = [(cx+118, cy-55), (cx+140, cy-175), (cx+35, cy-105)]
    for ear in (ear_l, ear_r):
        base = fill_poly(base, ear, fur, n=1500)
        base = outline(base, ear)
    # 耳内粉
    in_l = [(cx-105, cy-75), (cx-118, cy-140), (cx-55, cy-100)]
    in_r = [(cx+105, cy-75), (cx+118, cy-140), (cx+55, cy-100)]
    for inner in (in_l, in_r):
        base = fill_poly(base, inner, PINK, n=500, alpha=(150, 220))
    # 头
    head = C.blob(cx, cy, 132, 118, k=16, rough=0.13)
    base = fill_poly(base, head, fur, n=6500)
    base = outline(base, head)
    # 眼睛：两颗黑豆，大小故意不一样（笨拙）
    for ex, er in ((cx-52, 15), (cx+54, 12)):
        e = C.blob(ex, cy-8, er, er+2, k=10, rough=0.12)
        base = fill_poly(base, e, BLACK, n=400, alpha=(200, 255), feather=1, grow=1)
    # 鼻子
    nose = [(cx-14, cy+38), (cx+14, cy+38), (cx, cy+54)]
    base = fill_poly(base, nose, PINK, n=300, alpha=(180, 240), feather=1, grow=1)
    # 嘴：小w
    base = C.crayon_line(base, [(cx, cy+54), (cx-16, cy+70), (cx-30, cy+58)],
                         BLACK, width=(1.6, 2.4), alpha=(200, 255), wobble=0.6)
    base = C.crayon_line(base, [(cx, cy+54), (cx+16, cy+70), (cx+30, cy+58)],
                         BLACK, width=(1.6, 2.4), alpha=(200, 255), wobble=0.6)
    # 胡须
    for s in (-1, 1):
        for dy in (-14, 4, 22):
            y0 = cy + 30 + dy + random.uniform(-4, 4)
            base = C.crayon_line(base, [(cx + s*80, y0), (cx + s*150, y0 + random.uniform(-8, 8))],
                                 BLACK, width=(1.0, 1.8), alpha=(160, 230), wobble=0.8)
    # 腮红 scribble 两道
    for s in (-1, 1):
        m = C.soft_mask(C.blob(cx + s*88, cy+42, 20, 12, k=10, rough=0.2), feather=4, grow=1)
        base = C.scribble(base, m, PINK, n=6, length=(12, 26), direction=-30)
    return base

# 四格底色
for i, (bg, fur) in enumerate(PANELS):
    ox, oy = (i % 2) * 500, (i // 2) * 500
    img = fill_poly(img, C.poly_rect(ox, oy, ox+500, oy+500, wobble=4),
                    bg, n=9000, alpha=(150, 230), feather=4, grow=0)
    img = draw_cat(img, ox, oy, fur)

# 格子间的粗黑线
img = C.crayon_line(img, [(500, 0), (500, 1000)], BLACK, width=(3.0, 5.0), alpha=(210, 255), wobble=1.0)
img = C.crayon_line(img, [(0, 500), (1000, 500)], BLACK, width=(3.0, 5.0), alpha=(210, 255), wobble=1.0)

# 底句 + 签名
font = C.font_cjk(46)
cap = "笨拙波普 · 四格猫"
tw = C.wobbly_text_width(cap, font)
img = C.wobbly_text(img, cap, ((W-tw)/2, 1035), font, BLACK, rot=6, bounce=4)
sig = C.font_cjk(26)
img = C.wobbly_text(img, "雾染画", (W-150, 1095), sig, BLACK, rot=8, bounce=3)

img = C.paper_grain(img, 0.09)
out = os.path.join(os.path.dirname(__file__), "pop_cat_4panel.png")
img.convert("RGB").save(out)
print("saved", out)
