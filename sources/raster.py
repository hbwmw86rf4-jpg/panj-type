"""Shape Gurmukhi with HarfBuzz and rasterize glyph outlines."""

from __future__ import annotations

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw
import uharfbuzz as hb


def shape(path: str, text: str, font_upm: int = 1000):
    blob = hb.Blob.from_file_path(path)
    face = hb.Face(blob)
    font = hb.Font(face)
    font.scale = (font_upm, font_upm)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf)
    return list(buf.glyph_infos), list(buf.glyph_positions), font_upm


def _glyph_polygons(tt: TTFont, gid: int) -> list[list[tuple[int, int]]]:
    glyf = tt["glyf"]
    name = tt.getGlyphOrder()[gid]
    g = glyf[name]
    if g.isComposite() or g.numberOfContours == 0:
        return []
    coords, end_pts, flags = g.coordinates, g.endPtsOfContours, g.flags
    polys = []
    start = 0
    for end in end_pts:
        pts = [(int(coords[i][0]), int(coords[i][1])) for i in range(start, end + 1)]
        polys.append(pts)
        start = end + 1
    return polys


def draw_text(
    path: str,
    text: str,
    *,
    size: int = 72,
    fill: str = "#1c1915",
    canvas: Image.Image | None = None,
    origin: tuple[int, int] = (40, 40),
    width: int | None = None,
) -> Image.Image:
    tt = TTFont(path)
    infos, positions, upm = shape(path, text)
    scale = size / upm
    # measure
    pen_x = 0
    min_y, max_y = 0, 0
    for pos in positions:
        pen_x += pos.x_advance
    adv = pen_x
    # generous vertical
    if canvas is None:
        w = width or int(adv * scale) + origin[0] + 40
        h = int(size * 1.8) + origin[1]
        canvas = Image.new("RGB", (w, h), "#f7f4ee")
    d = ImageDraw.Draw(canvas)
    x, y_base = origin[0], origin[1] + int(size * 1.05)
    pen_x = pen_y = 0
    for info, pos in zip(infos, positions):
        gx = x + (pen_x + pos.x_offset) * scale
        gy = y_base - (pen_y + pos.y_offset) * scale
        for poly in _glyph_polygons(tt, info.codepoint):
            if len(poly) < 3:
                continue
            screen = [(gx + p[0] * scale, gy - p[1] * scale) for p in poly]
            d.polygon(screen, fill=fill)
        pen_x += pos.x_advance
        pen_y += pos.y_advance
    return canvas
