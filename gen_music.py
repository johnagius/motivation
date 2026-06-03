#!/usr/bin/env python3
"""Generate a public-domain backing track: Beethoven's "Für Elise" (the recurring
A-section theme), synthesised from scratch as a soft felt-piano / music-box tone.

Because every sample is generated here, the file is unambiguously free of any
recording/performance copyright (the composition itself is public domain). This
replaces the previously-used Clair de Lune *recording*, which carried its own
performance copyright.

Run:  python3 gen_music.py   ->   media/fur-elise.mp3
Requires: numpy, soundfile, static-ffmpeg
"""
import os, numpy as np, soundfile as sf

HERE   = os.path.dirname(os.path.abspath(__file__))
FFMPEG = "/usr/local/lib/python3.11/dist-packages/static_ffmpeg/bin/linux/ffmpeg"
SR = 44100
S  = 0.15                      # seconds per sixteenth note (gentle allegretto)

def midi(n): return 440.0 * 2 ** ((n - 69) / 12.0)

# ---- the A-section melody as (midi or None=rest, length in sixteenths) ----
E5,Ds5,B4,D5,C5,A4 = 76,75,71,74,72,69
C4,E4,Gs4 = 60,64,68
MEL = [
 (E5,1),(Ds5,1),
 (E5,1),(Ds5,1),(E5,1),(B4,1),(D5,1),(C5,1),
 (A4,3),(None,1),
 (C4,1),(E4,1),(A4,1),
 (B4,3),(None,1),
 (E4,1),(Gs4,1),(B4,1),
 (C5,3),(None,1),
 (E4,1),
 (E5,1),(Ds5,1),(E5,1),(Ds5,1),(E5,1),(B4,1),(D5,1),(C5,1),
 (A4,3),(None,1),
 (C4,1),(E4,1),(A4,1),
 (B4,3),(None,1),
 (E4,1),(C5,1),(B4,1),
 (A4,4),(None,2),
]
# ---- a soft low root under each phrase (A minor / E major) ----
A2,E2,A1,E1 = 45,40,33,28
BASS = [  # (start_in_sixteenths, midi, length_in_sixteenths)
 (0,  A1, 9), (10, A1, 4), (14, E1, 4), (18, A1, 4), (22, A1, 4),
 (25, A1, 9), (35, A1, 4), (39, E1, 4), (43, A1, 6),
]

def note(freq, dur, gain=0.5, tau=0.55):
    n = int(SR * dur)
    t = np.arange(n) / SR
    # felt-piano timbre: a few decaying harmonics
    h = [(1, 1.0), (2, 0.45), (3, 0.22), (4, 0.10), (6, 0.04)]
    wave = sum(a * np.sin(2 * np.pi * freq * k * t) for k, a in h)
    env = np.exp(-t / tau)                      # struck-and-decay
    atk = min(256, n)
    env[:atk] *= np.linspace(0, 1, atk)         # soft attack
    return (wave * env * gain).astype(np.float32)

def render(events, total_len, gain, tau):
    buf = np.zeros(int(SR * total_len) + SR, dtype=np.float32)
    for start_s, m, dur_s in events:
        if m is None:
            continue
        seg = note(midi(m), dur_s * S, gain, tau)
        i = int(SR * start_s * S)
        buf[i:i + len(seg)] += seg
    return buf

# place melody events sequentially
mel_events, t = [], 0
for m, d in MEL:
    mel_events.append((t, m, d))
    t += d
phrase_len = t                                  # length of one A-section, in sixteenths

# build a few repeats so it loops for a while
REPEATS = 5
total_sixteenths = phrase_len * REPEATS
total_len = total_sixteenths * S + 2.0
mel_all, bass_all = [], []
for r in range(REPEATS):
    off = r * phrase_len
    mel_all += [(s + off, m, d) for (s, m, d) in mel_events]
    bass_all += [(s + off, m, d) for (s, m, d) in BASS]

mix = render(mel_all, total_len, gain=0.42, tau=0.55) + render(bass_all, total_len, gain=0.30, tau=1.4)

# cheap, pleasant reverb: a few attenuated delayed taps
rev = np.zeros_like(mix)
for delay_ms, amp in [(53, 0.28), (97, 0.20), (151, 0.13), (211, 0.08)]:
    d = int(SR * delay_ms / 1000)
    rev[d:] += mix[:-d] * amp
mix = mix + 0.9 * rev

# normalise to a safe peak, soft stereo
mix /= max(1e-6, np.max(np.abs(mix))) / 0.85
stereo = np.stack([mix, np.r_[mix[40:], np.zeros(40)] * 0.96 + mix * 0.04], axis=1)

wav = os.path.join(HERE, "media", "_fur.wav")
sf.write(wav, stereo, SR)
out = os.path.join(HERE, "media", "fur-elise.mp3")
# loop-friendly: short fade-in only, no fade-out (would dip on every loop), and
# trim trailing silence so the loop point stays tight.
os.system(f'{FFMPEG} -y -loglevel error -i "{wav}" '
          f'-af "loudnorm=I=-20:TP=-2:LRA=11,afade=t=in:st=0:d=1.2,'
          f'silenceremove=start_periods=0:stop_periods=1:stop_silence=0.4:stop_threshold=-55dB:detection=peak" '
          f'-b:a 160k "{out}"')
os.unlink(wav)
print(f"wrote {out}  ({total_len:.1f}s, Für Elise A-section x{REPEATS})")
