#!/usr/bin/env python3
"""No.06 月份牌白猫·波普版 —— clumsy-crayon-pop
构图：竖幅月份牌版式。芥末黄光晕 + 花边双线框，顶部"月份牌"三字；
白猫女神半身像（奶油白毛、巧克力棕粗轮廓），大眼睛 + 复古青蝴蝶结，
手持团扇，拟声词"喵～"，底句"月份牌上的白猫女神"。
配色：复古波普（烫橙/芥末黄/复古青/巧克力棕/奶油）。
注意：crayon_lib 绘图函数都返回新图，必须 img = C.xxx(img, ...) 接住。
跑：python3 whitecat.py → ../../examples/06_whitecat_s1.png
"""
import sys, os, random, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "crayon"))
import crayon_lib as C
from PIL import Image

random.seed(19)

def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

# 复古波普
ORANGE = hx("#CC5500")   # 烫橙
YELLOW = hx("#E1AD01")   # 芥末黄
TEAL   = hx("#008B8B")   # 复古青
BROWN  = hx("#5C3317")   # 巧克力棕（轮廓）
CREAM  = hx("#F5E6C8")   # 奶油
FUR    = (255, 253, 248) # 猫毛：比奶油更白
WHITE  = (255, 255, 255)

W, H = 880, 1250
C.set_size(W, H)
img = Image.new("RGBA", (W, H), C.PAPER + (255,))

def fill_poly(base, pts, color, alpha=(170, 250), feather=3, grow=2, n=5200):
    m = C.soft_mask(pts, feather=feather, grow=grow)
    return C.crayon(base, m, color, direction=0, spread=8, n=n,
                    length=(14, 40), dot=(1.2, 2.4), alpha=alpha, jitter=14)

def outline(base, pts, color=BROWN, width=(2.6, 4.2)):
    return C.crayon_line(base, pts + [pts[0]], color, width=width, alpha=(200, 255), wobble=1.2)

# ── 底：奶油纸 + 芥末黄光晕 ──
img = fill_poly(img, C.poly_rect(0, 0, W, H, wobble=10), CREAM,
                n=22000, alpha=(140, 210), feather=6, grow=0)
img = fill_poly(img, C.blob(440, 620, 310, 350, k=18, rough=0.10), YELLOW,
                n=13000, alpha=(150, 225), feather=8, grow=2)

# ── 花边双线框 ──
img = outline(img, C.poly_rect(40, 40, 840, 1210, wobble=8), BROWN, width=(3.2, 5.0))
img = outline(img, C.poly_rect(72, 72, 808, 1178, wobble=6), ORANGE, width=(1.4, 2.4))

# ── 顶部扇形花边 ──
for x in range(130, 780, 62):
    img = fill_poly(img, C.blob(x, 205, 27, 18, k=10, rough=0.15), ORANGE,
                    n=500, alpha=(160, 230), feather=2, grow=1)

# ── 背景零星复古青圆点 ──
for (dx, dy, dr) in [(150, 320, 12), (730, 330, 10), (120, 1050, 10), (750, 1080, 12), (200, 950, 8)]:
    img = fill_poly(img, C.blob(dx, dy, dr, dr, k=10, rough=0.12), TEAL,
                    n=220, alpha=(120, 200), feather=2, grow=1)

# ── 肩膀/身体 ──
body = C.blob(440, 1000, 225, 140, k=16, rough=0.12)
img = fill_poly(img, body, FUR, n=7000, alpha=(165, 245))
img = outline(img, body)

# ── 蝴蝶结（脖子，复古青）──
knot = C.blob(440, 850, 28, 24, k=10, rough=0.12)
loop_l = [(412, 850), (300, 800), (315, 905)]
loop_r = [(468, 850), (580, 800), (565, 905)]
tail_l = [(422, 872), (392, 975), (432, 965)]
tail_r = [(458, 872), (488, 975), (448, 965)]
for p in (loop_l, loop_r, tail_l, tail_r, knot):
    img = fill_poly(img, p if isinstance(p, list) else p, TEAL, n=900, alpha=(165, 240), feather=2, grow=1)
for p in (loop_l, loop_r, tail_l, tail_r):
    img = outline(img, p, BROWN, width=(1.8, 2.8))
img = outline(img, knot, BROWN, width=(1.8, 2.8))

# ── 头 ──
head = C.blob(440, 620, 195, 180, k=18, rough=0.12)
img = fill_poly(img, head, FUR, n=9000, alpha=(165, 245))

# ── 耳朵 ──
ear_l = [(280, 505), (250, 360), (390, 455)]
ear_r = [(600, 505), (630, 360), (490, 455)]
for ear in (ear_l, ear_r):
    img = fill_poly(img, ear, FUR, n=1800, alpha=(165, 245))
    img = outline(img, ear)
in_l = [(295, 480), (278, 400), (360, 450)]
in_r = [(585, 480), (602, 400), (520, 450)]
for inner in (in_l, in_r):
    img = fill_poly(img, inner, ORANGE, n=600, alpha=(140, 220), feather=2, grow=1)

img = outline(img, head, BROWN, width=(3.0, 4.6))

# ── 大眼睛（无辜感拉满）──
for ex in (355, 525):
    white = C.blob(ex, 600, 48, 58, k=12, rough=0.10)
    img = fill_poly(img, white, WHITE, n=900, alpha=(200, 255), feather=1, grow=1)
    img = outline(img, white, BROWN, width=(1.8, 2.8))
    pupil = C.blob(ex + 6, 608, 22, 32, k=10, rough=0.10)
    img = fill_poly(img, pupil, BROWN, n=400, alpha=(210, 255), feather=1, grow=1)
    hl = C.blob(ex - 8, 588, 9, 9, k=8, rough=0.10)
    img = fill_poly(img, hl, WHITE, n=120, alpha=(220, 255), feather=1, grow=0)
    # 上眼睑 + 睫毛
    lid = [(ex - 52, 566), (ex - 20, 544), (ex + 20, 544), (ex + 52, 566)]
    img = C.crayon_line(img, lid, BROWN, width=(2.4, 3.6), alpha=(210, 255), wobble=0.7)
    s = -1 if ex < 440 else 1
    for i in range(3):
        img = C.crayon_line(img, [(ex + s*(46 + i*4), 560 - i*7), (ex + s*(62 + i*4), 548 - i*9)],
                            BROWN, width=(1.2, 2.0), alpha=(200, 255), wobble=0.5)

# ── 鼻子 + 嘴 ──
nose = [(428, 668), (452, 668), (440, 684)]
img = fill_poly(img, nose, BROWN, n=250, alpha=(200, 250), feather=1, grow=1)
img = C.crayon_line(img, [(440, 684), (424, 700), (410, 690)], BROWN,
                    width=(1.6, 2.4), alpha=(200, 255), wobble=0.6)
img = C.crayon_line(img, [(440, 684), (456, 700), (470, 690)], BROWN,
                    width=(1.6, 2.4), alpha=(200, 255), wobble=0.6)

# ── 腮红 + 胡须 ──
for s in (-1, 1):
    m = C.soft_mask(C.blob(440 + s*120, 700, 26, 16, k=10, rough=0.2), feather=4, grow=1)
    img = C.scribble(img, m, ORANGE, n=8, length=(10, 24), direction=-30)
    for dy in (-16, 2, 20):
        y0 = 680 + dy + random.uniform(-4, 4)
        img = C.crayon_line(img, [(440 + s*105, y0), (440 + s*185, y0 + random.uniform(-8, 8))],
                            BROWN, width=(1.0, 1.8), alpha=(160, 230), wobble=0.8)

# ── 团扇（右手）──
fan_c, fan_r = (670, 950), 95
fan = C.blob(fan_c[0], fan_c[1], fan_r, fan_r, k=20, rough=0.08)
img = fill_poly(img, fan, CREAM, n=3200, alpha=(165, 240))
img = outline(img, fan, BROWN, width=(2.6, 4.0))
# 扇面小花
for a in range(5):
    px = fan_c[0] + 34 * math.cos(2 * math.pi * a / 5 - 0.5)
    py = fan_c[1] + 34 * math.sin(2 * math.pi * a / 5 - 0.5)
    img = fill_poly(img, C.blob(px, py, 16, 16, k=8, rough=0.15), TEAL,
                    n=300, alpha=(150, 225), feather=2, grow=1)
img = fill_poly(img, C.blob(fan_c[0], fan_c[1], 15, 15, k=8, rough=0.12), ORANGE,
                n=300, alpha=(170, 240), feather=2, grow=1)
# 扇柄 + 爪子
img = C.crayon_line(img, [(fan_c[0], fan_c[1] + fan_r), (615, 1120)], BROWN,
                    width=(2.2, 3.4), alpha=(200, 255), wobble=0.8)
img = fill_poly(img, C.blob(610, 1105, 46, 34, k=10, rough=0.15), FUR,
                n=700, alpha=(165, 245), feather=2, grow=1)
img = outline(img, C.blob(610, 1105, 46, 34, k=10, rough=0.15), BROWN, width=(1.8, 2.8))

# ── 字 ──
tfont = C.font_cjk(62)
t = "月份牌"
tw = C.wobbly_text_width(t, tfont)
img = C.wobbly_text(img, t, ((W - tw) / 2, 92), tfont, BROWN, rot=7, bounce=4)

mfont = C.font_cjk(52)
img = C.wobbly_text(img, "喵～", (105, 400), mfont, TEAL, rot=12, bounce=5)

cfont = C.font_cjk(36)
cap = "月份牌上的白猫女神"
cw = C.wobbly_text_width(cap, cfont)
img = C.wobbly_text(img, cap, ((W - cw) / 2, 1140), cfont, BROWN, rot=5, bounce=3,
                    solid_alpha=0.95, density=0.18)

sfont = C.font_cjk(22)
img = C.wobbly_text(img, "雾染画", (730, 1185), sfont, BROWN, rot=8, bounce=2,
                    solid_alpha=0.95, density=0.18)

img = C.paper_grain(img, 0.09)
out = os.path.join(os.path.dirname(__file__), "..", "..", "examples", "06_whitecat_s1.png")
img.convert("RGB").save(out)
print("saved", out)
