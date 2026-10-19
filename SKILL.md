---
name: clumsy-crayon-pop
description: 蜡笔质感 × 波普配色——用 Python 一笔一笔撒出来的笨拙波普画。触发词：蜡笔波普、波普蜡笔、clumsy pop
---

# clumsy-crayon-pop —— 笨拙蜡笔波普

不是滤镜，不是生图模型。每一道笔触是一条短线，沿线撒几十个小圆点——颜色抖一抖、
透明度随机、位置歪一点，叠上去就是油画棒蹭纸的颗粒。配色走波普正典：高饱和撞色、
粗黑轮廓、平涂色块、留白高光。笨拙（clumsy）是态度：形要歪，线要抖，规整的是排版，歪的才是画。

依赖：`pip install pillow numpy`。Linux 上中文显示成方块是缺中文字体，装个 Noto CJK 或指定 `C.FONT_CJK`。

## 配色（5 组）

机器可读版：`palettes/palettes.json`。用法：深色打轮廓，亮色平涂，留白做高光。

**1. 玛丽莲·沃霍尔** —— 高饱和撞色平涂，暗夜紫只压轮廓和阴影，蜡笔多叠两层才够艳
电光粉 #FF2E88 · 柠檬黄 #FFE14D · 湖水青 #00C2D1 · 樱桃红 #E63946 · 暗夜紫 #2B2B3A

**2. 漫画网点·利希滕斯坦** —— 红黄蓝三原色 + 粗黑线是本体，米纸白留出来当网点高光
三原红 #E63946 · 三原黄 #FFD500 · 三原蓝 #1D6FE0 · 墨黑 #141414 · 米纸白 #F5F0E6

**3. 迷幻六十年代** —— 相邻色互相咬，奶油色只做小面积透气，别让画面糊成一团
橘子汽水 #FF7B00 · 品红 #E5007D · 酸性柠檬 #B8D800 · 电紫 #7B2FF7 · 奶油 #FFF3D6

**4. 霓虹波普** —— 深海军蓝打底越深越好，荧光色蜡笔轻涂两遍就有发光感
霓虹粉 #FF2E9A · 电光蓝 #00A8FF · 荧光黄 #E8FF47 · 深海军蓝 #0D1B4C · 纯白 #FFFFFF

**5. 复古波普** —— 低饱和暖色系，巧克力棕当轮廓线，比纯黑更复古
烫橙 #CC5500 · 芥末黄 #E1AD01 · 复古青 #008B8B · 巧克力棕 #5C3317 · 奶油 #F5E6C8

## 波普画法（在蜡笔引擎之上）

引擎：`crayon/crayon_lib.py`（函数说明见下）。波普和普通蜡笔的区别就五条：

1. **色块要实**：`crayon` 的 `alpha=(170,250)`，`soft_mask` 的 `feather` 收小（2–4），颜色才"跳"。
2. **粗黑轮廓**：主体描边 `crayon_line(pts, 黑, width=(2.5,4.0), alpha=(200,255))`，线要抖（wobble 1.2）。
3. **网点**：半调网点当阴影/背景——小圆点排成网格，`alpha=(60,120)`，疏密表现明暗。
4. **重复**：Warhol 式多格，同一主体换底色，2×2 或 3 格横排。
5. **留白**：高光和纸缝别涂死，`scribble` 划几道就行。

蜡笔三条老规矩照旧：**不临摹；每张里有一句是自己的**（底下那行手写）；**歪着画**（`quad` 歪、`wobbly_text` 逐字歪、`squiggle` 弯指线）。

## 引擎函数速查

| 函数 | 波普用法 |
|---|---|
| `soft_mask(polygon, feather, grow)` | 色块蒙版；波普 feather 2–4，grow 1–2（边缘利落） |
| `crayon(base, mask, color, direction, spread, n, length, dot, alpha, jitter)` | 平涂撒颗粒；波普 alpha (170,250)，n 按面积给足 |
| `crayon_line(base, pts, color, width, alpha, wobble)` | 粗黑轮廓 / 胡须 / 网点线；轮廓 width (2.5,4.0) |
| `blob(cx, cy, rx, ry, k, rough)` | 不规则椭圆主体；返回多边形点列，可直接描边 |
| `poly_rect(x0,y0,x1,y1,wobble)` | 抖过的矩形；多格画布的格子 |
| `wobbly_text(base, text, xy, font, color, rot, bounce)` | 拟声词 / 标题逐字歪；波普标题 rot 10 bounce 5 |
| `scribble(base, mask, color, n, length, direction)` | 色块上随手划几道，蜡笔涂过的痕迹 |
| `paper_grain(img, strength)` | 纸纹最后一步，0.08–0.10 |

## 主题

见 `themes.md`：午夜便利店、罐头与泡面、月份牌女郎·波普版、猫猫大头照、显像管电视机、可爱恐怖小物。
每个主题标注了推荐配色和构图要点。

## 工作流

1. 选配色（5 组里挑一组，别混）。
2. 选主题（`themes.md` 里挑，或按"3–7 个形 + 一个亮点"自己编）。
3. 写脚本：坐标全写成 `P = {...}` 字典；`random.seed` 固定。
4. 跑（几秒一张），**看图**：颜色够不够跳、轮廓够不够粗、字读不读得清。
5. 两版内改完。范例：`examples/pop_cat_4panel.py`。

## 署名

- 概念 绮思 · 代码 雾染 · 蜡笔引擎 绮思 & Hark 独立研究
