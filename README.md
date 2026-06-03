# Motivation — an illustrated library

Animated, illustrated "books" that summarise the best parts of a speech, text, or
film, and what they really mean. Each book is a single self-contained HTML file you
can open in any browser and flip through.

## What's here

| File | What it is |
|------|------------|
| `index.html` | The **library / landing page** — thumbnails of every book; tap one to open. |
| `moon-book.html` | **"We Choose to Go to the Moon"** — JFK's Rice University speech, illustrated, with the 8-stage journey to the Moon as a map for doing hard things. |
| `preview.png` | Link-preview image shown when the library is shared (WhatsApp, etc.). |
| `media/clair-de-lune.mp3` | Background music — Debussy's *Clair de Lune* (public-domain recording). |
| `media/narration/*.mp3` | Per-page narration, one file per page, plus `manifest.json`. |
| `gen_preview.py` | Regenerates `preview.png` (needs Pillow: `pip install Pillow`). |
| `build_narration.py` | Re-renders the narration audio with Piper neural TTS (see below). |

## Features

- **Mobile-first reading with real swipe.** In **portrait**, each page fills the screen
  and you turn pages with a real finger **swipe** (drag-to-turn, snaps, page counter).
  **Rotate to landscape** and it becomes the full **two-page animated book** that uses
  the whole screen — a "rotate for the full book" hint shows in portrait, and your place
  is kept when you rotate. On desktop it's the two-page book with page-turn animations.
- **Real background music.** Debussy's *Clair de Lune* (an actual recording, not
  synthesised). It fades in and loops gently.
- **Neural narration.** Each page is read aloud by a natural neural voice (rendered
  ahead of time with [Piper](https://github.com/rhasspy/piper)), so it sounds the same
  on every device. It turns the pages as it reads, and while it speaks the music
  automatically **ducks** to a low level.
- **Auto-start.** Browsers block audio until the reader interacts, so the music and
  narration start automatically on the **first tap/swipe**. The ♪ and 🔊 buttons toggle
  each on/off.
- **Back to the library.** Every book has a "‹ Library" link to return to `index.html`.

### Controls

- **Phone:** swipe to turn pages (portrait) · rotate for the two-page book · ♪ music ·
  🔊 narration · ‹ Library to go back.
- **Desktop:** `Space`/click play the showcase · `→` `←` step · ♪ music · 🔊 narration ·
  `G` record the whole book to video · `C` record the current spread.

## Re-rendering the narration

The narration MP3s are committed, so you don't need to rebuild them. To regenerate
(e.g. after editing the book text or to change the voice):

```bash
pip install piper-tts static-ffmpeg
# download a Piper voice to /tmp/piper/ryan.onnx (+ .onnx.json) from
# https://huggingface.co/rhasspy/piper-voices  (this uses en_US-ryan-high)
python3 build_narration.py
```

## Share it on WhatsApp (one-click link)

1. In this repo on GitHub: **Settings → Pages → Build and deployment → Deploy from a
   branch**, pick the **`main`** branch and **`/ (root)`** folder, then **Save**.
2. After a minute your library is live at:

   ```
   https://johnagius.github.io/motivation/
   ```

3. Paste that link into your WhatsApp status. It opens in any phone browser — one tap,
   then swipe to flip and read. The link shows a moon preview card (`preview.png`).

To link straight to a single book instead of the library, share
`https://johnagius.github.io/motivation/moon-book.html`.

## Adding another book

1. Create the new book's HTML file (copy `moon-book.html` as a starting point).
2. Add an entry to the `BOOKS` array near the bottom of `index.html`
   (`href`, `thumb`, `source`, `title`, `blurb`).
