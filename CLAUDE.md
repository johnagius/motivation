# CLAUDE.md — working agreement for this repo

**Motivation** is a static library of self-contained, animated illustrated "books"
(one HTML file each) hosted on GitHub Pages. `index.html` is the library landing page;
each book is a standalone `*-book.html`.

## Workflow rules (always)

- **Auto-commit & merge to `main`.** After completing a unit of work, commit with a
  clear message and **merge the working branch into `main` and push `main`** — Pages
  deploys from `main`. Do this without asking each time; it is the standing default
  here. (Use `git merge --no-ff <branch>` then `git push -u origin main`.)
- Do **not** open a pull request unless explicitly asked.
- Keep books **self-contained**: inline CSS/JS, no build step required to view. Only
  binary media lives under `media/`.
- All media used must be public-domain or otherwise clearly licensed.

## Repo map

| Path | What it is |
|------|------------|
| `index.html` | Library landing page — a grid of `.card` links, one per book. |
| `moon-book.html` | Reference book (JFK "We Choose to Go to the Moon"). Copy it to start a new book. |
| `media/moonlight-sonata.mp3` | Background music — Beethoven *Moonlight Sonata* mvt.1, a **public-domain recording** (Paul Pitman / Musopen, PD). |
| `media/narration/NN.mp3` + `manifest.json` | Per-page narration for a book. |
| `build_narration.py` | Renders narration with **Kokoro** neural TTS (natural prosody; replaced the robotic Piper voice). |
| `gen_preview.py` | Renders `preview.png` (1200×630 social card) with Pillow. |

## How a book is structured (read before editing audio/pages)

Pages live in `<script id="pagesrc" type="text/template">` separated by `<!--PAGE-->`.
Each page is a `<div class="pg ...">`. Key conventions:

- `class="pg blank"` pages are **layout-only** (right-hand padding in the two-page book)
  and are **never narrated**.
- A `.folio` element is the page number; it is stripped from narration text.
- `class="reveal"` / `data-anim` drive entrance animations.

### Reading modes (in JS at the bottom)
- **Phone portrait** → single-page finger-swipe pager (`single` = non-blank pages, 1:1
  with panels).
- **Phone landscape / desktop** → two-page animated book (`spreads` = flat `pages`
  grouped 2-by-2, **blanks included**).

### Narration indexing — the rule that must hold
Narration files are named by **non-blank page ordinal**: the Nth non-blank page →
`media/narration/NN.mp3`. `build_narration.py` produces them this way.

- Pager mode panels are already 1:1 with non-blank pages, so `mIdx` maps directly.
- Book mode iterates **flat** page indices (which include blanks), so it must translate
  through `narrIndex[]` (flat index → non-blank ordinal, blanks = `-1`). If you add or
  remove pages/blanks, this mapping keeps narration aligned. **Never** index narration
  files by a flat (blank-included) page number, or pages will be skipped / mis-read.

### Audio start behaviour
Browsers block silent autoplay. On the **first tap/swipe/key** the music starts at full
volume; **2 seconds later** narration begins (and ducks the music to a low level). The
♪ and 🔊 buttons toggle each. Keep this "music first, narration after 2s" ordering.

## Adding a new book

1. Copy `moon-book.html` → `<slug>-book.html`; replace the `pagesrc` pages and `<title>`.
2. Render narration: `pip install kokoro-onnx soundfile static-ffmpeg`, put the Kokoro
   model + voices in `/tmp/kokoro/` (`kokoro-v1.0.onnx`, `voices-v1.0.bin` from the
   kokoro-onnx `model-files-v1.0` release), then `python3 build_narration.py`
   (set `KOKORO_VOICE` to pick a voice, e.g. `am_michael`). **Do not** raise Piper's old
   `--sentence-silence`; Kokoro paces sentences itself via per-sentence rendering.
3. Add a `.card` link to `index.html` and (optionally) a preview image via
   `gen_preview.py`.
4. Commit, merge to `main`, push.

## Deploy
GitHub Pages serves `main` (Settings → Pages → Deploy from branch → `main` / root).
Live at https://johnagius.github.io/motivation/ a minute or two after pushing `main`.
