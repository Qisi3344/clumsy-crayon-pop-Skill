"""笨拙蜡笔波普 · 手感基准对照卡（不是作品，是尺子）。
每一格用 crayon_pop.py 里的基准档画一遍；新作品画完和这张并排看，粗细、密度、歪度对得上才算一套。
python standard.py   → examples/00_standard.png
"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
sys.path.insert(0, ROOT)
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
from crayon_pop import *
from crayon_pop import hex2rgb

def main(seed=7, out=os.path.join(ROOT, 'examples', '00_standard.png')):
    ensure_font()
    red, yel, blue, ink, cream = [hex2rgb(h) for h in ['#E63946', '#FFD500', '#1D6FE0', '#141414', '#F5F0E6']]
    cv = Canvas(seed, hex2rgb(PAPER)); r = cv.rng
    yy, xx = np.mgrid[:H, :W]
    labels = []
    def cell(i, j): return 60 + j * 300, 60 + i * 290   # 左上角
    E = lambda cx, cy, rx, ry, k='body', rot=0: blob(ellipse_pts(cx, cy, rx, ry, 9, rot, r, 0.06), r, wobble=WOBBLE[k])

    # 1 背景团 bg + 网点 + 错版
    x, y = cell(0, 0); bg = E(x + 120, y + 110, 115, 95, 'bg')
    std_fill(cv, mask_of(bg), blue, 'bg', angle=-0.7, shift=MIS)
    halftone(cv, mask_of(bg) & (xx + yy > x + y + 260), red, cell=HALFTONE['cell'], angle=HALFTONE['angle'],
             size_field=np.clip((xx + yy - (x + y + 260)) / 120, *HALFTONE['size']))
    labels.append((x, y + 222, "背景团 bg · wobble 14", "网点 cell12 · 错版 (3,-3)"))

    # 2 主体大色块 body + main 轮廓
    x, y = cell(0, 1); b = E(x + 120, y + 105, 105, 90, 'body', 0.3)
    std_fill(cv, mask_of(b), red, 'body', angle=1.1)
    std_line(cv, b, ink, 'main')
    labels.append((x, y + 222, "主体 body · wobble 6", "轮廓 main 5–10px ×2遍"))

    # 3 部件 part + part 轮廓
    x, y = cell(0, 2); p = E(x + 80, y + 105, 60, 75, 'part', 0.2); q = E(x + 170, y + 120, 50, 55, 'part')
    std_fill(cv, mask_of(p), yel, 'part', angle=0.3); std_line(cv, p, ink, 'part')
    std_fill(cv, mask_of(q), blue, 'part', angle=-0.5); std_line(cv, q, ink, 'part')
    labels.append((x, y + 222, "部件 part · wobble 3", "轮廓 part 4–7px"))

    # 4 五官：花纹先画、留空地、五官最后
    x, y = cell(1, 0); head = E(x + 120, y + 105, 110, 92, 'body')
    hm = mask_of(head); std_fill(cv, hm, yel, 'body', angle=1.0)
    eyes = [(x + 80, y + 100), (x + 160, y + 96)]
    clear = np.zeros_like(hm)
    for ex, ey in eyes: clear |= (xx - ex) ** 2 + (yy - ey) ** 2 < 38 ** 2
    for k in range(-2, 3):   # 额头花纹往上走，碰到空地就停
        P = dens([(x + 120 + k * 22, y + 60), (x + 120 + k * 26, y + 20)])
        P = P[~clear[P[:, 1].astype(int), P[:, 0].astype(int)]]
        if len(P) > 2: std_line(cv, P, ink, 'detail')
    std_line(cv, head, ink, 'main')
    for (ex, ey), s in zip(eyes, (1.0, 0.85)):   # 一大一小
        w_ = E(ex, ey, 22 * s, 24 * s, 'small'); std_fill(cv, mask_of(w_), cream, 'small')
        pu = E(ex + 3, ey + 4, 11 * s, 12 * s, 'dot'); std_fill(cv, mask_of(pu), ink, 'dot')
        std_line(cv, w_, ink, 'part', w=(3, 5))
    std_line(cv, dens([(x + 108, y + 140), (x + 120, y + 150), (x + 134, y + 139)]), ink, 'detail')
    labels.append((x, y + 222, "五官最后画", "花纹停在眼周空地外"))

    # 5 四档线
    x, y = cell(1, 1)
    for n, k in enumerate(['main', 'part', 'detail', 'fine']):
        yy0 = y + 30 + n * 48
        P = dens([(x + 10, yy0), (x + 120, yy0 - 12), (x + 230, yy0 + 4)])
        std_line(cv, P + periodic_noise(len(P), r, 1.5)[:, None], ink, k, closed=False)
    labels.append((x, y + 222, "线 main / part", "detail / fine"))

    # 6 小件和实心点
    x, y = cell(1, 2)
    for n in range(3):
        s = E(x + 50 + n * 75, y + 70, 28, 28, 'small'); std_fill(cv, mask_of(s), [red, yel, blue][n], 'small'); std_line(cv, s, ink, 'detail')
        d = E(x + 50 + n * 75, y + 160, 12, 12, 'dot'); std_fill(cv, mask_of(d), ink, 'dot')
    labels.append((x, y + 222, "小件 small · wobble 2", "实心点 dot"))

    # 7 英文拟声词（推荐）
    x, y = cell(2, 0)
    hand_word(cv, 'POP!', x - 10, y + 150, 85, red, ink, r, wave=5)
    labels.append((x, y + 222, "拟声词首选英文", "作品里字高110–160（卡上缩小）"))

    # 8 留白规则示意
    x, y = cell(2, 1)
    std_line(cv, dens([(x + 10, y + 10), (x + 230, y + 10), (x + 230, y + 190), (x + 10, y + 190), (x + 10, y + 10)]), blue, 'fine')
    m = E(x + 120, y + 100, 70, 60, 'body'); std_fill(cv, mask_of(m), yel, 'body'); std_line(cv, m, ink, 'main')
    labels.append((x, y + 222, "四周至少露 40px 纸", "（蓝框只是示意画幅）"))

    sign_date(cv, 'OCT 20 2026', ink, red, r)

    im = Image.fromarray(np.clip(cv.img, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 22); f2 = ImageFont.truetype(FONT, 18)
    for x, y, a, b in labels:
        d.text((x, y), a, font=f, fill=(20, 20, 20)); d.text((x, y + 28), b, font=f2, fill=(90, 80, 70))
    d.text((60, 22), "手感基准对照卡 · 新作品画完和它并排看", font=f, fill=(20, 20, 20))
    im.save(out); print('saved', out)

if __name__ == '__main__': main()
