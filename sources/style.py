"""Style axes for the Panj Type families.

These are original Gurmukhi designs. They occupy the same *roles* as well-known
Latin families (neo-grotesque UI, transitional serif, geometric, mono, …) but
they are not clones of those fonts and do not copy their outlines.
"""

from __future__ import annotations

from dataclasses import dataclass, replace


HEAD = 720.0
BASE = 0.0
ASCENDER = 980.0
DESCENDER = -280.0
UPM = 1000


@dataclass(frozen=True)
class Style:
    family: str
    style_name: str
    filename: str
    analogue: str
    role: str
    weight_class: int = 400
    stem: float = 86.0
    bar: float = 86.0
    thin: float = 86.0
    contrast: float = 1.0  # horizontal thickness / vertical thickness
    width: float = 1.0
    side: float = 70.0
    roundness: float = 0.2  # 0 square … 1 fully round terminals
    corner: float = 0.0
    serif: float = 0.0
    geometric: bool = False
    mono: bool = False
    mono_width: float = 620.0
    condensed: bool = False
    flare: float = 0.0  # extra terminal thickening
    aperture: float = 1.0  # 1 closed grotesque, >1 more open humanist
    overshoot: float = 12.0
    italic: float = 0.0

    @property
    def hstem(self) -> float:
        return max(18.0, self.stem * self.contrast)

    @property
    def cap_radius(self) -> float:
        if self.roundness >= 0.85:
            return self.stem * 0.5
        return self.stem * 0.5 * self.roundness

    def bold(self) -> "Style":
        scale = 1.38 if self.weight_class < 600 else 1.0
        return replace(
            self,
            style_name="Bold",
            filename=self.filename.replace("-Regular", "-Bold"),
            weight_class=700,
            stem=round(self.stem * scale, 1),
            bar=round(self.bar * scale, 1),
            thin=round(self.thin * scale * 0.92, 1),
            side=max(40.0, self.side * 0.88),
            serif=self.serif * 1.05,
        )


def families() -> list[Style]:
    nankana = Style(
        family="Nankana Grotesk",
        style_name="Regular",
        filename="NankanaGrotesk-Regular.ttf",
        analogue="Helvetica / Arial",
        role="Neo-grotesque sans — even colour, square-ish terminals, slightly closed counters.",
        stem=88.0,
        bar=88.0,
        thin=80.0,
        contrast=0.92,
        width=1.0,
        side=72.0,
        roundness=0.12,
        corner=4.0,
        aperture=0.92,
    )
    harmandir = Style(
        family="Harmandir Serif",
        style_name="Regular",
        filename="HarmandirSerif-Regular.ttf",
        analogue="Times New Roman / Georgia",
        role="Transitional serif — high contrast, bracketed serifs, elegant bowls.",
        stem=78.0,
        bar=64.0,
        thin=32.0,
        contrast=0.42,
        width=1.02,
        side=64.0,
        roundness=0.35,
        corner=8.0,
        serif=62.0,
        flare=0.18,
        aperture=1.05,
        overshoot=16.0,
    )
    anandpur = Style(
        family="Anandpur Sans",
        style_name="Regular",
        filename="AnandpurSans-Regular.ttf",
        analogue="Calibri / Gill Sans",
        role="Humanist sans — open apertures, mild modulation, sheared terminals.",
        stem=82.0,
        bar=76.0,
        thin=62.0,
        contrast=0.78,
        width=1.04,
        side=70.0,
        roundness=0.28,
        corner=10.0,
        flare=0.08,
        aperture=1.18,
        overshoot=14.0,
    )
    chandigarh = Style(
        family="Chandigarh Geo",
        style_name="Regular",
        filename="ChandigarhGeo-Regular.ttf",
        analogue="Futura / Avenir",
        role="Geometric sans — circular bowls, uniform stroke, long headline.",
        stem=80.0,
        bar=80.0,
        thin=80.0,
        contrast=1.0,
        width=1.06,
        side=68.0,
        roundness=1.0,
        corner=40.0,
        geometric=True,
        aperture=1.1,
        overshoot=18.0,
    )
    ludhiana = Style(
        family="Ludhiana Mono",
        style_name="Regular",
        filename="LudhianaMono-Regular.ttf",
        analogue="Courier New / Consolas",
        role="Monospace — fixed advance, slab terminals, technical colour.",
        stem=74.0,
        bar=74.0,
        thin=70.0,
        contrast=1.0,
        width=0.92,
        side=40.0,
        roundness=0.08,
        corner=2.0,
        serif=28.0,
        mono=True,
        mono_width=640.0,
        aperture=1.0,
    )
    amritsar = Style(
        family="Amritsar Rounded",
        style_name="Regular",
        filename="AmritsarRounded-Regular.ttf",
        analogue="Nunito / Varela Round",
        role="Rounded sans — fully round terminals, friendly and slightly wide.",
        stem=92.0,
        bar=92.0,
        thin=88.0,
        contrast=1.0,
        width=1.08,
        side=76.0,
        roundness=1.0,
        corner=46.0,
        aperture=1.12,
        overshoot=14.0,
    )
    patiala = Style(
        family="Patiala Compact",
        style_name="Regular",
        filename="PatialaCompact-Regular.ttf",
        analogue="Impact / Oswald",
        role="Condensed display — heavy stems, tight spacing, poster colour.",
        weight_class=800,
        stem=148.0,
        bar=128.0,
        thin=120.0,
        contrast=0.86,
        width=0.72,
        side=36.0,
        roundness=0.06,
        corner=2.0,
        condensed=True,
        aperture=0.85,
        overshoot=8.0,
    )
    styles = [nankana, harmandir, anandpur, chandigarh, ludhiana, amritsar, patiala]
    out: list[Style] = []
    for s in styles:
        out.append(s)
        if s.family != "Patiala Compact":
            out.append(s.bold())
    return out
