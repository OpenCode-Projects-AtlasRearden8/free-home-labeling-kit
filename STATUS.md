# STATUS

Project: **free-home-labeling-kit** — Free printables for taming small home mysteries.
Maintained by Asdale Dynamics, LLC.

## What was built

Seven HTML/CSS label sheets in `src/sheets/`, each carrying its own short
labeling article (a "why," a how-to, and a friendly tip) above the printable
area, plus a shared ink-light print stylesheet (`src/css/print.css`) targeting
US Letter:

1. `cable-charger-tags` — wrap tags for cords/chargers (21 tags, pre-filled starter names + blanks)
2. `breaker-box-directory` — 40-slot panel mapping, main-shutoff and "mapped on" fields
3. `water-shutoff-valve-labels` — cut-out valve stickers (main, water heater, toilet, sink, washer, dishwasher, sprinkler, icemaker + 2 blanks)
4. `kit-contents-labels` — lid checklists for first aid, sewing, and school kits
5. `seasonal-storage-labels` — 8 box labels (winter, summer, holiday, clothes, sports, keepsakes + 2 blanks)
6. `remote-cheat-cards` — four per-device cheat cards + a household "everything in three steps" card
7. `where-is-it-index` — "Where is it?" house index with 20 starter items and write-in room to grow

Supporting pieces:

- `build.py` — the one build script: renders every sheet through WeasyPrint
  to `printables/*.pdf`, then validates each PDF (magic bytes, page count,
  US Letter size, extractable text, unbranded-text check). CLI supports
  `--sheet <slug>` and `--clean`.
- `tests/test_build.py` — 15 pytest tests covering the required contract:
  every sheet builds a valid PDF, PDFs are unbranded and Letter-sized, CLI
  behavior, corruption detection, and a secrets guardrail over the source tree.
- `requirements.txt`, `pytest.ini`, `README.md`, `LICENSE` (MIT,
  Copyright (c) 2026 Asdale Dynamics, LLC).

The PDFs in `printables/` are intentionally unbranded (no logos or credits
inside); the LLC credit lives in the README and LICENSE. A guardrail test
fails the build if forbidden branding text ever appears in PDF text.

## How to run

```bash
pip install -r requirements.txt
python3 build.py          # build + validate all seven PDFs
python3 -m pytest         # run the tests
```

Print the PDFs at 100% scale ("Actual size") on US Letter paper.

## Verification results

- `python3 build.py` — all 7 sheets report `OK`, exit code 0.
- `python3 -m pytest` — **15 passed**, no failures, no deprecation noise.
- Page counts: breaker 1, cable 2, kits 1, remotes 1, storage 2, valves 1, index 1.
- Single-sheet builds (`--sheet`) and corrupted-file detection tested.

## Known gaps

- Sheets are US Letter only; no A4 variant yet.
- The breaker directory assumes standard "left/right column" numbering;
  panels with unusual layouts may need rows crossed off.
- Some rendered grids are validated by size/text but not yet by visual
  inspection at print time — worth one human print pass per sheet.
- Companion cross-link is one-directional: this README references the
  downloads-folder-taming-handbook, but that project cannot yet link back.
