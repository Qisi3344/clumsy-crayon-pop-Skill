"""笨拙蜡笔波普《RRRING!》— 响个不停的拨盘电话（利希滕斯坦配色）。
python ring.py [seed]   默认 seed 1
"""
import sys, math, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from crayon_pop import (Canvas, blob, ellipse_pts, mask_of, crayon_fill, crayon_line, stroke_path, halftone,
                        hex2rgb, hand_text, periodic_noise, W as S, PAPER)
PAPER = hex2rgb(PAPER)

def dens(P, step=5):
    P = np.array(P, float); o = [P[0]]
    for a, b in zip(P[:-1], P[1:]):
        n = max(2, int(np.linalg.norm(b - a) / step))
        for t in np.linspace(0, 1, n)[1:]: o.append(a + (b - a) * t)
    return np.array(o)

def letters(ch):
    """手画大写字母（单位方格，y 向下），返回 (笔画列表, 宽度比例)"""
    if ch == 'R': return [[(0, 1), (0, 0), (0.6, 0), (0.88, 0.14), (0.88, 0.36), (0.6, 0.5), (0.02, 0.5)], [(0.42, 0.5), (0.92, 1)]], 0.72
    if ch == 'I': return [[(0.5, 0), (0.5, 1)]], 0.3
    if ch == 'N': return [[(0, 1), (0, 0), (1, 1), (1, 0)]], 0.78
    if ch == 'G':
        t = np.linspace(-0.75, -2 * np.pi + 0.35, 30)
        return [list(zip(0.5 + 0.5 * np.cos(t), 0.5 + 0.5 * np.sin(t))) + [(0.97, 0.58), (0.58, 0.58)]], 0.8
    if ch == '!': return [[(0.5, 0), (0.5, 0.66)]], 0.3

def draw(seed=1, out='crayon_ring_s1.png'):
    pal = ['#E63946', '#FFD500', '#1D6FE0', '#141414', '#F5F0E6']   # Muse · 利希滕斯坦
    red, yellow, blue, ink, cream = [hex2rgb(h) for h in pal]
    cv = Canvas(seed, PAPER); r = cv.rng
    yy, xx = np.mgrid[:S, :S]
    cx, cy = 480, 640

    # 背景：歪歪的蓝色 Ben-Day 网点团 + 一圈黄色爆炸
    burst = []
    for i in range(22):
        a = 2 * math.pi * i / 22
        R0 = 330 if i % 2 == 0 else 250
        R0 *= r.uniform(0.92, 1.08)
        burst.append((cx + R0 * math.cos(a), cy - 30 + R0 * 0.92 * math.sin(a)))
    bm = mask_of(blob(burst, r, wobble=4, n=440))
    dots = blob([(90, 250), (480, 200), (880, 260), (900, 600), (850, 880), (470, 900), (80, 860), (60, 560)], r, wobble=14)
    halftone(cv, mask_of(dots) & ~bm, blue, cell=18, angle=0.35, size_field=0.62)
    crayon_fill(cv, bm, yellow, angle=-0.5, density=1.4, coverage=1.0, passes=3, length=(30, 80), overflow=0.1)
    crayon_line(cv, blob(burst, r, wobble=4, n=440), ink, w=(4, 7), passes=1, gap=0.06)

    # 电话机身：圆顶梯形，往右歪一点（被震得跳起来）
    A = 0.08
    def R(p): x, y = p; return (cx + (x - cx) * math.cos(A) - (y - cy) * math.sin(A), cy + (x - cx) * math.sin(A) + (y - cy) * math.cos(A))
    body = blob([R(p) for p in [(cx - 190, cy + 140), (cx - 170, cy - 30), (cx - 110, cy - 110), (cx, cy - 130), (cx + 110, cy - 110), (cx + 170, cy - 30), (cx + 190, cy + 140), (cx, cy + 150)]], r, wobble=4)
    bodym = mask_of(body)
    # 落地影：黑网点
    sh = blob(ellipse_pts(cx + 10, cy + 205, 200, 26, 8, 0, r, 0.05), r, wobble=2)
    halftone(cv, mask_of(sh), ink, cell=11, angle=0.2, size_field=0.55)
    crayon_fill(cv, bodym, red, angle=1.1, density=1.7, coverage=1.15, passes=3, length=(30, 80), overflow=0.05)
    halftone(cv, bodym & (xx > cx + 70), ink, cell=11, angle=0.35, size_field=0.35)   # 侧面暗部网点
    # 托架两个小叉（听筒原本放的地方）
    for sx in (-120, 120):
        p0 = R((cx + sx, cy - 105)); p1 = R((cx + sx * 1.12, cy - 150))
        stroke_path(cv, [p0, p1], ink, w=(14, 16), passes=2)
    # 拨盘
    dc = R((cx, cy + 20))
    dial = blob(ellipse_pts(dc[0], dc[1], 95, 88, 8, 0, r, 0.03), r, wobble=2)
    crayon_fill(cv, mask_of(dial), cream, density=2.2, coverage=1.3, passes=3, overflow=0)
    crayon_line(cv, dial, ink, w=(5, 8), passes=2, gap=0.03)
    for i in range(10):
        a = -2.4 + i * 0.47
        hx, hy = dc[0] + 62 * math.cos(a), dc[1] + 58 * math.sin(a)
        hole = blob(ellipse_pts(hx, hy, 13, 13, 6, 0, r, 0.05), r, wobble=0.6, n=60)
        crayon_fill(cv, mask_of(hole), ink, density=4, coverage=1.5, passes=2, overflow=0)
    cen = blob(ellipse_pts(dc[0], dc[1], 30, 28, 7, 0, r, 0.04), r, wobble=1)
    crayon_fill(cv, mask_of(cen), yellow, density=3, coverage=1.4, passes=2, overflow=0)
    crayon_line(cv, cen, ink, w=(3, 5), passes=1)
    stroke_path(cv, [(dc[0] + 70, dc[1] + 50), (dc[0] + 100, dc[1] + 72)], ink, w=(6, 8), passes=1)   # 拨盘挡片
    crayon_line(cv, body, ink, w=(7, 11), passes=2, gap=0.04)

    # 听筒：弹在半空，哑铃形，斜着
    hc, ha = np.array([470, 305]), -0.22
    def H(u, v): return (hc[0] + u * math.cos(ha) - v * math.sin(ha), hc[1] + u * math.sin(ha) + v * math.cos(ha))
    hand = blob([H(*p) for p in [(-230, -10), (-200, -45), (-130, -50), (-100, -25), (100, -25), (130, -50), (200, -45), (230, -10), (200, 40), (130, 40), (100, 15), (-100, 15), (-130, 40), (-200, 40)]], r, wobble=3)
    crayon_fill(cv, mask_of(hand), red, angle=0.0, density=2, coverage=1.2, passes=3, overflow=0)
    halftone(cv, mask_of(hand) & (yy > hc[1] + 8), ink, cell=10, angle=0.3, size_field=0.3)
    crayon_line(cv, hand, ink, w=(7, 10), passes=2, gap=0.03)
    for u in (-170, 170):   # 听筒两头的小孔
        for k in range(3):
            p = H(u - 20 + k * 20, 15)
            stroke_path(cv, [p, (p[0] + 2, p[1] + 3)], ink, w=(6, 7), passes=1)

    # 卷卷电话线：从机身左边绕到听筒左端
    t = np.linspace(0, 1, 420)
    a0 = np.array(R((cx - 180, cy + 60))); a1 = np.array(H(-215, 20))
    mid = np.array([150, 560])
    base = ((1 - t) ** 2)[:, None] * a0 + (2 * (1 - t) * t)[:, None] * mid + (t ** 2)[:, None] * a1
    tang = np.gradient(base, axis=0); tang /= np.linalg.norm(tang, axis=1, keepdims=True)
    nrm = np.stack([-tang[:, 1], tang[:, 0]], 1)
    ph = t * 2 * np.pi * 16
    P = base + nrm * (18 * np.sin(ph))[:, None] + tang * (10 * np.cos(ph))[:, None]
    stroke_path(cv, P, ink, w=(9, 11), passes=1)
    stroke_path(cv, P + (-2, -2), red, w=(4, 6), passes=1)

    # 震动线：机身和听筒周围一道道弧线
    for (px, py, R0, a0_, a1_) in ((cx, cy, 250, 2.6, 3.6), (cx, cy, 250, -0.5, 0.5), (cx, cy, 290, 2.7, 3.5), (cx, cy, 290, -0.4, 0.4),
                                  (470, 305, 290, 2.85, 3.4), (470, 305, 290, -0.3, 0.25)):
        th = np.linspace(a0_, a1_, 20)
        stroke_path(cv, np.stack([px + R0 * np.cos(th), py + R0 * 0.8 * np.sin(th)], 1), ink, w=(6, 8), passes=1)
    for k in range(5):   # 机身底下跳起来的小线
        x0 = cx - 140 + k * 70
        stroke_path(cv, [(x0, cy + 175), (x0 + 6, cy + 192)], ink, w=(5, 6), passes=1)

    # 拟声词 RRRING!：手画粗字母，黄填色 + 黑描边 + 黑错版影
    x, base_y, h = 150, 170, 120
    for i, ch in enumerate('RRRING!'):
        strokes, wr = letters(ch)
        w_ = h * wr; rot = r.normal(0, 0.06) + (0.04 * (i - 3)); hh = h * (1 + 0.05 * (i - 3))
        ca, sa = math.cos(rot), math.sin(rot); b = base_y + 10 * math.sin(i * 1.1)
        def T(p): u, v = p[0] * w_, (p[1] - 1) * hh; return (x + u * ca - v * sa, b + u * sa + v * ca)
        for st in strokes:
            Pp = dens([T(p) for p in st]); Pp = Pp + periodic_noise(len(Pp), r, 1.2)[:, None]
            stroke_path(cv, Pp + 8, ink, w=(30, 34), passes=1)
            stroke_path(cv, Pp, ink, w=(32, 36), passes=1)
            stroke_path(cv, Pp, yellow, w=(17, 21), passes=2)
        if ch == '!':
            d = T((0.5, 0.92)); dot = blob(ellipse_pts(d[0], d[1], 15, 15, 6, 0, r, 0.05), r, wobble=0.8, n=60)
            crayon_fill(cv, mask_of(dot), ink, density=4, coverage=1.6, passes=2, overflow=0)
        x += w_ + 28

    hand_text(cv, 'OCT 19 2026', 668, 948, 30, ink, red, r, w=(5, 7))
    Image.fromarray(np.clip(cv.img, 0, 255).astype(np.uint8)).save(out)
    print('saved', out)

if __name__ == '__main__':
    s = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    draw(s, sys.argv[2] if len(sys.argv) > 2 else f'crayon_ring_s{s}.png')
