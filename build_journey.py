#!/usr/bin/env python3
"""Render the immersive, feeling-tuned narration for 'The Quiet Turn'.

Single-screen audio book: one warm narrator, slow measured pace, real pauses,
emphasis through phrasing. Outputs media/journey/NN.mp3 + chapters.json
(title, time-marker, duration) for the player to sequence.
"""
import os, re, json, html
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

HERE   = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "media/journey")
FFMPEG = "/usr/local/lib/python3.11/dist-packages/static_ffmpeg/bin/linux/ffmpeg"
FFPROBE= "/usr/local/lib/python3.11/dist-packages/static_ffmpeg/bin/linux/ffprobe"
KMODEL = "/tmp/kokoro/kokoro-v1.0.onnx"
KVOICE = "/tmp/kokoro/voices-v1.0.bin"
VOICE  = os.environ.get("KOKORO_VOICE", "am_michael")
SPEED  = 0.88          # slower, intimate, measured
SR     = 24000
os.makedirs(OUTDIR, exist_ok=True)

# (time-marker, chapter title, narration).  [p]=short beat  [pp]=long beat
# blank line = paragraph pause.
CHAPTERS = [
 ("", "", """Before we begin… settle in. [p] Put something in your ears, find a few quiet minutes where no one needs you, [p] and just walk with me for a while. [pp] You don't have to fix anything tonight. You don't have to take a single note. [p] Just listen. [pp] That's all this is."""),

 ("Sunday, just past nine", "The weight no one sees", """It's Sunday. [p] Just past nine. [p] The dishes are done, the house has gone quiet, and tomorrow is already sitting on your chest. [pp] You can't quite name it. It isn't sadness, exactly. It's more like… weight. [p] A low, grey hum, underneath everything. [pp] From the outside, your life looks fine. The job. The people. The photos. [p] And still — some part of you is tired in a way that sleep doesn't touch. [pp] So here is the first thing, and I need you to actually hear it. [pp] There is nothing wrong with you. [pp] You are not broken. You are not weak. And you are not the only one. [p] You're carrying something heavy — the way so many men your age are carrying it — [p] and no one ever taught you how to set it down. [pp] That's all this is. [p] A few quiet weeks… learning how to set it down. [p] So let's start. Gently."""),

 ("Monday morning", "The body knows first", """Monday. [p] You're at your desk, and an email lands. [p] You haven't even finished reading it… but your body already has. [pp] The jaw tightens. The chest pulls in. That hot, electric thing climbs the back of your neck. [pp] Before a single clear thought arrives, the body has already decided: threat. [pp] This is older than you. It's the same wiring that kept your ancestors alive. [p] It just can't tell the difference between a tiger… and a message from your boss. [pp] And here is what almost no one tells you. [p] You cannot think your way out of this. Not in this moment. [p] Logic doesn't reach the part of you that's lit up. [pp] But the breath does. [pp] So try this. Just once. [p] Two short breaths in, through the nose… [p] and one long, slow breath out, through the mouth. [pp] Again. In… in… and out. [pp] That long exhale is a switch. Scientists at Stanford gave it a name — the physiological sigh — [p] the fastest way we know to tell the body: you are safe now. [pp] You don't have to believe me. [p] Just try it once tomorrow, before you open the laptop. [p] That's the whole assignment."""),

 ("A few days in", "The story you're telling", """Your phone buzzes. [p] It's your partner. [p] One word. [pp] 'Fine.' [pp] And just like that, the projector in your mind flickers on. [p] She's pulling away. You've done something. This is how it starts. By Friday you'll be— [pp] Stop. [pp] Look at what actually happened. [p] Four letters arrived on a screen. [pp] Everything after that… you wrote. [p] The fear. The whole grim little movie. That was a story — and you were its author — and you never even noticed picking up the pen. [pp] A thought is not a fact. [p] It is not an instruction. [p] It's a passing weather system in the mind. And you… are the sky. Not the storm. [pp] There's a number worth knowing. [p] The chemical rush of an emotion — the real, physical surge of it — moves through your body in about ninety seconds. [p] After that, you are keeping it alive… by re-telling the story. [pp] So the next time the wave comes… let it. [p] Name it. 'This is fear.' 'This is hurt.' [p] Give it its ninety seconds. [pp] And then answer what was actually said… not the movie you made of it."""),

 ("That same night", "What's in your hands", """It's late. You should be asleep. [p] Instead you're staring at the ceiling, running the numbers. [pp] The restructure. The mortgage. What he meant in that meeting. The economy. [pp] Now notice something. [p] Every single thing on that midnight list… is outside your hands. [pp] Almost two thousand years ago, a man wrote — by lamplight — that we suffer more in our imagination than in reality. [p] And that peace begins the moment you separate what you can control… from what you can't. [pp] You get one tank of energy a day. One. [p] And you have been pouring it, all of it, into the column you cannot change — the markets, the weather, other people's minds. [pp] So draw the line. [p] What is not in my hands? [p] Set it down. Out loud, if you have to. [p] 'Not mine. Not tonight.' [pp] And what is in my hands — the next small thing, the next conversation, the next breath — [p] that is where the whole of you goes. [pp] That isn't giving up. [p] That is where your power actually lives."""),

 ("The thing you avoid", "The smallest step", """There's a thing you keep meaning to do. [p] You know the one. [pp] The project in the garage. The gym bag by the door. The call you owe. [pp] And every day it doesn't happen, it gets a little heavier… and you quietly call yourself lazy. [pp] You're not lazy. [p] You're frozen. And those are not the same thing. [pp] We've all been sold a lie — that motivation comes first. That one day you'll wake up wanting it… and then you'll act. [pp] It's backwards. [pp] Action comes first. The feeling follows. [p] You don't wait until you feel like moving. You move — and the wanting catches up. [pp] So make the step absurdly small. [p] Don't go for the run. Just put on the shoes. [p] Don't write the chapter. Open the page, and write one ugly sentence. [pp] Two minutes. That is the whole bar. [pp] Because the hardest part was never the work. [p] It was the inertia of standing still. [p] Beat that today — with one tiny thing — and let momentum carry the rest."""),

 ("Past midnight", "The thief in your pocket", """It's past midnight again. [p] You meant to sleep an hour ago. [p] But you're holding the little glowing rectangle, thumb moving on its own, [p] feeding on other people's best moments. [pp] The old friend who seems to have it all. The guy your age who sold his company. [p] And with every swipe, a small, quiet acid: everyone is ahead of you. [pp] Two things you should know. [pp] First — that device was designed, by very clever people, to do exactly this. To keep your thumb moving. The pull you feel is engineering. It is not weakness. [pp] Second — what you are watching is a trailer. [p] Carefully cut. The wins, and never the three-in-the-morning fear. [p] You are holding your whole messy behind-the-scenes… up against everyone else's highlight reel. [p] It was never a fair fight. [pp] That spike of pleasure, and the flat grey dip that always follows it — that is chemistry. Not character. [pp] So give yourself one mercy this week. [p] One night. Phone out of the bedroom. [pp] And notice how much quieter your mind becomes… when you stop letting strangers set the price of your evening."""),

 ("One ordinary morning", "The unglamorous medicine", """Something small has shifted. [p] You won't have noticed it yet. [pp] One morning — maybe almost by accident — you step outside with your coffee instead of your phone. [p] The air is cold. The light is just coming up. [pp] And here is a secret, hidden in plain sight. [pp] The most powerful things for how you feel are free… and boring… and you already own them. [pp] Sleep. [p] The thing you keep stealing from, to buy a few more hours. [p] It is not a luxury. It is the ground the whole day stands on. Guard it like it matters — because it does. [pp] Light. [p] Ten minutes of morning sun in your eyes sets a clock inside you — a steadier mood today, and deeper sleep tonight. [pp] And movement. [p] A twenty-minute walk is the most under-used medicine on earth. It grows the brain. It burns off the stress. And it costs you nothing. [pp] No supplement. No hack. No purchase. [p] Just light… and sleep… and a body that gets to move. [pp] Start with tomorrow. [p] Coffee on the step. Let the day find you outside."""),

 ("Catching up with a friend", "The thing you stopped saying", """You're with a friend. [p] Catching up. Half-watching the game. [p] And he says it — the thing men say without thinking. [p] 'You good?' [pp] And you open your mouth to give the answer you always give. [p] 'Yeah. All good, mate.' [pp] But this time… you don't. [pp] This time you say: 'Honestly? Not really. It's been a hard year.' [pp] And the world doesn't end. [pp] He doesn't flinch. He doesn't pity you. He doesn't walk away. [p] He just goes quiet for a second… and then he says: [pp] 'Yeah. Me too.' [pp] Me too. [p] Two of the most healing words there are. [pp] The longest study ever run on human happiness — eighty years, thousands of lives — landed on one finding, clear as a bell. [pp] It isn't money. It isn't status. [p] It is the warmth of your connections that decides how well, and how long, you live. [pp] And we get it exactly backwards. We go silent… right when we should speak. [pp] Asking for help was never weakness. [p] It is the bravest thing in the room. [pp] So this week — tell one person, one true thing. [p] Just one. [p] And watch what comes back."""),

 ("Back at home", "One turn toward", """And then there is home. [pp] The person closest to you… and somehow, lately, the furthest away. [pp] It didn't break in a fight. [p] It drifted — in a thousand small turnings-away. The phone instead of the question. The half-listen. The 'in a minute' that never came. [pp] Love, it turns out, is not kept alive by the grand gesture. [pp] It's kept alive in the small moments. [p] The turn toward… instead of away. [pp] So tonight, try the smallest version of it. [p] Put the phone face-down. In another room. [pp] Look at her. And ask one real question — about her day, her worry, her — [p] and then do the hardest thing of all. [pp] Just listen. [p] Don't fix it. Don't solve it. [pp] Your presence is the gift. You — showing up, fully — for ninety honest seconds. [pp] That is how the distance closes. [p] Not all at once. [p] One turn toward… at a time."""),

 ("A few weeks in", "Who you're becoming", """It's been a few weeks now. [pp] And one morning, you catch yourself… lacing up your shoes before your mind can even start the argument. [pp] You don't feel transformed. There was no lightning. [p] But something underneath is changing — and it's worth understanding how. [pp] You do not rise to the level of your goals. [p] You fall to the level of who you believe you are. [pp] And here is the quiet magic of it. [p] Every small action is a vote. [pp] Every walk. Every early night. Every true word. [p] A vote… for a new version of you. [pp] You are not 'trying to get fit.' You are not 'trying to be calmer.' [p] You are becoming the kind of man who moves in the morning. Who tells the truth. Who sets the weight down. [pp] You don't need a hundred votes today. [p] You need one. [p] And then, tomorrow… one more. [pp] And when the old voice says 'I can't' — add one small word to the end of it. [pp] 'I can't… yet.' [pp] That word keeps the door open. [p] And lately… you've been walking through it."""),

 ("When it returns", "Weather, not climate", """I won't lie to you. [pp] The bad days come back. [pp] One lands now — out of nowhere, like the old days. The heaviness. The grey. [p] But notice — it doesn't pull you all the way under this time. [p] And it doesn't stay as long. [pp] This is the part most people never learn. [pp] A hard day is weather. [p] It is not the climate. [pp] It moves through — if you let it — and it is not a verdict on your whole life. [pp] So on that day, do the one thing you'd never have thought to do before. [pp] Be kind to yourself. [pp] Talk to yourself the way you'd talk to a good friend in the very same hole. [p] Not 'what is wrong with you' — [p] but 'this is hard… and you're doing your best… and it will pass.' [pp] The cruel inner voice never made anyone stronger. [p] It only ever made them freeze. [pp] And here is the strange grace of it. [p] The men who come through the hard seasons rarely come through unchanged. [pp] They come through deeper. Steadier. More use to the people they love. [pp] This isn't only breaking you. [p] Quietly… it has been building you."""),

 ("Sunday, again", "The turn has begun", """It's Sunday again. [p] Just past nine. [pp] The house is quiet — the way it was at the start. [pp] And the weight… is lighter. [pp] Not gone. Some nights, it still finds you. [p] But now you know what it is. [p] And you know how to set it down. [pp] You breathe — two in… one long out — and the body softens. [p] You catch the story before it runs away with you. [p] You take the small step. You stand in the morning light. You say the true thing. You turn toward the people you love. [pp] None of it was a cure… because you were never sick. [pp] You were a good man, carrying too much, in the dark — with no one to hold the lamp. [pp] So let me say the thing I came here to say. [pp] You don't have to do all of it. [p] Pick one. Tonight. [p] The breath. The walk. The honest sentence. [pp] Just one… and let the next quiet week begin. [pp] The turn does not arrive like thunder. [p] It's slow. And small. And almost invisible from the outside. [pp] But it is real. [pp] And if you've walked this far with me… [pp] it has already begun."""),
]

PAUSE = {"[p]": 0.85, "[pp]": 1.7}

def silence(sec): return np.zeros(int(SR*sec), dtype=np.float32)

def split_sentences(s):
    return [x.strip() for x in re.split(r'(?<=[.!?:;])\s+', s.strip()) if x.strip()]

def synth_segment(kokoro, text):
    """Synthesize a text run (may contain several sentences) with small gaps."""
    chunks=[]
    for i,sent in enumerate(split_sentences(text)):
        sent = sent.replace("…", ",").replace("—", ",")   # espeak-friendly soft pauses
        sent = re.sub(r"\s+", " ", sent).strip()
        if not sent: continue
        samples,sr = kokoro.create(sent, voice=VOICE, speed=SPEED, lang="en-us")
        assert sr==SR
        if i: chunks.append(silence(0.34))
        chunks.append(samples.astype(np.float32))
    return np.concatenate(chunks) if chunks else silence(0.1)

def render():
    kokoro = Kokoro(KMODEL, KVOICE)
    manifest=[]
    for idx,(tmark,title,body) in enumerate(CHAPTERS):
        # normalize paragraph / line breaks into pause tokens
        b = body.strip()
        b = re.sub(r"\n\s*\n", " [pp] ", b)
        b = re.sub(r"\n", " [p] ", b)
        b = html.unescape(b)
        # tokenize on pause markers, keeping them
        parts = re.split(r"(\[pp\]|\[p\])", b)
        audio=[]
        for part in parts:
            part=part.strip()
            if not part: continue
            if part in PAUSE:
                audio.append(silence(PAUSE[part]))
            else:
                audio.append(synth_segment(kokoro, part))
        full = np.concatenate(audio) if audio else silence(0.2)
        wav = os.path.join(OUTDIR, f"_{idx:02d}.wav")
        sf.write(wav, full, SR)
        out = os.path.join(OUTDIR, f"{idx:02d}.mp3")
        # warm, intimate VO: trim edges, gentle high-pass + low shelf warmth, a touch of
        # room, loudness-normalize, soft limiter.
        af = ("silenceremove=start_periods=1:start_silence=0.05:start_threshold=-50dB:detection=peak,"
              "areverse,silenceremove=start_periods=1:start_silence=0.5:start_threshold=-50dB:detection=peak,areverse,"
              "highpass=f=75,equalizer=f=180:t=q:w=1:g=1.5,"
              "aecho=0.9:0.9:38:0.07,"
              "loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.9")
        os.system(f'{FFMPEG} -y -loglevel error -i "{wav}" -af "{af}" -ac 1 -ar 44100 -b:a 168k "{out}"')
        os.unlink(wav)
        dur = float(os.popen(f'{FFPROBE} -v error -show_entries format=duration -of csv=p=0 "{out}"').read().strip() or 0)
        manifest.append({"id":idx,"time":tmark,"title":title,"file":f"{idx:02d}.mp3","dur":round(dur,2)})
        print(f"  {idx:02d}  {dur:5.1f}s  {tmark or '(intro)':22s} | {title}")
    json.dump({"chapters":manifest,"voice":VOICE},
              open(os.path.join(OUTDIR,"chapters.json"),"w"), indent=1)
    total=sum(c["dur"] for c in manifest)
    print(f"done: {len(manifest)} tracks, {total/60:.1f} min total, voice={VOICE}")

if __name__=="__main__":
    render()
