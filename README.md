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
| `gen_preview.py` | Regenerates `preview.png` (needs Pillow: `pip install Pillow`). |

## Features

- **Mobile-first reading.** On phones each page fills the screen and you turn pages
  with a natural finger **swipe** (one page at a time, with a page counter). On wide
  screens it becomes a two-page animated book with page-turn animations.
- **Background music.** Beethoven's *Für Elise*, synthesised in the browser — no audio
  files, nothing to download. It's **off by default** (no autoplay); tap the ♪ button
  to start it.
- **Automatic narration.** Tap the speaker button and the book reads itself aloud,
  turning pages as it goes. While narration plays, the music automatically **ducks**
  (drops to a low background level) and the voice sits at ~80% volume.
- **Back to the library.** Every book has a "‹ Library" link to return to `index.html`.

### Controls

- **Phone:** swipe to turn pages · ♪ music · 🔊 narration · ‹ Library to go back.
- **Desktop:** `Space`/click play the showcase · `→` `←` step · ♪ music · 🔊 narration ·
  `G` record the whole book to video · `C` record the current spread.

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
