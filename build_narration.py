#!/usr/bin/env python3
"""Render per-page narration audio for moon-book.html using Kokoro (neural TTS).

Kokoro is far more natural than the old Piper voice: real pitch movement,
sentence-level prosody, proper pauses, and correct number/date reading
("1962" -> "nineteen sixty-two", not "nineteen hundred sixty-two").

Outputs media/narration/NN.mp3 (NN = non-blank page ordinal) + manifest.json.

Run:  python3 build_narration.py
Requires:
  pip install kokoro-onnx soundfile static-ffmpeg
  model + voices in /tmp/kokoro/ :
    kokoro-v1.0.onnx  voices-v1.0.bin
    from https://github.com/thewh1teagle/kokoro-onnx/releases (model-files-v1.0)
"""
import os, re, json, html
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

HERE   = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "media", "narration")
FFMPEG = "/usr/local/lib/python3.11/dist-packages/static_ffmpeg/bin/linux/ffmpeg"
KMODEL = "/tmp/kokoro/kokoro-v1.0.onnx"
KVOICE = "/tmp/kokoro/voices-v1.0.bin"
VOICE  = os.environ.get("KOKORO_VOICE", "am_michael")   # warm US male narrator
SPEED  = 0.95                                            # slightly measured, like a reading
os.makedirs(OUTDIR, exist_ok=True)

# ---- pull the page templates out of the book ----
htmltext = open(os.path.join(HERE, "moon-book.html"), encoding="utf-8").read()
raw = re.search(r'<script id="pagesrc"[^>]*>(.*?)</script>', htmltext, re.S).group(1)
pages = [p.strip() for p in raw.split("<!--PAGE-->") if p.strip()]

# ---- integer -> words (so "240,000" reads "two hundred forty thousand", not digits) ----
_ONES = ['zero','one','two','three','four','five','six','seven','eight','nine','ten','eleven',
         'twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen']
_TENS = ['','','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety']
def _below_thousand(n):
    w = []
    if n >= 100:
        w.append(_ONES[n // 100]); w.append('hundred'); n %= 100
    if n >= 20:
        w.append(_TENS[n // 10] + ('-' + _ONES[n % 10] if n % 10 else ''))
    elif n > 0:
        w.append(_ONES[n])
    return ' '.join(w)
def num_to_words(n):
    if n == 0:
        return 'zero'
    parts = []
    for div, name in [(10**9, 'billion'), (10**6, 'million'), (10**3, 'thousand')]:
        if n >= div:
            parts.append(_below_thousand(n // div) + ' ' + name); n %= div
    if n > 0:
        parts.append(_below_thousand(n))
    return ' '.join(parts)

def page_text(ph):
    if 'class="pg blank"' in ph:
        return ""
    is_stage_b = 'class="pg stage-b"' in ph
    ph = re.sub(r'<div class="folio[^"]*"[^>]*>.*?</div>', ' ', ph, flags=re.S)  # drop page number
    ph = re.sub(r'<svg.*?</svg>', ' ', ph, flags=re.S)                            # drop art
    # ONE title per section: drop the repeated (ghost) heading, and on the second
    # page of a spread the repeated eyebrow, so the title isn't narrated twice.
    ph = re.sub(r'<h3[^>]*class="[^"]*ghost[^"]*"[^>]*>.*?</h3>', ' ', ph, flags=re.S)
    if is_stage_b:
        ph = re.sub(r'<div class="phase[^"]*"[^>]*>.*?</div>', ' ', ph, flags=re.S)
    # a section label ("The Mission" / "Your Climb") must end with a full stop, or it
    # runs straight into the sentence after it.
    ph = re.sub(r'<span class="lbl">(.*?)</span>', r'\1. ', ph, flags=re.S)
    ph = re.sub(r'(?i)</(blockquote|p|h1|h2|h3|h4|div|li)>', '\n', ph)            # block -> break
    ph = re.sub(r'(?i)<br\s*/?>', ' ', ph)
    ph = re.sub(r'<[^>]+>', ' ', ph)                                             # strip tags
    ph = html.unescape(ph)
    ph = ph.replace('&', ' and ')                                                # speak the ampersand
    ph = re.sub(r'\b\d{1,3}(?:,\d{3})+\b',                                       # 240,000 -> words
                lambda m: num_to_words(int(m.group(0).replace(',', ''))), ph)
    # Speak-friendly punctuation so prosody/pauses land naturally.
    ph = ph.replace('·', '. ').replace('•', '. ')        # middle dots -> stop
    ph = re.sub(r'\s*[—–]\s*', ' — ', ph)                # tidy dashes (espeak handles as pause)
    ph = ph.replace('…', '. ')
    ph = ph.replace('“', '').replace('”', '').replace('"', '')
    ph = ph.replace('‘', "'").replace('’', "'")
    ph = re.sub(r'[*_`|#<>]', ' ', ph)
    segs = []
    for line in ph.split("\n"):
        s = re.sub(r'\s+', ' ', line).strip()
        s = re.sub(r'\s+([,.!?;:])', r'\1', s)
        s = re.sub(r'(,\s*)+', ', ', s).strip(' ,')
        if not s:
            continue
        if s[-1] not in '.!?:;\'\)':
            s += '.'
        segs.append(s)
    return "\n".join(segs).strip()

def sentences(block):
    """Split a page into sentence-ish chunks for paced, per-sentence synthesis."""
    out = []
    for line in block.split("\n"):
        # split on sentence enders but keep them
        for s in re.split(r'(?<=[.!?:;])\s+', line.strip()):
            s = s.strip()
            if s:
                out.append(s)
    return out

SR = 24000
def silence(seconds):
    return np.zeros(int(SR * seconds), dtype=np.float32)

def render():
    kokoro = Kokoro(KMODEL, KVOICE)
    manifest = {"count": 0, "files": {}}
    panel = 0  # index among non-blank pages (matches the book's panel/flat-page index)
    for ph in pages:
        if 'class="pg blank"' in ph:
            continue
        txt = page_text(ph)
        name = f"{panel:02d}.mp3"
        if txt:
            chunks = []
            for i, sent in enumerate(sentences(txt)):
                samples, sr = kokoro.create(sent, voice=VOICE, speed=SPEED, lang="en-us")
                assert sr == SR
                if i:
                    chunks.append(silence(0.32))        # a real breath between sentences
                chunks.append(samples.astype(np.float32))
            audio = np.concatenate(chunks) if chunks else silence(0.2)
            wav = os.path.join(OUTDIR, f"_{panel:02d}.wav")
            sf.write(wav, audio, SR)
            # trim edge silence, gentle high-pass, loudness-normalize, limit below 0 dBFS
            clean = ("silenceremove=start_periods=1:start_silence=0.04:start_threshold=-50dB:detection=peak,"
                     "areverse,"
                     "silenceremove=start_periods=1:start_silence=0.30:start_threshold=-50dB:detection=peak,"
                     "areverse,"
                     "highpass=f=70,loudnorm=I=-17:TP=-1.5:LRA=11,alimiter=limit=0.85")
            os.system(f'{FFMPEG} -y -loglevel error -i "{wav}" -af "{clean}" '
                      f'-ac 1 -ar 44100 -b:a 160k "{os.path.join(OUTDIR, name)}"')
            os.unlink(wav)
            manifest["files"][str(panel)] = name
            print(f"  page {panel:02d}: {len(txt):4d} chars -> {name}")
        panel += 1
    manifest["count"] = panel
    json.dump(manifest, open(os.path.join(OUTDIR, "manifest.json"), "w"), indent=0)
    print(f"done: {len(manifest['files'])} narration files, {panel} pages total, voice={VOICE}")

if __name__ == "__main__":
    render()
