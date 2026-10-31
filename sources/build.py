#!/usr/bin/env python3
"""Build the Panj Type Gurmukhi families."""

from __future__ import annotations

import json
import os
import sys
from collections import defaultdict

from fontTools.fontBuilder import FontBuilder
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph as TTGlyph

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gurmukhi import GlyphOut, all_gurmukhi
from latin import all_latin
from style import ASCENDER, DESCENDER, HEAD, UPM, Style, families

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FONT_DIR = os.path.join(ROOT, "fonts", "ttf")
SPEC_DIR = os.path.join(ROOT, "documentation", "specimens")


ABOVE_CPS = {0x0A02, 0x0A01, 0x0A47, 0x0A48, 0x0A4B, 0x0A4C, 0x0A70, 0x0A71, 0x0A51, 0x0A76}
BELOW_CPS = {0x0A41, 0x0A42, 0x0A4D, 0x0A3C, 0x0A75}


def collect(s: Style) -> list[GlyphOut]:
    glyphs = all_latin(s) + all_gurmukhi(s)
    # unique names
    seen: set[str] = set()
    out: list[GlyphOut] = []
    for g in glyphs:
        if g.name in seen:
            continue
        seen.add(g.name)
        out.append(g)
    return out


def fea_text(glyphs: list[GlyphOut]) -> str:
    bases = [g for g in glyphs if g.gdef == "base" and g.outline.contours]
    above = [g.name for g in glyphs if g.unicodes and g.unicodes[0] in ABOVE_CPS]
    below = [g.name for g in glyphs if g.unicodes and g.unicodes[0] in BELOW_CPS]
    lines = [
        "languagesystem DFLT dflt;",
        "languagesystem guru dflt;",
        "languagesystem gur2 dflt;",
        "languagesystem latn dflt;",
        "",
    ]
    for name in above:
        lines.append(f"markClass {name} <anchor 0 0> @ABOVE;")
    for name in below:
        lines.append(f"markClass {name} <anchor 0 0> @BELOW;")
    lines += ["", "feature mark {"]
    for g in bases:
        ax, ay = g.anchors.get("above", (g.advance * 0.5, HEAD + 40))
        bx, by = g.anchors.get("below", (g.advance * 0.5, -30))
        lines.append(
            f"  pos base {g.name} <anchor {int(ax)} {int(ay)}> mark @ABOVE "
            f"<anchor {int(bx)} {int(by)}> mark @BELOW;"
        )
    lines += [
        "} mark;",
        "",
        "feature mkmk {",
        "  pos mark @ABOVE <anchor 0 40> mark @ABOVE;",
        "  pos mark @BELOW <anchor 0 -40> mark @BELOW;",
        "} mkmk;",
        "",
        "feature ccmp {",
        "  sub uni0A4C by uni0A4B uni0A3E;",
        "} ccmp;",
    ]
    return "\n".join(lines) + "\n"


def build_font(s: Style) -> str:
    glyphs = collect(s)
    order = [g.name for g in glyphs]
    if ".notdef" not in order:
        raise RuntimeError("missing .notdef")
    # .notdef must be first
    glyphs = sorted(glyphs, key=lambda g: 0 if g.name == ".notdef" else 1)
    order = [g.name for g in glyphs]

    glyf = {}
    metrics = {}
    cmap = {}
    gdef_class = {}
    for g in glyphs:
        try:
            glyf[g.name] = g.outline.to_tt_glyph(order)
        except Exception as e:
            print(f"  ! glyph {g.name}: {e}", file=sys.stderr)
            glyf[g.name] = TTGlyph()
        adv = int(round(g.advance))
        xmin, ymin, xmax, ymax = g.outline.bounds()
        lsb = int(round(xmin)) if g.outline.contours else 0
        metrics[g.name] = (adv, lsb)
        for cp in g.unicodes:
            cmap[cp] = g.name
        gdef_class[g.name] = {"base": 1, "ligature": 2, "mark": 3}.get(g.gdef, 1)

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyf)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=int(ASCENDER), descent=int(DESCENDER), lineGap=80)
    family = s.family
    full = f"{s.family} {s.style_name}"
    fb.setupNameTable({
        "familyName": family,
        "styleName": s.style_name,
        "uniqueFontIdentifier": f"panj-type:{s.filename}",
        "fullName": full,
        "psName": family.replace(" ", "") + "-" + s.style_name,
        "version": "1.000",
        "copyright": "Copyright 2026 Panj Type. Released under the SIL Open Font License 1.1.",
        "trademark": f"{family} is a reserved font name.",
        "manufacturer": "Panj Type",
        "designer": "Panj Type parametric Gurmukhi engine",
        "description": (
            f"Original Gurmukhi typeface in the {s.analogue} role. "
            f"{s.role} Not a clone of any proprietary Latin font."
        ),
        "licenseDescription": "SIL Open Font License 1.1 — https://openfontlicense.org",
        "licenseInfoURL": "https://openfontlicense.org",
        "vendorURL": "https://openfontlicense.org",
        "sampleText": "ੴ ਸਤਿ ਨਾਮੁ ਕਰਤਾ ਪੁਰਖੁ। ਪੰਜਾਬੀ ਭਾਸ਼ਾ।",
    })
    fb.setupOS2(
        sTypoAscender=int(ASCENDER),
        sTypoDescender=int(DESCENDER),
        sTypoLineGap=80,
        usWinAscent=int(ASCENDER),
        usWinDescent=int(-DESCENDER),
        achVendID="PANJ",
        fsSelection=0x40 if s.weight_class < 600 else 0x20,
        usWeightClass=s.weight_class,
        usWidthClass=3 if s.condensed else (5 if not s.mono else 5),
        sxHeight=470,
        sCapHeight=700,
        ulCodePageRange1=1 << 17,  # Gurmukhi OEM-ish; plus Latin
        ulUnicodeRange1=(1 << 0) | (1 << 1),  # Basic Latin + Latin-1
        ulUnicodeRange2=1 << (15),  # Gurmukhi is bit 15 of range2? 
    )
    # Unicode range bit for Gurmukhi is 80, which is ulUnicodeRange2 bit 16? 
    # Bits 0-31 range1, 32-63 range2, 64-95 range3. Gurmukhi = 80 → range3 bit 16.
    fb.font["OS/2"].ulUnicodeRange3 = 1 << 16
    fb.setupPost()
    fb.setupHead(fontRevision=1.0, unitsPerEm=UPM, macStyle=0 if s.weight_class < 600 else 1)
    fb.setupMaxp()
    try:
        fb.addOpenTypeFeatures(fea_text(glyphs))
    except Exception as e:
        print(f"  ! OpenType features failed ({s.filename}): {e}", file=sys.stderr)

    os.makedirs(FONT_DIR, exist_ok=True)
    path = os.path.join(FONT_DIR, s.filename)
    fb.save(path)
    return path


def export_svg_catalog(s: Style, glyphs: list[GlyphOut], sample: str) -> dict:
    """SVG path snippets for the specimen canvas."""
    by_cp = {}
    for g in glyphs:
        for cp in g.unicodes:
            by_cp[cp] = g
    letters = []
    x = 0.0
    paths = []
    for ch in sample:
        if ch == " ":
            x += 280
            continue
        g = by_cp.get(ord(ch))
        if not g:
            x += 280
            continue
        d = g.outline.to_svg_d(sx=1, sy=-1, ox=x, oy=0)
        if d:
            paths.append({"d": d, "advance": g.advance, "name": g.name, "ch": ch})
        letters.append({"ch": ch, "name": g.name, "advance": g.advance, "x": x})
        x += g.advance
    charset = []
    for g in glyphs:
        if g.unicodes and min(g.unicodes) >= 0x0A00:
            charset.append({
                "name": g.name,
                "cp": f"U+{g.unicodes[0]:04X}",
                "ch": chr(g.unicodes[0]),
                "d": g.outline.to_svg_d(sx=1, sy=-1, ox=0, oy=0),
                "advance": g.advance,
                "ymin": g.outline.bounds()[1],
                "ymax": g.outline.bounds()[3],
            })
    return {
        "family": s.family,
        "style": s.style_name,
        "analogue": s.analogue,
        "role": s.role,
        "weight": s.weight_class,
        "filename": s.filename,
        "sample_width": x,
        "sample_paths": paths,
        "charset": charset,
    }


def main() -> None:
    os.makedirs(FONT_DIR, exist_ok=True)
    os.makedirs(SPEC_DIR, exist_ok=True)
    catalog = []
    sample = "ੴ ਸਤਿ ਨਾਮੁ  ਪੰਜਾਬੀ"
    built = []
    for s in families():
        print(f"Building {s.family} {s.style_name} …")
        path = build_font(s)
        glyphs = collect(s)
        n_g = sum(1 for g in glyphs if g.unicodes and min(g.unicodes) >= 0x0A00)
        n_l = sum(1 for g in glyphs if g.unicodes and min(g.unicodes) < 0x0A00)
        print(f"  wrote {path}  ({n_g} Gurmukhi, {n_l} other)")
        built.append(path)
        if s.style_name == "Regular":
            catalog.append(export_svg_catalog(s, glyphs, sample))
            # also export a full alphabet line
            alpha = "ਸ ਹ ਕ ਖ ਗ ਘ ਙ ਚ ਛ ਜ ਝ ਞ ਟ ਠ ਡ ਢ ਣ ਤ ਥ ਦ ਧ ਨ ਪ ਫ ਬ ਭ ਮ ਯ ਰ ਲ ਵ ੜ"
            catalog[-1]["alpha"] = export_svg_catalog(s, glyphs, alpha.replace(" ", ""))["sample_paths"]
            catalog[-1]["alpha_width"] = export_svg_catalog(s, glyphs, alpha.replace(" ", ""))["sample_width"]
            vowels = "ਅ ਆ ਇ ਈ ਉ ਊ ਏ ਐ ਓ ਔ"
            catalog[-1]["vowels"] = export_svg_catalog(s, glyphs, vowels.replace(" ", ""))["sample_paths"]
            digits = "੦੧੨੩੪੫੬੭੮੯"
            catalog[-1]["digits"] = export_svg_catalog(s, glyphs, digits)["sample_paths"]
            matras = "ਕਾ ਕਿ ਕੀ ਕੁ ਕੂ ਕੇ ਕੈ ਕੋ ਕੌ ਕੰ ਕੱ"
            catalog[-1]["matras_raw"] = matras
    with open(os.path.join(SPEC_DIR, "catalog.json"), "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False)
    print("done", len(built), "fonts")


if __name__ == "__main__":
    main()
