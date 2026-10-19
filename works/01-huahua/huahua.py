"""笨拙蜡笔波普 No.01《喵？》— 玳瑁猫花花（复古 70s 配色）。
python huahua.py [seed]   默认 seed 5
"""
import sys, math, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from crayon_pop import (Canvas, blob, ellipse_pts, mask_of, crayon_fill, crayon_line, stroke_path, halftone,
                        hex2rgb, periodic_noise, ensure_font, text_mask, hand_text, W as S, PAPER)
PAPER = hex2rgb(PAPER)

def draw(seed=5, out='crayon_huahua_s5.png'):
    ensure_font()
    pal = ['#CC5500', '#E1AD01', '#008B8B', '#5C3317', '#F5E6C8']   # Muse · 复古 70s（玳瑁的焦糖+黑棕）
    orange, mustard, teal, brown, cream = [hex2rgb(h) for h in pal]
    dark = brown * 0.62                                            # 玳瑁黑：棕色重压
    cv = Canvas(seed, PAPER); r = cv.rng
    yy, xx = np.mgrid[:S, :S]
    MIS = (3, -3)

    frame = blob([(22, 24), (480, 18), (940, 26), (936, 480), (942, 936), (480, 940), (20, 934), (26, 480)], r, wobble=1.5)
    head = blob([(470, 165), (575, 180), (650, 250), (672, 345), (640, 440), (560, 495), (470, 505),
                 (380, 495), (300, 440), (270, 345), (295, 250), (370, 182)], r, wobble=6)
    earL = blob([(300, 262), (318, 92), (420, 190)], r, wobble=4, n=180)
    earR = blob([(525, 185), (618, 82), (645, 270)], r, wobble=4, n=180)
    inL = blob([(318, 240), (330, 128), (395, 195)], r, wobble=3, n=120)
    inR = blob([(545, 192), (608, 120), (625, 245)], r, wobble=3, n=120)
    body = blob([(470, 440), (600, 470), (665, 580), (700, 720), (690, 840), (610, 885), (470, 892),
                 (330, 885), (255, 830), (250, 700), (290, 570), (360, 470)], r, wobble=7)
    t = np.linspace(0, 1, 50)
    sp = np.stack([300 - 150 * t + 20 * np.sin(t * 4), 860 - 40 * t - 230 * t ** 2.2], 1)
    d = np.gradient(sp, axis=0); nr = np.stack([-d[:, 1], d[:, 0]], 1); nr /= np.linalg.norm(nr, axis=1, keepdims=True)
    tw = (30 - 12 * t)[:, None]; tail = np.concatenate([sp + nr * tw, (sp - nr * tw)[::-1]])
    legs = [blob([(400, 640), (452, 640), (458, 860), (395, 860)], r, wobble=3, n=200),
            blob([(492, 640), (545, 640), (550, 860), (488, 860)], r, wobble=3, n=200)]
    paws = [blob(ellipse_pts(424, 868, 46, 28, 7, 0, r, 0.08), r, wobble=3),
            blob(ellipse_pts(522, 868, 46, 28, 7, 0, r, 0.08), r, wobble=3)]
    bubble = blob(ellipse_pts(790, 150, 140, 72, 10, 0.05, r, 0.05), r, wobble=4)
    btail = blob([(700, 200), (742, 212), (660, 262)], r, wobble=2, n=120)

    hm, bm, tm = mask_of(head), mask_of(body), mask_of(tail)
    eLm, eRm = mask_of(earL), mask_of(earR)
    lm = [mask_of(l) for l in legs]; pm = [mask_of(p) for p in paws]
    catm = hm | bm | tm | eLm | eRm | lm[0] | lm[1] | pm[0] | pm[1]
    catd = ndi.binary_dilation(catm, iterations=4)
    bubm = np.zeros((S, S), bool)

    # 背景：歪青色大圆 + 右下网点
    bg = blob(ellipse_pts(470, 470, 360, 350, 9, 0.4, r, 0.1), r, wobble=14)
    bgm = mask_of(bg) & ~catd & ~bubm
    crayon_fill(cv, bgm, teal, angle=-0.75, density=0.9, coverage=0.75, passes=3, width=(3, 6), length=(25, 65), shift=MIS)
    hz = bgm & (xx + yy > 1050)
    halftone(cv, hz, brown, cell=14, angle=0.5, size_field=np.clip((xx + yy - 1050) / 300, 0.25, 0.9), shift=MIS)
    # 地上一道芥末黄（沙发扶手）
    sofa = blob([(150, 850), (480, 880), (690, 845), (700, 912), (480, 925), (140, 912)], r, wobble=5)
    crayon_fill(cv, mask_of(sofa) & ~catd, mustard, angle=0.1, density=1.1, coverage=0.85, passes=2, length=(40, 90))

    # 玳瑁：先整只涂深棕，再按低频噪声撒焦糖橙、芥末黄斑块
    def mottle(mask, ang, k, thr_o=0.42, thr_y=0.74):
        crayon_fill(cv, mask, dark, angle=ang, density=1.5, coverage=1.05, passes=3, overflow=0.1)
        n = ndi.gaussian_filter(r.random((S, S)), k); n = (n - n.min()) / (n.max() - n.min())
        crayon_fill(cv, mask & (n > thr_o), orange, angle=ang + 0.3, density=1.3, coverage=0.95, passes=2, overflow=0, width=(3, 6))
        crayon_fill(cv, mask & (n > thr_y), mustard, angle=ang - 0.3, density=1.0, coverage=0.75, passes=2, overflow=0, width=(3, 5))
    mottle(tm, -1.0, 9)
    mottle(bm, 1.0, 16)
    for m in lm + pm: mottle(m, 1.4, 7, 0.4, 0.7)
    for em, im_, ang in ((eLm, mask_of(inL), 1.3), (eRm, mask_of(inR), -0.9)):
        crayon_fill(cv, em, dark, angle=ang, density=1.5, coverage=1.0, passes=3)
        crayon_fill(cv, im_ & em, orange, angle=ang + 0.4, density=1.5, coverage=0.95, passes=2, width=(3, 5), overflow=0)
    # 脸：黑面具居中，左额、右颊两块焦糖（照片里的花色）
    crayon_fill(cv, hm, dark, angle=0.3, density=1.6, coverage=1.08, passes=3)
    patchA = blob([(300, 300), (360, 215), (410, 250), (385, 330), (330, 380)], r, wobble=6)
    patchB = blob([(555, 330), (640, 300), (668, 380), (620, 465), (560, 450)], r, wobble=6)
    patchC = blob([(540, 200), (600, 205), (575, 260)], r, wobble=4, n=150)
    for p, a in ((patchA, 1.1), (patchB, -0.9), (patchC, 0.4)):
        crayon_fill(cv, mask_of(p) & hm, orange, angle=a, density=1.4, coverage=0.95, passes=2, overflow=0)
    crayon_fill(cv, mask_of(blob([(600, 360), (640, 350), (630, 420)], r, wobble=3, n=120)) & hm, mustard,
                density=1.2, coverage=0.8, passes=2, overflow=0)

    # 轮廓：深棕外线
    for C in (tail, body, earL, earR, head):
        crayon_line(cv, C, dark * 0.8, w=(5, 10), passes=2, gap=0.05)
    for C in legs + paws:
        crayon_line(cv, C, orange, w=(3, 6), passes=1, gap=0.15)
    for p in paws:   # 爪缝
        c = p.mean(0)
        for k in (-1, 1): stroke_path(cv, [(c[0] + k * 14, c[1] - 10), (c[0] + k * 15, c[1] + 18)], orange, w=(3, 4), passes=1)

    # 眼睛：大圆、黄绿，瞪着你
    for (cx, cy, rx, ry) in ((405, 330, 50, 52), (548, 322, 44, 47)):
        e = blob(ellipse_pts(cx, cy, rx, ry, 8, 0.1, r, 0.05), r, wobble=2)
        em = mask_of(e)
        crayon_fill(cv, em, mustard, angle=0.9, density=2.2, coverage=1.25, passes=3, width=(3, 5), overflow=0)
        ring = em & ~mask_of(blob(ellipse_pts(cx, cy, rx * 0.78, ry * 0.78, 8, 0, r, 0.04), r, wobble=1.5))
        crayon_fill(cv, ring, teal, angle=-0.4, density=1.8, coverage=0.8, passes=2, width=(2, 4), overflow=0)
        pu = blob(ellipse_pts(cx + 2, cy + 3, rx * 0.5, ry * 0.55, 7, 0, r, 0.06), r, wobble=1.5)
        crayon_fill(cv, mask_of(pu), dark * 0.7, density=3, coverage=1.4, passes=3, width=(3, 5), overflow=0)
        crayon_line(cv, e, cream, w=(3, 5), passes=1, gap=0.15)
        hl = blob(ellipse_pts(cx - rx * 0.22, cy - ry * 0.25, 9, 8, 5, 0, r, 0.1), r, wobble=1, n=60)
        crayon_fill(cv, mask_of(hl), cream, density=4, coverage=1.7, passes=2, width=(2, 4), overflow=0, edge_follow=False)
    # 鼻嘴：奶油色细线勾在黑脸上
    nose = [(458, 395), (492, 392), (476, 415), (458, 395)]
    stroke_path(cv, nose, cream, w=(3, 5), passes=2)
    stroke_path(cv, [(476, 416), (474, 435), (456, 446)], cream, w=(3, 4), passes=1)
    stroke_path(cv, [(474, 435), (494, 447)], cream, w=(3, 4), passes=1)
    for (a, b) in [((430, 420), (300, 400)), ((430, 432), (295, 448)), ((520, 418), (650, 395)), ((520, 430), (665, 440)), ((518, 442), (630, 480))]:
        mid = ((a[0] + b[0]) / 2 + r.normal(0, 3), (a[1] + b[1]) / 2 + r.normal(0, 5))
        stroke_path(cv, [a, mid, b], cream, w=(3, 4), passes=2)

    # 拟声词「喵？」：不要对话框，粗蜡笔字直接压在纸上，棕色错版影
    tmk = text_mask('喵？', 790, 160, 150, 8, r, wobble=4)
    tacc = ndi.gaussian_filter(tmk.astype(float), 0.9) * 2.4
    cv.deposit(np.roll(tacc, (5, 5), axis=(0, 1)) * 0.9, brown)
    cv.deposit(tacc, orange)
    # 小涂鸦：头顶三道「？」似的惊讶线
    for k, a in enumerate((-2.3, -1.9, -1.5)):
        c = (470, 120)
        stroke_path(cv, [(c[0] + 20 * math.cos(a) * 3, c[1] + 15 * math.sin(a) + 20), (c[0] + 30 * math.cos(a) * 3.3, c[1] + 25 * math.sin(a))],
                    dark * 0.8, w=(3, 5), passes=1)

    # 角落手写日期（不画边框，她 2026-10-19 说不要）
    hand_text(cv, 'OCT 19 2026', 668, 915, 30, brown, orange, r, w=(5, 7))

    Image.fromarray(np.clip(cv.img, 0, 255).astype(np.uint8)).save(out)
    print('saved', out)

if __name__ == '__main__':
    s = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    draw(s, sys.argv[2] if len(sys.argv) > 2 else f'crayon_huahua_s{s}.png')
