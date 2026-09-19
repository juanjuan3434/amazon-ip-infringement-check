# -*- coding: utf-8 -*-
"""zoom.py — 把用户提供的产品图/截图裁剪 + 放大 + 增强，用于看清肉眼在缩略图上
看不到的缝线、材质、模具线、图案。

为什么需要它：
  Amazon 主图常把「成品」和「内胆」叠在一起。内胆是光面 PVC（有模具同心环线、无缝合线），
  成品是织物外罩（有缝纫线、哑光织纹）。若不做放大判别，很容易把内胆的模具环线
  误判成外罩图案，进而错误命中「环带纹外观专利」，把风险分打高。

用法：
  python zoom.py <图片路径> [x0,y0,x1,y1 相对比例] [放大倍数]
  python zoom.py shot.jpg 0.46,0,1,0.46 5      # 取右上区域放大 5 倍

输出（与输入同目录）：
  zoom_colour.png  彩色放大图（判材质：光泽/织纹/缝合线）
  zoom_gray.png    灰度高对比图（判结构：缝线走向、分瓣、环线）
  如需再裁别处，改参数重跑即可。

依赖：Pillow（本机已随 managed Python 3.13 提供，PIL 12.x）
"""
import os
import sys

from PIL import Image, ImageEnhance, ImageOps


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    src = sys.argv[1]
    if len(sys.argv) > 2:
        bx = [float(v) for v in sys.argv[2].split(",")]
    else:
        bx = [0.0, 0.0, 1.0, 1.0]
    scale = int(sys.argv[3]) if len(sys.argv) > 3 else 4

    out = os.path.dirname(os.path.abspath(src))
    im = Image.open(src).convert("RGB")
    W, H = im.size
    box = (int(W * bx[0]), int(H * bx[1]), int(W * bx[2]), int(H * bx[3]))
    crop = im.crop(box)
    crop = crop.resize((crop.width * scale, crop.height * scale), Image.LANCZOS)
    crop = ImageEnhance.Sharpness(crop).enhance(1.6)
    crop.save(os.path.join(out, "zoom_colour.png"))

    g = ImageOps.grayscale(crop)
    g = ImageOps.autocontrast(g, cutoff=2)
    g = ImageEnhance.Contrast(g).enhance(2.2)
    g.save(os.path.join(out, "zoom_gray.png"))

    print("size=%dx%d box=%s scale=%d -> zoom_colour.png / zoom_gray.png" % (W, H, box, scale))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
