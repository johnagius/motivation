#!/usr/bin/env python3
"""Render per-page narration audio for moon-book.html using Piper (neural TTS).
Outputs media/narration/NN.mp3 (NN = page index) + media/narration/manifest.json.
Run:  python3 build_narration.py
Requires: piper-tts, static-ffmpeg, and the Piper voice model in /tmp/piper/ryan.onnx
"""
import os, re, json, html, subprocess, tempfile

HERE   = os.path.dirname(os.path.abspath(__file__))
MODEL  = "/tmp/piper/ryan.onnx"
OUTDIR = os.path.join(HERE, "media", "narration")
FFMPEG = "/usr/local/lib/python3.11/dist-packages/static_ffmpeg/bin/linux/ffmpeg"
os.makedirs(OUTDIR, exist_ok=True)

# ---- pull the page templates out of the book ----
htmltext = open(os.path.join(HERE, "moon-book.html"), encoding="utf-8").read()
m = re.search(r'<script id="pagesrc"[^>]*>(.*?)</script>', htmltext, re.S)
raw = m.group(1)
pages = [p.strip() for p in raw.split("<!--PAGE-->")]
pages = [p for p in pages if p]

def page_text(ph):
    if 'class="pg blank"' in ph:
        return ""
    ph = re.sub(r'<div class="folio[^"]*"[^>]*>.*?</div>', ' ', ph, flags=re.S)  # drop page number
    ph = re.sub(r'<svg.*?</svg>', ' ', ph, flags=re.S)                            # drop art
    ph = re.sub(r'(?i)</(blockquote|p|h1|h2|h3|h4|div|li)>', '\n', ph)            # block -> break
    ph = re.sub(r'(?i)<br\s*/?>', ' ', ph)
    ph = re.sub(r'<[^>]+>', ' ', ph)                                             # strip tags
    ph = html.unescape(ph)
    segs = []
    for line in ph.split("\n"):
        s = re.sub(r'\s+', ' ', line).strip()
        if not s:
            continue
        if s[-1] not in '.!?:;…"”’)':   # ensure a sentence end so Piper pauses
            s += '.'
        segs.append(s)
    return " ".join(segs).strip()

manifest = {"count": 0, "files": {}}
panel = 0  # index among non-blank pages (matches the book's panel/flat-page index)
for ph in pages:
    if 'class="pg blank"' in ph:
        continue
    txt = page_text(ph)
    name = f"{panel:02d}.mp3"
    if txt:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tw:
            wav = tw.name
        subprocess.run(["piper", "-m", MODEL, "--length-scale", "1.07",
                        "--sentence-silence", "0.45", "-f", wav],
                       input=txt.encode("utf-8"), check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", wav,
                        "-ac", "1", "-b:a", "80k", os.path.join(OUTDIR, name)], check=True)
        os.unlink(wav)
        manifest["files"][str(panel)] = name
        print(f"  page {panel:02d}: {len(txt):4d} chars -> {name}")
    panel += 1

manifest["count"] = panel
json.dump(manifest, open(os.path.join(OUTDIR, "manifest.json"), "w"), indent=0)
print(f"done: {len(manifest['files'])} narration files, {panel} pages total")
