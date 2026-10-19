"""笨拙蜡笔波普《BOO!》— 万圣节小幽灵 + 南瓜灯（迷幻 60s 配色）。
python boo.py [seed]   默认 seed 3
"""
import sys, math, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from crayon_pop import (Canvas, blob, ellipse_pts, mask_of, crayon_fill, crayon_line, stroke_path, halftone,
                        hex2rgb, ensure_font, text_mask, hand_text, W as S, PAPER)
PAPER = hex2rgb(PAPER)

def draw(seed=3, out='crayon_boo_s3.png'):
    ensure_font()
    pal = ['#FF7B00', '#E5007D', '#B8D800', '#7B2FF7', '#FFF3D6']   # Muse · 迷幻 60s
    orange, magenta, lime, purple, cream = [hex2rgb(h) for h in pal]
    ink = purple * 0.45                                              # 轮廓：深紫
    ghostc = np.array([255., 252., 244.])
    cv = Canvas(seed, PAPER); r = cv.rng
    yy, xx = np.mgrid[:S, :S]
    MIS = (3, -3)

    # 幽灵：圆脑袋 + 波浪下摆，往左上飘，两只小手举起来吓人
    hem = []
    for i, x in enumerate(np.linspace(560, 160, 7)):
        hem.append((x, 720 + (40 if i % 2 else -10) + r.normal(0, 8)))
    ghost = blob([(360, 170), (470, 190), (545, 280), (575, 420), (575, 560)] + hem + [(160, 560), (175, 400), (225, 260), (280, 195)], r, wobble=8, n=480)
    armL = blob([(185, 430), (85, 330), (70, 300), (110, 300), (205, 380)], r, wobble=3, n=200)
    armR = blob([(550, 400), (650, 300), (680, 285), (668, 325), (565, 455)], r, wobble=3, n=200)
    # 南瓜灯：右下，三瓣
    pc = (735, 735)
    pumpkin = blob(ellipse_pts(pc[0], pc[1], 170, 135, 10, 0, r, 0.06), r, wobble=6)
    stem = blob([(720, 610), (750, 600), (775, 545), (760, 535), (728, 590)], r, wobble=2, n=150)
    leaf = blob([(760, 590), (835, 560), (860, 590), (800, 610)], r, wobble=2, n=150)

    gm = mask_of(ghost) | mask_of(armL) | mask_of(armR)
    pm = mask_of(pumpkin)
    fig = ndi.binary_dilation(gm | pm | mask_of(stem) | mask_of(leaf), iterations=4)

    # 背景：歪紫色大团 + 品红网点；下面一抹柠檬绿光
    bg = blob(ellipse_pts(480, 470, 380, 360, 9, 0.3, r, 0.1), r, wobble=16)
    bgm = mask_of(bg) & ~fig
    crayon_fill(cv, bgm, purple, angle=-0.8, density=1.0, coverage=0.85, passes=3, width=(3, 6), length=(25, 70), shift=MIS)
    hz = bgm & (xx + yy > 1000)
    halftone(cv, hz, magenta, cell=14, angle=0.45, size_field=np.clip((xx + yy - 1000) / 280, 0.25, 0.85), shift=MIS)
    glow = blob([(520, 860), (740, 840), (940, 870), (930, 915), (700, 920), (500, 905)], r, wobble=5)
    crayon_fill(cv, mask_of(glow) & ~fig, lime, angle=0.1, density=1.0, coverage=0.8, passes=2, length=(40, 90))
    shadow = blob(ellipse_pts(360, 845, 150, 26, 8, 0, r, 0.1), r, wobble=3)
    halftone(cv, mask_of(shadow), purple, cell=11, angle=0.3, size_field=0.7)

    # 幽灵涂白（白比纸亮一点），身体右侧一点淡紫阴影网点
    crayon_fill(cv, gm, ghostc, angle=1.1, density=1.5, coverage=1.1, passes=3, length=(25, 70), overflow=0.05)
    sh = mask_of(ghost) & (xx > 470) & (yy > 300)
    halftone(cv, sh, purple * 0.6 + ghostc * 0.4, cell=10, angle=0.3, size_field=np.clip((xx - 470) / 120, 0.2, 0.7))
    for C in (armL, armR):
        crayon_line(cv, C, ink, w=(5, 9), passes=2, gap=0.05)
    crayon_fill(cv, mask_of(ghost), ghostc, angle=1.0, density=0.8, coverage=0.7, passes=1, overflow=0)  # 盖住手根的线
    crayon_line(cv, ghost, ink, w=(6, 11), passes=2, gap=0.05)
    # 脸：黑豆眼一大一小、张大嘴（品红舌头）、腮红
    for (cx, cy, rx, ry) in ((305, 360, 26, 34), (430, 350, 22, 29)):
        e = blob(ellipse_pts(cx, cy, rx, ry, 7, 0.1, r, 0.06), r, wobble=2)
        crayon_fill(cv, mask_of(e), ink, density=3, coverage=1.5, passes=3, width=(3, 5), overflow=0)
        hl = blob(ellipse_pts(cx - rx * 0.3, cy - ry * 0.35, 7, 7, 5, 0, r, 0.1), r, wobble=1, n=60)
        crayon_fill(cv, mask_of(hl), ghostc, density=4, coverage=1.8, passes=2, width=(2, 4), overflow=0, edge_follow=False)
    mouth = blob([(325, 430), (410, 425), (400, 500), (365, 520), (335, 500)], r, wobble=3, n=200)
    mm = mask_of(mouth)
    crayon_fill(cv, mm, ink, density=2.5, coverage=1.4, passes=3, width=(3, 5), overflow=0)
    tongue = blob(ellipse_pts(368, 498, 26, 16, 7, 0, r, 0.08), r, wobble=2)
    crayon_fill(cv, mask_of(tongue) & mm, magenta, density=3, coverage=1.4, passes=3, width=(3, 5), overflow=0)
    crayon_line(cv, mouth, ink, w=(4, 7), passes=1, gap=0)
    for (cx, cy) in ((255, 425), (480, 410)):
        ck = mask_of(ghost) & ((xx - cx) ** 2 + ((yy - cy) * 1.4) ** 2 < 34 ** 2)
        halftone(cv, ck, magenta, cell=9, angle=0.3, size_field=0.75)
    # 飘动线
    for k in range(3):
        y = 610 + k * 45
        stroke_path(cv, [(620, y), (680, y - 8), (720, y + 4)], ink, w=(3, 6), passes=1)

    # 南瓜：橙色，竖瓣线，脸是挖空的，里面透柠檬绿光
    crayon_fill(cv, pm, orange, angle=0.2, density=1.5, coverage=1.05, passes=3, heavy_spot=(650, 700, 60))
    crayon_fill(cv, mask_of(stem), lime * 0.6 + ink * 0.4, angle=1.2, density=2, coverage=1.2, passes=2, overflow=0)
    crayon_fill(cv, mask_of(leaf), lime, angle=0.3, density=2, coverage=1.2, passes=2, overflow=0)
    crayon_line(cv, leaf, ink, w=(3, 5), passes=1)
    crayon_line(cv, stem, ink, w=(3, 6), passes=1)
    for dx in (-85, 0, 85):
        t = np.linspace(-1, 1, 20)
        P = np.stack([pc[0] + dx * np.cos(t * 0.9) * (1 - 0.15 * t ** 2), pc[1] + 128 * t], 1)
        stroke_path(cv, P, ink * 0.7 + orange * 0.3, w=(3, 6), passes=1)
    crayon_line(cv, pumpkin, ink, w=(6, 10), passes=2, gap=0.04)
    face = [blob([(665, 690), (705, 690), (685, 650)], r, wobble=1.5, n=90),
            blob([(765, 690), (805, 690), (790, 648)], r, wobble=1.5, n=90),
            blob([(650, 760), (690, 790), (735, 770), (780, 792), (825, 758), (790, 825), (735, 838), (680, 825)], r, wobble=2, n=220)]
    for f in face:
        crayon_fill(cv, mask_of(f), lime, density=3, coverage=1.5, passes=3, width=(3, 5), overflow=0)
        crayon_line(cv, f, ink, w=(3, 5), passes=1, gap=0)

    # 小糖果
    for (cx, cy, rot) in ((120, 820, 0.4), (540, 95, -0.3)):
        c = blob(ellipse_pts(cx, cy, 24, 18, 6, rot, r, 0.05), r, wobble=1.5)
        crayon_fill(cv, mask_of(c), magenta, density=3, coverage=1.4, passes=2, overflow=0)
        crayon_line(cv, c, ink, w=(3, 5), passes=1)
        for sgn in (-1, 1):
            ex, ey = cx + sgn * 24 * math.cos(rot), cy + sgn * 24 * math.sin(rot)
            tw = blob([(ex, ey), (ex + sgn * 26 * math.cos(rot - 0.5), ey + sgn * 26 * math.sin(rot - 0.5)),
                       (ex + sgn * 26 * math.cos(rot + 0.5), ey + sgn * 26 * math.sin(rot + 0.5))], r, wobble=1, n=90)
            crayon_fill(cv, mask_of(tw), orange, density=3, coverage=1.3, passes=2, overflow=0)
            crayon_line(cv, tw, ink, w=(2, 4), passes=1)

    # 拟声词 BOO!：手画粗字母（这款字体的拉丁字母是空心的，不用）
    th = np.linspace(0, 2 * np.pi, 36)
    tb = np.linspace(-np.pi / 2, np.pi / 2, 16)
    LET = {'B': [[(0.05, 0), (0.02, 1)],
                 [(0.05, 0.02)] + list(zip(0.4 + 0.45 * np.cos(tb), 0.25 + 0.23 * np.sin(tb))) + [(0.04, 0.48)],
                 [(0.04, 0.5)] + list(zip(0.45 + 0.5 * np.cos(tb), 0.74 + 0.25 * np.sin(tb))) + [(0.03, 0.99)]],
           'O': [list(zip(0.5 + 0.5 * np.cos(th), 0.5 + 0.5 * np.sin(th)))],
           '!': [[(0.5, 0), (0.45, 0.66)]]}
    def dens(P, step=5):
        P = np.array(P, float); o = [P[0]]
        for a_, b_ in zip(P[:-1], P[1:]):
            n_ = max(2, int(np.linalg.norm(b_ - a_) / step))
            for t_ in np.linspace(0, 1, n_)[1:]: o.append(a_ + (b_ - a_) * t_)
        return np.array(o)
    x = 610
    for i, ch in enumerate('BOO!'):
        hgt = 120 * r.uniform(0.9, 1.1); wid = (30 if ch == '!' else 78) * r.uniform(0.92, 1.08)
        base = 250 - i * 14 + r.normal(0, 5); rot = r.normal(-0.1, 0.06)
        ca_, sa_ = math.cos(rot), math.sin(rot)
        def T(p): u, v = p[0] * wid, (p[1] - 1) * hgt; return (x + u * ca_ - v * sa_, base + u * sa_ + v * ca_)
        for st in LET[ch]:
            P = dens([T(p) for p in st]); P = P + np.array([[0.0, 0.0]])
            stroke_path(cv, P + np.array([6, 5]), ink, w=(10, 14), passes=1)
            stroke_path(cv, P, orange, w=(18, 24), passes=2)
        if ch == '!':
            d = blob(ellipse_pts(*T((0.45, 0.92)), 12, 11, 6, 0, r, 0.1), r, wobble=1.5, n=80)
            crayon_fill(cv, mask_of(d), orange, density=4, coverage=1.6, passes=2, width=(3, 5), overflow=0)
        x += wid + 24
    hand_text(cv, 'OCT 19 2026', 668, 948, 30, ink, magenta, r, w=(5, 7))
    Image.fromarray(np.clip(cv.img, 0, 255).astype(np.uint8)).save(out)
    print('saved', out)

if __name__ == '__main__':
    s = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    draw(s, sys.argv[2] if len(sys.argv) > 2 else f'crayon_boo_s{s}.png')
