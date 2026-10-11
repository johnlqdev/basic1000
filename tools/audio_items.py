"""List the audio clips a range of steps needs, as a tts "batch" request body.

  python3 tools/audio_items.py 10        # steps 1-10 (Unit 1)
  python3 tools/audio_items.py 11 20     # steps 11-20

Each word is read by the woman; example 1 by the woman and example 2 by the man, unless the
sentence says who is speaking ("I am a man." is always the man). Keep voice_for() the same as
voiceFor() in audio.js.
"""
import json, re, sys, os
MALE = 'man|boy|father|brother|son|husband'
FEMALE = 'woman|girl|mother|sister|daughter|wife'

def voice_for(s, fallback):
    t = s.lower()
    if re.search(r'\bi am an? (' + MALE + r')\b', t) or re.search(r'\bi am not an? (' + FEMALE + r')\b', t): return 'man'
    if re.search(r'\bi am an? (' + FEMALE + r')\b', t) or re.search(r'\bi am not an? (' + MALE + r')\b', t): return 'woman'
    return fallback

def norm(t): return re.sub(r'\s+', ' ', t).strip()

lo, hi = (1, int(sys.argv[1])) if len(sys.argv) == 2 else (int(sys.argv[1]), int(sys.argv[2]))
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
items, seen = [], set()
for n in range(1, 5):
    for line in open(os.path.join(root, f'data-{n}.txt')):
        p = line.rstrip('\n').split('|')
        if len(p) < 9 or not (lo <= int(p[3]) <= hi): continue
        for text, voice in [(p[0], 'woman'), (p[5], voice_for(p[5], 'woman')), (p[7], voice_for(p[7], 'man'))]:
            k = (voice, norm(text))
            if k not in seen:
                seen.add(k); items.append({'text': norm(text), 'voice': voice})
print(json.dumps({'action': 'batch', 'items': items}))
