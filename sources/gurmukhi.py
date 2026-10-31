"""Gurmukhi letter constructions.

Each glyph is an original stroke drawing of the traditional Gurmukhi
skeleton (painti akhari), not a Devanagari look-alike and not a copy of
any existing font. Headlines run the full advance so letters join in a word.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from geom import Outline, bezier_points
from style import BASE, HEAD, Style


@dataclass
class GlyphOut:
    name: str
    unicodes: list[int]
    outline: Outline
    advance: float
    anchors: dict[str, tuple[float, float]] = field(default_factory=dict)
    gdef: str = "base"


def _o(s: Style) -> Outline:
    return Outline(stem=s.stem, roundness=s.roundness, corner=s.corner, serif=s.serif)


def _cap(s: Style) -> str:
    return "round" if s.roundness >= 0.25 else "square"


class Box:
    def __init__(self, s: Style, body: float = 540.0):
        self.s = s
        self.body = body * s.width
        if s.mono:
            self.adv = s.mono_width
            self.left = (self.adv - self.body) / 2.0
        else:
            pad = s.side * (0.45 if s.condensed else 0.55)
            self.left = pad
            self.adv = self.left + self.body + pad
        self.right = self.left + self.body
        self.head = HEAD
        self.base = BASE
        self.mid = HEAD * 0.48
        self.stem_t = s.stem
        self.bar_t = s.bar
        self.hstem = s.hstem
        self.stem_x = self.right - s.stem * 0.45
        self.r = s.cap_radius

    def p(self, fx: float, fy: float) -> tuple[float, float]:
        return (self.left + self.body * fx, self.head * fy)

    def headline(self, o: Outline, x0: float | None = None, x1: float | None = None) -> None:
        # Full advance so neighbouring Gurmukhi letters share one bar.
        x0 = 0.0 if x0 is None else x0
        x1 = self.adv if x1 is None else x1
        o.hbar(x0, x1, self.head, t=self.bar_t, r=min(self.s.corner, self.bar_t / 2))

    def stem(self, o: Outline, y0: float = 70.0, y1: float | None = None, x: float | None = None) -> None:
        y1 = self.head if y1 is None else y1
        x = self.stem_x if x is None else x
        o.vbar(x, y0, y1, t=self.stem_t, r=self.s.corner)
        if self.s.serif > 20 and y0 < 120:
            o.slab_serif(x, y0, "bottom", t=self.stem_t)

    def anchors(self, extra: dict | None = None) -> dict[str, tuple[float, float]]:
        a = {
            "above": (self.left + self.body * 0.50, self.head + self.bar_t * 0.5 + 40),
            "below": (self.left + self.body * 0.50, self.base - 36),
            "post": (self.right + 8, self.mid),
        }
        if extra:
            a.update(extra)
        return a


def _stroke(o: Outline, pts: list[tuple[float, float]], t: float, s: Style) -> None:
    o.stroke(pts, t=t, cap=_cap(s))


def _bez(o: Outline, p0, p1, p2, p3, t: float, s: Style) -> None:
    o.stroke(bezier_points(p0, p1, p2, p3, n=22), t=t, cap=_cap(s))


def _chain(o: Outline, pts: list[tuple[float, float]], t: float, s: Style) -> None:
    """Smooth polyline through points using quadratic midpoints."""
    if len(pts) < 2:
        return
    if len(pts) == 2:
        _stroke(o, pts, t, s)
        return
    seq = [pts[0]]
    for i in range(len(pts) - 2):
        a, b, c = pts[i], pts[i + 1], pts[i + 2]
        seq += bezier_points(a, b, b, c, n=10)[1:]
    # last segment already included via last cubic; ensure end
    if seq[-1] != pts[-1]:
        seq.append(pts[-1])
    _stroke(o, seq, t, s)


# ---------------------------------------------------------------------------
# Shared Gurmukhi motifs (original constructions)
# ---------------------------------------------------------------------------

def _hook_to_stem(o: Outline, b: Box, *, deep: float = 0.18, left: float = 0.12, attach: float = 0.22) -> None:
    """C / J hook that lands on the right stem."""
    _bez(
        o,
        (b.left + b.body * left, b.head * 0.78),
        (b.left + b.body * (left - 0.04), b.head * 0.40),
        (b.left + b.body * 0.36, b.head * deep),
        (b.stem_x, b.head * attach),
        b.stem_t,
        b.s,
    )


def _u_to_stem(o: Outline, b: Box, *, left: float = 0.08, deep: float = 0.16, top: float = 0.78) -> None:
    """Open U from the left into the right stem. ਪ ਖ ਥ ਯ."""
    _bez(
        o,
        b.p(left, top),
        b.p(left - 0.04, 0.40),
        b.p(0.40, deep),
        (b.stem_x, b.head * 0.28),
        b.stem_t,
        b.s,
    )


def _three(o: Outline, b: Box, *, closed_bottom: bool = False) -> None:
    """Stacked open-left '3' used by ਤ ੲ ਡ ਭ."""
    _bez(o, b.p(0.78, 0.78), b.p(0.08, 0.82), b.p(0.08, 0.52), b.p(0.70, 0.50), b.stem_t, b.s)
    if closed_bottom:
        _bez(o, b.p(0.70, 0.50), b.p(0.05, 0.46), b.p(0.08, 0.08), b.p(0.78, 0.20), b.stem_t, b.s)
    else:
        _bez(o, b.p(0.70, 0.50), b.p(0.12, 0.42), b.p(0.16, 0.10), b.p(0.78, 0.16), b.stem_t, b.s)


def _out(name: str, cp: int, b: Box, o: Outline) -> GlyphOut:
    return GlyphOut(name, [cp], o, b.adv, b.anchors())


# ---------------------------------------------------------------------------
# Consonants — painti order after the three bearers
# ---------------------------------------------------------------------------

def g_sa(s: Style) -> GlyphOut:
    """ਸ — left J-hook, mid bar, right stem."""
    b, o = Box(s, 520), _o(s)
    b.headline(o)
    b.stem(o, y0=70)
    lx = b.left + b.body * 0.26
    o.vbar(lx, b.head * 0.44, b.head, t=b.stem_t)
    o.hbar(lx, b.stem_x, b.head * 0.48, t=b.hstem)
    # rounded J, overlapping the left stem so there is no spike
    o.arc(lx - b.body * 0.02, b.head * 0.30, b.body * 0.18, b.head * 0.20, 50, 240, t=b.stem_t, cap=_cap(s))
    return _out("sa", 0x0A38, b, o)


def g_ha(s: Style) -> GlyphOut:
    """ਹ — deep C opening to the right stem."""
    b, o = Box(s, 500), _o(s)
    b.headline(o)
    b.stem(o, y0=90)
    _hook_to_stem(o, b, deep=0.14, left=0.14, attach=0.20)
    return _out("ha", 0x0A39, b, o)


def g_ka(s: Style) -> GlyphOut:
    """ਕ — a 2-shaped loop that starts and ends on the stem."""
    b, o = Box(s, 540), _o(s)
    b.headline(o)
    b.stem(o, y0=40)
    _bez(
        o,
        (b.stem_x, b.head * 0.74),
        (b.left + b.body * 0.08, b.head * 0.88),
        (b.left + b.body * 0.02, b.head * 0.18),
        (b.stem_x, b.head * 0.28),
        b.stem_t,
        s,
    )
    return _out("ka", 0x0A15, b, o)


def g_kha(s: Style) -> GlyphOut:
    """ਖ — wide U into the stem (not a Devanagari kha)."""
    b, o = Box(s, 540), _o(s)
    b.headline(o)
    b.stem(o, y0=70)
    _u_to_stem(o, b, left=0.10, deep=0.18, top=0.80)
    return _out("kha", 0x0A16, b, o)


def g_ga(s: Style) -> GlyphOut:
    """ਗ — shallower hook than ਹ; stem stops with the hook."""
    b, o = Box(s, 500), _o(s)
    b.headline(o)
    b.stem(o, y0=120)
    _hook_to_stem(o, b, deep=0.20, left=0.16, attach=0.28)
    return _out("ga", 0x0A17, b, o)


def g_gha(s: Style) -> GlyphOut:
    """ਘ — two-bay wave into the stem, like a w + vertical."""
    b, o = Box(s, 580), _o(s)
    b.headline(o)
    b.stem(o, y0=70)
    _chain(
        o,
        [b.p(0.08, 0.80), b.p(0.18, 0.22), b.p(0.48, 0.22), b.p(0.62, 0.55), (b.stem_x, b.head * 0.30)],
        b.stem_t,
        s,
    )
    return _out("gha", 0x0A18, b, o)


def g_nga(s: Style) -> GlyphOut:
    """ਙ — rare; stacked open bowls, no long stem."""
    b, o = Box(s, 500), _o(s)
    b.headline(o)
    _bez(o, b.p(0.18, 0.78), b.p(0.05, 0.58), b.p(0.55, 0.52), b.p(0.82, 0.70), b.stem_t, s)
    _bez(o, b.p(0.22, 0.48), b.p(0.05, 0.22), b.p(0.70, 0.10), b.p(0.88, 0.36), b.stem_t, s)
    o.vbar(b.left + b.body * 0.80, b.head * 0.36, b.head, t=b.stem_t * 0.9)
    return _out("nga", 0x0A19, b, o)


def g_ca(s: Style) -> GlyphOut:
    """ਚ — C-hook with a left beak."""
    b, o = Box(s, 520), _o(s)
    b.headline(o)
    b.stem(o, y0=140)
    _hook_to_stem(o, b, deep=0.16, left=0.16, attach=0.24)
    o.disc(b.left + b.body * 0.18, b.head * 0.62, max(16.0, b.stem_t * 0.38))
    return _out("ca", 0x0A1A, b, o)


def g_cha(s: Style) -> GlyphOut:
    """ਛ — snake from the stem into a barred oval (not a Devanagari cha)."""
    b, o = Box(s, 540), _o(s)
    b.headline(o)
    o.vbar(b.stem_x, b.head * 0.55, b.head, t=b.stem_t)
    _bez(o, (b.stem_x, b.head * 0.58), b.p(0.15, 0.62), b.p(0.10, 0.38), b.p(0.50, 0.36), b.stem_t, s)
    cx, cy = b.left + b.body * 0.46, b.head * 0.28
    o.ring(cx, cy, b.body * 0.32, b.head * 0.16, t=b.stem_t * 0.95)
    o.hbar(cx - b.body * 0.28, cx + b.body * 0.28, cy, t=b.hstem * 0.85)
    return _out("cha", 0x0A1B, b, o)


def g_ja(s: Style) -> GlyphOut:
    """ਜ — two stems, mid bar, left tick. Distinctly Gurmukhi."""
    b, o = Box(s, 520), _o(s)
    b.headline(o)
    b.stem(o, y0=70)
    lx = b.left + b.body * 0.28
    o.vbar(lx, 70, b.head, t=b.stem_t)
    o.hbar(lx - b.body * 0.16, b.stem_x, b.head * 0.50, t=b.hstem)
    o.disc(lx - b.body * 0.16, b.head * 0.50, max(20.0, b.stem_t * 0.48))
    if s.serif > 20:
        o.slab_serif(lx, 70, "bottom")
    return _out("ja", 0x0A1C, b, o)


def g_jha(s: Style) -> GlyphOut:
    """ਝ — ਜ plus a small n-curve above the bar."""
    g = g_ja(s)
    g.name, g.unicodes = "jha", [0x0A1D]
    b = Box(s, 500)
    g.outline.arc(b.left + b.body * 0.38, b.head + 48, b.body * 0.20, 44, 200, 20, t=s.hstem)
    return g


def g_nya(s: Style) -> GlyphOut:
    """ਞ — two stems with a lower left hook."""
    b, o = Box(s, 560), _o(s)
    b.headline(o)
    o.vbar(b.left + b.body * 0.28, 90, b.head, t=b.stem_t)
    b.stem(o, y0=90)
    o.hbar(b.left + b.body * 0.28, b.stem_x, b.head * 0.50, t=b.hstem)
    _bez(o, b.p(0.28, 0.28), b.p(0.08, 0.20), b.p(0.10, 0.08), b.p(0.36, 0.12), b.stem_t, s)
    return _out("nya", 0x0A1E, b, o)


def g_tta(s: Style) -> GlyphOut:
    """ਟ — candy-cane hook from the bar, open at the bottom-right."""
    b, o = Box(s, 500), _o(s)
    b.headline(o)
    o.vbar(b.stem_x, b.head * 0.52, b.head, t=b.stem_t)
    _bez(o, (b.stem_x, b.head * 0.54), b.p(0.12, 0.58), b.p(0.08, 0.12), b.p(0.78, 0.16), b.stem_t, s)
    return _out("tta", 0x0A1F, b, o)


def g_ttha(s: Style) -> GlyphOut:
    """ਠ — lollipop: oval hanging from a short centre stem."""
    b, o = Box(s, 500), _o(s)
    b.headline(o)
    cx = (b.left + b.right) / 2.0
    cy = b.head * 0.32
    ry = b.head * 0.20
    o.vbar(cx, cy + ry - b.stem_t * 0.3, b.head, t=b.stem_t)
    o.ring(cx, cy, b.body * 0.32, ry, t=b.stem_t)
    return _out("ttha", 0x0A20, b, o)


def g_dda(s: Style) -> GlyphOut:
    """ਡ — '3' whose lower bowl closes."""
    b, o = Box(s, 520), _o(s)
    b.headline(o)
    o.vbar(b.stem_x, b.head * 0.58, b.head, t=b.stem_t * 0.9)
    _three(o, b, closed_bottom=True)
    return _out("dda", 0x0A21, b, o)


def g_ddha(s: Style) -> GlyphOut:
    g = g_dda(s)
    g.name, g.unicodes = "ddha", [0x0A22]
    b = Box(s, 520)
    g.outline.disc(b.left + b.body * 0.40, b.head * 0.28, max(14.0, s.stem * 0.22))
    return g


def g_nna(s: Style) -> GlyphOut:
    """ਣ — diagonal from the bar into a bottom hook."""
    b, o = Box(s, 520), _o(s)
    b.headline(o)
    _stroke(o, [b.p(0.88, 0.92), b.p(0.28, 0.48)], b.stem_t, s)
    _bez(o, b.p(0.28, 0.48), b.p(0.06, 0.36), b.p(0.12, 0.08), b.p(0.78, 0.14), b.stem_t, s)
    return _out("nna", 0x0A23, b, o)


def g_ta(s: Style) -> GlyphOut:
    """ਤ — open '3' hanging from a short stem."""
    b, o = Box(s, 500), _o(s)
    b.headline(o)
    o.vbar(b.stem_x, b.head * 0.58, b.head, t=b.stem_t * 0.9)
    _three(o, b, closed_bottom=False)
    return _out("ta", 0x0A24, b, o)


def g_tha(s: Style) -> GlyphOut:
    """ਥ — U into a stem (rounder than ਖ)."""
    b, o = Box(s, 520), _o(s)
    b.headline(o)
    b.stem(o, y0=70)
    _u_to_stem(o, b, left=0.12, deep=0.20, top=0.78)
    return _out("tha", 0x0A25, b, o)


def g_da(s: Style) -> GlyphOut:
    """ਦ — C-hook with a left beak, open at the bottom-right."""
    b, o = Box(s, 520), _o(s)
    b.headline(o)
    o.vbar(b.stem_x, b.head * 0.50, b.head, t=b.stem_t)
    _bez(o, (b.stem_x, b.head * 0.52), b.p(0.12, 0.62), b.p(0.08, 0.12), b.p(0.72, 0.14), b.stem_t, s)
    o.disc(b.left + b.body * 0.16, b.head * 0.58, max(16.0, b.stem_t * 0.36))
    return _out("da", 0x0A26, b, o)


def g_dha(s: Style) -> GlyphOut:
    """ਧ — upper loop plus a lower open hook."""
    b, o = Box(s, 520), _o(s)
    b.headline(o)
    o.vbar(b.stem_x, b.head * 0.55, b.head, t=b.stem_t)
    _bez(o, (b.stem_x, b.head * 0.58), b.p(0.15, 0.72), b.p(0.12, 0.38), b.p(0.70, 0.42), b.stem_t, s)
    _bez(o, b.p(0.70, 0.42), b.p(0.10, 0.36), b.p(0.14, 0.08), b.p(0.78, 0.14), b.stem_t, s)
    return _out("dha", 0x0A27, b, o)


def g_na(s: Style) -> GlyphOut:
    """ਨ — omega / horseshoe, open at the bottom, stem planted on the arch."""
    b, o = Box(s, 520), _o(s)
    b.headline(o)
    cx = (b.left + b.right) / 2.0
    cy = b.head * 0.38
    ry = b.head * 0.26
    # 200° → -20° decreasing goes over the TOP (90°), so the arch meets the stem
    o.vbar(cx, cy + ry - b.stem_t * 0.6, b.head, t=b.stem_t)
    o.arc(cx, cy, b.body * 0.34, ry, 205, -25, t=b.stem_t, cap=_cap(s))
    return _out("na", 0x0A28, b, o)


def g_pa(s: Style) -> GlyphOut:
    """ਪ — headline beak, then a wide U into the stem."""
    b, o = Box(s, 540), _o(s)
    beak = b.left + b.body * 0.04
    join = b.left + b.body * 0.18
    b.headline(o, x0=beak)
    b.stem(o, y0=70)
    _bez(
        o,
        (join, b.head - b.bar_t * 0.2),
        (b.left + b.body * 0.08, b.head * 0.35),
        (b.left + b.body * 0.40, b.head * 0.10),
        (b.stem_x, b.head * 0.24),
        b.stem_t,
        s,
    )
    return _out("pa", 0x0A2A, b, o)


def g_pha(s: Style) -> GlyphOut:
    """pha: bar from the stem into a bottom loop."""
    b, o = Box(s, 520), _o(s)
    b.headline(o)
    o.vbar(b.stem_x, b.head * 0.52, b.head, t=b.stem_t)
    _bez(o, (b.stem_x, b.head * 0.54), b.p(0.12, 0.58), b.p(0.08, 0.22), b.p(0.55, 0.20), b.stem_t, s)
    o.arc(b.left + b.body * 0.48, b.head * 0.26, b.body * 0.30, b.head * 0.16, 20, 200, t=b.stem_t, cap=_cap(s))
    return _out("pha", 0x0A2B, b, o)


def g_ba(s: Style) -> GlyphOut:
    """ਬ — two stacked bowls into the stem (B / 3)."""
    b, o = Box(s, 540), _o(s)
    b.headline(o)
    b.stem(o, y0=70)
    _bez(o, b.p(0.10, 0.80), b.p(0.06, 0.58), b.p(0.55, 0.52), (b.stem_x, b.head * 0.48), b.stem_t, s)
    _bez(o, (b.stem_x, b.head * 0.48), b.p(0.08, 0.42), b.p(0.16, 0.12), (b.stem_x, b.head * 0.22), b.stem_t, s)
    return _out("ba", 0x0A2C, b, o)


def g_bha(s: Style) -> GlyphOut:
    """ਭ — upper loop and a lower open hook."""
    b, o = Box(s, 520), _o(s)
    b.headline(o)
    o.vbar(b.stem_x, b.head * 0.58, b.head, t=b.stem_t)
    _three(o, b, closed_bottom=False)
    return _out("bha", 0x0A2D, b, o)


def g_ma(s: Style) -> GlyphOut:
    """ਮ — H / π: left leg kicks out, mid bar, right stem. No sa pearl."""
    b, o = Box(s, 540), _o(s)
    b.headline(o)
    b.stem(o, y0=70)
    lx = b.left + b.body * 0.26
    o.vbar(lx, b.head * 0.46, b.head, t=b.stem_t)
    o.hbar(lx, b.stem_x, b.head * 0.48, t=b.hstem)
    _bez(
        o,
        (lx, b.head * 0.48),
        (lx, b.head * 0.22),
        (lx - b.body * 0.22, b.head * 0.10),
        (lx - b.body * 0.14, b.head * 0.06),
        b.stem_t,
        s,
    )
    return _out("ma", 0x0A2E, b, o)


def g_ya(s: Style) -> GlyphOut:
    """ya: J / U into the stem, starting further in than pa."""
    b, o = Box(s, 520), _o(s)
    b.headline(o)
    b.stem(o, y0=70)
    _u_to_stem(o, b, left=0.18, deep=0.14, top=0.78)
    return _out("ya", 0x0A2F, b, o)


def g_ra(s: Style) -> GlyphOut:
    """ਰ — smaller C than ਹ; stem ends with the hook."""
    b, o = Box(s, 480), _o(s)
    b.headline(o)
    b.stem(o, y0=130)
    _hook_to_stem(o, b, deep=0.22, left=0.16, attach=0.28)
    return _out("ra", 0x0A30, b, o)


def g_la(s: Style) -> GlyphOut:
    """ਲ — two hanging loops that meet in a mid valley."""
    b, o = Box(s, 560), _o(s)
    b.headline(o)
    valley = (b.left + b.body * 0.50, b.head * 0.50)
    _bez(
        o,
        (b.left + b.body * 0.16, b.head - b.bar_t * 0.15),
        (b.left + b.body * 0.10, b.head * 0.22),
        (b.left + b.body * 0.34, b.head * 0.10),
        valley,
        b.stem_t,
        s,
    )
    _bez(
        o,
        valley,
        (b.left + b.body * 0.66, b.head * 0.10),
        (b.left + b.body * 0.90, b.head * 0.22),
        (b.left + b.body * 0.84, b.head - b.bar_t * 0.15),
        b.stem_t,
        s,
    )
    return _out("la", 0x0A32, b, o)


def g_va(s: Style) -> GlyphOut:
    """ਵ — e / E: mid arm from the stem, then a lower open hook."""
    b, o = Box(s, 520), _o(s)
    b.headline(o)
    o.vbar(b.stem_x, b.head * 0.52, b.head, t=b.stem_t)
    o.hbar(b.left + b.body * 0.18, b.stem_x, b.head * 0.52, t=b.hstem)
    _bez(o, (b.left + b.body * 0.18, b.head * 0.52), b.p(0.06, 0.28), b.p(0.30, 0.10), b.p(0.82, 0.18), b.stem_t, s)
    return _out("va", 0x0A35, b, o)


def g_rra(s: Style) -> GlyphOut:
    """ੜ — '3' with two forked feet. Punjabi-only letter."""
    b, o = Box(s, 540), _o(s)
    b.headline(o)
    o.vbar(b.stem_x, b.head * 0.58, b.head, t=b.stem_t * 0.85)
    _three(o, b, closed_bottom=False)
    _stroke(o, [b.p(0.28, 0.22), b.p(0.12, 0.02)], b.stem_t * 0.9, s)
    _stroke(o, [b.p(0.62, 0.18), b.p(0.78, 0.02)], b.stem_t * 0.9, s)
    return _out("rra", 0x0A5C, b, o)


def g_sha(s: Style) -> GlyphOut:
    g = g_sa(s)
    g.name, g.unicodes = "sha", [0x0A36]
    b = Box(s, 520)
    g.outline.disc(b.left + b.body * 0.40, b.head * 0.22, max(14.0, s.stem * 0.22))
    return g


def g_lla(s: Style) -> GlyphOut:
    g = g_la(s)
    g.name, g.unicodes = "lla", [0x0A33]
    b = Box(s, 560)
    g.outline.disc(b.left + b.body * 0.50, b.head * 0.16, max(14.0, s.stem * 0.22))
    return g


def _nukta_on(g: GlyphOut, s: Style, x_frac: float = 0.42, y_frac: float = 0.20) -> GlyphOut:
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
    g = _nukta_on(g_ja(s), s, 0.28, 0.16)
    g.name, g.unicodes = "za", [0x0A5B]
    return g


def g_fa(s: Style) -> GlyphOut:
    g = _nukta_on(g_pha(s), s)
    g.name, g.unicodes = "fa", [0x0A5E]
    return g


# ---------------------------------------------------------------------------
# Bearers and independent vowels
# ---------------------------------------------------------------------------

def g_ura(s: Style) -> GlyphOut:
    """ੳ — theta: the oval is cut by the headline and rises above it."""
    b, o = Box(s, 560), _o(s)
    cx = (b.left + b.right) / 2.0
    cy = b.head * 0.50
    rx, ry = b.body * 0.36, b.head * 0.58 + s.overshoot
    o.ring(cx, cy, rx, ry, t=b.stem_t)
    b.headline(o)
    o.vbar(b.stem_x, cy + 40, b.head + 16, t=b.stem_t)
    return GlyphOut("ura", [0x0A73], o, b.adv, b.anchors({"above": (cx, b.head + 70)}))


def g_iri(s: Style) -> GlyphOut:
    """ੲ — open '3' / hook. Bearer for i / ī / e."""
    b, o = Box(s, 500), _o(s)
    b.headline(o)
    o.vbar(b.stem_x, b.head * 0.55, b.head, t=b.stem_t)
    _three(o, b, closed_bottom=False)
    return _out("iri", 0x0A72, b, o)


def g_a(s: Style) -> GlyphOut:
    """ਅ — n-shape on the left, gap, right stem. Broken headline."""
    b, o = Box(s, 640), _o(s)
    gap0 = b.left + b.body * 0.42
    gap1 = b.left + b.body * 0.58
    b.headline(o, x0=0.0, x1=gap0)
    b.headline(o, x0=gap1, x1=b.adv)
    b.stem(o, y0=70)
    lx = b.left + b.body * 0.20
    o.vbar(lx, b.head * 0.30, b.head, t=b.stem_t)
    _bez(
        o,
        (lx, b.head * 0.32),
        (lx + b.body * 0.06, b.head * 0.10),
        (lx + b.body * 0.22, b.head * 0.10),
        (lx + b.body * 0.26, b.head * 0.58),
        b.stem_t,
        s,
    )
    return _out("a", 0x0A05, b, o)


def g_aa(s: Style) -> GlyphOut:
    g = g_a(s)
    g.name, g.unicodes = "aa", [0x0A06]
    extra = 88 * s.width
    g.outline.vbar(g.advance - s.side * 0.2 + extra * 0.15, BASE, HEAD, t=s.stem)
    g.advance += extra
    return g


def g_i(s: Style) -> GlyphOut:
    iri = g_iri(s)
    sih = g_sihari(s)
    shift = sih.advance * 0.90
    iri.outline.translate(shift, 0)
    for c in sih.outline.contours:
        iri.outline.contours.append(list(c))
    adv = iri.advance + shift
    return GlyphOut("i", [0x0A07], iri.outline, adv, {"above": (adv * 0.58, HEAD + 50), "below": (adv * 0.58, -28)})


def g_ii(s: Style) -> GlyphOut:
    iri = g_iri(s)
    x = iri.advance - s.side * 0.25
    iri.outline.vbar(x + 36, BASE, HEAD + 165, t=s.stem * 0.92)
    iri.outline.arc(x + 36, HEAD + 155, 88 * s.width, 68, 10, 170, t=s.hstem)
    return GlyphOut("ii", [0x0A08], iri.outline, iri.advance + 88 * s.width, iri.anchors)


def g_u(s: Style) -> GlyphOut:
    ura = g_ura(s)
    cx = ura.advance * 0.48
    ura.outline.arc(cx, BASE - 36, 68 * s.width, 46, 200, 340, t=s.hstem)
    return GlyphOut("u", [0x0A09], ura.outline, ura.advance, ura.anchors)


def g_uu(s: Style) -> GlyphOut:
    ura = g_ura(s)
    cx = ura.advance * 0.48
    ura.outline.arc(cx, BASE - 36, 76 * s.width, 50, 200, 350, t=s.hstem)
    ura.outline.stroke([(cx + 68 * s.width, BASE - 16), (cx + 96 * s.width, BASE - 88)], t=s.stem * 0.85, cap=_cap(s))
    return GlyphOut("uu", [0x0A0A], ura.outline, ura.advance, ura.anchors)


def g_ee(s: Style) -> GlyphOut:
    iri = g_iri(s)
    iri.outline.stroke([(iri.advance * 0.52, HEAD + 22), (iri.advance * 0.72, HEAD + 108)], t=s.hstem, cap=_cap(s))
    return GlyphOut("ee", [0x0A0F], iri.outline, iri.advance, iri.anchors)


def g_ai(s: Style) -> GlyphOut:
    a = g_a(s)
    x = a.advance * 0.52
    a.outline.stroke([(x, HEAD + 18), (x + 68, HEAD + 98)], t=s.hstem, cap=_cap(s))
    a.outline.stroke([(x + 26, HEAD + 18), (x + 94, HEAD + 98)], t=s.hstem, cap=_cap(s))
    return GlyphOut("ai", [0x0A10], a.outline, a.advance, a.anchors)


def g_oo(s: Style) -> GlyphOut:
    g = g_ura(s)
    g.name, g.unicodes = "oo", [0x0A13]
    b = Box(s, 560)
    g.outline.arc(b.left + b.body * 0.52, b.head + 56, b.body * 0.26, 40, 15, 165, t=s.hstem)
    return g


def g_au(s: Style) -> GlyphOut:
    a = g_a(s)
    extra = 88 * s.width
    a.outline.vbar(a.advance - s.side * 0.2, BASE, HEAD, t=s.stem)
    a.outline.arc(a.advance * 0.52, HEAD + 32, 78 * s.width, 50, 10, 170, t=s.hstem)
    a.advance += extra
    return GlyphOut("au", [0x0A14], a.outline, a.advance, a.anchors)


def g_ekonkar(s: Style) -> GlyphOut:
    """ੴ — Gurmukhi one + ura + the traditional top swash."""
    one = g_digit(s, 1)
    ura = g_ura(s)
    o = _o(s)
    one_w = one.advance * 0.88
    for c in one.outline.contours:
        o.contours.append(c)
    ura.outline.translate(one_w * 0.78, 0)
    for c in ura.outline.contours:
        o.contours.append(c)
    x1 = one_w * 0.78 + ura.advance
    _chain(o, [(x1 - 50, HEAD + 8), (x1 + 70 * s.width, HEAD + 95), (x1 + 150 * s.width, HEAD + 62)], s.stem * 0.9, s)
    adv = x1 + 130 * s.width
    return GlyphOut("ekonkar", [0x0A74], o, adv, {"above": (adv * 0.6, HEAD + 80), "below": (adv * 0.5, -28)})


# ---------------------------------------------------------------------------
# Marks
# ---------------------------------------------------------------------------

def g_sihari(s: Style) -> GlyphOut:
    o = _o(s)
    h = HEAD + 170
    x = 68 * s.width
    o.vbar(x, BASE + 40, h, t=s.stem * 0.92)
    o.arc(x, h - 8, 68 * s.width, 56, 10, 175, t=s.hstem)
    adv = 145 * s.width if not s.mono else s.mono_width * 0.45
    return GlyphOut("sihari", [0x0A3F], o, adv, {}, gdef="mark")


def g_bihari(s: Style) -> GlyphOut:
    o = _o(s)
    x = 18
    o.vbar(x, BASE, HEAD + 170, t=s.stem * 0.92)
    o.arc(x, HEAD + 162, 76 * s.width, 58, 10, 170, t=s.hstem)
    return GlyphOut("bihari", [0x0A40], o, 108 * s.width if not s.mono else s.mono_width * 0.35, {"_mark": (x, HEAD + 40)}, gdef="mark")


def g_kanna(s: Style) -> GlyphOut:
    o = _o(s)
    o.vbar(s.stem * 0.55, BASE, HEAD, t=s.stem)
    if s.serif > 20:
        o.slab_serif(s.stem * 0.55, BASE, "bottom")
        o.slab_serif(s.stem * 0.55, HEAD, "top")
    adv = s.stem + s.side * 0.85
    return GlyphOut("kanna", [0x0A3E], o, adv if not s.mono else s.mono_width * 0.4, {}, gdef="mark")


def g_aunkar(s: Style) -> GlyphOut:
    o = _o(s)
    o.arc(0, 0, 60 * s.width, 40, 200, 340, t=s.hstem)
    return GlyphOut("aunkar", [0x0A41], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_dulainkar(s: Style) -> GlyphOut:
    o = _o(s)
    o.arc(0, 0, 68 * s.width, 44, 200, 350, t=s.hstem)
    o.stroke([(52 * s.width, 8), (76 * s.width, -50)], t=s.stem * 0.8, cap=_cap(s))
    return GlyphOut("dulainkar", [0x0A42], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_lanvan(s: Style) -> GlyphOut:
    o = _o(s)
    o.stroke([(0, 0), (60 * s.width, 76)], t=s.hstem, cap=_cap(s))
    return GlyphOut("lanvan", [0x0A47], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_dulanvan(s: Style) -> GlyphOut:
    o = _o(s)
    o.stroke([(-8, 0), (52 * s.width, 76)], t=s.hstem, cap=_cap(s))
    o.stroke([(16, 0), (76 * s.width, 76)], t=s.hstem, cap=_cap(s))
    return GlyphOut("dulanvan", [0x0A48], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_hora(s: Style) -> GlyphOut:
    o = _o(s)
    o.arc(0, 0, 70 * s.width, 48, 10, 170, t=s.hstem)
    return GlyphOut("hora", [0x0A4B], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_kanaura(s: Style) -> GlyphOut:
    # Above arc only; ccmp expands ੌ → ੋ + ਾ so the kanna sits after the letter.
    o = _o(s)
    o.arc(0, 0, 70 * s.width, 48, 10, 170, t=s.hstem)
    return GlyphOut("kanaura", [0x0A4C], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_virama(s: Style) -> GlyphOut:
    o = _o(s)
    o.stroke([(-28, 18), (34, -38)], t=s.thin, cap=_cap(s))
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
    o.arc(0, 8, 26, 20, 200, 340, t=s.hstem * 0.85)
    o.disc(0, -4, max(10.0, s.stem * 0.18))
    return GlyphOut("tippi", [0x0A70], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_addak(s: Style) -> GlyphOut:
    o = _o(s)
    o.arc(0, 0, 34, 26, 200, 20, t=s.hstem)
    o.arc(0, 8, 20, 14, 200, 20, t=s.thin)
    return GlyphOut("addak", [0x0A71], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_udaat(s: Style) -> GlyphOut:
    o = _o(s)
    o.stroke([(0, 0), (0, 70)], t=s.thin, cap=_cap(s))
    return GlyphOut("udaat", [0x0A51], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_yakash(s: Style) -> GlyphOut:
    o = _o(s)
    o.arc(0, 0, 38 * s.width, 26, 20, 200, t=s.hstem * 0.8)
    return GlyphOut("yakash", [0x0A75], o, 0, {"_mark": (0, 0)}, gdef="mark")


def g_abbrev(s: Style) -> GlyphOut:
    o = _o(s)
    o.stroke([(0, HEAD * 0.2), (40, HEAD * 0.7)], t=s.thin, cap=_cap(s))
    o.disc(48, HEAD * 0.78, max(10.0, s.stem * 0.18))
    return GlyphOut("abbrev", [0x0A76], o, 80 * s.width, {}, gdef="mark")


# ---------------------------------------------------------------------------
# Gurmukhi digits (not Devanagari numerals)
# ---------------------------------------------------------------------------

def g_digit(s: Style, n: int) -> GlyphOut:
    b, o = Box(s, 460 if not s.mono else 500), _o(s)
    cx, cy = (b.left + b.right) / 2.0, HEAD * 0.42
    t = b.stem_t
    names = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    cps = list(range(0x0A66, 0x0A70))
    if n == 0:
        o.ring(cx, cy, b.body * 0.32, HEAD * 0.34 + s.overshoot, t=t)
    elif n == 1:
        # ੧ — loop like a 9, stem down
        o.arc(cx - 8, cy + 70, b.body * 0.22, HEAD * 0.16, 40, 320, t=t, cap=_cap(s))
        _stroke(o, [(cx + b.body * 0.12, cy + 70), (cx + b.body * 0.08, b.base + 16)], t, s)
    elif n == 2:
        o.arc(cx, cy + 90, b.body * 0.26, HEAD * 0.14, 200, 20, t=t, cap=_cap(s))
        _stroke(o, [(cx + b.body * 0.20, cy + 78), (cx - b.body * 0.20, b.base + 28)], t, s)
        o.hbar(cx - b.body * 0.22, cx + b.body * 0.22, b.base + 28, t=s.hstem)
    elif n == 3:
        o.arc(cx, cy + 88, b.body * 0.24, HEAD * 0.14, 200, 20, t=t, cap=_cap(s))
        o.arc(cx, cy - 30, b.body * 0.28, HEAD * 0.20, 20, 200, t=t, cap=_cap(s))
    elif n == 4:
        # ੪ — stacked rings, gap at the top (Gurmukhi four, not Devanagari ४)
        o.arc(cx, cy + 78, b.body * 0.22, HEAD * 0.15, 50, 310, t=t, cap=_cap(s))
        o.ring(cx, cy - 40, b.body * 0.24, HEAD * 0.18, t=t)
    elif n == 5:
        _stroke(o, [(cx + b.body * 0.16, cy + 118), (cx - b.body * 0.08, cy + 36), (cx + b.body * 0.10, b.base + 18)], t, s)
        o.arc(cx, cy + 100, b.body * 0.20, HEAD * 0.12, 200, 20, t=t, cap=_cap(s))
    elif n == 6:
        o.arc(cx, cy, b.body * 0.30, HEAD * 0.32, 40, 280, t=t, cap=_cap(s))
        o.disc(cx - b.body * 0.16, cy + 36, t * 0.42)
    elif n == 7:
        _stroke(o, [(cx - b.body * 0.20, cy + 108), (cx + b.body * 0.12, cy + 108), (cx - b.body * 0.04, b.base + 18)], t, s)
    elif n == 8:
        o.arc(cx, cy + 36, b.body * 0.26, HEAD * 0.28, 40, 140, t=t, cap=_cap(s))
        o.arc(cx, cy + 36, b.body * 0.26, HEAD * 0.28, 220, 320, t=t, cap=_cap(s))
    else:
        o.arc(cx, cy + 78, b.body * 0.24, HEAD * 0.16, 200, 20, t=t, cap=_cap(s))
        _stroke(o, [(cx + b.body * 0.18, cy + 62), (cx + b.body * 0.06, b.base + 28)], t, s)
        o.arc(cx, cy - 36, b.body * 0.26, HEAD * 0.18, 20, 160, t=t, cap=_cap(s))
    return GlyphOut(names[n], [cps[n]], o, b.adv, b.anchors())


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
    for g in glyphs:
        if g.unicodes:
            g.name = f"uni{g.unicodes[0]:04X}"
    return glyphs
