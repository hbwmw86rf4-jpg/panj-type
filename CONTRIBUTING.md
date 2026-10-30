# Contributing to Panj Type

These fonts are parametric. Prefer editing the construction in `sources/`
over hand-patching a TTF.

## Build

```bash
python3 -m pip install -r requirements.txt
cd sources
python3 build.py
python3 specimen.py
```

TTFs land in `fonts/ttf/`. Specimens land in `documentation/specimens/`.

## What to change where

| Change | File |
|---|---|
| Weight, width, serifs, roundness | `sources/style.py` |
| A Gurmukhi letter | `sources/gurmukhi.py` |
| Latin companion glyphs | `sources/latin.py` |
| Stroke / ellipse drawing | `sources/geom.py` |
| OpenType mark attachment | `sources/build.py` |

Please keep reserved family names unless you are forking under the OFL
and renaming the fonts. Do not copy outlines from proprietary Latin fonts.

## License

Contributions are accepted under the SIL Open Font License 1.1 (`OFL.txt`).
