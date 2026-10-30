"""Companion Latin glyphs so mixed English/Punjabi text keeps one colour."""

from __future__ import annotations

from geom import Outline
from gurmukhi import Box, GlyphOut, _cap, _o
from style import BASE, HEAD, Style


CAP = 700.0
XH = 470.0


def _latin_box(s: Style, body: float) -> Box:
    return Box(s, body)


def _notdef(s: Style) -> GlyphOut:
    b, o = Box(s, 500), _o(s)
    o.rect(b.left, BASE, b.body, HEAD, r=s.corner)
    o.rect(b.left + s.stem, BASE + s.stem, b.body - 2 * s.stem, HEAD - 2 * s.stem, r=s.corner, hole=True)
    return GlyphOut(".notdef", [], o, b.adv, {})


def _space(s: Style) -> GlyphOut:
    adv = s.mono_width if s.mono else (280 if s.condensed else 320)
    return GlyphOut("space", [0x20, 0xA0], Outline(), adv, {}, gdef="base")


def _zwj(s: Style, cp: int, name: str) -> GlyphOut:
    return GlyphOut(name, [cp], Outline(), 0, {}, gdef="base")


def _period(s: Style) -> GlyphOut:
    o = _o(s)
    r = max(16.0, s.stem * 0.38)
    o.disc(s.side + r, r * 1.1, r)
    adv = s.side * 2 + r * 2 if not s.mono else s.mono_width
    return GlyphOut("period", [0x2E], o, adv, {})


def _comma(s: Style) -> GlyphOut:
    o = _o(s)
    r = max(16.0, s.stem * 0.36)
    x = s.side + r
    o.disc(x, r * 1.2, r)
    o.stroke([(x + 4, r), (x - 8, -r * 1.6)], t=s.stem * 0.7, cap=_cap(s))
    return GlyphOut("comma", [0x2C], o, s.side * 2 + r * 2 if not s.mono else s.mono_width, {})


def _colon(s: Style) -> GlyphOut:
    o = _o(s)
    r = max(15.0, s.stem * 0.34)
    x = s.side + r
    o.disc(x, XH * 0.28, r)
    o.disc(x, XH * 0.78, r)
    return GlyphOut("colon", [0x3A], o, s.side * 2 + r * 2 if not s.mono else s.mono_width, {})


def _semicolon(s: Style) -> GlyphOut:
    g = _comma(s)
    r = max(15.0, s.stem * 0.34)
    g.outline.disc(s.side + r, XH * 0.78, r)
    g.name, g.unicodes = "semicolon", [0x3B]
    return g


def _exclam(s: Style) -> GlyphOut:
    o = _o(s)
    x = s.side + s.stem
    o.vbar(x, BASE + s.stem * 1.8, CAP, t=s.stem)
    o.disc(x, s.stem * 0.42, s.stem * 0.42)
    return GlyphOut("exclam", [0x21], o, s.stem + s.side * 2 if not s.mono else s.mono_width, {})


def _question(s: Style) -> GlyphOut:
    b, o = Box(s, 420), _o(s)
    o.arc(b.left + b.body * 0.48, CAP * 0.72, b.body * 0.32, CAP * 0.22, 180, 10, t=s.stem)
    o.vbar(b.left + b.body * 0.55, BASE + s.stem * 2.2, CAP * 0.52, t=s.stem)
    o.disc(b.left + b.body * 0.55, s.stem * 0.42, s.stem * 0.42)
    return GlyphOut("question", [0x3F], o, b.adv, {})


def _hyphen(s: Style) -> GlyphOut:
    o = _o(s)
    w = 220 * s.width
    o.hbar(s.side, s.side + w, XH * 0.52, t=s.hstem)
    return GlyphOut("hyphen", [0x2D, 0x2010, 0x2013], o, w + s.side * 2 if not s.mono else s.mono_width, {})


def _slash(s: Style, name: str, cp: int, flip: bool = False) -> GlyphOut:
    o = _o(s)
    w = 280 * s.width
    if flip:
        o.stroke([(s.side, CAP), (s.side + w, BASE)], t=s.thin, cap=_cap(s))
    else:
        o.stroke([(s.side, BASE), (s.side + w, CAP)], t=s.thin, cap=_cap(s))
    return GlyphOut(name, [cp], o, w + s.side * 2 if not s.mono else s.mono_width, {})


def _angle(s: Style, name: str, cp: int, opening_left: bool) -> GlyphOut:
    o = _o(s)
    w = 280 * s.width
    mid = CAP * 0.5
    if opening_left:
        o.stroke([(s.side + w, CAP * 0.18), (s.side + 8, mid)], t=s.stem, cap=_cap(s))
        o.stroke([(s.side + 8, mid), (s.side + w, CAP * 0.82)], t=s.stem, cap=_cap(s))
    else:
        o.stroke([(s.side, CAP * 0.18), (s.side + w - 8, mid)], t=s.stem, cap=_cap(s))
        o.stroke([(s.side + w - 8, mid), (s.side, CAP * 0.82)], t=s.stem, cap=_cap(s))
    return GlyphOut(name, [cp], o, w + s.side * 2 if not s.mono else s.mono_width, {})


def _paren(s: Style, left: bool) -> GlyphOut:
    o = _o(s)
    cx = s.side + 70 * s.width
    if left:
        o.arc(cx + 40, CAP * 0.5, 80 * s.width, CAP * 0.52, 110, 250, t=s.stem)
        name, cp = "parenleft", 0x28
    else:
        o.arc(cx, CAP * 0.5, 80 * s.width, CAP * 0.52, 290, 430, t=s.stem)
        name, cp = "parenright", 0x29
    return GlyphOut(name, [cp], o, 180 * s.width if not s.mono else s.mono_width, {})


def _quotes(s: Style, name: str, cps: list[int], n: int = 1) -> GlyphOut:
    o = _o(s)
    r = s.stem * 0.4
    for i in range(n):
        o.rect(s.side + i * (r * 2.2), CAP - 80, r * 1.1, 70, r=s.corner)
    adv = s.side * 2 + n * r * 2.4
    return GlyphOut(name, cps, o, adv if not s.mono else s.mono_width, {})


def _cap_I(s: Style) -> GlyphOut:
    b, o = Box(s, 280 if not s.mono else 420), _o(s)
    o.vbar((b.left + b.right) / 2, BASE, CAP, t=s.stem)
    if s.serif > 10:
        o.hbar(b.left, b.right, CAP, t=s.hstem)
        o.hbar(b.left, b.right, BASE, t=s.hstem)
    return GlyphOut("I", [0x49], o, b.adv, {})


def _cap_H(s: Style) -> GlyphOut:
    b, o = Box(s, 560), _o(s)
    o.vbar(b.left + s.stem / 2, BASE, CAP, t=s.stem)
    o.vbar(b.right - s.stem / 2, BASE, CAP, t=s.stem)
    o.hbar(b.left, b.right, CAP * 0.52, t=s.hstem)
    return GlyphOut("H", [0x48], o, b.adv, {})


def _cap_L(s: Style) -> GlyphOut:
    b, o = Box(s, 480), _o(s)
    o.vbar(b.left + s.stem / 2, BASE, CAP, t=s.stem)
    o.hbar(b.left, b.right, BASE + s.hstem / 2, t=s.hstem)
    return GlyphOut("L", [0x4C], o, b.adv, {})


def _cap_T(s: Style) -> GlyphOut:
    b, o = Box(s, 520), _o(s)
    o.hbar(b.left, b.right, CAP, t=s.bar)
    o.vbar((b.left + b.right) / 2, BASE, CAP, t=s.stem)
    return GlyphOut("T", [0x54], o, b.adv, {})


def _cap_E(s: Style) -> GlyphOut:
    b, o = Box(s, 500), _o(s)
    o.vbar(b.left + s.stem / 2, BASE, CAP, t=s.stem)
    o.hbar(b.left, b.right, CAP, t=s.bar)
    o.hbar(b.left, b.left + b.body * 0.78, CAP * 0.52, t=s.hstem)
    o.hbar(b.left, b.right, BASE + s.hstem / 2, t=s.hstem)
    return GlyphOut("E", [0x45], o, b.adv, {})


def _cap_F(s: Style) -> GlyphOut:
    g = _cap_E(s)
    # remove bottom bar by rebuilding
    b, o = Box(s, 500), _o(s)
    o.vbar(b.left + s.stem / 2, BASE, CAP, t=s.stem)
    o.hbar(b.left, b.right, CAP, t=s.bar)
    o.hbar(b.left, b.left + b.body * 0.78, CAP * 0.52, t=s.hstem)
    return GlyphOut("F", [0x46], o, b.adv, {})


def _cap_O(s: Style) -> GlyphOut:
    b, o = Box(s, 600), _o(s)
    cx, cy = (b.left + b.right) / 2, CAP * 0.5
    o.ring(cx, cy, b.body * 0.46, CAP * 0.48 + s.overshoot, t=s.stem)
    return GlyphOut("O", [0x4F], o, b.adv, {})


def _cap_C(s: Style) -> GlyphOut:
    b, o = Box(s, 560), _o(s)
    cx, cy = (b.left + b.right) / 2 + 10, CAP * 0.5
    o.arc(cx, cy, b.body * 0.44, CAP * 0.48, 50, 310, t=s.stem, cap=_cap(s))
    return GlyphOut("C", [0x43], o, b.adv, {})


def _cap_G(s: Style) -> GlyphOut:
    g = _cap_C(s)
    b = Box(s, 560)
    g.outline.hbar(b.left + b.body * 0.50, b.right - 8, CAP * 0.42, t=s.hstem)
    g.outline.vbar(b.right - s.stem, BASE + 40, CAP * 0.42, t=s.stem)
    g.name, g.unicodes = "G", [0x47]
    return g


def _cap_S(s: Style) -> GlyphOut:
    b, o = Box(s, 500), _o(s)
    o.arc(b.left + b.body * 0.50, CAP * 0.72, b.body * 0.34, CAP * 0.22, 40, 230, t=s.stem, cap=_cap(s))
    o.arc(b.left + b.body * 0.50, CAP * 0.28, b.body * 0.34, CAP * 0.22, 220, 410, t=s.stem, cap=_cap(s))
    return GlyphOut("S", [0x53], o, b.adv, {})


def _cap_U(s: Style) -> GlyphOut:
    b, o = Box(s, 560), _o(s)
    o.vbar(b.left + s.stem / 2, CAP * 0.38, CAP, t=s.stem)
    o.vbar(b.right - s.stem / 2, CAP * 0.38, CAP, t=s.stem)
    o.arc((b.left + b.right) / 2, CAP * 0.38, b.body * 0.42, CAP * 0.32, 200, 340, t=s.stem, cap=_cap(s))
    return GlyphOut("U", [0x55], o, b.adv, {})


def _cap_V(s: Style) -> GlyphOut:
    b, o = Box(s, 560), _o(s)
    m = (b.left + b.right) / 2
    o.stroke([(b.left + 8, CAP), (m, BASE)], t=s.stem, cap=_cap(s))
    o.stroke([(b.right - 8, CAP), (m, BASE)], t=s.stem, cap=_cap(s))
    return GlyphOut("V", [0x56], o, b.adv, {})


def _cap_A(s: Style) -> GlyphOut:
    b, o = Box(s, 580), _o(s)
    m = (b.left + b.right) / 2
    o.stroke([(b.left + 8, BASE), (m, CAP)], t=s.stem, cap=_cap(s))
    o.stroke([(b.right - 8, BASE), (m, CAP)], t=s.stem, cap=_cap(s))
    o.hbar(b.left + b.body * 0.22, b.right - b.body * 0.22, CAP * 0.38, t=s.hstem)
    return GlyphOut("A", [0x41], o, b.adv, {})


def _cap_N(s: Style) -> GlyphOut:
    b, o = Box(s, 580), _o(s)
    o.vbar(b.left + s.stem / 2, BASE, CAP, t=s.stem)
    o.vbar(b.right - s.stem / 2, BASE, CAP, t=s.stem)
    o.stroke([(b.left + s.stem / 2, CAP), (b.right - s.stem / 2, BASE)], t=s.stem, cap=_cap(s))
    return GlyphOut("N", [0x4E], o, b.adv, {})


def _cap_M(s: Style) -> GlyphOut:
    b, o = Box(s, 680), _o(s)
    o.vbar(b.left + s.stem / 2, BASE, CAP, t=s.stem)
    o.vbar(b.right - s.stem / 2, BASE, CAP, t=s.stem)
    m = (b.left + b.right) / 2
    o.stroke([(b.left + s.stem / 2, CAP), (m, BASE + CAP * 0.18)], t=s.stem, cap=_cap(s))
    o.stroke([(b.right - s.stem / 2, CAP), (m, BASE + CAP * 0.18)], t=s.stem, cap=_cap(s))
    return GlyphOut("M", [0x4D], o, b.adv, {})


def _cap_W(s: Style) -> GlyphOut:
    b, o = Box(s, 720), _o(s)
    m = (b.left + b.right) / 2
    q1 = b.left + b.body * 0.28
    q2 = b.left + b.body * 0.72
    o.stroke([(b.left, CAP), (q1, BASE)], t=s.stem, cap=_cap(s))
    o.stroke([(m, CAP * 0.55), (q1, BASE)], t=s.stem, cap=_cap(s))
    o.stroke([(m, CAP * 0.55), (q2, BASE)], t=s.stem, cap=_cap(s))
    o.stroke([(b.right, CAP), (q2, BASE)], t=s.stem, cap=_cap(s))
    return GlyphOut("W", [0x57], o, b.adv, {})


def _cap_Y(s: Style) -> GlyphOut:
    b, o = Box(s, 560), _o(s)
    m = (b.left + b.right) / 2
    o.stroke([(b.left + 8, CAP), (m, CAP * 0.48)], t=s.stem, cap=_cap(s))
    o.stroke([(b.right - 8, CAP), (m, CAP * 0.48)], t=s.stem, cap=_cap(s))
    o.vbar(m, BASE, CAP * 0.48, t=s.stem)
    return GlyphOut("Y", [0x59], o, b.adv, {})


def _cap_X(s: Style) -> GlyphOut:
    b, o = Box(s, 540), _o(s)
    o.stroke([(b.left + 8, CAP), (b.right - 8, BASE)], t=s.stem, cap=_cap(s))
    o.stroke([(b.right - 8, CAP), (b.left + 8, BASE)], t=s.stem, cap=_cap(s))
    return GlyphOut("X", [0x58], o, b.adv, {})


def _cap_Z(s: Style) -> GlyphOut:
    b, o = Box(s, 520), _o(s)
    o.hbar(b.left, b.right, CAP, t=s.bar)
    o.hbar(b.left, b.right, BASE + s.hstem / 2, t=s.hstem)
    o.stroke([(b.right - 8, CAP), (b.left + 8, BASE)], t=s.stem, cap=_cap(s))
    return GlyphOut("Z", [0x5A], o, b.adv, {})


def _cap_K(s: Style) -> GlyphOut:
    b, o = Box(s, 560), _o(s)
    o.vbar(b.left + s.stem / 2, BASE, CAP, t=s.stem)
    o.stroke([(b.left + s.stem, CAP * 0.48), (b.right - 8, CAP)], t=s.stem, cap=_cap(s))
    o.stroke([(b.left + s.stem, CAP * 0.48), (b.right - 8, BASE)], t=s.stem, cap=_cap(s))
    return GlyphOut("K", [0x4B], o, b.adv, {})


def _cap_R(s: Style) -> GlyphOut:
    b, o = Box(s, 560), _o(s)
    o.vbar(b.left + s.stem / 2, BASE, CAP, t=s.stem)
    o.arc(b.left + b.body * 0.42, CAP * 0.74, b.body * 0.36, CAP * 0.24, 270, 90, t=s.stem)
    o.hbar(b.left, b.left + b.body * 0.42, CAP, t=s.bar)
    o.hbar(b.left, b.left + b.body * 0.42, CAP * 0.52, t=s.hstem)
    o.stroke([(b.left + b.body * 0.40, CAP * 0.52), (b.right - 6, BASE)], t=s.stem, cap=_cap(s))
    return GlyphOut("R", [0x52], o, b.adv, {})


def _cap_P(s: Style) -> GlyphOut:
    b, o = Box(s, 520), _o(s)
    o.vbar(b.left + s.stem / 2, BASE, CAP, t=s.stem)
    o.arc(b.left + b.body * 0.42, CAP * 0.74, b.body * 0.36, CAP * 0.24, 270, 90, t=s.stem)
    o.hbar(b.left, b.left + b.body * 0.42, CAP, t=s.bar)
    o.hbar(b.left, b.left + b.body * 0.42, CAP * 0.52, t=s.hstem)
    return GlyphOut("P", [0x50], o, b.adv, {})


def _cap_B(s: Style) -> GlyphOut:
    b, o = Box(s, 540), _o(s)
    o.vbar(b.left + s.stem / 2, BASE, CAP, t=s.stem)
    o.arc(b.left + b.body * 0.40, CAP * 0.76, b.body * 0.32, CAP * 0.20, 270, 90, t=s.stem)
    o.arc(b.left + b.body * 0.42, CAP * 0.28, b.body * 0.36, CAP * 0.24, 270, 90, t=s.stem)
    o.hbar(b.left, b.left + b.body * 0.40, CAP, t=s.bar)
    o.hbar(b.left, b.left + b.body * 0.40, CAP * 0.52, t=s.hstem)
    o.hbar(b.left, b.left + b.body * 0.42, BASE + s.hstem / 2, t=s.hstem)
    return GlyphOut("B", [0x42], o, b.adv, {})


def _cap_D(s: Style) -> GlyphOut:
    b, o = Box(s, 580), _o(s)
    o.vbar(b.left + s.stem / 2, BASE, CAP, t=s.stem)
    o.arc(b.left + s.stem, CAP * 0.5, b.body * 0.62, CAP * 0.48, 270, 90, t=s.stem)
    o.hbar(b.left, b.left + s.stem + 20, CAP, t=s.bar)
    o.hbar(b.left, b.left + s.stem + 20, BASE + s.hstem / 2, t=s.hstem)
    return GlyphOut("D", [0x44], o, b.adv, {})


def _cap_J(s: Style) -> GlyphOut:
    b, o = Box(s, 480), _o(s)
    o.vbar(b.right - s.stem / 2, CAP * 0.32, CAP, t=s.stem)
    o.arc(b.left + b.body * 0.48, CAP * 0.32, b.body * 0.40, CAP * 0.28, 200, 340, t=s.stem, cap=_cap(s))
    o.hbar(b.left + b.body * 0.25, b.right, CAP, t=s.bar)
    return GlyphOut("J", [0x4A], o, b.adv, {})


def _cap_Q(s: Style) -> GlyphOut:
    g = _cap_O(s)
    b = Box(s, 600)
    g.outline.stroke([(b.left + b.body * 0.58, CAP * 0.28), (b.right - 4, BASE - 10)], t=s.stem, cap=_cap(s))
    g.name, g.unicodes = "Q", [0x51]
    return g


def _lc_from_cap(g: GlyphOut, name: str, cp: int, scale_y: float = 0.68) -> GlyphOut:
    """Very rough lowercase: reuse cap at x-height. Better than tofu."""
    o = Outline(stem=g.outline.stem, roundness=g.outline.roundness, corner=g.outline.corner, serif=g.outline.serif)
    factor = XH / CAP
    for c in g.outline.contours:
        o.contours.append([(x, BASE + (y - BASE) * factor) for x, y in c])
    return GlyphOut(name, [cp], o, g.advance, {})


def _lc_o(s: Style) -> GlyphOut:
    b, o = Box(s, 500), _o(s)
    o.ring((b.left + b.right) / 2, XH * 0.5, b.body * 0.42, XH * 0.48 + s.overshoot, t=s.stem)
    return GlyphOut("o", [0x6F], o, b.adv, {})


def _lc_n(s: Style) -> GlyphOut:
    b, o = Box(s, 500), _o(s)
    o.vbar(b.left + s.stem / 2, BASE, XH, t=s.stem)
    o.arc(b.left + b.body * 0.50, XH * 0.62, b.body * 0.38, XH * 0.38, 0, 180, t=s.stem)
    o.vbar(b.right - s.stem / 2, BASE, XH * 0.62, t=s.stem)
    return GlyphOut("n", [0x6E], o, b.adv, {})


def _lc_h(s: Style) -> GlyphOut:
    g = _lc_n(s)
    b = Box(s, 500)
    g.outline.vbar(b.left + s.stem / 2, BASE, CAP, t=s.stem)
    g.name, g.unicodes = "h", [0x68]
    return g


def _lc_u(s: Style) -> GlyphOut:
    b, o = Box(s, 500), _o(s)
    o.vbar(b.left + s.stem / 2, XH * 0.38, XH, t=s.stem)
    o.vbar(b.right - s.stem / 2, BASE, XH, t=s.stem)
    o.arc((b.left + b.right) / 2, XH * 0.38, b.body * 0.38, XH * 0.32, 200, 340, t=s.stem)
    return GlyphOut("u", [0x75], o, b.adv, {})


def _lc_m(s: Style) -> GlyphOut:
    b, o = Box(s, 740), _o(s)
    o.vbar(b.left + s.stem / 2, BASE, XH, t=s.stem)
    third = b.body / 3
    o.arc(b.left + third, XH * 0.62, third * 0.7, XH * 0.38, 0, 180, t=s.stem)
    o.vbar(b.left + third + s.stem / 2, BASE, XH * 0.62, t=s.stem)
    o.arc(b.left + 2 * third, XH * 0.62, third * 0.7, XH * 0.38, 0, 180, t=s.stem)
    o.vbar(b.right - s.stem / 2, BASE, XH * 0.62, t=s.stem)
    return GlyphOut("m", [0x6D], o, b.adv, {})


def _lc_r(s: Style) -> GlyphOut:
    b, o = Box(s, 380), _o(s)
    o.vbar(b.left + s.stem / 2, BASE, XH, t=s.stem)
    o.arc(b.left + b.body * 0.48, XH * 0.72, b.body * 0.40, XH * 0.26, 10, 170, t=s.stem, cap=_cap(s))
    return GlyphOut("r", [0x72], o, b.adv, {})


def _lc_i(s: Style) -> GlyphOut:
    b, o = Box(s, 240 if not s.mono else 400), _o(s)
    x = (b.left + b.right) / 2
    o.vbar(x, BASE, XH, t=s.stem)
    o.disc(x, XH + s.stem * 0.85, s.stem * 0.38)
    return GlyphOut("i", [0x69], o, b.adv, {})


def _lc_l(s: Style) -> GlyphOut:
    b, o = Box(s, 240 if not s.mono else 400), _o(s)
    o.vbar((b.left + b.right) / 2, BASE, CAP, t=s.stem)
    return GlyphOut("l", [0x6C], o, b.adv, {})


def _lc_t(s: Style) -> GlyphOut:
    b, o = Box(s, 360), _o(s)
    o.vbar((b.left + b.right) / 2, BASE, CAP * 0.82, t=s.stem)
    o.hbar(b.left, b.right, XH, t=s.hstem)
    return GlyphOut("t", [0x74], o, b.adv, {})


def _lc_f(s: Style) -> GlyphOut:
    b, o = Box(s, 380), _o(s)
    o.vbar(b.left + b.body * 0.45, BASE, CAP * 0.78, t=s.stem)
    o.arc(b.left + b.body * 0.55, CAP * 0.82, b.body * 0.32, CAP * 0.16, 10, 170, t=s.stem, cap=_cap(s))
    o.hbar(b.left, b.right, XH, t=s.hstem)
    return GlyphOut("f", [0x66], o, b.adv, {})


def _lc_j(s: Style) -> GlyphOut:
    b, o = Box(s, 280), _o(s)
    x = (b.left + b.right) / 2
    o.vbar(x, BASE + 40, XH, t=s.stem)
    o.arc(x - 40 * s.width, BASE + 40, 50 * s.width, 70, 200, 340, t=s.stem, cap=_cap(s))
    o.disc(x, XH + s.stem * 0.85, s.stem * 0.38)
    return GlyphOut("j", [0x6A], o, b.adv, {})


def _lc_a(s: Style) -> GlyphOut:
    b, o = Box(s, 500), _o(s)
    o.ring(b.left + b.body * 0.42, XH * 0.48, b.body * 0.36, XH * 0.42, t=s.stem)
    o.vbar(b.right - s.stem / 2, BASE, XH * 0.78, t=s.stem)
    return GlyphOut("a", [0x61], o, b.adv, {})


def _lc_e(s: Style) -> GlyphOut:
    b, o = Box(s, 500), _o(s)
    o.arc((b.left + b.right) / 2, XH * 0.50, b.body * 0.40, XH * 0.46, 20, 330, t=s.stem, cap=_cap(s))
    o.hbar(b.left + b.body * 0.12, b.right - b.body * 0.12, XH * 0.52, t=s.hstem)
    return GlyphOut("e", [0x65], o, b.adv, {})


def _lc_c(s: Style) -> GlyphOut:
    b, o = Box(s, 480), _o(s)
    o.arc((b.left + b.right) / 2 + 8, XH * 0.5, b.body * 0.40, XH * 0.46, 50, 310, t=s.stem, cap=_cap(s))
    return GlyphOut("c", [0x63], o, b.adv, {})


def _lc_s(s: Style) -> GlyphOut:
    b, o = Box(s, 440), _o(s)
    o.arc(b.left + b.body * 0.50, XH * 0.72, b.body * 0.32, XH * 0.22, 40, 230, t=s.stem, cap=_cap(s))
    o.arc(b.left + b.body * 0.50, XH * 0.28, b.body * 0.32, XH * 0.22, 220, 410, t=s.stem, cap=_cap(s))
    return GlyphOut("s", [0x73], o, b.adv, {})


def _lc_b(s: Style) -> GlyphOut:
    b, o = Box(s, 500), _o(s)
    o.vbar(b.left + s.stem / 2, BASE, CAP, t=s.stem)
    o.ring(b.left + b.body * 0.52, XH * 0.48, b.body * 0.36, XH * 0.44, t=s.stem)
    return GlyphOut("b", [0x62], o, b.adv, {})


def _lc_d(s: Style) -> GlyphOut:
    b, o = Box(s, 500), _o(s)
    o.vbar(b.right - s.stem / 2, BASE, CAP, t=s.stem)
    o.ring(b.left + b.body * 0.42, XH * 0.48, b.body * 0.36, XH * 0.44, t=s.stem)
    return GlyphOut("d", [0x64], o, b.adv, {})


def _lc_p(s: Style) -> GlyphOut:
    b, o = Box(s, 500), _o(s)
    o.vbar(b.left + s.stem / 2, -180, XH, t=s.stem)
    o.ring(b.left + b.body * 0.52, XH * 0.48, b.body * 0.36, XH * 0.44, t=s.stem)
    return GlyphOut("p", [0x70], o, b.adv, {})


def _lc_q(s: Style) -> GlyphOut:
    b, o = Box(s, 500), _o(s)
    o.vbar(b.right - s.stem / 2, -180, XH, t=s.stem)
    o.ring(b.left + b.body * 0.42, XH * 0.48, b.body * 0.36, XH * 0.44, t=s.stem)
    return GlyphOut("q", [0x71], o, b.adv, {})


def _lc_g(s: Style) -> GlyphOut:
    b, o = Box(s, 500), _o(s)
    o.ring(b.left + b.body * 0.45, XH * 0.52, b.body * 0.36, XH * 0.42, t=s.stem)
    o.vbar(b.right - s.stem / 2, -40, XH * 0.52, t=s.stem)
    o.arc(b.left + b.body * 0.48, -20, b.body * 0.36, 90, 200, 20, t=s.stem, cap=_cap(s))
    return GlyphOut("g", [0x67], o, b.adv, {})


def _lc_k(s: Style) -> GlyphOut:
    b, o = Box(s, 500), _o(s)
    o.vbar(b.left + s.stem / 2, BASE, CAP, t=s.stem)
    o.stroke([(b.left + s.stem, XH * 0.5), (b.right - 8, XH)], t=s.stem, cap=_cap(s))
    o.stroke([(b.left + s.stem * 1.4, XH * 0.48), (b.right - 8, BASE)], t=s.stem, cap=_cap(s))
    return GlyphOut("k", [0x6B], o, b.adv, {})


def _lc_v(s: Style) -> GlyphOut:
    b, o = Box(s, 480), _o(s)
    m = (b.left + b.right) / 2
    o.stroke([(b.left + 6, XH), (m, BASE)], t=s.stem, cap=_cap(s))
    o.stroke([(b.right - 6, XH), (m, BASE)], t=s.stem, cap=_cap(s))
    return GlyphOut("v", [0x76], o, b.adv, {})


def _lc_w(s: Style) -> GlyphOut:
    b, o = Box(s, 680), _o(s)
    m = (b.left + b.right) / 2
    q1 = b.left + b.body * 0.28
    q2 = b.left + b.body * 0.72
    o.stroke([(b.left, XH), (q1, BASE)], t=s.stem, cap=_cap(s))
    o.stroke([(m, XH * 0.55), (q1, BASE)], t=s.stem, cap=_cap(s))
    o.stroke([(m, XH * 0.55), (q2, BASE)], t=s.stem, cap=_cap(s))
    o.stroke([(b.right, XH), (q2, BASE)], t=s.stem, cap=_cap(s))
    return GlyphOut("w", [0x77], o, b.adv, {})


def _lc_x(s: Style) -> GlyphOut:
    b, o = Box(s, 480), _o(s)
    o.stroke([(b.left + 6, XH), (b.right - 6, BASE)], t=s.stem, cap=_cap(s))
    o.stroke([(b.right - 6, XH), (b.left + 6, BASE)], t=s.stem, cap=_cap(s))
    return GlyphOut("x", [0x78], o, b.adv, {})


def _lc_y(s: Style) -> GlyphOut:
    b, o = Box(s, 480), _o(s)
    m = (b.left + b.right) / 2
    o.stroke([(b.left + 6, XH), (m, BASE + 40)], t=s.stem, cap=_cap(s))
    o.stroke([(b.right - 6, XH), (m - 10, -160)], t=s.stem, cap=_cap(s))
    return GlyphOut("y", [0x79], o, b.adv, {})


def _lc_z(s: Style) -> GlyphOut:
    b, o = Box(s, 460), _o(s)
    o.hbar(b.left, b.right, XH, t=s.hstem)
    o.hbar(b.left, b.right, BASE + s.hstem / 2, t=s.hstem)
    o.stroke([(b.right - 6, XH), (b.left + 6, BASE)], t=s.stem, cap=_cap(s))
    return GlyphOut("z", [0x7A], o, b.adv, {})


def _digit_latin(s: Style, ch: str) -> GlyphOut:
    """Western digits, geometric enough to match each family."""
    b, o = Box(s, 500), _o(s)
    cx, cy = (b.left + b.right) / 2, CAP * 0.5
    t = s.stem
    n = int(ch)
    if n == 0:
        o.ring(cx, cy, b.body * 0.36, CAP * 0.42 + s.overshoot, t=t)
    elif n == 1:
        o.vbar(cx, BASE, CAP, t=t)
        o.stroke([(cx, CAP), (cx - b.body * 0.22, CAP - 80)], t=t, cap=_cap(s))
        o.hbar(cx - b.body * 0.22, cx + b.body * 0.22, BASE + s.hstem / 2, t=s.hstem)
    elif n == 2:
        o.arc(cx, CAP * 0.72, b.body * 0.32, CAP * 0.22, 180, 20, t=t, cap=_cap(s))
        o.stroke([(cx + b.body * 0.28, CAP * 0.64), (b.left + 20, BASE + s.hstem)], t=t, cap=_cap(s))
        o.hbar(b.left, b.right, BASE + s.hstem / 2, t=s.hstem)
    elif n == 3:
        o.arc(cx, CAP * 0.72, b.body * 0.30, CAP * 0.20, 200, 20, t=t, cap=_cap(s))
        o.arc(cx, CAP * 0.28, b.body * 0.32, CAP * 0.24, 20, 200, t=t, cap=_cap(s))
    elif n == 4:
        o.stroke([(cx + 20, CAP), (b.left + 20, CAP * 0.38)], t=t, cap=_cap(s))
        o.hbar(b.left + 10, b.right - 10, CAP * 0.38, t=s.hstem)
        o.vbar(cx + 30, BASE, CAP * 0.55, t=t)
    elif n == 5:
        o.hbar(b.left + 10, b.right - 20, CAP, t=s.bar)
        o.vbar(b.left + s.stem, CAP * 0.48, CAP, t=t)
        o.arc(cx, CAP * 0.32, b.body * 0.34, CAP * 0.26, 200, 40, t=t, cap=_cap(s))
    elif n == 6:
        o.arc(cx, cy, b.body * 0.34, CAP * 0.42, 50, 280, t=t, cap=_cap(s))
        o.ring(cx, CAP * 0.32, b.body * 0.26, CAP * 0.20, t=t)
    elif n == 7:
        o.hbar(b.left, b.right, CAP, t=s.bar)
        o.stroke([(b.right - 12, CAP), (b.left + b.body * 0.28, BASE)], t=t, cap=_cap(s))
    elif n == 8:
        o.ring(cx, CAP * 0.72, b.body * 0.28, CAP * 0.20, t=t)
        o.ring(cx, CAP * 0.28, b.body * 0.32, CAP * 0.24, t=t)
    else:
        o.ring(cx, CAP * 0.70, b.body * 0.28, CAP * 0.20, t=t)
        o.arc(cx, cy, b.body * 0.34, CAP * 0.42, 260, 40, t=t, cap=_cap(s))
    return GlyphOut(f"digit{n}", [ord(ch)], o, b.adv, {})


def all_latin(s: Style) -> list[GlyphOut]:
    glyphs: list[GlyphOut] = [
        _notdef(s),
        _space(s),
        _zwj(s, 0x200C, "zwnj"),
        _zwj(s, 0x200D, "zwj"),
        _period(s),
        _comma(s),
        _colon(s),
        _semicolon(s),
        _exclam(s),
        _question(s),
        _hyphen(s),
        _slash(s, "slash", 0x2F),
        _slash(s, "backslash", 0x5C, True),
        _angle(s, "less", 0x3C, True),
        _angle(s, "greater", 0x3E, False),
        _paren(s, True),
        _paren(s, False),
        _quotes(s, "quotedbl", [0x22], 2),
        _quotes(s, "quotesingle", [0x27], 1),
        GlyphOut("numbersign", [0x23], _o(s), Box(s, 500).adv, {}),
        GlyphOut("dollar", [0x24], _o(s), Box(s, 500).adv, {}),
        GlyphOut("percent", [0x25], _o(s), Box(s, 540).adv, {}),
        GlyphOut("ampersand", [0x26], _o(s), Box(s, 600).adv, {}),
        GlyphOut("asterisk", [0x2A], _o(s), Box(s, 400).adv, {}),
        GlyphOut("plus", [0x2B], _o(s), Box(s, 500).adv, {}),
        GlyphOut("equal", [0x3D], _o(s), Box(s, 500).adv, {}),
        GlyphOut("at", [0x40], _o(s), Box(s, 700).adv, {}),
        GlyphOut("bracketleft", [0x5B], _o(s), Box(s, 280).adv, {}),
        GlyphOut("bracketright", [0x5D], _o(s), Box(s, 280).adv, {}),
        GlyphOut("asciicircum", [0x5E], _o(s), Box(s, 400).adv, {}),
        GlyphOut("underscore", [0x5F], _o(s), Box(s, 500).adv, {}),
        GlyphOut("grave", [0x60], _o(s), Box(s, 300).adv, {}),
        GlyphOut("braceleft", [0x7B], _o(s), Box(s, 320).adv, {}),
        GlyphOut("bar", [0x7C], _o(s), Box(s, 220).adv, {}),
        GlyphOut("braceright", [0x7D], _o(s), Box(s, 320).adv, {}),
        GlyphOut("asciitilde", [0x7E], _o(s), Box(s, 500).adv, {}),
        _cap_A(s), _cap_B(s), _cap_C(s), _cap_D(s), _cap_E(s), _cap_F(s),
        _cap_G(s), _cap_H(s), _cap_I(s), _cap_J(s), _cap_K(s), _cap_L(s),
        _cap_M(s), _cap_N(s), _cap_O(s), _cap_P(s), _cap_Q(s), _cap_R(s),
        _cap_S(s), _cap_T(s), _cap_U(s), _cap_V(s), _cap_W(s), _cap_X(s),
        _cap_Y(s), _cap_Z(s),
        _lc_a(s), _lc_b(s), _lc_c(s), _lc_d(s), _lc_e(s), _lc_f(s), _lc_g(s),
        _lc_h(s), _lc_i(s), _lc_j(s), _lc_k(s), _lc_l(s), _lc_m(s), _lc_n(s),
        _lc_o(s), _lc_p(s), _lc_q(s), _lc_r(s), _lc_s(s), _lc_t(s), _lc_u(s),
        _lc_v(s), _lc_w(s), _lc_x(s), _lc_y(s), _lc_z(s),
    ]
    # simple remaining symbols
    for g in glyphs:
        if g.name == "numbersign":
            b = Box(s, 500)
            g.outline.vbar(b.left + b.body * 0.35, BASE + 40, CAP - 20, t=s.thin)
            g.outline.vbar(b.left + b.body * 0.65, BASE + 40, CAP - 20, t=s.thin)
            g.outline.hbar(b.left, b.right, CAP * 0.62, t=s.hstem)
            g.outline.hbar(b.left, b.right, CAP * 0.38, t=s.hstem)
        elif g.name == "plus":
            b = Box(s, 500)
            g.outline.vbar((b.left + b.right) / 2, CAP * 0.2, CAP * 0.8, t=s.stem)
            g.outline.hbar(b.left + 20, b.right - 20, CAP * 0.5, t=s.hstem)
        elif g.name == "equal":
            b = Box(s, 500)
            g.outline.hbar(b.left + 20, b.right - 20, CAP * 0.58, t=s.hstem)
            g.outline.hbar(b.left + 20, b.right - 20, CAP * 0.38, t=s.hstem)
        elif g.name == "asterisk":
            b = Box(s, 400)
            cx, cy = (b.left + b.right) / 2, CAP * 0.62
            for ang in range(0, 180, 60):
                import math
                dx = math.cos(math.radians(ang)) * 70
                dy = math.sin(math.radians(ang)) * 70
                g.outline.stroke([(cx - dx, cy - dy), (cx + dx, cy + dy)], t=s.thin, cap=_cap(s))
        elif g.name == "underscore":
            b = Box(s, 500)
            g.outline.hbar(b.left, b.right, -40, t=s.hstem)
        elif g.name == "bar":
            b = Box(s, 220)
            g.outline.vbar((b.left + b.right) / 2, BASE - 40, CAP + 40, t=s.thin)
        elif g.name == "bracketleft":
            b = Box(s, 280)
            g.outline.vbar(b.left + s.stem / 2, BASE, CAP, t=s.stem)
            g.outline.hbar(b.left, b.right - 20, CAP, t=s.hstem)
            g.outline.hbar(b.left, b.right - 20, BASE + s.hstem / 2, t=s.hstem)
        elif g.name == "bracketright":
            b = Box(s, 280)
            g.outline.vbar(b.right - s.stem / 2, BASE, CAP, t=s.stem)
            g.outline.hbar(b.left + 20, b.right, CAP, t=s.hstem)
            g.outline.hbar(b.left + 20, b.right, BASE + s.hstem / 2, t=s.hstem)
        elif g.name == "percent":
            b = Box(s, 540)
            g.outline.ring(b.left + 80, CAP - 90, 55, 55, t=s.thin)
            g.outline.ring(b.right - 80, BASE + 90, 55, 55, t=s.thin)
            g.outline.stroke([(b.right - 40, CAP - 20), (b.left + 40, BASE + 20)], t=s.thin, cap=_cap(s))
        elif g.name == "ampersand":
            b = Box(s, 600)
            g.outline.arc(b.left + b.body * 0.42, CAP * 0.70, 90, 80, 40, 230, t=s.stem, cap=_cap(s))
            g.outline.arc(b.left + b.body * 0.42, CAP * 0.32, 110, 90, 200, 40, t=s.stem, cap=_cap(s))
            g.outline.stroke([(b.left + b.body * 0.50, CAP * 0.40), (b.right - 10, BASE)], t=s.stem, cap=_cap(s))
        elif g.name == "dollar":
            b = Box(s, 500)
            g.outline.arc(b.left + b.body * 0.50, CAP * 0.68, b.body * 0.30, 90, 40, 230, t=s.stem, cap=_cap(s))
            g.outline.arc(b.left + b.body * 0.50, CAP * 0.32, b.body * 0.30, 90, 220, 410, t=s.stem, cap=_cap(s))
            g.outline.vbar((b.left + b.right) / 2, BASE, CAP, t=s.thin)
        elif g.name == "at":
            b = Box(s, 700)
            g.outline.ring((b.left + b.right) / 2, CAP * 0.48, b.body * 0.42, CAP * 0.42, t=s.stem)
            g.outline.ring((b.left + b.right) / 2, CAP * 0.48, b.body * 0.18, CAP * 0.18, t=s.thin)
        elif g.name == "asciicircum":
            b = Box(s, 400)
            m = (b.left + b.right) / 2
            g.outline.stroke([(b.left + 10, CAP * 0.55), (m, CAP)], t=s.stem, cap=_cap(s))
            g.outline.stroke([(b.right - 10, CAP * 0.55), (m, CAP)], t=s.stem, cap=_cap(s))
        elif g.name == "asciitilde":
            b = Box(s, 500)
            g.outline.arc(b.left + b.body * 0.32, CAP * 0.55, 70, 40, 200, 20, t=s.stem, cap=_cap(s))
            g.outline.arc(b.left + b.body * 0.68, CAP * 0.45, 70, 40, 20, 200, t=s.stem, cap=_cap(s))
        elif g.name == "grave":
            b = Box(s, 300)
            g.outline.stroke([(b.left + 40, CAP), (b.left + 10, CAP - 80)], t=s.thin, cap=_cap(s))
        elif g.name == "braceleft":
            b = Box(s, 320)
            g.outline.arc(b.right - 20, CAP * 0.78, 50, 80, 90, 180, t=s.stem, cap=_cap(s))
            g.outline.arc(b.right - 20, CAP * 0.22, 50, 80, 180, 270, t=s.stem, cap=_cap(s))
        elif g.name == "braceright":
            b = Box(s, 320)
            g.outline.arc(b.left + 20, CAP * 0.78, 50, 80, 0, 90, t=s.stem, cap=_cap(s))
            g.outline.arc(b.left + 20, CAP * 0.22, 50, 80, 270, 360, t=s.stem, cap=_cap(s))

    for d in "0123456789":
        glyphs.append(_digit_latin(s, d))
    return glyphs
