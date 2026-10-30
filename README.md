# free-home-labeling-kit

Free printables for taming the small home mysteries that sneak up on everyone:
untagged cords, mystery breakers, forgotten valves, and "mom, where's the tape?"
Every sheet is a single HTML/CSS page that prints to PDF with plain paper — no
label stock required.

Made with care by **Asdale Dynamics, LLC** as part of a growing set of free,
beginner-friendly home and AI guides. It pairs naturally with our companion
project, the **downloads-folder-taming-handbook** — that one tames your
computer's clutter, this one tames the house around it.

## What's inside

Seven printable sheets, one PDF each, in `printables/`:

| PDF | What it solves |
| --- | --- |
| `cable-charger-tags.pdf` | Cut-out wrap tags so every cord says what it belongs to |
| `breaker-box-directory.pdf` | 40-slot mapping sheet for what each breaker actually controls, plus main-shutoff fields |
| `water-shutoff-valve-labels.pdf` | Sticker-style labels for main water, water heater, toilet, sink, washer, dishwasher, sprinkler, icemaker valves |
| `kit-contents-labels.pdf` | Lid checklists for first aid, sewing, and school/craft kits |
| `seasonal-storage-labels.pdf` | Box labels with season, box number, shelf, and contents lines |
| `remote-cheat-cards.pdf` | Small cheat cards that capture the three presses that get the TV working |
| `where-is-it-index.pdf` | A "Where is it?" house index page with 20 starter items and room to grow |

## How to print

- Paper: US Letter (8.5 x 11 in). The PDFs are built for that exactly.
- "Actual size" / 100% scale in your print dialog — never "fit to page."
- Plain paper + scissors + clear tape is all you need. Cardstock lasts longer
  on boxes and the breaker sheet.
- The PDFs are intentionally unbranded: no logos, no credits inside. Print
  freely and share freely (MIT).

## Build it yourself

Requires Python 3.10+ with WeasyPrint, pypdf, and pytest:

```bash
pip install -r requirements.txt
python3 build.py                 # render all sheets to printables/*.pdf and validate
python3 build.py --clean         # wipe old PDFs first
python3 build.py --sheet cable-charger-tags   # rebuild one sheet
python3 -m pytest                # verify every sheet builds a valid PDF
```

The one build script (`build.py`) renders each HTML sheet in `src/sheets/`
through WeasyPrint, then validates the result: magic bytes, page count,
US Letter size, extractable text, and an unbranded-text check. Every sheet
carries its own short labeling article — a "why," a how-to, and a friendly
tip — above the printable area.

## Project layout

```
build.py            one build script: HTML sheets -> validated PDFs
src/sheets/         7 HTML label sheets (one article + labels per sheet)
src/css/print.css   shared print stylesheet (Letter, ink-light design)
printables/         generated unbranded PDF output
tests/              pytest suite: every sheet builds a valid PDF
```

## Contribute

Adding a sheet is just an HTML file in `src/sheets/` that follows the
existing pattern and shows up in the next build. Keep new sheets ink-light,
Letter-sized, and unbranded.

## License

MIT — see `LICENSE`. Copyright (c) 2026 Asdale Dynamics, LLC.
