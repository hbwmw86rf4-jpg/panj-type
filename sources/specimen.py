#!/usr/bin/env python3
"""Render PNG specimens of the Panj Type families."""

from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FONT_DIR = os.path.join(ROOT, "fonts", "ttf")
SPEC_DIR = os.path.join(ROOT, "documentation", "specimens")

CONSONANTS = "ਸਹਕਖਗਘਙਚਛਜਝਞਟਠਡਢਣਤਥਦਧਨਪਫਬਭਮਯਰਲਵੜ"
VOWELS = "ਅਆਇਈਉਊਏਐਓਔੲੳੴ"
DIGITS = "੦੧੨੩੪੫੬੭੮੯"
MATRAS = "ਕਾ ਕਿ ਕੀ ਕੁ ਕੂ ਕੇ ਕੈ ਕੋ ਕੌ ਕੰ ਕੱ ਕਂ"
WORDS = "ੴ ਸਤਿ ਨਾਮੁ ਕਰਤਾ ਪੁਰਖੁ ਨਿਰਭਉ ਨਿਰਵੈਰੁ"
PUNJABI = "ਪੰਜਾਬੀ ਭਾਸ਼ਾ ਸੁੰਦਰ ਹੈ। ਗੁਰਮੁਖੀ ਲਿਪੀ।"
LATIN = "Nankana Harmandir Anandpur Chandigarh"


def load(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size=size)


def sheet(fontfile: str, title: str, analogue: str, outfile: str) -> None:
    W, H = 2200, 2800
    img = Image.new("RGB", (W, H), "#f7f4ee")
    d = ImageDraw.Draw(img)
    title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    sub_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    d.rectangle((0, 0, W, 110), fill="#1c1915")
    d.text((48, 28), title, font=title_font, fill="#f7f4ee")
    d.text((48, 72), f"Latin role: {analogue}   ·   SIL OFL 1.1   ·   original Gurmukhi outlines", font=sub_font, fill="#c4b8a8")

    big = load(fontfile, 92)
    mid = load(fontfile, 64)
    sm = load(fontfile, 48)
    y = 150
    for label, text, fnt in [
        ("Mul Mantar", WORDS, mid),
        ("Sentence", PUNJABI, mid),
        ("Independent vowels", VOWELS, big),
        ("Consonants", CONSONANTS, big),
        ("Matras on KA", MATRAS, mid),
        ("Gurmukhi digits", DIGITS, big),
        ("Latin companion", LATIN + "  ABCDEFGHIJKLMNOPQRSTUVWXYZ  abcdefghijklmnopqrstuvwxyz  0123456789", sm),
    ]:
        d.text((48, y), label, font=sub_font, fill="#6b6156")
        y += 32
        d.text((48, y), text, font=fnt, fill="#1c1915", language="pa", anchor="la")
        bbox = d.textbbox((48, y), text, font=fnt, language="pa")
        y = max(y + 90, bbox[3] + 36)

    # glyph grid
    d.text((48, y), "Unicode Gurmukhi block", font=sub_font, fill="#6b6156")
    y += 40
    grid_font = load(fontfile, 42)
    cps = [cp for cp in range(0x0A01, 0x0A77) if chr(cp).isprintable() or True]
    x0, col_w, row_h = 48, 120, 88
    col = 0
    for cp in range(0x0A01, 0x0A77):
        ch = chr(cp)
        x = x0 + (col % 16) * col_w
        yy = y + (col // 16) * row_h
        d.text((x, yy), f"{cp:04X}", font=sub_font, fill="#9a8f82")
        try:
            d.text((x, yy + 22), ch, font=grid_font, fill="#1c1915")
        except Exception:
            pass
        col += 1
    img.save(outfile)
    print("wrote", outfile)


def comparison() -> None:
    files = [
        ("NankanaGrotesk-Regular.ttf", "Nankana Grotesk", "Helvetica / Arial"),
        ("HarmandirSerif-Regular.ttf", "Harmandir Serif", "Times / Georgia"),
        ("AnandpurSans-Regular.ttf", "Anandpur Sans", "Calibri / Gill Sans"),
        ("ChandigarhGeo-Regular.ttf", "Chandigarh Geo", "Futura / Avenir"),
        ("LudhianaMono-Regular.ttf", "Ludhiana Mono", "Courier / Consolas"),
        ("AmritsarRounded-Regular.ttf", "Amritsar Rounded", "Nunito / Varela"),
        ("PatialaCompact-Regular.ttf", "Patiala Compact", "Impact / Oswald"),
    ]
    W, H = 2400, 1600
    img = Image.new("RGB", (W, H), "#f7f4ee")
    d = ImageDraw.Draw(img)
    title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 34)
    sub_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    d.rectangle((0, 0, W, 100), fill="#1c1915")
    d.text((48, 24), "Panj Type — seven original Gurmukhi families", font=title_font, fill="#f7f4ee")
    d.text((48, 66), "Same Punjabi line in each style. These are original designs, not clones of the Latin fonts named as roles.", font=sub_font, fill="#c4b8a8")
    line = "ੴ ਸਤਿ ਨਾਮੁ ਕਰਤਾ ਪੁਰਖੁ  ਪੰਜਾਬੀ"
    y = 130
    for fname, name, analogue in files:
        d.text((48, y), f"{name}", font=sub_font, fill="#6b6156")
        d.text((420, y), analogue, font=sub_font, fill="#9a8f82")
        fnt = load(fname, 56)
        d.text((48, y + 26), line, font=fnt, fill="#1c1915", language="pa")
        y += 200
    path = os.path.join(SPEC_DIR, "comparison.png")
    img.save(path)
    print("wrote", path)

    # bold vs regular for grotesk
    img = Image.new("RGB", (2200, 700), "#f7f4ee")
    d = ImageDraw.Draw(img)
    d.text((48, 30), "Weight axis — Nankana Grotesk Regular / Bold", font=title_font, fill="#1c1915")
    d.text((48, 120), line, font=load("NankanaGrotesk-Regular.ttf", 72), fill="#1c1915")
    d.text((48, 280), line, font=load("NankanaGrotesk-Bold.ttf", 72), fill="#1c1915")
    d.text((48, 460), "ABCDEFGHIJKLMNOPQRSTUVWXYZ  abcdefghijklmnopqrstuvwxyz", font=load("NankanaGrotesk-Regular.ttf", 40), fill="#1c1915")
    d.text((48, 540), "ABCDEFGHIJKLMNOPQRSTUVWXYZ  abcdefghijklmnopqrstuvwxyz", font=load("NankanaGrotesk-Bold.ttf", 40), fill="#1c1915")
    img.save(os.path.join(SPEC_DIR, "weights.png"))


def singles(fontfile: str, outdir: str) -> None:
    os.makedirs(outdir, exist_ok=True)
    fnt = load(fontfile, 180)
    for cp in list(range(0x0A05, 0x0A3A)) + [0x0A5C, 0x0A72, 0x0A73, 0x0A74] + list(range(0x0A66, 0x0A70)):
        img = Image.new("RGB", (320, 360), "white")
        d = ImageDraw.Draw(img)
        d.text((40, 40), chr(cp), font=fnt, fill="black")
        d.text((12, 320), f"U+{cp:04X}", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16), fill="#888")
        img.save(os.path.join(outdir, f"{cp:04X}.png"))


def main() -> None:
    os.makedirs(SPEC_DIR, exist_ok=True)
    mapping = [
        ("NankanaGrotesk-Regular.ttf", "Nankana Grotesk Regular", "Helvetica / Arial"),
        ("HarmandirSerif-Regular.ttf", "Harmandir Serif Regular", "Times New Roman / Georgia"),
        ("AnandpurSans-Regular.ttf", "Anandpur Sans Regular", "Calibri / Gill Sans"),
        ("ChandigarhGeo-Regular.ttf", "Chandigarh Geo Regular", "Futura / Avenir"),
        ("LudhianaMono-Regular.ttf", "Ludhiana Mono Regular", "Courier New / Consolas"),
        ("AmritsarRounded-Regular.ttf", "Amritsar Rounded Regular", "Nunito / Varela Round"),
        ("PatialaCompact-Regular.ttf", "Patiala Compact Regular", "Impact / Oswald"),
    ]
    for fname, title, analogue in mapping:
        sheet(fname, title, analogue, os.path.join(SPEC_DIR, fname.replace(".ttf", ".png")))
    comparison()
    singles("NankanaGrotesk-Regular.ttf", os.path.join(SPEC_DIR, "nankana-singles"))


if __name__ == "__main__":
    main()
