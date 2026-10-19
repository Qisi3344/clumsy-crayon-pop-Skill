"""笨拙蜡笔波普《嘶溜～》— 深夜杯面（沃霍尔配色）。
python noodles.py [seed]   默认 seed 1
"""
import sys, math, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from crayon_pop import (Canvas, blob, ellipse_pts, mask_of, crayon_fill, crayon_line, stroke_path, halftone,
                        hex2rgb, ensure_font, text_mask, hand_text, periodic_noise, W as S, PAPER)
PAPER = hex2rgb(PAPER)

def rot(pts, cx, cy, a):
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca) for x, y in pts]

def draw(seed=1, out='crayon_noodles_s1.png'):
    ensure_font()
    pal = ['#FF2E88', '#FFE14D', '#00C2D1', '#E63946', '#2B2B3A']   # Muse · 沃霍尔
    pink, yellow, cyan, red, ink = [hex2rgb(h) for h in pal]
    cv = Canvas(seed, PAPER); r = cv.rng
    yy, xx = np.mgrid[:S, :S]
    cx, top, bot, A = 470, 455, 830, -0.07     # 杯子往左歪一点

    # 背景：一大团歪歪的青色 + 粉网点
    bg = blob([(120, 200), (480, 130), (850, 230), (880, 560), (800, 860), (440, 880), (110, 800), (80, 480)], r, wobble=16)
    crayon_fill(cv, mask_of(bg), cyan, angle=-0.6, density=1.3, coverage=0.95, passes=3, length=(30, 80), overflow=0.2)
    body = blob(rot([(cx - 205, top), (cx, top + 8), (cx + 205, top), (cx + 180, 640), (cx + 150, bot), (cx, bot + 12), (cx - 150, bot), (cx - 180, 640)], cx, 640, A), r, wobble=4)
    bm = mask_of(body)
    halftone(cv, mask_of(bg) & ~ndi.binary_dilation(bm, iterations=6) & (yy > 600), pink, cell=15, angle=0.4, size_field=np.clip((yy - 600) / 280, 0.15, 0.55))

    # 杯身：上宽下窄
    crayon_fill(cv, bm, yellow, angle=1.2, density=1.6, coverage=1.1, passes=3, length=(30, 80), overflow=0.05)
    # 红色腰带 + 圆形标签
    band = blob(rot([(cx - 200, 520), (cx, 532), (cx + 200, 520), (cx + 195, 585), (cx, 597), (cx - 195, 585)], cx, 640, A), r, wobble=2)
    crayon_fill(cv, mask_of(band) & bm, red, angle=0.1, density=2, coverage=1.2, passes=3, overflow=0, edge_follow=False)
    lab = blob(ellipse_pts(cx + 5, 700, 78, 72, 8, 0, r, 0.05), r, wobble=2)
    crayon_fill(cv, mask_of(lab), pink, density=2.2, coverage=1.25, passes=3, overflow=0)
    crayon_line(cv, lab, ink, w=(4, 6), passes=1, gap=0.05)
    # 标签里一个小碗图标：三道面 + 碗
    bowl = blob([(cx - 40, 700), (cx + 50, 694), (cx + 30, 735), (cx - 22, 738)], r, wobble=1.5)
    crayon_fill(cv, mask_of(bowl), PAPER, density=3, coverage=1.4, passes=2, overflow=0)
    crayon_line(cv, bowl, ink, w=(3, 5), passes=1)
    for k in range(3):
        t = np.linspace(0, 1, 20); x0 = cx - 18 + k * 18
        stroke_path(cv, np.stack([x0 + 5 * np.sin(t * 9), 690 - 30 * t], 1), ink, w=(3, 4), passes=1)
    # 杯身竖向小网点 + 轮廓
    halftone(cv, bm & ~mask_of(band) & ~mask_of(lab) & (xx > cx + 90), red, cell=12, angle=0.2, size_field=0.4)
    crayon_line(cv, body, ink, w=(6, 10), passes=2, gap=0.04)

    # 杯口：深色面汤，面条卷卷溢出来
    rim = blob(ellipse_pts(cx - 14, top + 2, 205, 46, 10, A, r, 0.02), r, wobble=2)
    crayon_fill(cv, mask_of(rim), red * 0.55 + ink * 0.45, angle=0.0, density=2.2, coverage=1.3, passes=3, overflow=0)
    for k in range(13):
        x0 = cx - 190 + k * 29 + r.normal(0, 4)
        yb = top + 25 - abs(k - 6) * 3
        t = np.linspace(0, 1, 40)
        P = np.stack([x0 + 10 * np.sin(t * 10 + k), yb - (40 + r.uniform(0, 30)) * t + 0], 1)
        stroke_path(cv, P + 2, ink, w=(5, 6), passes=1)
        stroke_path(cv, P, yellow, w=(7, 10), passes=2)
    crayon_line(cv, rim, ink, w=(6, 9), passes=2, gap=0.03)

    # 盖子：揭开一半往后翘，奶油色带粉色斜纹
    lid = blob([(cx - 60, top - 30), (cx + 120, top - 160), (cx + 255, top - 205), (cx + 300, top - 140), (cx + 210, top - 30), (cx + 120, top - 10)], r, wobble=4)
    lm = mask_of(lid)
    crayon_fill(cv, lm, PAPER * 0.6 + yellow * 0.4, angle=0.8, density=1.8, coverage=1.1, passes=2, overflow=0)
    for k in range(5):
        st = lm & (np.abs((xx - (cx + 40 + k * 55)) + (yy - (top - 100)) * 0.7) < 10)
        crayon_fill(cv, st, pink, density=3, coverage=1.3, passes=2, overflow=0, edge_follow=False)
    crayon_line(cv, lid, ink, w=(5, 8), passes=2, gap=0.04)

    # 筷子：两根，夹起一缕面往上拉
    for d, c0 in ((0, ink), (26, red)):
        a0, a1 = np.array([cx - 70 + d, top + 15]), np.array([cx - 230 + d * 1.6, top - 260])
        stroke_path(cv, [a0, a1], ink, w=(12, 14), passes=2)
        stroke_path(cv, [a1 + (a0 - a1) * 0.0, a1 + (a0 - a1) * 0.22], c0 if d else pink, w=(8, 10), passes=2)
    for k in range(4):     # 被夹起来的面：从汤里一路卷到筷子尖
        t = np.linspace(0, 1, 60)
        x = (cx - 60 + k * 9) + (-95 + k * 4) * t + 13 * np.sin(t * 11 + k * 1.7)
        y = top + 10 - 195 * t
        P = np.stack([x, y], 1)
        stroke_path(cv, P + 3, ink, w=(5, 6), passes=1)
        stroke_path(cv, P, yellow, w=(8, 10), passes=2)
    for k in range(3):     # 面上滴下来的汤
        dx_, dy_ = cx - 120 + k * 22, top - 120 + k * 30
        drop = blob(ellipse_pts(dx_, dy_, 6, 9, 6, 0, r, 0.05), r, wobble=0.5, n=60)
        crayon_fill(cv, mask_of(drop), red, density=4, coverage=1.5, passes=2, overflow=0)

    # 热气：粉色粗卷线
    for k, sx in enumerate((cx + 10, cx + 110, cx + 200)):
        t = np.linspace(0, 1, 50)
        P = np.stack([sx + 18 * np.sin(t * 6.5 + k * 1.3), top - 70 - 150 * t - k * 10], 1)
        stroke_path(cv, P, pink, w=(8, 11), passes=2)

    # 拟声词「嘶溜～」：红色重压，深色错版影
    tmk = ndi.binary_dilation(text_mask('嘶溜～', 270, 125, 140, 6, r, wobble=2.5), iterations=2)
    tacc = ndi.gaussian_filter(tmk.astype(float), 0.9) * 2.4
    cv.deposit(np.roll(tacc, (6, 6), axis=(0, 1)) * 0.95, ink)
    cv.deposit(tacc, red)
    for k in range(3):
        stroke_path(cv, [(70, 70 + k * 38), (40, 60 + k * 44)], yellow, w=(4, 6), passes=1)

    hand_text(cv, 'OCT 19 2026', 668, 948, 30, ink, pink, r, w=(5, 7))
    Image.fromarray(np.clip(cv.img, 0, 255).astype(np.uint8)).save(out)
    print('saved', out)

if __name__ == '__main__':
    s = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    draw(s, sys.argv[2] if len(sys.argv) > 2 else f'crayon_noodles_s{s}.png')
