"""笨拙蜡笔波普《MWAH!》— 月份牌白猫（复古 70s 配色）。
老上海月份牌重画：放射光芒、雪花膏铁罐、梅花团扇、祥云；主角白猫照参考图（不画爪子）：白毛、粉耳、紫蝴蝶结、蓝眼影、红唇。
python mwah.py [seed]   默认 seed 1
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

def heart(cx, cy, s, r, rot=0):
    t = np.linspace(0, 2 * np.pi, 16, endpoint=False)
    x = 16 * np.sin(t) ** 3; y = -(13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t))
    ca, sa = math.cos(rot), math.sin(rot)
    return blob([(cx + s * (a * ca - b * sa), cy + s * (a * sa + b * ca)) for a, b in zip(x, y)], r, wobble=1, n=160)

def draw(seed=1, out='crayon_mwah_s1.png'):
    pal = ['#CC5500', '#E1AD01', '#008B8B', '#5C3317', '#F5E6C8']   # Muse · 复古 70s
    orange, mustard, teal, brown, cream = [hex2rgb(h) for h in pal]
    ink = brown * 0.7
    # 主角照参考图的颜色
    fur, pinkear = np.array([255., 252., 246.]), hex2rgb('#F3A9A4')
    lav, lavd = hex2rgb('#B48CD2'), hex2rgb('#8457AE')
    shadow, lip, iris = hex2rgb('#6F9FDB'), hex2rgb('#D7263D'), hex2rgb('#2A1E2E')
    cv = Canvas(seed, PAPER); r = cv.rng
    yy, xx = np.mgrid[:S, :S]
    MIS = (3, -3)
    cx, cy = 480, 440

    # ---------------- 形状
    head = blob([(480, 300), (570, 312), (628, 365), (640, 440), (610, 510), (545, 552), (480, 560),
                 (415, 552), (350, 510), (322, 440), (334, 365), (392, 312)], r, wobble=5)
    EL = [(332, 360), (298, 255), (300, 160), (342, 178), (425, 270), (445, 318)]
    ER = [(960 - x, y) for x, y in EL]
    def shrink(P, k):
        c = np.mean(P, 0); return [tuple(c + (np.array(p) - c) * k + [0, 12]) for p in P]
    earL = blob(EL, r, wobble=3, n=300); earR = blob(ER, r, wobble=3, n=300)
    inL = blob(shrink(EL, 0.62), r, wobble=2, n=240); inR = blob(shrink(ER, 0.62), r, wobble=2, n=240)
    chest = blob([(420, 540), (545, 540), (595, 630), (625, 730), (480, 750), (335, 730), (365, 630)], r, wobble=4)
    bowL = blob([(470, 610), (380, 540), (270, 530), (225, 600), (250, 690), (340, 700), (465, 650)], r, wobble=5)
    bowR = blob([(495, 610), (585, 545), (695, 530), (740, 600), (715, 690), (625, 700), (500, 650)], r, wobble=5)
    knot = blob(ellipse_pts(482, 630, 42, 34, 8, 0, r, 0.05), r, wobble=2)
    pawL = blob(ellipse_pts(452, 585, 40, 32, 8, -0.2, r, 0.05), r, wobble=2)
    pawR = blob(ellipse_pts(515, 588, 40, 32, 8, 0.2, r, 0.05), r, wobble=2)
    hm = mask_of(head); eLm, eRm = mask_of(earL), mask_of(earR)
    cm = mask_of(chest); bLm, bRm, km = mask_of(bowL), mask_of(bowR), mask_of(knot)
    pLm, pRm = mask_of(pawL), mask_of(pawR)
    catm = hm | eLm | eRm | cm
    figm = catm | bLm | bRm | km
    figd = ndi.binary_dilation(figm, iterations=5)

    # 雪花膏罐（左下）、梅花团扇（右下）
    tin = blob([(95, 760), (255, 760), (262, 880), (88, 880)], r, wobble=2)
    tlid = blob(ellipse_pts(175, 760, 88, 26, 10, 0, r, 0.02), r, wobble=1.5)
    tbot = blob(ellipse_pts(175, 880, 87, 24, 10, 0, r, 0.02), r, wobble=1.5)
    fan = blob(ellipse_pts(805, 690, 108, 100, 10, 0.2, r, 0.03), r, wobble=2.5)
    tinm = mask_of(tin) | mask_of(tlid) | mask_of(tbot); fanm = mask_of(fan)
    propd = ndi.binary_dilation(tinm | fanm, iterations=5)

    # ---------------- 背景：芥末黄大团 + 头后一轮烫橙月洞门（不用放射光芒，像抽奖转盘）
    bgb = blob(ellipse_pts(cx, cy + 20, 430, 415, 12, 0.1, r, 0.05), r, wobble=14)
    bgm = mask_of(bgb) & ~figd & ~propd
    crayon_fill(cv, bgm, mustard, angle=0.7, density=1.2, coverage=0.95, passes=3, length=(25, 70), overflow=0.12)
    moon = blob(ellipse_pts(cx, 405, 285, 280, 12, 0, r, 0.03), r, wobble=5)
    mm = mask_of(moon) & ~figd
    crayon_fill(cv, mm, orange, angle=-0.6, density=1.5, coverage=1.08, passes=3, length=(30, 80), overflow=0, shift=MIS, heavy_spot=(560, 250, 90))
    rr = np.hypot(yy - 405, xx - cx)
    halftone(cv, mm & (rr > 170), mustard, cell=12, angle=0.4, size_field=np.clip((rr - 170) / 120, 0.1, 0.55))
    crayon_line(cv, moon, ink, w=(5, 8), passes=2, gap=0.06)
    inner = blob(ellipse_pts(cx, 405, 255, 250, 12, 0, r, 0.02), r, wobble=3)
    crayon_line(cv, inner, cream, w=(3, 5), passes=1, gap=0.2)
    # 月洞门外的芥末黄上：青色回纹小角花
    for (x0, y0, sx, sy) in ((70, 300, 1, 1), (890, 560, -1, -1)):
        P = [(0, 0), (60, 0), (60, 40), (20, 40), (20, 20), (40, 20)]
        stroke_path(cv, dens([(x0 + sx * u, y0 + sy * v) for u, v in P]), teal, w=(5, 7), passes=1)
    # 地面：青色网点一条
    ground = blob([(40, 830), (480, 850), (930, 830), (925, 905), (480, 915), (35, 905)], r, wobble=4)
    halftone(cv, mask_of(ground) & ~propd & ~figd, teal, cell=13, angle=0.35, size_field=np.clip((yy - 820) / 90, 0.2, 0.7))

    # 祥云（芥末黄卷卷，青线）
    for (x0, y0, sgn) in ((95, 470, 1), (865, 430, -1)):
        t = np.linspace(0, 3.4 * np.pi, 60); rad = 36 * (1 - t / (4.4 * np.pi))
        P = np.stack([x0 + sgn * rad * np.cos(t), y0 + rad * np.sin(t)], 1)
        tail = np.stack([x0 + sgn * np.linspace(36, 95, 15), y0 + 12 * np.sin(np.linspace(0, np.pi, 15))], 1)
        stroke_path(cv, np.concatenate([tail[::-1], P]), cream, w=(13, 16), passes=2)
        stroke_path(cv, np.concatenate([tail[::-1], P]), teal, w=(4, 6), passes=1)

    # 梅枝（右上），梅花红唇色
    br = dens([(950, 60), (860, 95), (790, 90), (735, 130)]) + 0
    br = br + periodic_noise(len(br), r, 2)[:, None]
    stroke_path(cv, br, ink, w=(7, 11), passes=2)
    stroke_path(cv, dens([(860, 95), (840, 150), (800, 175)]), ink, w=(5, 7), passes=1)
    for (bx, by, s) in ((790, 92, 1), (740, 128, 0.85), (840, 152, 0.8), (900, 75, 0.9), (805, 178, 0.7)):
        pet = np.zeros((S, S), bool)
        for i in range(5):
            a = i * 2 * np.pi / 5 + 0.3
            pet |= mask_of(blob(ellipse_pts(bx + 14 * s * math.cos(a), by + 14 * s * math.sin(a), 11 * s, 11 * s, 6, 0, r, 0.1), r, wobble=1, n=60))
        crayon_fill(cv, pet, lip, density=3, coverage=1.4, passes=2, overflow=0, width=(2, 4))
        halftone(cv, pet, mustard, cell=6, angle=0, size_field=np.clip(1 - np.hypot(xx - bx, yy - by) / (8 * s), 0, 1))

    # ---------------- 蝴蝶结（参考图的淡紫）
    for m_, C in ((bLm, bowL), (bRm, bowR)):
        crayon_fill(cv, m_ & ~cm, lav, angle=0.9, density=1.6, coverage=1.1, passes=3, overflow=0, length=(25, 60))
    halftone(cv, (bLm | bRm) & ~cm & (yy > 640), lavd, cell=10, angle=0.3, size_field=0.55)
    for (x0, y0, x1, y1) in ((440, 615, 300, 580), (440, 640, 310, 665), (525, 615, 665, 580), (525, 640, 655, 668)):
        stroke_path(cv, dens([(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2 + 8), (x1, y1)]), lavd, w=(4, 6), passes=1)
    crayon_line(cv, bowL, ink, w=(5, 9), passes=2, gap=0.04); crayon_line(cv, bowR, ink, w=(5, 9), passes=2, gap=0.04)

    # ---------------- 白猫
    crayon_fill(cv, catm, fur, angle=1.1, density=1.6, coverage=1.15, passes=3, length=(25, 65), overflow=0)
    crayon_fill(cv, mask_of(inL), pinkear, angle=1.3, density=2.2, coverage=1.25, passes=3, overflow=0)
    crayon_fill(cv, mask_of(inR), pinkear, angle=1.3, density=2.2, coverage=1.25, passes=3, overflow=0)
    sh = (hm & (xx > 575)) | (cm & (xx > 545))
    halftone(cv, sh, lav * 0.55 + fur * 0.45, cell=9, angle=0.3, size_field=np.clip((xx - 545) / 90, 0.2, 0.65))
    crayon_line(cv, earL, ink, w=(5, 8), passes=2, gap=0.04); crayon_line(cv, earR, ink, w=(5, 8), passes=2, gap=0.04)
    crayon_line(cv, chest, ink, w=(5, 8), passes=2, gap=0.05)
    crayon_fill(cv, hm, fur, angle=1.0, density=1.8, coverage=1.25, passes=3, overflow=0)   # 盖住耳根和光圈线
    crayon_line(cv, head, ink, w=(5, 9), passes=2, gap=0.04)
    # 蝴蝶结结子

    # 腮红（粉网点）
    for (x, y) in ((380, 480), (588, 476)):
        halftone(cv, hm & ((xx - x) ** 2 + ((yy - y) * 1.5) ** 2 < 34 ** 2), pinkear * 0.8 + lip * 0.2, cell=8, angle=0.3, size_field=0.75)
    # 胡子：从脸颊往外，避开眼和嘴
    for sgn, x0 in ((-1, 420), (1, 545)):
        for dy, a in ((-6, -0.12), (8, 0.05), (22, 0.2)):
            P = [(x0, 490 + dy), (x0 + sgn * 90, 490 + dy + 90 * a), (x0 + sgn * 175, 490 + dy + 175 * a + 6)]
            stroke_path(cv, dens(P), ink, w=(2, 3), passes=1)

    # 五官最后画：半垂的媚眼 + 蓝眼影 + 长睫毛
    for (ex, ey, sgn) in ((420, 418, -1), (545, 414, 1)):
        lid = blob(ellipse_pts(ex, ey - 9, 42, 22, 9, 0, r, 0.03), r, wobble=1.5)
        crayon_fill(cv, mask_of(lid), shadow, density=2.4, coverage=1.3, passes=3, overflow=0, width=(2, 4))
        eye = blob(ellipse_pts(ex, ey + 2, 35, 25, 10, sgn * -0.12, r, 0.02), r, wobble=1)
        em = mask_of(eye)
        crayon_fill(cv, em, fur, density=3, coverage=1.6, passes=3, overflow=0, width=(2, 4))
        pup = mask_of(blob(ellipse_pts(ex - sgn * 4, ey + 7, 16, 19, 8, 0, r, 0.03), r, wobble=1)) & em & (yy > ey - 6)
        crayon_fill(cv, pup, iris, density=3.5, coverage=1.7, passes=3, overflow=0, width=(2, 4), edge_follow=False)
        hl = blob(ellipse_pts(ex - sgn * 8, ey + 1, 4, 4, 5, 0, r, 0.1), r, wobble=0.5, n=40)
        crayon_fill(cv, mask_of(hl), fur, density=4, coverage=1.8, passes=2, overflow=0, width=(2, 3), edge_follow=False)
        # 上眼睑：粗线压在眼白上沿（眼睛半垂）
        t = np.linspace(np.pi + 0.05, 2 * np.pi - 0.05, 20)
        P = np.stack([ex + 36 * np.cos(t), ey + 4 + 18 * np.sin(t) * 0.55], 1)
        stroke_path(cv, P, ink, w=(6, 8), passes=2)
        t = np.linspace(0.15, np.pi - 0.15, 16)
        stroke_path(cv, np.stack([ex + 34 * np.cos(t), ey + 2 + 24 * np.sin(t)], 1), ink, w=(2, 3), passes=1)
        ox = ex + sgn * 36
        for i, (lx, ly) in enumerate(((sgn * 26, -14), (sgn * 30, -2), (sgn * 24, 10))):
            stroke_path(cv, [(ox - sgn * i * 5, ey - 4 - i * 2), (ox + lx * 0.6 - sgn * i * 4, ey - 6 + ly * 0.6), (ox + lx, ey + ly - 6)], ink, w=(3, 5), passes=1)
    # 鼻子 + 嘟起的红唇（亲亲）
    nose = blob(ellipse_pts(483, 470, 11, 8, 7, 0, r, 0.05), r, wobble=0.8, n=70)
    crayon_fill(cv, mask_of(nose), ink, density=3.5, coverage=1.7, passes=3, overflow=0, width=(2, 4))
    lips = heart(484, 512, 1.15, r)
    crayon_fill(cv, mask_of(lips), lip, density=3.5, coverage=1.6, passes=3, overflow=0, width=(2, 4))
    stroke_path(cv, [(474, 512), (484, 515), (494, 511)], ink * 0.8 + lip * 0.2, w=(2, 3), passes=1)
    crayon_line(cv, lips, ink, w=(2, 4), passes=1, gap=0)
    # 飞出来的小爱心
    for (hx, hy, s, ro) in ((700, 355, 1.9, 0.3), (765, 300, 1.4, 0.45), (812, 262, 1.0, 0.6)):
        h = heart(hx, hy, s, r, ro)
        crayon_fill(cv, mask_of(h), lip, density=3, coverage=1.5, passes=3, overflow=0, width=(2, 4))
        crayon_line(cv, h, ink, w=(3, 4), passes=1, gap=0)

    # ---------------- 雪花膏铁罐：青罐身、芥末盖、奶油标签上一朵梅
    crayon_fill(cv, mask_of(tin) | mask_of(tbot), teal, angle=1.3, density=2, coverage=1.2, passes=3, overflow=0)
    lab = blob(ellipse_pts(175, 822, 46, 38, 8, 0, r, 0.04), r, wobble=1.5)
    crayon_fill(cv, mask_of(lab), cream, density=2.6, coverage=1.4, passes=3, overflow=0)
    for i in range(5):
        a = i * 2 * np.pi / 5 - 0.3
        p = blob(ellipse_pts(175 + 12 * math.cos(a), 822 + 12 * math.sin(a), 9, 9, 6, 0, r, 0.1), r, wobble=0.8, n=50)
        crayon_fill(cv, mask_of(p), lip, density=3, coverage=1.4, passes=2, overflow=0, width=(2, 3))
    crayon_line(cv, lab, ink, w=(3, 4), passes=1)
    crayon_line(cv, tin, ink, w=(5, 8), passes=2, gap=0.03)
    crayon_fill(cv, mask_of(tlid), mustard, density=2.4, coverage=1.3, passes=3, overflow=0)
    halftone(cv, mask_of(tlid), orange, cell=8, angle=0.2, size_field=0.4)
    crayon_line(cv, tlid, ink, w=(4, 7), passes=2, gap=0.02)
    for k_ in range(3):
        stroke_path(cv, [(112 + k_ * 10, 790), (118 + k_ * 10, 865)], cream, w=(3, 5), passes=1)

    # ---------------- 团扇：奶油绢面 + 一枝梅，棕柄，橙流苏
    hdl = dens([(745, 778), (700, 840), (676, 872)])
    stroke_path(cv, hdl, ink, w=(9, 12), passes=2)
    for k_ in range(4):
        stroke_path(cv, [(672 + k_ * 3, 875), (660 + k_ * 5, 922)], orange, w=(3, 5), passes=1)
    crayon_fill(cv, fanm, cream, angle=0.4, density=1.8, coverage=1.2, passes=3, overflow=0)
    halftone(cv, fanm, mustard, cell=10, angle=0.3, size_field=np.clip((np.hypot(xx - 805, yy - 690) - 50) / 70, 0.1, 0.5))
    stroke_path(cv, dens([(735, 740), (790, 690), (850, 650), (880, 630)]), ink, w=(4, 6), passes=1)
    for (bx, by) in ((790, 690), (840, 655), (765, 712), (868, 640)):
        for i in range(5):
            a = i * 2 * np.pi / 5
            p = blob(ellipse_pts(bx + 11 * math.cos(a), by + 11 * math.sin(a), 10, 10, 6, 0, r, 0.1), r, wobble=0.6, n=40)
            crayon_fill(cv, mask_of(p), lip, density=3, coverage=1.4, passes=2, overflow=0, width=(2, 3))
    crayon_line(cv, fan, ink, w=(5, 8), passes=2, gap=0.03)
    ring = blob(ellipse_pts(805, 690, 96, 88, 10, 0.2, r, 0.02), r, wobble=1.5)
    crayon_line(cv, ring, orange, w=(3, 4), passes=1, gap=0.15)

    # ---------------- 拟声词 MWAH!：手画粗字母，芥末黄 + 棕错位影
    LET = {'M': [[(0.02, 1), (0.06, 0), (0.5, 0.62), (0.94, 0), (0.98, 1)]],
           'W': [[(0.0, 0), (0.22, 1), (0.5, 0.38), (0.78, 1), (1.0, 0)]],
           'A': [[(0.02, 1), (0.5, 0), (0.98, 1)], [(0.24, 0.64), (0.78, 0.62)]],
           'H': [[(0.06, 0), (0.04, 1)], [(0.94, 0), (0.96, 1)], [(0.05, 0.5), (0.95, 0.48)]],
           '!': [[(0.5, 0), (0.45, 0.66)]]}
    x = 42
    for i, ch in enumerate('MWAH!'):
        hgt = 84 * r.uniform(0.92, 1.08); wid = {'M': 74, 'W': 80, 'A': 62, 'H': 56, '!': 22}[ch] * r.uniform(0.94, 1.06)
        base = 168 - i * 9 + r.normal(0, 4); rot_ = r.normal(-0.08, 0.06)
        ca_, sa_ = math.cos(rot_), math.sin(rot_)
        def T(p): u, v = p[0] * wid, (p[1] - 1) * hgt; return (x + u * ca_ - v * sa_, base + u * sa_ + v * ca_)
        for st in LET[ch]:
            P = dens([T(p) for p in st])
            stroke_path(cv, P + np.array([5, 5]), ink, w=(9, 12), passes=1)
            stroke_path(cv, P, orange, w=(15, 19), passes=2)
        if ch == '!':
            d = blob(ellipse_pts(*T((0.45, 0.92)), 10, 9, 6, 0, r, 0.1), r, wobble=1.2, n=70)
            crayon_fill(cv, mask_of(np.array(d)), orange, density=4, coverage=1.6, passes=2, width=(3, 5), overflow=0)
        x += wid + 16

    hand_text(cv, 'OCT 19 2026', 668, 948, 30, ink, orange, r, w=(5, 7))
    Image.fromarray(np.clip(cv.img, 0, 255).astype(np.uint8)).save(out)
    print('saved', out)

if __name__ == '__main__':
    s = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    draw(s, sys.argv[2] if len(sys.argv) > 2 else f'crayon_mwah_s{s}.png')
