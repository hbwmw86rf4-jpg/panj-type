"""Original Gurmukhi constructions. Traditional skeleton, parametric flesh."""

from __future__ import annotations

from dataclasses import dataclass, field

from geom import Outline
from style import BASE, HEAD, Style


@dataclass
class GlyphOut:
    name: str
    unicodes: list[int]
    outline: Outline
    advance: float
    anchors: dict[str, tuple[float, float]] = field(default_factory=dict)
    gdef: str = "base"  # base | mark | ligature


def _o(s: Style) -> Outline:
    return Outline(stem=s.stem, roundness=s.roundness, corner=s.corner, serif=s.serif)


class Box:
    def __init__(self, s: Style, body: float = 540.0):
        self.s = s
        self.body = body * s.width
        if s.mono:
            self.adv = s.mono_width
            self.left = (self.adv - self.body) / 2.0
        else:
            self.left = s.side * (0.7 if s.condensed else 1.0)
            self.adv = self.left + self.body + s.side * (0.7 if s.condensed else 1.0)
        self.right = self.left + self.body
        self.head = HEAD
        self.base = BASE
        self.mid = (HEAD + BASE) * 0.5
        self.stem_t = s.stem
        self.bar_t = s.bar
        self.hstem = s.hstem
        self.stem_x = self.right - s.stem / 2.0
        self.r = s.cap_radius

    def headline(self, o: Outline, x0: float | None = None, x1: float | None = None) -> None:
        x0 = self.left if x0 is None else x0
        x1 = self.right if x1 is None else x1
        o.hbar(x0, x1, self.head, t=self.bar_t, r=min(self.s.corner, self.bar_t / 2))
        if self.s.serif > 20:
            o.slab_serif(x0, self.head, "left", t=self.bar_t)
            o.slab_serif(x1, self.head, "right", t=self.bar_t)

    def stem(self, o: Outline, y0: float | None = None, y1: float | None = None, x: float | None = None) -> None:
        y0 = self.base if y0 is None else y0
        y1 = self.head if y1 is None else y1
        x = self.stem_x if x is None else x
        o.vbar(x, y0, y1, t=self.stem_t, r=self.s.corner)
        if self.s.serif > 20:
            o.slab_serif(x, y0, "bottom", t=self.stem_t)

    def anchors(self, extra: dict | None = None) -> dict[str, tuple[float, float]]:
        a = {
            "above": (self.left + self.body * 0.52, self.head + self.bar_t * 0.5 + 36),
            "below": (self.left + self.body * 0.52, self.base - 28),
            "post": (self.right + 8, self.mid),
        }
        if extra:
            a.update(extra)
        return a


def _cap(s: Style) -> str:
    return "round" if s.roundness >= 0.4 else "square"


# ---------------------------------------------------------------------------
# Shared bowls
# ---------------------------------------------------------------------------

def _open_c(o: Outline, b: Box, cx: float, cy: float, rx: float, ry: float, a0: float, a1: float, t: float | None = None) -> None:
    o.arc(cx, cy, rx, ry, a0, a1, t=t or b.stem_t, cap=_cap(b.s))


def _loop_left_of_stem(o: Outline, b: Box, cy: float, rx: float, ry: float, open_gap: float = 0.0) -> None:
    """Oval loop that kisses the right stem."""
    cx = b.stem_x - rx * 0.72
    t = b.stem_t
    if open_gap > 0:
        o.arc(cx, cy, rx, ry, 110, 430 - open_gap, t=t, cap=_cap(b.s))
    else:
        o.ring(cx, cy, rx, ry, t=t)


# ---------------------------------------------------------------------------
# Consonants
# ---------------------------------------------------------------------------

def g_ka(s: Style) -> GlyphOut:
    b, o = Box(s, 560), _o(s)
    b.headline(o)
    b.stem(o, y0=b.base + 24)
    cx = b.stem_x - b.body * 0.28
    cy = b.head * 0.50
    # open loop that the stem closes — classic ka
    o.arc(cx, cy, b.body * 0.32, b.head * 0.27, 100, 445, t=b.stem_t, cap=_cap(s))
    return GlyphOut("ka", [0x0A15], o, b.adv, b.anchors())


def g_kha(s: Style) -> GlyphOut:
    b, o = Box(s, 560), _o(s)
    b.headline(o)
    b.stem(o)
    cx, cy = b.left + b.body * 0.36, b.head * 0.48
    _open_c(o, b, cx, cy, b.body * 0.34, b.head * 0.34, 125, 400)
    o.stroke(
        [(cx - b.body * 0.06, cy + b.head * 0.12), (b.stem_x - b.stem_t, cy - 8)],
        t=b.hstem,
        cap=_cap(s),
    )
    return GlyphOut("kha", [0x0A16], o, b.adv, b.anchors())


def g_ga(s: Style) -> GlyphOut:
    b, o = Box(s, 540), _o(s)
    b.headline(o)
    b.stem(o, y0=b.base + 40)
    _open_c(o, b, b.left + b.body * 0.32, b.head * 0.50, b.body * 0.30, b.head * 0.34, 125, 300)
    return GlyphOut("ga", [0x0A17], o, b.adv, b.anchors())


def g_gha(s: Style) -> GlyphOut:
    b, o = Box(s, 620), _o(s)
    b.headline(o, x0=b.left + b.body * 0.08)
    b.stem(o)
    # two hanging bowls, B-like
    t = b.stem_t
    y1, y2 = b.head * 0.68, b.head * 0.32
    rx, ry = b.body * 0.22, b.head * 0.20
    for cx, cy in ((b.left + b.body * 0.30, y1), (b.left + b.body * 0.48, y2)):
        _open_c(o, b, cx, cy, rx, ry, 200, 480, t=t)
    o.hbar(b.left + b.body * 0.22, b.stem_x, b.mid, t=b.hstem)
    return GlyphOut("gha", [0x0A18], o, b.adv, b.anchors())


def g_nga(s: Style) -> GlyphOut:
    b, o = Box(s, 500), _o(s)
    b.headline(o)
    cx, cy = b.left + b.body * 0.50, b.head * 0.46
    _open_c(o, b, cx, cy + 70, b.body * 0.30, b.head * 0.16, 200, 340)
    _open_c(o, b, cx, cy - 80, b.body * 0.34, b.head * 0.22, 20, 200)
    o.vbar(b.left + b.body * 0.72, cy - 40, cy + 50, t=b.stem_t * 0.9)
    return GlyphOut("nga", [0x0A19], o, b.adv, b.anchors())


def g_ca(s: Style) -> GlyphOut:
    b, o = Box(s, 540), _o(s)
    b.headline(o)
    b.stem(o, y0=b.base + 50)
    cx, cy = b.left + b.body * 0.42, b.head * 0.46
    _open_c(o, b, cx, cy, b.body * 0.34, b.head * 0.34, 200, 420)
    o.teardrop(b.left + b.body * 0.22, cy + b.head * 0.16, b.stem_t * 0.42, "left")
    return GlyphOut("ca", [0x0A1A], o, b.adv, b.anchors())


def g_cha(s: Style) -> GlyphOut:
    b, o = Box(s, 540), _o(s)
    b.headline(o)
    b.stem(o, y0=b.mid)
    cx = b.left + b.body * 0.42
    o.ring(cx, b.head * 0.62, b.body * 0.28, b.head * 0.14, t=b.stem_t * 0.95)
    o.ring(cx, b.head * 0.28, b.body * 0.30, b.head * 0.18, t=b.stem_t * 0.95)
    o.hbar(cx - b.body * 0.18, b.stem_x, b.head * 0.46, t=b.hstem)
    return GlyphOut("cha", [0x0A1B], o, b.adv, b.anchors())


def g_ja(s: Style) -> GlyphOut:
    b, o = Box(s, 540), _o(s)
    b.headline(o)
    b.stem(o)
    lx = b.left + b.body * 0.22
    o.vbar(lx, b.base, b.mid + 40, t=b.stem_t)
    o.hbar(lx, b.stem_x, b.mid + 8, t=b.hstem)
    o.teardrop(lx - b.stem_t * 0.15, b.mid + 8, b.stem_t * 0.48, "left")
    if s.serif > 20:
        o.slab_serif(lx, b.base, "bottom")
    return GlyphOut("ja", [0x0A1C], o, b.adv, b.anchors())


def g_jha(s: Style) -> GlyphOut:
    g = g_ja(s)
    g.name, g.unicodes = "jha", [0x0A1D]
    b = Box(s, 540)
    g.outline.arc(b.left + b.body * 0.30, b.head + 36, b.body * 0.18, 52, 200, 20, t=s.hstem)
    return g


def g_nya(s: Style) -> GlyphOut:
    b, o = Box(s, 620), _o(s)
    b.headline(o)
    o.vbar(b.left + b.body * 0.28, b.base + 40, b.head, t=b.stem_t)
    o.vbar(b.stem_x, b.base + 40, b.head, t=b.stem_t)
    o.hbar(b.left + b.body * 0.28, b.stem_x, b.mid, t=b.hstem)
    _open_c(o, b, b.left + b.body * 0.18, b.head * 0.32, b.body * 0.16, b.head * 0.20, 40, 200)
    return GlyphOut("nya", [0x0A1E], o, b.adv, b.anchors())


def g_tta(s: Style) -> GlyphOut:
    b, o = Box(s, 540), _o(s)
    b.headline(o)
    o.vbar(b.stem_x, b.mid + 20, b.head, t=b.stem_t)
    _open_c(o, b, b.left + b.body * 0.46, b.head * 0.38, b.body * 0.38, b.head * 0.32, 200, 40)
    return GlyphOut("tta", [0x0A1F], o, b.adv, b.anchors())


def g_ttha(s: Style) -> GlyphOut:
    b, o = Box(s, 520), _o(s)
    b.headline(o)
    o.vbar((b.left + b.right) / 2.0, b.mid + 40, b.head, t=b.stem_t)
    o.ring((b.left + b.right) / 2.0, b.head * 0.38, b.body * 0.36, b.head * 0.30, t=b.stem_t)
    return GlyphOut("ttha", [0x0A20], o, b.adv, b.anchors())


def g_dda(s: Style) -> GlyphOut:
    b, o = Box(s, 540), _o(s)
    b.headline(o)
    cx = b.left + b.body * 0.50
    _open_c(o, b, cx, b.head * 0.62, b.body * 0.28, b.head * 0.14, 200, 20)
    _open_c(o, b, cx - 10, b.head * 0.30, b.body * 0.34, b.head * 0.22, 30, 230)
    o.vbar(b.stem_x, b.mid, b.head, t=b.stem_t * 0.9)
    return GlyphOut("dda", [0x0A21], o, b.adv, b.anchors())


def g_ddha(s: Style) -> GlyphOut:
    g = g_dda(s)
    g.name, g.unicodes = "ddha", [0x0A22]
    b = Box(s, 540)
    g.outline.disc(b.left + b.body * 0.42, b.head * 0.34, s.stem * 0.28)
    return g


def g_nna(s: Style) -> GlyphOut:
    b, o = Box(s, 540), _o(s)
    b.headline(o)
    # diagonal from headline into a C
    o.stroke(
        [
            (b.stem_x - 20, b.head - b.bar_t),
            (b.left + b.body * 0.42, b.mid + 20),
            (b.left + b.body * 0.28, b.mid - 40),
        ],
        t=b.stem_t,
        cap=_cap(s),
    )
    _open_c(o, b, b.left + b.body * 0.42, b.head * 0.32, b.body * 0.36, b.head * 0.26, 200, 40)
    return GlyphOut("nna", [0x0A23], o, b.adv, b.anchors())


def g_ta(s: Style) -> GlyphOut:
    b, o = Box(s, 540), _o(s)
    b.headline(o)
    cx = b.left + b.body * 0.46
    o.vbar(b.stem_x, b.mid + 16, b.head, t=b.stem_t * 0.9)
    o.arc(cx, b.head * 0.64, b.body * 0.28, b.head * 0.13, 200, 20, t=b.stem_t, cap=_cap(s))
    o.arc(cx, b.head * 0.30, b.body * 0.34, b.head * 0.24, 20, 200, t=b.stem_t, cap=_cap(s))
    return GlyphOut("ta", [0x0A24], o, b.adv, b.anchors())


def g_tha(s: Style) -> GlyphOut:
    b, o = Box(s, 540), _o(s)
    b.headline(o)
    b.stem(o, y0=b.mid)
    o.ring(b.left + b.body * 0.40, b.head * 0.40, b.body * 0.34, b.head * 0.28, t=b.stem_t)
    return GlyphOut("tha", [0x0A25], o, b.adv, b.anchors())


def g_da(s: Style) -> GlyphOut:
    b, o = Box(s, 520), _o(s)
    b.headline(o)
    o.vbar(b.stem_x, b.mid, b.head, t=b.stem_t)
    _open_c(o, b, b.left + b.body * 0.42, b.head * 0.42, b.body * 0.34, b.head * 0.32, 200, 400)
    o.teardrop(b.left + b.body * 0.22, b.head * 0.55, b.stem_t * 0.40, "left")
    return GlyphOut("da", [0x0A26], o, b.adv, b.anchors())


def g_dha(s: Style) -> GlyphOut:
    b, o = Box(s, 540), _o(s)
    b.headline(o)
    o.vbar(b.stem_x, b.mid - 20, b.head, t=b.stem_t)
    o.ring(b.left + b.body * 0.40, b.head * 0.46, b.body * 0.32, b.head * 0.22, t=b.stem_t)
    _open_c(o, b, b.left + b.body * 0.40, b.head * 0.22, b.body * 0.34, b.head * 0.18, 20, 200)
    return GlyphOut("dha", [0x0A27], o, b.adv, b.anchors())


def g_na(s: Style) -> GlyphOut:
    b, o = Box(s, 560), _o(s)
    b.headline(o)
    cx = (b.left + b.right) / 2.0
    o.vbar(cx, b.mid + 40, b.head, t=b.stem_t)
    # hanging horseshoe, open at the bottom
    o.arc(cx, b.head * 0.46, b.body * 0.36, b.head * 0.30, 200, 340, t=b.stem_t, cap=_cap(s))
    return GlyphOut("na", [0x0A28], o, b.adv, b.anchors())


def g_pa(s: Style) -> GlyphOut:
    b, o = Box(s, 540), _o(s)
    o.hbar(b.stem_x - b.body * 0.22, b.right, b.head, t=b.bar_t)
    b.stem(o)
    _open_c(o, b, b.left + b.body * 0.38, b.head * 0.48, b.body * 0.34, b.head * 0.36, 130, 400)
    o.vbar(b.left + b.body * 0.14, b.head - 8, b.head * 0.78, t=b.stem_t * 0.9)
    return GlyphOut("pa", [0x0A2A], o, b.adv, b.anchors())


def g_pha(s: Style) -> GlyphOut:
    b, o = Box(s, 540), _o(s)
    b.headline(o)
    o.vbar(b.stem_x, b.mid + 20, b.head, t=b.stem_t)
    o.ring(b.left + b.body * 0.42, b.head * 0.36, b.body * 0.36, b.head * 0.26, t=b.stem_t)
    o.stroke(
        [(b.stem_x, b.head - b.bar_t), (b.stem_x - b.body * 0.06, b.mid + 40), (b.left + b.body * 0.22, b.mid + 10)],
        t=b.stem_t * 0.9,
        cap=_cap(s),
    )
    return GlyphOut("pha", [0x0A2B], o, b.adv, b.anchors())


def g_ba(s: Style) -> GlyphOut:
    b, o = Box(s, 560), _o(s)
    b.headline(o)
    b.stem(o)
    _open_c(o, b, b.left + b.body * 0.38, b.head * 0.66, b.body * 0.30, b.head * 0.16, 200, 400)
    _open_c(o, b, b.left + b.body * 0.40, b.head * 0.32, b.body * 0.34, b.head * 0.24, 160, 410)
    return GlyphOut("ba", [0x0A2C], o, b.adv, b.anchors())


def g_bha(s: Style) -> GlyphOut:
    b, o = Box(s, 540), _o(s)
    b.headline(o)
    o.vbar(b.stem_x, b.mid, b.head, t=b.stem_t)
    o.ring(b.left + b.body * 0.44, b.head * 0.52, b.body * 0.26, b.head * 0.16, t=b.stem_t)
    _open_c(o, b, b.left + b.body * 0.40, b.head * 0.26, b.body * 0.36, b.head * 0.22, 20, 200)
    return GlyphOut("bha", [0x0A2D], o, b.adv, b.anchors())


def g_ma(s: Style) -> GlyphOut:
    b, o = Box(s, 560), _o(s)
    b.headline(o)
    b.stem(o)
    lx = b.left + b.body * 0.22
    o.vbar(lx, b.mid - 10, b.head, t=b.stem_t)
    o.teardrop(lx, b.mid - 70, b.stem_t * 0.55, "down")
    o.hbar(lx, b.stem_x, b.mid + 12, t=b.hstem)
    return GlyphOut("ma", [0x0A2E], o, b.adv, b.anchors())


def g_ya(s: Style) -> GlyphOut:
    b, o = Box(s, 560), _o(s)
    b.headline(o)
    b.stem(o)
    cx, cy = b.left + b.body * 0.36, b.head * 0.48
    o.arc(cx, cy, b.body * 0.32, b.head * 0.30, 125, 400, t=b.stem_t, cap=_cap(s))
    o.hbar(cx, b.stem_x, cy - 8, t=b.hstem)
    return GlyphOut("ya", [0x0A2F], o, b.adv, b.anchors())


def g_ra(s: Style) -> GlyphOut:
    b, o = Box(s, 480), _o(s)
    b.headline(o)
    b.stem(o, y0=b.base + 90)
    o.arc(
        b.left + b.body * 0.40,
        b.head * 0.50,
        b.body * 0.32,
        b.head * 0.28,
        205,
        400,
        t=b.stem_t,
        cap=_cap(s),
    )
    return GlyphOut("ra", [0x0A30], o, b.adv, b.anchors())


def g_la(s: Style) -> GlyphOut:
    b, o = Box(s, 600), _o(s)
    b.headline(o)
    cx = (b.left + b.right) / 2.0
    o.stroke(
        [(b.left + b.body * 0.16, b.head - b.bar_t * 0.3), (cx, b.mid + 28)],
        t=b.stem_t,
        cap=_cap(s),
    )
    o.stroke(
        [(b.right - b.body * 0.16, b.head - b.bar_t * 0.3), (cx, b.mid + 28)],
        t=b.stem_t,
        cap=_cap(s),
    )
    o.arc(b.left + b.body * 0.32, b.head * 0.34, b.body * 0.20, b.head * 0.22, 200, 340, t=b.stem_t, cap=_cap(s))
    o.arc(b.left + b.body * 0.68, b.head * 0.34, b.body * 0.20, b.head * 0.22, 200, 340, t=b.stem_t, cap=_cap(s))
    return GlyphOut("la", [0x0A32], o, b.adv, b.anchors())


def g_va(s: Style) -> GlyphOut:
    b, o = Box(s, 520), _o(s)
    b.headline(o)
    o.vbar(b.stem_x, b.mid, b.head, t=b.stem_t)
    cx = b.left + b.body * 0.40
    _open_c(o, b, cx, b.head * 0.66, b.body * 0.30, b.head * 0.14, 200, 20)
    _open_c(o, b, cx, b.head * 0.32, b.body * 0.32, b.head * 0.20, 20, 200)
    o.hbar(cx - b.body * 0.10, b.stem_x, b.mid, t=b.hstem * 0.9)
    return GlyphOut("va", [0x0A35], o, b.adv, b.anchors())


def g_sa(s: Style) -> GlyphOut:
    b, o = Box(s, 560), _o(s)
    b.headline(o)
    b.stem(o)
    lx = b.left + b.body * 0.24
    o.vbar(lx, b.mid + 8, b.head, t=b.stem_t)
    o.teardrop(lx, b.mid - 55, b.stem_t * 0.58, "down")
    o.hbar(lx, b.stem_x, b.mid + 18, t=b.hstem)
    return GlyphOut("sa", [0x0A38], o, b.adv, b.anchors())


def g_ha(s: Style) -> GlyphOut:
    b, o = Box(s, 520), _o(s)
    b.headline(o)
    b.stem(o, y0=b.base + 80)
    o.arc(
        b.left + b.body * 0.42,
        b.head * 0.46,
        b.body * 0.34,
        b.head * 0.32,
        205,
        405,
        t=b.stem_t,
        cap=_cap(s),
    )
    return GlyphOut("ha", [0x0A39], o, b.adv, b.anchors())


def g_rra(s: Style) -> GlyphOut:
    b, o = Box(s, 560), _o(s)
    b.headline(o)
    cx = b.left + b.body * 0.48
    _open_c(o, b, cx, b.head * 0.64, b.body * 0.28, b.head * 0.13, 200, 20)
    _open_c(o, b, cx, b.head * 0.34, b.body * 0.34, b.head * 0.20, 20, 200)
    o.vbar(b.stem_x, b.mid + 10, b.head, t=b.stem_t * 0.85)
    # forked feet
    o.stroke([(cx - 40, b.base + 80), (cx - 70, b.base + 10)], t=b.stem_t * 0.85, cap=_cap(s))
    o.stroke([(cx + 30, b.base + 80), (cx + 70, b.base + 10)], t=b.stem_t * 0.85, cap=_cap(s))
    return GlyphOut("rra", [0x0A5C], o, b.adv, b.anchors())


def g_sha(s: Style) -> GlyphOut:
    g = g_sa(s)
    g.name, g.unicodes = "sha", [0x0A36]
    b = Box(s, 560)
    g.outline.disc(b.left + b.body * 0.42, b.head * 0.28, max(14.0, s.stem * 0.22))
    return g


def g_lla(s: Style) -> GlyphOut:
    g = g_la(s)
    g.name, g.unicodes = "lla", [0x0A33]
    b = Box(s, 600)
    g.outline.disc(b.left + b.body * 0.50, b.head * 0.18, max(14.0, s.stem * 0.22))
    return g


def _nukta_on(g: GlyphOut, s: Style, x_frac: float = 0.42, y_frac: float = 0.22) -> GlyphOut:
    xmin, ymin, xmax, ymax = g.outline.bounds()
    g.outline.disc(xmin + (xmax - xmin) * x_frac, ymin + (ymax - ymin) * y_frac, max(13.0, s.stem * 0.22))
    return g


def g_khha(s: Style) -> GlyphOut:
    g = _nukta_on(g_kha(s), s)
    g.name, g.unicodes = "khha", [0x0A59]
    return g


def g_ghha(s: Style) -> GlyphOut:
    g = _nukta_on(g_ga(s), s)
    g.name, g.unicodes = "ghha", [0x0A5A]
    return g


def g_za(s: Style) -> GlyphOut:
    g = _nukta_on(g_ja(s), s, 0.35, 0.18)
    g.name, g.unicodes = "za", [0x0A5B]
    return g


def g_fa(s: Style) -> GlyphOut:
    g = _nukta_on(g_pha(s), s)
    g.name, g.unicodes = "fa", [0x0A5E]
    return g


# ---------------------------------------------------------------------------
# Independent vowels and bearers
# ---------------------------------------------------------------------------

def g_ura(s: Style) -> GlyphOut:
    b, o = Box(s, 560), _o(s)
    cx = (b.left + b.right) / 2.0 - b.stem_t * 0.08
    cy = b.head * 0.46
    rx, ry = b.body * 0.40, b.head * 0.40 + s.overshoot
    o.ring(cx, cy, rx, ry, t=b.stem_t)
    # headline as a bar that sits on top of the oval, slightly wider
    o.hbar(cx - rx - 8, b.right, b.head, t=b.bar_t)
    o.vbar(b.stem_x, cy, b.head, t=b.stem_t)
    return GlyphOut("ura", [0x0A73], o, b.adv, b.anchors({"above": (cx, b.head + 50)}))


def g_oo(s: Style) -> GlyphOut:
    g = g_ura(s)
    g.name, g.unicodes = "oo", [0x0A13]
    b = Box(s, 560)
    g.outline.arc(b.left + b.body * 0.52, b.head + 58, b.body * 0.26, 40, 15, 165, t=s.hstem)
    return g


def g_iri(s: Style) -> GlyphOut:
    b, o = Box(s, 520), _o(s)
    b.headline(o)
    o.vbar(b.stem_x, b.mid, b.head, t=b.stem_t)
    _open_c(o, b, b.left + b.body * 0.40, b.head * 0.55, b.body * 0.32, b.head * 0.22, 150, 400)
    _open_c(o, b, b.left + b.body * 0.42, b.head * 0.28, b.body * 0.34, b.head * 0.22, 20, 200)
    return GlyphOut("iri", [0x0A72], o, b.adv, b.anchors())


def g_a(s: Style) -> GlyphOut:
    b, o = Box(s, 640), _o(s)
    o.hbar(b.left, b.left + b.body * 0.46, b.head, t=b.bar_t)
    o.hbar(b.stem_x - b.body * 0.16, b.right, b.head, t=b.bar_t)
    b.stem(o)
    x1 = b.left + b.body * 0.16
    x2 = b.left + b.body * 0.38
    o.vbar(x1, b.mid + 20, b.head, t=b.stem_t)
    o.vbar(x2, b.mid + 20, b.head, t=b.stem_t)
    o.teardrop(x1, b.mid - 50, b.stem_t * 0.55, "down")
    o.teardrop(x2, b.mid - 50, b.stem_t * 0.55, "down")
    o.stroke(
        [(x1, b.head - b.bar_t * 0.4), (x1 + (x2 - x1) / 2, b.mid + 90), (x2, b.head - b.bar_t * 0.4)],
        t=b.hstem,
        cap=_cap(s),
    )
    return GlyphOut("a", [0x0A05], o, b.adv, b.anchors())


def g_aa(s: Style) -> GlyphOut:
    g = g_a(s)
    g.name, g.unicodes = "aa", [0x0A06]
    # extra kanna
    b = Box(s, 640)
    extra = 90 * s.width
    g.outline.vbar(g.advance - s.side * 0.3 + extra * 0.15, BASE, HEAD, t=s.stem)
    g.advance += extra
    return g


def g_i(s: Style) -> GlyphOut:
    iri = g_iri(s)
    sih = g_sihari(s)
    o = iri.outline
    # place sihari to the left
    shift = sih.advance * 0.85
    iri.outline.translate(shift, 0)
    for c in sih.outline.contours:
        o.contours.append([(x, y) for x, y in c])
    adv = iri.advance + shift
    return GlyphOut("i", [0x0A07], o, adv, {"above": (adv * 0.55, HEAD + 50), "below": (adv * 0.55, -28)})


def g_ii(s: Style) -> GlyphOut:
    iri = g_iri(s)
    o = iri.outline
    x = iri.advance - s.side * 0.4
    o.vbar(x + 40, BASE, HEAD + 160, t=s.stem * 0.92)
    o.arc(x + 40, HEAD + 150, 90 * s.width, 70, 10, 170, t=s.hstem)
    return GlyphOut("ii", [0x0A08], o, iri.advance + 90 * s.width, iri.anchors)


def g_u(s: Style) -> GlyphOut:
    ura = g_ura(s)
    o = ura.outline
    cx = ura.advance * 0.48
    o.arc(cx, BASE - 40, 70 * s.width, 48, 200, 340, t=s.hstem)
    return GlyphOut("u", [0x0A09], o, ura.advance, ura.anchors)


def g_uu(s: Style) -> GlyphOut:
    ura = g_ura(s)
    o = ura.outline
    cx = ura.advance * 0.48
    o.arc(cx, BASE - 40, 78 * s.width, 52, 200, 350, t=s.hstem)
    o.stroke([(cx + 70 * s.width, BASE - 20), (cx + 95 * s.width, BASE - 90)], t=s.stem * 0.85, cap=_cap(s))
    return GlyphOut("uu", [0x0A0A], o, ura.advance, ura.anchors)


def g_ee(s: Style) -> GlyphOut:
    iri = g_iri(s)
    o = iri.outline
    o.stroke(
        [(iri.advance * 0.55, HEAD + 24), (iri.advance * 0.72, HEAD + 110)],
        t=s.hstem,
        cap=_cap(s),
    )
    return GlyphOut("ee", [0x0A0F], o, iri.advance, iri.anchors)


def g_ai(s: Style) -> GlyphOut:
    a = g_a(s)
    o = a.outline
    x = a.advance * 0.55
    o.stroke([(x, HEAD + 20), (x + 70, HEAD + 100)], t=s.hstem, cap=_cap(s))
    o.stroke([(x + 28, HEAD + 20), (x + 98, HEAD + 100)], t=s.hstem, cap=_cap(s))
    return GlyphOut("ai", [0x0A10], o, a.advance, a.anchors)


def g_au(s: Style) -> GlyphOut:
    a = g_a(s)
    extra = 90 * s.width
    a.outline.vbar(a.advance - s.side * 0.25, BASE, HEAD, t=s.stem)
    a.outline.arc(a.advance * 0.52, HEAD + 30, 80 * s.width, 52, 10, 170, t=s.hstem)
    a.advance += extra
    return GlyphOut("au", [0x0A14], a.outline, a.advance, a.anchors)


def g_ekonkar(s: Style) -> GlyphOut:
    one = g_digit(s, 1)
    ura = g_ura(s)
    o = _o(s)
    # digit one on the left
    one_w = one.advance * 0.92
    for c in one.outline.contours:
        o.contours.append(c)
    ura.outline.translate(one_w * 0.85, 0)
    for c in ura.outline.contours:
        o.contours.append(c)
    # trailing swash
    x1 = one_w * 0.85 + ura.advance
    o.stroke(
        [(x1 - 40, HEAD + 10), (x1 + 80 * s.width, HEAD + 90), (x1 + 160 * s.width, HEAD + 70)],
        t=s.stem * 0.9,
        cap="round",
    )
    adv = x1 + 140 * s.width
    return GlyphOut("ekonkar", [0x0A74], o, adv, {"above": (adv * 0.6, HEAD + 80), "below": (adv * 0.5, -28)})


# ---------------------------------------------------------------------------
# Marks
# ---------------------------------------------------------------------------

def g_sihari(s: Style) -> GlyphOut:
    o = _o(s)
    h = HEAD + 170
    x = 70 * s.width
    o.vbar(x, BASE + 40, h, t=s.stem * 0.92)
    o.arc(x, h - 8, 70 * s.width, 58, 10, 175, t=s.hstem)
    adv = 150 * s.width if not s.mono else s.mono_width * 0.45
    return GlyphOut("sihari", [0x0A3F], o, adv, {}, gdef="mark")


def g_bihari(s: Style) -> GlyphOut:
    o = _o(s)
    x = 20
    o.vbar(x, BASE, HEAD + 170, t=s.stem * 0.92)
    o.arc(x, HEAD + 162, 78 * s.width, 60, 10, 170, t=s.hstem)
    return GlyphOut("bihari", [0x0A40], o, 110 * s.width if not s.mono else s.mono_width * 0.35, {"_mark": (x, HEAD + 40)}, gdef="mark")


def g_kanna(s: Style) -> GlyphOut:
    o = _o(s)
    o.vbar(s.stem * 0.6, BASE, HEAD, t=s.stem)
    if s.serif > 20:
        o.slab_serif(s.stem * 0.6, BASE, "bottom")
        o.slab_serif(s.stem * 0.6, HEAD, "top")
    adv = s.stem + s.side * 0.9
    return GlyphOut("kanna", [0x0A3E], o, adv if not s.mono else s.mono_width * 0.4, {}, gdef="mark")


def g_aunkar(s: Style) -> GlyphOut:
    o = _o(s)
    o.arc(0, 0, 62 * s.width, 42, 200, 340, t=s.hstem)
    return GlyphOut("aunkar", [0x0A41], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_dulainkar(s: Style) -> GlyphOut:
    o = _o(s)
    o.arc(0, 0, 70 * s.width, 46, 200, 350, t=s.hstem)
    o.stroke([(55 * s.width, 8), (78 * s.width, -52)], t=s.stem * 0.8, cap=_cap(s))
    return GlyphOut("dulainkar", [0x0A42], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_lanvan(s: Style) -> GlyphOut:
    o = _o(s)
    o.stroke([(0, 0), (62 * s.width, 78)], t=s.hstem, cap=_cap(s))
    return GlyphOut("lanvan", [0x0A47], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_dulanvan(s: Style) -> GlyphOut:
    o = _o(s)
    o.stroke([(-8, 0), (54 * s.width, 78)], t=s.hstem, cap=_cap(s))
    o.stroke([(18, 0), (80 * s.width, 78)], t=s.hstem, cap=_cap(s))
    return GlyphOut("dulanvan", [0x0A48], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_hora(s: Style) -> GlyphOut:
    o = _o(s)
    o.arc(0, 0, 72 * s.width, 50, 10, 170, t=s.hstem)
    return GlyphOut("hora", [0x0A4B], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_kanaura(s: Style) -> GlyphOut:
    o = _o(s)
    o.arc(0, 0, 72 * s.width, 50, 10, 170, t=s.hstem)
    o.vbar(90 * s.width, -HEAD * 0.15, 20, t=s.stem * 0.9)
    return GlyphOut("kanaura", [0x0A4C], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_virama(s: Style) -> GlyphOut:
    o = _o(s)
    o.stroke([(-30, 20), (36, -40)], t=s.thin, cap=_cap(s))
    return GlyphOut("virama", [0x0A4D], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_nukta(s: Style) -> GlyphOut:
    o = _o(s)
    o.disc(0, 0, max(12.0, s.stem * 0.22))
    return GlyphOut("nukta", [0x0A3C], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_bindi(s: Style) -> GlyphOut:
    o = _o(s)
    o.disc(0, 0, max(14.0, s.stem * 0.24))
    return GlyphOut("bindi", [0x0A02], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_adakbindi(s: Style) -> GlyphOut:
    o = _o(s)
    o.disc(-18, 0, max(12.0, s.stem * 0.20))
    o.disc(18, 8, max(12.0, s.stem * 0.20))
    return GlyphOut("adakbindi", [0x0A01], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_visarga(s: Style) -> GlyphOut:
    o = _o(s)
    r = max(13.0, s.stem * 0.22)
    o.disc(0, 22, r)
    o.disc(0, -22, r)
    adv = s.side + s.stem
    return GlyphOut("visarga", [0x0A03], o, adv if not s.mono else s.mono_width * 0.3, {}, gdef="mark")


def g_tippi(s: Style) -> GlyphOut:
    o = _o(s)
    o.arc(0, 0, 28, 22, 200, 340, t=s.hstem * 0.85)
    o.disc(0, -6, max(10.0, s.stem * 0.18))
    return GlyphOut("tippi", [0x0A70], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_addak(s: Style) -> GlyphOut:
    o = _o(s)
    o.arc(0, 0, 36, 28, 200, 20, t=s.hstem)
    o.arc(0, 8, 22, 16, 200, 20, t=s.thin)
    return GlyphOut("addak", [0x0A71], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_udaat(s: Style) -> GlyphOut:
    o = _o(s)
    o.stroke([(0, 0), (0, 70)], t=s.thin, cap=_cap(s))
    return GlyphOut("udaat", [0x0A51], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_yakash(s: Style) -> GlyphOut:
    o = _o(s)
    o.arc(0, 0, 40 * s.width, 28, 20, 200, t=s.hstem * 0.8)
    return GlyphOut("yakash", [0x0A75], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_abbrev(s: Style) -> GlyphOut:
    o = _o(s)
    o.stroke([(0, HEAD * 0.2), (40, HEAD * 0.7)], t=s.thin, cap=_cap(s))
    o.disc(48, HEAD * 0.78, max(10.0, s.stem * 0.18))
    return GlyphOut("abbrev", [0x0A76], o, 80 * s.width, {}, gdef="mark")


# ---------------------------------------------------------------------------
# Digits
# ---------------------------------------------------------------------------

def g_digit(s: Style, n: int) -> GlyphOut:
    b, o = Box(s, 480 if not s.mono else 500), _o(s)
    cx, cy = (b.left + b.right) / 2.0, HEAD * 0.42
    t = b.stem_t
    names = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    cps = list(range(0x0A66, 0x0A70))
    if n == 0:
        o.ring(cx, cy, b.body * 0.34, HEAD * 0.36 + s.overshoot, t=t)
    elif n == 1:
        o.ring(cx - 10, cy + 70, b.body * 0.22, HEAD * 0.18, t=t)
        o.stroke([(cx + b.body * 0.10, cy + 70), (cx + b.body * 0.12, b.base + 20)], t=t, cap=_cap(s))
    elif n == 2:
        _open_c(o, b, cx, cy + 90, b.body * 0.28, HEAD * 0.16, 200, 20)
        o.stroke([(cx + b.body * 0.22, cy + 70), (cx - b.body * 0.22, b.base + 30)], t=t, cap=_cap(s))
        o.hbar(cx - b.body * 0.24, cx + b.body * 0.24, b.base + 30, t=s.hstem)
    elif n == 3:
        _open_c(o, b, cx, cy + 90, b.body * 0.26, HEAD * 0.16, 200, 20)
        _open_c(o, b, cx, cy - 40, b.body * 0.30, HEAD * 0.22, 20, 200)
    elif n == 4:
        o.ring(cx, cy + 80, b.body * 0.24, HEAD * 0.16, t=t)
        o.ring(cx, cy - 50, b.body * 0.26, HEAD * 0.20, t=t)
        # gap at top of upper ring — extra cut via overlapping white is hard; open the top with a short gap stroke skip
        o.rect(cx - t * 0.4, cy + 80 + HEAD * 0.16 - t * 0.6, t * 0.8, t * 1.1, r=0)  # visual notch via extra fill is wrong
    elif n == 5:
        o.stroke([(cx + b.body * 0.18, cy + 120), (cx - b.body * 0.10, cy + 40), (cx + b.body * 0.06, b.base + 20)], t=t, cap=_cap(s))
        _open_c(o, b, cx, cy + 100, b.body * 0.22, HEAD * 0.14, 200, 20)
    elif n == 6:
        _open_c(o, b, cx, cy, b.body * 0.32, HEAD * 0.34, 40, 280)
        o.teardrop(cx - b.body * 0.18, cy + 40, t * 0.45, "left")
    elif n == 7:
        o.stroke([(cx - b.body * 0.22, cy + 110), (cx + b.body * 0.10, cy + 110), (cx - b.body * 0.06, b.base + 20)], t=t, cap=_cap(s))
    elif n == 8:
        _open_c(o, b, cx, cy + 40, b.body * 0.28, HEAD * 0.30, 40, 140)
        _open_c(o, b, cx, cy + 40, b.body * 0.28, HEAD * 0.30, 220, 320)
    else:  # 9
        _open_c(o, b, cx, cy + 80, b.body * 0.26, HEAD * 0.18, 200, 20)
        o.stroke([(cx + b.body * 0.20, cy + 60), (cx + b.body * 0.06, b.base + 30)], t=t, cap=_cap(s))
        _open_c(o, b, cx, cy - 40, b.body * 0.28, HEAD * 0.20, 20, 160)
    return GlyphOut(names[n], [cps[n]], o, b.adv, b.anchors())


# ---------------------------------------------------------------------------
# Punctuation used in Punjabi
# ---------------------------------------------------------------------------

def g_danda(s: Style) -> GlyphOut:
    o = _o(s)
    x = s.side * 0.5
    o.vbar(x, BASE, HEAD, t=s.stem)
    return GlyphOut("danda", [0x0964], o, s.stem + s.side, {})


def g_doubledanda(s: Style) -> GlyphOut:
    o = _o(s)
    gap = s.stem * 1.4
    o.vbar(s.side * 0.4, BASE, HEAD, t=s.stem)
    o.vbar(s.side * 0.4 + gap, BASE, HEAD, t=s.stem)
    return GlyphOut("doubledanda", [0x0965], o, gap + s.stem + s.side, {})


def all_gurmukhi(s: Style) -> list[GlyphOut]:
    glyphs = [
        g_ka(s), g_kha(s), g_ga(s), g_gha(s), g_nga(s),
        g_ca(s), g_cha(s), g_ja(s), g_jha(s), g_nya(s),
        g_tta(s), g_ttha(s), g_dda(s), g_ddha(s), g_nna(s),
        g_ta(s), g_tha(s), g_da(s), g_dha(s), g_na(s),
        g_pa(s), g_pha(s), g_ba(s), g_bha(s), g_ma(s),
        g_ya(s), g_ra(s), g_la(s), g_va(s), g_sa(s), g_ha(s), g_rra(s),
        g_sha(s), g_lla(s), g_khha(s), g_ghha(s), g_za(s), g_fa(s),
        g_a(s), g_aa(s), g_i(s), g_ii(s), g_u(s), g_uu(s),
        g_ee(s), g_ai(s), g_oo(s), g_au(s), g_iri(s), g_ura(s), g_ekonkar(s),
        g_sihari(s), g_bihari(s), g_kanna(s), g_aunkar(s), g_dulainkar(s),
        g_lanvan(s), g_dulanvan(s), g_hora(s), g_kanaura(s),
        g_virama(s), g_nukta(s), g_bindi(s), g_adakbindi(s), g_visarga(s),
        g_tippi(s), g_addak(s), g_udaat(s), g_yakash(s), g_abbrev(s),
        g_danda(s), g_doubledanda(s),
    ]
    for n in range(10):
        glyphs.append(g_digit(s, n))
    # Stable Unicode names — Latin already claimed a/i/u etc.
    for g in glyphs:
        if g.unicodes:
            g.name = f"uni{g.unicodes[0]:04X}"
    return glyphs
