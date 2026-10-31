"""Parametric drawing: strokes, ellipses, and TrueType / SVG export."""

from __future__ import annotations

import math
from typing import Iterable, Sequence

from fontTools.pens.ttGlyphPen import TTGlyphPen

Pt = tuple[float, float]


def _v(a: Pt, b: Pt) -> Pt:
    return (b[0] - a[0], b[1] - a[1])


def _add(a: Pt, b: Pt) -> Pt:
    return (a[0] + b[0], a[1] + b[1])


def _mul(a: Pt, s: float) -> Pt:
    return (a[0] * s, a[1] * s)


def _len(a: Pt) -> float:
    return math.hypot(a[0], a[1])


def _norm(a: Pt) -> Pt:
    n = _len(a)
    if n < 1e-9:
        return (0.0, 0.0)
    return (a[0] / n, a[1] / n)


def _rot90(a: Pt) -> Pt:
    return (-a[1], a[0])


def _lerp(a: Pt, b: Pt, t: float) -> Pt:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _q(p: Pt) -> Pt:
    return (round(p[0], 2), round(p[1], 2))


def bezier_points(p0: Pt, p1: Pt, p2: Pt, p3: Pt, n: int = 18) -> list[Pt]:
    pts: list[Pt] = []
    for i in range(n + 1):
        t = i / n
        u = 1.0 - t
        x = u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


def quad_points(p0: Pt, p1: Pt, p2: Pt, n: int = 12) -> list[Pt]:
    pts: list[Pt] = []
    for i in range(n + 1):
        t = i / n
        u = 1.0 - t
        x = u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]
        y = u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


def signed_area(pts: Sequence[Pt]) -> float:
    a = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return a / 2.0


def force_winding(pts: list[Pt], clockwise: bool) -> list[Pt]:
    area = signed_area(pts)
    is_cw = area < 0
    if clockwise != is_cw:
        return list(reversed(pts))
    return pts


def arc_points(cx: float, cy: float, rx: float, ry: float, a0: float, a1: float, n: int | None = None) -> list[Pt]:
    a0 = math.radians(a0)
    a1 = math.radians(a1)
    da = a1 - a0
    if n is None:
        n = max(8, int(abs(da) * max(rx, ry) / 14.0))
    return [
        (cx + rx * math.cos(a0 + da * i / n), cy + ry * math.sin(a0 + da * i / n))
        for i in range(n + 1)
    ]


def ellipse_points(cx: float, cy: float, rx: float, ry: float, clockwise: bool = True) -> list[Pt]:
    n = max(24, int((rx + ry) * 0.22))
    # start at right, clockwise in y-up is decreasing angle
    pts = []
    for i in range(n):
        a = -2 * math.pi * i / n if clockwise else 2 * math.pi * i / n
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    return pts


def rounded_rect_points(x: float, y: float, w: float, h: float, r: float, clockwise: bool = True) -> list[Pt]:
    r = max(0.0, min(r, abs(w) / 2.0 - 0.1, abs(h) / 2.0 - 0.1))
    if w < 0:
        x, w = x + w, -w
    if h < 0:
        y, h = y + h, -h
    if r < 0.6:
        pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        return pts if clockwise else list(reversed(pts))
    pts: list[Pt] = []
    # clockwise y-up: BL round, BR, TR, TL
    pts += arc_points(x + r, y + r, r, r, 180, 270)
    pts += arc_points(x + w - r, y + r, r, r, 270, 360)
    pts += arc_points(x + w - r, y + h - r, r, r, 0, 90)
    pts += arc_points(x + r, y + h - r, r, r, 90, 180)
    return pts if clockwise else list(reversed(pts))


def _offset_polyline(points: Sequence[Pt], dist: float, closed: bool) -> list[Pt]:
    pts = list(points)
    if len(pts) < 2:
        return list(pts)
    # drop near-duplicates
    cleaned = [pts[0]]
    for p in pts[1:]:
        if _len(_v(cleaned[-1], p)) > 0.4:
            cleaned.append(p)
    pts = cleaned
    if len(pts) < 2:
        return pts
    n = len(pts)
    out: list[Pt] = []
    for i in range(n):
        if closed:
            prev = pts[i - 1]
            nxt = pts[(i + 1) % n]
        else:
            prev = pts[i - 1] if i > 0 else _add(pts[i], _v(pts[i + 1], pts[i]))
            nxt = pts[i + 1] if i < n - 1 else _add(pts[i], _v(pts[i - 1], pts[i]))
        d_in = _norm(_v(prev, pts[i]))
        d_out = _norm(_v(pts[i], nxt))
        n_in = _rot90(d_in)
        n_out = _rot90(d_out)
        nrm = _add(n_in, n_out)
        ln = _len(nrm)
        if ln < 0.12:
            nrm = n_out
            ln = _len(nrm) or 1.0
        nrm = _mul(nrm, 1.0 / ln)
        # miter cap
        dot = max(-0.999, min(0.999, n_in[0] * n_out[0] + n_in[1] * n_out[1]))
        miter = min(4.0, 1.0 / max(0.18, math.sqrt(0.5 * (1.0 + dot))))
        out.append(_add(pts[i], _mul(nrm, dist * miter)))
    return out


def stroke_contour(
    points: Sequence[Pt],
    thickness: float,
    closed: bool = False,
    cap: str = "round",
) -> list[Pt]:
    """Closed clockwise contour of a stroke around `points`."""
    r = thickness / 2.0
    pts = list(points)
    if len(pts) < 2:
        return []
    left = _offset_polyline(pts, r, closed)
    right = list(reversed(_offset_polyline(pts, -r, closed)))
    if closed:
        return left  # caller should also add the inner hole separately for rings
    cap_pts: list[Pt] = []
    # end cap at pts[-1]
    end = pts[-1]
    d = _norm(_v(pts[-2], pts[-1]))
    if cap == "round":
        n = max(6, int(r * 0.5))
        start_ang = math.atan2(_rot90(d)[1], _rot90(d)[0])
        cap_end = [
            (end[0] + r * math.cos(start_ang - math.pi * i / n), end[1] + r * math.sin(start_ang - math.pi * i / n))
            for i in range(1, n)
        ]
        start = pts[0]
        d0 = _norm(_v(pts[0], pts[1]))
        start_ang0 = math.atan2((-_rot90(d0)[1]), (-_rot90(d0)[0]))
        cap_start = [
            (start[0] + r * math.cos(start_ang0 - math.pi * i / n), start[1] + r * math.sin(start_ang0 - math.pi * i / n))
            for i in range(1, n)
        ]
        return left + cap_end + right + cap_start
    if cap == "square":
        left = left + [_add(left[-1], _mul(d, r)), _add(right[0], _mul(d, r))]
        d0 = _norm(_v(pts[0], pts[1]))
        right = right + [_add(right[-1], _mul(d0, -r)), _add(left[0], _mul(d0, -r))]
        return left + right
    return left + right


class Outline:
    def __init__(self, stem: float = 86.0, roundness: float = 0.2, corner: float = 0.0, serif: float = 0.0):
        self.stem = stem
        self.roundness = roundness
        self.corner = corner
        self.serif = serif
        self.contours: list[list[Pt]] = []  # each a closed ring, CW = fill

    def add(self, pts: Iterable[Pt], reverse: bool = False) -> None:
        seq = [_q(p) for p in pts]
        if len(seq) < 3:
            return
        if _len(_v(seq[0], seq[-1])) < 0.3:
            seq = seq[:-1]
        # reverse=True means a hole (counter-clockwise in y-up).
        # Fill contours are clockwise so overlapping fills union under non-zero winding.
        seq = force_winding(seq, clockwise=not reverse)
        self.contours.append(seq)

    def rect(self, x: float, y: float, w: float, h: float, r: float | None = None, hole: bool = False) -> None:
        if r is None:
            r = self.corner
        self.add(rounded_rect_points(x, y, w, h, r), reverse=hole)

    def vbar(self, x: float, y0: float, y1: float, t: float | None = None, r: float | None = None) -> None:
        t = self.stem if t is None else t
        lo, hi = (y0, y1) if y0 < y1 else (y1, y0)
        self.rect(x - t / 2.0, lo, t, hi - lo, r)

    def hbar(self, x0: float, x1: float, y: float, t: float | None = None, r: float | None = None) -> None:
        t = self.stem if t is None else t
        lo, hi = (x0, x1) if x0 < x1 else (x1, x0)
        self.rect(lo, y - t / 2.0, hi - lo, t, r)

    def disc(self, cx: float, cy: float, r: float, hole: bool = False) -> None:
        self.add(ellipse_points(cx, cy, r, r), reverse=hole)

    def oval(self, cx: float, cy: float, rx: float, ry: float, hole: bool = False) -> None:
        self.add(ellipse_points(cx, cy, rx, ry), reverse=hole)

    def ring(self, cx: float, cy: float, rx: float, ry: float, t: float | None = None) -> None:
        t = self.stem if t is None else t
        self.oval(cx, cy, rx, ry)
        ix, iy = max(8.0, rx - t), max(8.0, ry - t)
        if ix > 4 and iy > 4:
            self.oval(cx, cy, ix, iy, hole=True)

    def stroke(self, pts: Sequence[Pt], t: float | None = None, closed: bool = False, cap: str | None = None) -> None:
        t = self.stem if t is None else t
        if cap is None:
            cap = "round" if self.roundness >= 0.45 else ("square" if self.roundness < 0.2 else "round")
        if closed:
            outer = _offset_polyline(pts, t / 2.0, True)
            inner = _offset_polyline(pts, -t / 2.0, True)
            self.add(outer)
            self.add(inner, reverse=True)
            return
        self.add(stroke_contour(pts, t, closed=False, cap=cap))

    def arc(self, cx: float, cy: float, rx: float, ry: float, a0: float, a1: float, t: float | None = None, cap: str | None = None) -> None:
        self.stroke(arc_points(cx, cy, rx, ry, a0, a1), t=t, cap=cap)

    def curve(self, p0: Pt, p1: Pt, p2: Pt, p3: Pt, t: float | None = None, cap: str | None = None, n: int = 18) -> None:
        self.stroke(bezier_points(p0, p1, p2, p3, n=n), t=t, cap=cap)

    def path(self, pts: Sequence[Pt], t: float | None = None, cap: str | None = None) -> None:
        self.stroke(pts, t=t, cap=cap)

    def teardrop(self, cx: float, cy: float, r: float, pointing: str = "down") -> None:
        """Round blob terminal. A disc unions cleanly with stems."""
        self.disc(cx, cy, r)

    def slab_serif(self, x: float, y: float, direction: str, t: float | None = None) -> None:
        if self.serif <= 1:
            return
        t = self.stem if t is None else t
        s = self.serif
        h = max(18.0, t * 0.42)
        if direction == "left":
            self.rect(x - s, y - h / 2.0, s, h, r=min(4, h / 3))
        elif direction == "right":
            self.rect(x, y - h / 2.0, s, h, r=min(4, h / 3))
        elif direction == "bottom":
            self.rect(x - s / 2.0, y - h, s, h, r=min(4, h / 3))
        elif direction == "top":
            self.rect(x - s / 2.0, y, s, h, r=min(4, h / 3))

    def bounds(self) -> tuple[float, float, float, float]:
        xs: list[float] = []
        ys: list[float] = []
        for c in self.contours:
            for x, y in c:
                xs.append(x)
                ys.append(y)
        if not xs:
            return (0, 0, 0, 0)
        return (min(xs), min(ys), max(xs), max(ys))

    def translate(self, dx: float, dy: float) -> None:
        self.contours = [[(x + dx, y + dy) for x, y in c] for c in self.contours]

    def to_tt_glyph(self, glyph_order: list[str]):
        pen = TTGlyphPen(glyphSet=None)
        for cont in self.contours:
            if len(cont) < 3:
                continue
            pen.moveTo((int(round(cont[0][0])), int(round(cont[0][1]))))
            for x, y in cont[1:]:
                pen.lineTo((int(round(x)), int(round(y))))
            pen.closePath()
        return pen.glyph()

    def to_svg_d(self, sx: float = 1.0, sy: float = -1.0, ox: float = 0.0, oy: float = 0.0) -> str:
        parts: list[str] = []
        for cont in self.contours:
            if len(cont) < 3:
                continue
            x0, y0 = cont[0]
            parts.append(f"M{x0 * sx + ox:.1f} {y0 * sy + oy:.1f}")
            for x, y in cont[1:]:
                parts.append(f"L{x * sx + ox:.1f} {y * sy + oy:.1f}")
            parts.append("Z")
        return " ".join(parts)
