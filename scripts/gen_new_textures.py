"""Generates 6 new preset displacement textures (metal x2, ceramic, fabric,
stone, concrete) to extend the built-in preset library. One-off script, not
part of the build; run manually then delete/ignore.
"""
import math
import random

from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageOps

OUT = "assets/textures"
SIZE = 512


def tileable_blur(im, radius):
    """Gaussian-blur `im` as if it repeats infinitely (torus), so the result
    still tiles with no seam at the edges."""
    w, h = im.size
    canvas = Image.new(im.mode, (w * 3, h * 3))
    for jy in range(3):
        for jx in range(3):
            canvas.paste(im, (jx * w, jy * h))
    canvas = canvas.filter(ImageFilter.GaussianBlur(radius))
    return canvas.crop((w, h, 2 * w, 2 * h))


def vertical_box_blur(im, taps):
    """Directional (y-only) blur via averaging toroidal y-offsets — keeps
    horizontal grain crisp while softening vertical banding. Seamless."""
    w, h = im.size
    out = Image.new("L", (w, h))
    opx = out.load()
    n = 2 * taps + 1
    shifts = [ImageChops.offset(im, 0, dy).load() for dy in range(-taps, taps + 1)]
    for y in range(h):
        for x in range(w):
            s = 0
            for sp in shifts:
                s += sp[x, y]
            opx[x, y] = s // n
    return out


def save(name, im, quality=90):
    path = f"{OUT}/{name}"
    if name.lower().endswith(".jpg") or name.lower().endswith(".jpeg"):
        im.convert("RGB").save(path, quality=quality)
    else:
        im.convert("RGBA").save(path)
    print("wrote", path, im.size)


# ── 1. Brushed Metal ─────────────────────────────────────────────────────────
def gen_brushed_metal():
    rnd = random.Random(1)
    w = h = SIZE
    im = Image.new("L", (w, h))
    px = im.load()
    # Broad low-frequency swaths (tileable: integer periods over w).
    terms = [(rnd.randint(1, 4), rnd.uniform(0, math.tau), rnd.uniform(6, 18))
             for _ in range(5)]
    for x in range(w):
        base = 150.0
        for k, phase, amp in terms:
            base += amp * math.sin(2 * math.pi * k * x / w + phase)
        for y in range(h):
            px[x, y] = int(max(0, min(255, base)))
    # Per-row grain jitter (thousands of independent rows -> fine horizontal
    # streaks, inherently seamless since rows are self-contained).
    im2 = Image.new("L", (w, h))
    p2 = im2.load()
    for y in range(h):
        jitter = rnd.uniform(-22, 22)
        for x in range(w):
            p2[x, y] = int(max(0, min(255, px[x, y] + jitter)))
    im = vertical_box_blur(im2, 1)
    # Sparse bright scratch streaks.
    draw = ImageDraw.Draw(im)
    for _ in range(900):
        y = rnd.randint(0, h - 1)
        x0 = rnd.randint(0, w - 1)
        length = rnd.randint(10, 90)
        shade = rnd.randint(190, 255) if rnd.random() < 0.7 else rnd.randint(20, 60)
        for dx in range(length):
            xx = (x0 + dx) % w
            cur = im.getpixel((xx, y))
            im.putpixel((xx, y), int((cur + shade) / 2))
    save("metalBrushed.jpg", im)


# ── 2. Diamond Plate ─────────────────────────────────────────────────────────
def gen_diamond_plate():
    w = h = SIZE
    cell = 64
    cols = w // cell
    rows = h // cell
    im = Image.new("L", (w, h), 60)
    draw = ImageDraw.Draw(im)
    rw, rh = cell * 0.34, cell * 0.62
    for ry in range(rows):
        offset = (cell // 2) if (ry % 2) else 0
        for rc in range(-1, cols + 1):
            cx = (rc * cell + offset + cell // 2) % w
            cy = ry * cell + cell // 2
            pts = [
                (cx, cy - rh / 2),
                (cx + rw / 2, cy),
                (cx, cy + rh / 2),
                (cx - rw / 2, cy),
            ]
            # Beveled diamond boss: light half (upper-left) + dark half
            # (lower-right) for a raised-3D read.
            draw.polygon(pts, fill=170)
            lit = [pts[3], pts[0], pts[1]]
            draw.polygon(lit, fill=235)
            shadow = [pts[1], pts[2], pts[3]]
            draw.polygon(shadow, fill=95)
            if cx - rw / 2 - cell < w and cx + rw / 2 + cell > 0:
                pass
    # Wrap-safe redraw for the seam columns (rc spans -1..cols already covers
    # both edges via modulo on cx).
    im = tileable_blur(im, 0.6)
    save("diamondPlate.jpg", im)


# ── 3. Ceramic Tile ──────────────────────────────────────────────────────────
def gen_ceramic_tile():
    w = h = SIZE
    cell = 128
    grout = 10
    im = Image.new("L", (w, h), 15)
    draw = ImageDraw.Draw(im)
    cols = w // cell
    rows = h // cell
    for ry in range(rows):
        for rc in range(cols):
            x0, y0 = rc * cell, ry * cell
            x1, y1 = x0 + cell - grout, y0 + cell - grout
            draw.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=225)
            # glossy corner highlight
            draw.rounded_rectangle([x0 + 3, y0 + 3, x1 - 3, y0 + cell * 0.28],
                                    radius=5, fill=250)
            # bottom-right bevel shadow
            draw.line([x0, y1, x1, y1], fill=170, width=2)
            draw.line([x1, y0, x1, y1], fill=170, width=2)
    save("ceramicTile.png", im)


# ── 4. Canvas Fabric ─────────────────────────────────────────────────────────
def gen_canvas_fabric():
    w = h = SIZE
    thread = 16
    im = Image.new("L", (w, h), 40)
    draw = ImageDraw.Draw(im)
    cols = w // thread
    rows = h // thread
    for ry in range(rows):
        for rc in range(cols):
            over = (rc + ry) % 2 == 0
            x0, y0 = rc * thread, ry * thread
            x1, y1 = x0 + thread, y0 + thread
            base = 205 if over else 130
            draw.rectangle([x0, y0, x1, y1], fill=base)
            # thread rounding: brighter center line, darker seam edges
            if over:
                draw.rectangle([x0 + 2, y0, x1 - 2, y1], fill=225)
                draw.line([x0, y0, x0, y1], fill=150, width=2)
                draw.line([x1 - 1, y0, x1 - 1, y1], fill=150, width=2)
            else:
                draw.rectangle([x0, y0 + 2, x1, y1 - 2], fill=150)
                draw.line([x0, y0, x1, y0], fill=90, width=2)
                draw.line([x0, y1 - 1, x1, y1 - 1], fill=90, width=2)
    im = tileable_blur(im, 0.5)
    save("canvasFabric.png", im)


# ── 5. Flagstone ──────────────────────────────────────────────────────────────
def gen_flagstone():
    rnd = random.Random(7)
    w = h = SIZE
    im = Image.new("L", (w, h), 20)
    draw = ImageDraw.Draw(im)
    row_h = 128
    rows = h // row_h
    for ry in range(rows):
        y0 = ry * row_h
        y1 = y0 + row_h
        x = 0
        cells = []
        while x < w:
            cw = rnd.randint(90, 190)
            cells.append(cw)
            x += cw
        # rescale so the row sums exactly to w (keeps horizontal tiling clean)
        scale = w / sum(cells)
        x = 0.0
        xs = [0.0]
        for cw in cells:
            x += cw * scale
            xs.append(x)
        for i in range(len(cells)):
            x0, x1 = xs[i], xs[i + 1]
            jitter = row_h * 0.12
            pts = [
                (x0 + rnd.uniform(2, 6), y0 + rnd.uniform(0, jitter)),
                (x1 - rnd.uniform(2, 6), y0 + rnd.uniform(0, jitter)),
                (x1 - rnd.uniform(2, 6), y1 - rnd.uniform(0, jitter)),
                (x0 + rnd.uniform(2, 6), y1 - rnd.uniform(0, jitter)),
            ]
            shade = rnd.randint(150, 205)
            draw.polygon(pts, fill=shade)
    # mottle each stone with soft noise, then re-cut grout lines on top
    noise = Image.effect_noise((w, h), 40)
    noise = tileable_blur(noise, 2.0)
    im = Image.blend(im.convert("L"), ImageChops.multiply(im, noise), 0.35)
    save("flagstone.jpg", im, quality=88)


# ── 6. Concrete ──────────────────────────────────────────────────────────────
def gen_concrete():
    rnd = random.Random(3)
    w = h = SIZE
    base = Image.effect_noise((w, h), 24)
    base = tileable_blur(base, 3.0)
    base = ImageOps.autocontrast(base, cutoff=1)
    # remap into a narrow mid-gray band
    lut = [int(120 + (v / 255.0) * 70) for v in range(256)]
    base = base.point(lut)
    im = base.copy()
    draw = ImageDraw.Draw(im)
    grid = 24
    for gy in range(0, h, grid):
        for gx in range(0, w, grid):
            if rnd.random() < 0.55:
                continue
            cx = gx + rnd.uniform(2, grid - 2)
            cy = gy + rnd.uniform(2, grid - 2)
            r = rnd.uniform(1.5, 4.5)
            shade = rnd.randint(60, 235)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=shade)
    im = tileable_blur(im, 0.4)
    save("concreteAggregate.jpg", im, quality=88)


if __name__ == "__main__":
    gen_brushed_metal()
    gen_diamond_plate()
    gen_ceramic_tile()
    gen_canvas_fabric()
    gen_flagstone()
    gen_concrete()
