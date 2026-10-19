"""笨拙蜡笔波普《叮咚！》— 午夜便利店（霓虹配色）。
python konbini.py [seed]   默认 seed 4
"""
import sys, math, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from crayon_pop import (Canvas, blob, ellipse_pts, mask_of, crayon_fill, crayon_line, stroke_path, halftone,
                        hex2rgb, ensure_font, text_mask, hand_text, periodic_noise, W as S, PAPER)
PAPER = hex2rgb(PAPER)

def dens(P, step=5):
    P = np.array(P, float); o = [P[0]]
    for a, b in zip(P[:-1], P[1:]):
        n = max(2, int(np.linalg.norm(b - a) / step))
        for t in np.linspace(0, 1, n)[1:]: o.append(a + (b - a) * t)
    return np.array(o)

def quad(x0, y0, x1, y1, r, wob=3):
    return blob([(x0, y0), ((x0 + x1) / 2, y0), (x1, y0), (x1, (y0 + y1) / 2), (x1, y1), ((x0 + x1) / 2, y1), (x0, y1), (x0, (y0 + y1) / 2)], r, wobble=wob)

def draw(seed=4, out='crayon_konbini_s4.png'):
    ensure_font()
    pal = ['#FF2E9A', '#00A8FF', '#E8FF47', '#0D1B4C', '#FFFFFF']   # Muse · 霓虹
    pink, blue, lime, navy, white = [hex2rgb(h) for h in pal]
    cv = Canvas(seed, PAPER); r = cv.rng
    yy, xx = np.mgrid[:S, :S]

    night = blob([(48, 60), (480, 40), (915, 58), (925, 480), (912, 868), (480, 878), (52, 866), (36, 480)], r, wobble=10)
    shop = quad(165, 300, 795, 840, r, 4)
    sign = quad(150, 290, 810, 392, r, 3)
    awn = quad(185, 392, 775, 445, r, 2)
    win = quad(205, 470, 520, 800, r, 3)
    door = quad(565, 470, 760, 840, r, 3)
    pot = quad(250, 700, 470, 790, r, 3)
    nm, sm = mask_of(night), mask_of(shop) | mask_of(sign)
    wm, dm = mask_of(win), mask_of(door)

    # 夜：海军蓝重涂，边上露奶油纸
    crayon_fill(cv, nm & ~ndi.binary_dilation(sm, iterations=3), navy, angle=-0.7, density=1.5, coverage=1.08, passes=3, length=(30, 80), overflow=0.15)
    # 月亮 + 星星
    moon = blob(ellipse_pts(140, 150, 50, 50, 8, 0, r, 0.05), r, wobble=2)
    bite = mask_of(blob(ellipse_pts(165, 132, 44, 44, 8, 0, r, 0.05), r, wobble=2))
    crayon_fill(cv, mask_of(moon) & ~bite, lime, density=2.5, coverage=1.4, passes=3, overflow=0)
    for (cx, cy, R0) in ((300, 110, 16), (520, 170, 11), (420, 80, 8), (860, 330, 10), (95, 420, 9)):
        for a in (0, math.pi / 2):
            stroke_path(cv, [(cx - R0 * math.cos(a), cy - R0 * math.sin(a)), (cx + R0 * math.cos(a), cy + R0 * math.sin(a))], white, w=(3, 5), passes=1)

    # 店：蓝墙
    crayon_fill(cv, mask_of(shop) & ~wm & ~dm, blue, angle=1.3, density=1.4, coverage=1.0, passes=3, length=(30, 80), overflow=0)
    # 屋檐条纹：粉白相间，下摆扇贝
    am = mask_of(awn)
    for i in range(10):
        x0 = 185 + i * 59
        stripe = am & (xx >= x0) & (xx < x0 + 59)
        crayon_fill(cv, stripe, pink if i % 2 == 0 else white, angle=1.5, density=1.8, coverage=1.1, passes=2, overflow=0, edge_follow=False)
        sc = blob(ellipse_pts(x0 + 29.5, 445, 29, 18, 8, 0, r, 0.05), r, wobble=1.5)
        crayon_fill(cv, mask_of(sc) & (yy > 445), pink if i % 2 == 0 else white, density=2, coverage=1.2, passes=2, overflow=0)
        crayon_line(cv, [p for p in sc if p[1] > 445], navy, w=(3, 5), passes=1, closed=False)
    crayon_line(cv, awn, navy, w=(4, 7), passes=1, gap=0.05)
    # 招牌：粉底，24H 柠檬绿灯管
    crayon_fill(cv, mask_of(sign), pink, angle=0.1, density=1.6, coverage=1.1, passes=3, overflow=0, length=(40, 100))
    crayon_line(cv, sign, navy, w=(6, 10), passes=2, gap=0.03)
    GL = {'2': [[(0.05, 0.25), (0.35, 0), (0.85, 0.12), (0.8, 0.45), (0.05, 1), (0.95, 0.98)]],
          '4': [[(0.7, 1), (0.68, 0), (0.02, 0.68), (0.98, 0.66)]],
          'H': [[(0.05, 0), (0.03, 1)], [(0.95, 0), (0.97, 1)], [(0.04, 0.5), (0.96, 0.48)]]}
    x = 365
    for ch in '24H':
        w_, h_ = 68, 74; base = 378 + r.normal(0, 3)
        for st in GL[ch]:
            P = dens([(x + u * w_, base - (1 - v) * h_) for u, v in st])
            P = P + periodic_noise(len(P), r, 1.2)[:, None]
            stroke_path(cv, P, white, w=(22, 26), passes=1)          # 灯管光晕
            stroke_path(cv, P, lime, w=(11, 15), passes=2)
        x += w_ + 34
    for k in range(4):   # 招牌发光的小线
        a = -2.6 + k * 0.35
        stroke_path(cv, [(480 + 300 * math.cos(a) * 0.6, 270 + 60 * math.sin(a)), (480 + 330 * math.cos(a) * 0.62, 250 + 75 * math.sin(a))], lime, w=(3, 5), passes=1)

    # 橱窗：亮白 + 柠檬绿网点光，货架上一排小商品
    crayon_fill(cv, wm, white, angle=0.6, density=1.6, coverage=1.1, passes=3, overflow=0)
    halftone(cv, wm & (yy > 600), lime, cell=11, angle=0.3, size_field=np.clip((yy - 600) / 200, 0.2, 0.6))
    for sy in (560, 650):
        stroke_path(cv, [(210, sy), (365, sy + 3), (515, sy)], blue, w=(5, 7), passes=1)
        x = 222
        while x < 495:
            w_ = r.uniform(20, 34); h_ = r.uniform(30, 55)
            it = quad(x, sy - h_, x + w_, sy - 3, r, 1.5)
            col = [pink, blue, lime][r.integers(0, 3)]
            crayon_fill(cv, mask_of(it), col, density=2.5, coverage=1.3, passes=2, overflow=0, edge_follow=False)
            crayon_line(cv, it, navy, w=(2, 4), passes=1)
            x += w_ + r.uniform(6, 14)
    # 关东煮锅：粉色锅身，串子插出来，热气卷卷往上
    crayon_fill(cv, mask_of(pot), pink, angle=0.2, density=2, coverage=1.2, passes=3, overflow=0)
    for sx in range(262, 470, 24):
        stroke_path(cv, [(sx, 712), (sx + 3, 724)], navy, w=(2, 3), passes=1)
    items = [('tri', 285, 675), ('ball', 330, 668), ('egg', 375, 676), ('tri', 420, 670), ('ball', 450, 680)]
    for kind, cx, cy in items:
        stroke_path(cv, [(cx, cy + 34), (cx + 2, cy - 48)], navy * 0.6 + PAPER * 0.4, w=(3, 4), passes=1)
        if kind == 'tri': sh = blob([(cx - 20, cy + 18), (cx + 20, cy + 18), (cx, cy - 18)], r, wobble=1.5, n=90); col = blue * 0.5 + navy * 0.5
        elif kind == 'egg': sh = blob(ellipse_pts(cx, cy, 16, 21, 7, 0, r, 0.05), r, wobble=1); col = lime
        else: sh = blob(ellipse_pts(cx, cy, 15, 15, 7, 0, r, 0.05), r, wobble=1); col = pink * 0.6 + navy * 0.4
        crayon_fill(cv, mask_of(sh), col, density=3, coverage=1.4, passes=2, overflow=0)
        crayon_line(cv, sh, navy, w=(2, 4), passes=1)
    crayon_line(cv, pot, navy, w=(4, 7), passes=2, gap=0.02)
    for k, sx in enumerate((300, 360, 425)):
        t = np.linspace(0, 1, 40)
        P = np.stack([sx + 12 * np.sin(t * 7 + k), 655 - 75 * t], 1)
        stroke_path(cv, P, blue, w=(5, 7), passes=1)
    crayon_line(cv, win, navy, w=(5, 9), passes=2, gap=0.03)

    # 玻璃门：亮白，门框，把手，门口光
    crayon_fill(cv, dm, white, angle=1.0, density=1.6, coverage=1.1, passes=3, overflow=0)
    halftone(cv, dm & (yy > 650), lime, cell=11, angle=0.3, size_field=0.45)
    stroke_path(cv, [(662, 475), (664, 835)], navy, w=(5, 8), passes=1)
    for hx in (640, 686):
        stroke_path(cv, [(hx, 620), (hx, 690)], pink, w=(6, 8), passes=1)
    crayon_line(cv, door, navy, w=(5, 9), passes=2, gap=0.03)
    for k in range(3):   # 门上反光斜线
        stroke_path(cv, [(585 + k * 18, 560), (625 + k * 18, 510)], blue, w=(3, 4), passes=1)
    crayon_line(cv, shop, navy, w=(6, 10), passes=2, gap=0.04)
    # 地上：店里的光泼出来（柠檬绿网点）
    gl = blob([(180, 843), (780, 843), (860, 872), (100, 872)], r, wobble=3)
    halftone(cv, mask_of(gl) & nm, lime, cell=12, angle=0.2, size_field=np.clip(1 - (yy - 843) / 40, 0.25, 0.8))

    # 拟声词「叮咚！」：粉色重压，白色错版影
    tmk = ndi.binary_dilation(text_mask('叮咚！', 730, 175, 120, -7, r, wobble=2.5), iterations=3)
    tacc = ndi.gaussian_filter(tmk.astype(float), 0.9) * 2.4
    cv.deposit(np.roll(tacc, (6, 6), axis=(0, 1)) * 0.95, white)
    cv.deposit(tacc, pink)
    for k in range(3):
        a = 0.5 + k * 0.4
        stroke_path(cv, [(905 + 0 * a, 120 + k * 40), (930, 112 + k * 40)], lime, w=(3, 5), passes=1)

    hand_text(cv, 'OCT 19 2026', 668, 948, 30, navy, pink, r, w=(5, 7))
    Image.fromarray(np.clip(cv.img, 0, 255).astype(np.uint8)).save(out)
    print('saved', out)

if __name__ == '__main__':
    s = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    draw(s, sys.argv[2] if len(sys.argv) > 2 else f'crayon_konbini_s{s}.png')
