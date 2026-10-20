"""笨拙蜡笔波普 Clumsy Crayon Pop — 引擎。
先画歪，再涂花，最后印错一点点。
作品脚本 import 这个文件；系列规格：960×960、奶油纸 #F5EAD6、拟声词、角落手写日期。
"""
import sys, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

W, H = 960, 960
PAPER = '#F5EAD6'   # 全系列统一纸色

def hex2rgb(h):
    h = h.lstrip('#'); return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], float)

def lum(c): return 0.299*c[0] + 0.587*c[1] + 0.114*c[2]
def sat(c): return (c.max() - c.min()) / (c.max() + 1e-6)

def assign_roles(hexes):
    """自动分角色：最浅=纸，最深=轮廓，最艳=点睛，其余=主色块"""
    cs = [hex2rgb(h) for h in hexes]
    idx = list(range(len(cs)))
    paper = max(idx, key=lambda i: lum(cs[i])); idx.remove(paper)
    line = min(idx, key=lambda i: lum(cs[i])); idx.remove(line)
    accent = max(idx, key=lambda i: sat(cs[i]) * (0.5 + lum(cs[i]) / 510)); idx.remove(accent)
    return dict(paper=cs[paper], line=cs[line], accent=cs[accent], main=[cs[i] for i in idx])

# ---------------------------------------------------------------- noise / paper
class Canvas:
    def __init__(self, seed, paper, tooth=1.0):
        self.rng = np.random.default_rng(seed)
        r = self.rng
        n1 = ndi.gaussian_filter(r.random((H, W)), 0.8)
        n2 = ndi.gaussian_filter(r.random((H, W)), 2.5)
        fib = ndi.gaussian_filter(r.random((H, W)), (0.6, 4.0))   # 横向纸纤维
        h = (n1 - n1.mean()) / n1.std() * 0.55 + (n2 - n2.mean()) / n2.std() * 0.35 \
            + (fib - fib.mean()) / fib.std() * 0.3 * tooth
        self.tooth = 1 / (1 + np.exp(-h * 1.6))        # 0..1 纸面高度
        big = ndi.gaussian_filter(r.random((H, W)), 60)
        big = (big - big.min()) / (big.max() - big.min())
        self.img = np.ones((H, W, 3)) * paper * (0.97 + 0.04 * big[..., None])
        self.img *= (0.985 + 0.03 * self.tooth[..., None])
        self.layers = []   # (rgb, alpha) for misregistration later

    # ---------------------------------------------------------- deposit wax
    def deposit(self, acc, color, shift=(0, 0), keep=True):
        a = np.clip((acc * 0.62 + self.tooth - 0.92) / 0.16, 0, 1) * np.clip(acc / 0.25, 0, 1)
        if shift != (0, 0):
            a = np.roll(a, shift, axis=(0, 1))
        heavy = np.clip(acc - 1.2, 0, 1.5)[..., None]
        col = color[None, None, :] * (1 - 0.10 * heavy)            # 涂厚处颜色更浓
        col = col * (0.94 + 0.08 * self.tooth[..., None])
        self.img = self.img * (1 - a[..., None]) + col * a[..., None]
        return a

def periodic_noise(n, rng, amp, octaves=((2, 1.0), (3, 0.6), (5, 0.35), (9, 0.15))):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    out = np.zeros(n)
    for k, w in octaves:
        out += w * np.sin(k * t + rng.uniform(0, 2 * np.pi))
    return out * amp

def blob(pts, rng, wobble=10, n=360):
    """控制点 → 闭合 Catmull-Rom → 沿法向低频推挤，画歪"""
    P = np.array(pts, float); m = len(P)
    out = []
    per = n // m
    for i in range(m):
        p0, p1, p2, p3 = P[(i - 1) % m], P[i], P[(i + 1) % m], P[(i + 2) % m]
        for t in np.linspace(0, 1, per, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    C = np.array(out)
    d = np.roll(C, -1, 0) - np.roll(C, 1, 0)
    nrm = np.stack([d[:, 1], -d[:, 0]], 1); nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9
    C = C + nrm * periodic_noise(len(C), rng, wobble)[:, None]
    return C

def ellipse_pts(cx, cy, rx, ry, k=8, rot=0, rng=None, jit=0.08):
    pts = []
    for i in range(k):
        a = 2 * np.pi * i / k + rot
        j = 1 + (rng.uniform(-jit, jit) if rng is not None else 0)
        pts.append((cx + rx * j * math.cos(a), cy + ry * j * math.sin(a)))
    return pts

def mask_of(C):
    im = Image.new('L', (W, H), 0)
    ImageDraw.Draw(im).polygon([tuple(p) for p in C], fill=255)
    return np.asarray(im) > 127

# ---------------------------------------------------------- crayon fill
def crayon_fill(cv, mask, color, angle=0.6, density=1.0, coverage=0.8, edge_follow=True,
                overflow=0.25, passes=3, width=(3, 6), length=(18, 55), shift=(0, 0), heavy_spot=None):
    r = cv.rng
    ys, xs = np.nonzero(mask)
    if len(xs) == 0: return
    area = len(xs)
    dist = ndi.distance_transform_edt(mask)
    gy, gx = np.gradient(ndi.gaussian_filter(dist, 3))
    # 允许越界：只在噪声挑中的一两段
    ov_noise = ndi.gaussian_filter(r.random((H, W)), 40)
    ov_noise = (ov_noise - ov_noise.min()) / (ov_noise.max() - ov_noise.min())
    grow = ndi.binary_dilation(mask, iterations=10) & (ov_noise > 1 - overflow)
    allow = mask | grow
    acc = np.zeros((H, W))
    n = int(area / 260 * density)
    for p in range(passes):
        im = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(im)
        ang0 = angle + r.normal(0, 0.12)
        k = r.integers(0, len(xs), n)
        for i in k:
            x, y = xs[i], ys[i]
            if edge_follow and dist[y, x] < 22:
                a = math.atan2(gy[y, x], gx[y, x]) + math.pi / 2 + r.normal(0, 0.15)
                L = r.uniform(*length) * 0.8
            else:
                a = ang0 + r.normal(0, 0.18)
                L = r.uniform(*length)
            dx, dy = math.cos(a) * L / 2, math.sin(a) * L / 2
            pr = r.uniform(0.45, 1.0)
            wd = int(r.integers(width[0], width[1] + 1))
            # 来回涂：一笔带个小折返
            bend = r.normal(0, 3)
            dr.line([(x - dx, y - dy), (x + bend, y - bend), (x + dx, y + dy)], fill=int(90 * pr), width=wd)
        acc += np.asarray(im, float) / 90.0
    # 涂不满：低频覆盖率
    cov = ndi.gaussian_filter(r.random((H, W)), 25)
    cov = (cov - cov.mean()) / (cov.std() + 1e-9)
    acc *= np.clip(coverage + 0.18 * cov, 0.25, 1.3)
    if heavy_spot is not None:   # 反复涂的一处
        cx, cy, rad = heavy_spot
        yy, xx = np.ogrid[:H, :W]
        acc *= 1 + 0.9 * np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * rad ** 2))
    acc *= allow
    acc = ndi.gaussian_filter(acc, 0.6)
    return cv.deposit(acc, color, shift)

# ---------------------------------------------------------- crayon line
def crayon_line(cv, C, color, w=(5, 11), passes=2, gap=0.06, closed=True, jitter=2.5, shift=(0, 0)):
    r = cv.rng
    acc = np.zeros((H, W))
    C = np.asarray(C, float)
    N = len(C)
    for p in range(passes):
        im = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(im)
        off = r.normal(0, jitter, 2) * (1 if p else 0.3)
        wn = periodic_noise(N, r, 1.0, ((3, 1), (7, .5), (13, .3)))
        wn = (wn - wn.min()) / (np.ptp(wn) + 1e-9)
        start = r.integers(0, N); seglen = r.integers(25, 60)
        i = 0
        while i < N - (0 if closed else 1):
            if r.random() < gap and p == 0:          # 断口
                i += r.integers(4, 12); continue
            if p == 1 and r.random() < 0.55:         # 第二遍只描一部分（重描）
                i += r.integers(6, 20); continue
            j = min(i + r.integers(3, 8), N if closed else N - 1)
            seg = [tuple(C[k % N] + off + r.normal(0, 0.6, 2)) for k in range(i, j + 1)]
            wd = int(w[0] + (w[1] - w[0]) * wn[i % N])
            dr.line(seg, fill=int(r.uniform(70, 100)), width=max(2, wd), joint='curve')
            i = j
        acc += np.asarray(im, float) / 80.0
    acc = ndi.gaussian_filter(acc, 0.7)
    return cv.deposit(acc * 1.25, color, shift)

def stroke_path(cv, pts, color, w=(5, 9), passes=2, shift=(0, 0)):
    return crayon_line(cv, pts, color, w=w, passes=passes, gap=0.0, closed=False, shift=shift)

# ---------------------------------------------------------- halftone
def halftone(cv, mask, color, cell=16, angle=0.4, size_field=None, shift=(0, 0)):
    yy, xx = np.mgrid[:H, :W].astype(float)
    ca, sa = math.cos(angle), math.sin(angle)
    u = xx * ca + yy * sa; v = -xx * sa + yy * ca
    fu = (u % cell) - cell / 2; fv = (v % cell) - cell / 2
    d = np.sqrt(fu ** 2 + fv ** 2)
    rad = cell * 0.42 * (size_field if size_field is not None else 1.0)
    dot = np.clip((rad - d) / 1.2, 0, 1) * mask
    a = dot * np.clip((cv.tooth - 0.15) / 0.2, 0, 1)   # 印在纸上也会稍微吃纹
    if shift != (0, 0): a = np.roll(a, shift, axis=(0, 1))
    cv.img = cv.img * (1 - a[..., None]) + color[None, None, :] * a[..., None]


# ---------------------------------------------------------- 拟声词（字体只当骨架）
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, 'fonts', 'kuaile.ttf')
FONT_URL = 'https://github.com/google/fonts/raw/main/ofl/zcoolkuaile/ZCOOLKuaiLe-Regular.ttf'

def ensure_font():
    if not os.path.exists(FONT):
        import urllib.request
        os.makedirs(os.path.dirname(FONT), exist_ok=True)
        urllib.request.urlretrieve(FONT_URL, FONT)

def text_mask(txt, cx, cy, size, rot_deg, rng, wobble=4.0):
    """字体只拿来当骨架：栅格化 → 旋转 → 低频扭一扭，让字也画歪"""
    f = ImageFont.truetype(FONT, size)
    im = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(im)
    bb = d.textbbox((0, 0), txt, font=f)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]), txt, font=f, fill=255)
    im = im.rotate(rot_deg, center=(cx, cy), resample=Image.BILINEAR)
    a = np.asarray(im, float) / 255
    dy = ndi.gaussian_filter(rng.normal(0, 1, (H, W)), 18); dx = ndi.gaussian_filter(rng.normal(0, 1, (H, W)), 18)
    dy *= wobble / (dy.std() + 1e-9); dx *= wobble / (dx.std() + 1e-9)
    yy, xx = np.mgrid[:H, :W].astype(float)
    a = ndi.map_coordinates(a, [yy + dy, xx + dx], order=1)
    return a > 0.5


# ---------------------------------------------------------- 手写日期
GLY = {  # 手画日期字形，单位方格 0..1
    'O': None, 'C': 'C', 'T': [[(0, 0), (1, 0.02)], [(0.5, 0.01), (0.48, 1)]],
    '1': [[(0.25, 0.2), (0.55, 0), (0.52, 1)]],
    '9': None, '2': [[(0.05, 0.25), (0.35, 0), (0.85, 0.12), (0.8, 0.45), (0.05, 1), (0.95, 0.98)]],
    '0': None, '6': None,
}
def glyph(ch):
    th = np.linspace(0, 2 * np.pi, 30)
    if ch in 'O0': return [list(zip(0.5 + 0.48 * np.cos(th), 0.5 + 0.5 * np.sin(th)))]
    if ch == 'C': t = np.linspace(0.6, 2 * np.pi - 0.6, 24); return [list(zip(0.55 + 0.48 * np.cos(t), 0.5 + 0.5 * np.sin(t)))]
    if ch == '9':
        t = np.linspace(0, 2 * np.pi, 24); return [list(zip(0.5 + 0.4 * np.cos(t), 0.3 + 0.3 * np.sin(t))), [(0.9, 0.3), (0.85, 0.7), (0.35, 1)]]
    if ch == '6':
        t = np.linspace(np.pi, 3 * np.pi, 26); return [[(0.7, 0.0), (0.35, 0.15), (0.13, 0.5)] + list(zip(0.5 + 0.37 * np.cos(t), 0.66 + 0.33 * np.sin(t)))]
    return GLY[ch]

def dens(P, step=4):
    P = np.array(P, float); out = [P[0]]
    for a, b in zip(P[:-1], P[1:]):
        n = max(2, int(np.linalg.norm(b - a) / step))
        for t in np.linspace(0, 1, n)[1:]: out.append(a + (b - a) * t)
    return np.array(out)

def hand_text(cv, txt, x, base, h, col, shadow, r, w=(5, 7)):
    for ch in txt:
        if ch == ' ': x += h * 0.45; continue
        wid = h * 0.62 * r.uniform(0.9, 1.1); rot = r.normal(-0.05, 0.05); ca, sa = math.cos(rot), math.sin(rot)
        b = base + r.normal(0, 1.5)
        def T(p): u, v = p[0] * wid, (p[1] - 1) * h; return (x + u * ca - v * sa, b + u * sa + v * ca)
        for s in glyph(ch):
            P = dens([T(p) for p in s]); P = P + periodic_noise(len(P), r, 0.8)[:, None]
            stroke_path(cv, P + np.array([2, 2]), shadow, w=(2, 3), passes=1)
            stroke_path(cv, P, col, w=w, passes=1)
        x += wid + h * 0.22



# ---------------------------------------------------------- 手感基准（全系列统一，谁画都用这一套）
# 从 No.01–06 实际用过的参数里取的中位数。画的时候按部件大小选一档，
# 只在确有理由时改一两个数（写在注释里），别整套重调。
WOBBLE = {'bg': 14, 'body': 6, 'part': 3, 'small': 2, 'dot': 1}        # blob 歪多少
FILL = {
    'bg':    dict(density=1.2, coverage=0.92, passes=3, width=(3, 6), length=(25, 70), overflow=0.12),  # 背景大团
    'body':  dict(density=1.5, coverage=1.08, passes=3, width=(3, 6), length=(30, 80), overflow=0.05),  # 主体大色块
    'part':  dict(density=2.0, coverage=1.20, passes=3, width=(3, 6), length=(18, 55), overflow=0),     # 耳朵、衣服、叶子
    'small': dict(density=2.6, coverage=1.35, passes=2, width=(2, 4), length=(18, 55), overflow=0),     # 小物件、眼白、标签
    'dot':   dict(density=3.5, coverage=1.50, passes=3, width=(3, 5), length=(18, 55), overflow=0),     # 瞳孔、小洞、实心点
}
LINE = {
    'main':   dict(w=(5, 10), passes=2, gap=0.04),   # 主体外轮廓
    'part':   dict(w=(4, 7),  passes=2, gap=0.03),   # 部件轮廓
    'detail': dict(w=(3, 5),  passes=1, gap=0.0),    # 花纹、胡子、小线
    'fine':   dict(w=(2, 3),  passes=1, gap=0.0),    # 最细：叶脉、高光边
}
HALFTONE = dict(cell=12, angle=0.35, size=(0.3, 0.7))   # 网点：每张最多两处
MIS = (3, -3)                                            # 套色偏移，只给背景/一个色版
TEXT = dict(size=(100, 150), rot=(-8, 8), wobble=2.5, dilate=3, shadow=(6, 6))  # 中文拟声词
MARGIN = 40                                              # 四周至少露这么多奶油纸

def std_fill(cv, mask, color, kind='body', angle=0.6, **kw):
    """按基准档涂色：std_fill(cv, m, red, 'body', angle=1.1)"""
    p = dict(FILL[kind]); p.update(kw)
    return crayon_fill(cv, mask, color, angle=angle, **p)

def std_line(cv, C, color, kind='main', **kw):
    p = dict(LINE[kind]); p.update(kw)
    if kw.get('closed', True) is False or kind in ('detail', 'fine'):
        p.pop('gap', None); return stroke_path(cv, C, color, w=p['w'], passes=p['passes'], shift=p.get('shift', (0, 0)))
    return crayon_line(cv, C, color, **p)

def sign_date(cv, txt, ink, accent, r):
    """右下角日期签，位置大小全系列固定"""
    hand_text(cv, txt, 668, 948, 30, ink, accent, r, w=(5, 7))


# ---------------------------------------------------------- 英文拟声词（推荐）：手画大写字母
def _arc(cx, cy, rx, ry, a0, a1, n=24):
    t = np.linspace(a0, a1, n); return list(zip(cx + rx * np.cos(t), cy + ry * np.sin(t)))
LETTERS = {  # 单位方格，y 向下；(笔画列表, 宽度比例)
    'A': ([[(0, 1), (0.5, 0), (1, 1)], [(0.22, 0.62), (0.78, 0.62)]], 0.8),
    'B': ([[(0, 1), (0, 0), (0.55, 0), (0.82, 0.12), (0.8, 0.36), (0.5, 0.48), (0.02, 0.48)],
           [(0.5, 0.48), (0.88, 0.6), (0.9, 0.86), (0.6, 1), (0, 1)]], 0.72),
    'C': ([_arc(0.55, 0.5, 0.5, 0.5, -0.7, -2 * np.pi + 0.7)], 0.78),
    'D': ([[(0, 0), (0, 1)], [(0, 0), (0.45, 0)] + _arc(0.45, 0.5, 0.45, 0.5, -np.pi / 2, np.pi / 2, 18) + [(0, 1)]], 0.76),
    'E': ([[(0.85, 0), (0, 0), (0, 1), (0.88, 1)], [(0, 0.5), (0.7, 0.5)]], 0.66),
    'G': ([_arc(0.5, 0.5, 0.5, 0.5, -0.75, -2 * np.pi + 0.35, 30) + [(0.97, 0.58), (0.58, 0.58)]], 0.8),
    'H': ([[(0, 0), (0, 1)], [(1, 0), (1, 1)], [(0, 0.5), (1, 0.5)]], 0.76),
    'I': ([[(0.5, 0), (0.5, 1)]], 0.3),
    'K': ([[(0, 0), (0, 1)], [(0.9, 0), (0.05, 0.58)], [(0.32, 0.4), (0.95, 1)]], 0.72),
    'L': ([[(0, 0), (0, 1), (0.82, 1)]], 0.6),
    'M': ([[(0, 1), (0.05, 0), (0.5, 0.62), (0.95, 0), (1, 1)]], 0.92),
    'N': ([[(0, 1), (0, 0), (1, 1), (1, 0)]], 0.78),
    'O': ([_arc(0.5, 0.5, 0.5, 0.5, 0, 2 * np.pi, 32)], 0.82),
    'P': ([[(0, 1), (0, 0), (0.6, 0), (0.9, 0.15), (0.9, 0.38), (0.6, 0.52), (0.02, 0.52)]], 0.7),
    'R': ([[(0, 1), (0, 0), (0.6, 0), (0.88, 0.14), (0.88, 0.36), (0.6, 0.5), (0.02, 0.5)], [(0.42, 0.5), (0.92, 1)]], 0.72),
    'S': ([[(0.9, 0.12), (0.6, 0), (0.25, 0.02), (0.05, 0.2), (0.15, 0.42), (0.85, 0.58), (0.95, 0.8), (0.72, 1), (0.3, 1), (0.05, 0.88)]], 0.7),
    'T': ([[(0, 0), (1, 0.02)], [(0.5, 0.01), (0.48, 1)]], 0.76),
    'U': ([[(0, 0), (0, 0.65)] + _arc(0.5, 0.65, 0.5, 0.35, np.pi, 0, 16) + [(1, 0)]], 0.78),
    'W': ([[(0, 0), (0.22, 1), (0.5, 0.35), (0.78, 1), (1, 0)]], 1.0),
    'Y': ([[(0, 0), (0.5, 0.52), (1, 0)], [(0.5, 0.52), (0.5, 1)]], 0.76),
    'Z': ([[(0.02, 0), (0.95, 0.02), (0.05, 1), (1, 0.98)]], 0.72),
    '!': ([[(0.5, 0), (0.5, 0.66)]], 0.3),
    '?': ([[(0.08, 0.22), (0.3, 0.02), (0.72, 0.02), (0.92, 0.22), (0.85, 0.42), (0.5, 0.55), (0.5, 0.7)]], 0.66),
}
def hand_word(cv, txt, x, base, h, fill, ink, r, w=None, gap=None, wave=10, tilt=0.04):
    """英文拟声词：黑粗线打底 + 彩色细线压上 + 右下错位黑影（同 No.05 RRRING!）。
    h=字高(推荐 110–160)，fill=字芯颜色(点睛色)，ink=最深色。返回最后的 x。"""
    k = h / 120.0
    w = w or (int(32 * k), int(36 * k)); wi = (int(17 * k), int(21 * k)); sh = int(8 * k)
    gap = gap if gap is not None else 26 * k
    n = len(txt)
    for i, ch in enumerate(txt.upper()):
        if ch == ' ': x += h * 0.4; continue
        strokes, wr = LETTERS[ch]
        w_ = h * wr; rot = r.normal(0, 0.06) + tilt * (i - n / 2); hh = h * (1 + 0.04 * (i - n / 2))
        ca, sa = math.cos(rot), math.sin(rot); b = base + wave * math.sin(i * 1.1)
        def T(p): u, v = p[0] * w_, (p[1] - 1) * hh; return (x + u * ca - v * sa, b + u * sa + v * ca)
        for st in strokes:
            P = dens([T(p) for p in st]); P = P + periodic_noise(len(P), r, 1.2)[:, None]
            stroke_path(cv, P + sh, ink, w=(w[0] - 2, w[1] - 2), passes=1)
            stroke_path(cv, P, ink, w=w, passes=1)
            stroke_path(cv, P, fill, w=wi, passes=2)
        if ch in '!?':
            d = T((0.5, 0.92)); dot = blob(ellipse_pts(d[0], d[1], 15 * k, 15 * k, 6, 0, r, 0.05), r, wobble=0.8, n=60)
            crayon_fill(cv, mask_of(dot), ink, density=4, coverage=1.6, passes=2, overflow=0)
        x += w_ + gap
    return x
