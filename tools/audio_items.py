"""List the audio clips a range of steps needs, as a tts "batch" request body.

  python3 tools/audio_items.py 10        # steps 1-10 (Unit 1)
  python3 tools/audio_items.py 11 20     # steps 11-20

Every word and every sentence is read by Daniel (voice "man"), except a sentence spoken by a
woman ("I am a woman.", "I am not a man."), which Sarah reads (voice "woman").
Keep voice_for() the same as voiceFor() in audio.js.
"""
import json, re, sys, os
MALE = 'man|boy|father|brother|son|husband'
FEMALE = 'woman|girl|mother|sister|daughter|wife'

def voice_for(s):
    t = s.lower()
    if re.search(r'\bi am an? (' + FEMALE + r')\b', t) or re.search(r'\bi am not an? (' + MALE + r')\b', t): return 'woman'
    return 'man'

def norm(t): return re.sub(r'\s+', ' ', t).strip()

lo, hi = (1, int(sys.argv[1])) if len(sys.argv) == 2 else (int(sys.argv[1]), int(sys.argv[2]))
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
items, seen = [], set()
for n in range(1, 5):
    for line in open(os.path.join(root, f'data-{n}.txt')):
        p = line.rstrip('\n').split('|')
        if len(p) < 9 or not (lo <= int(p[3]) <= hi): continue
        for text, voice in [(p[0], 'man'), (p[5], voice_for(p[5])), (p[7], voice_for(p[7]))]:
            k = (voice, norm(text))
            if k not in seen:
                seen.add(k); items.append({'text': norm(text), 'voice': voice})
print(json.dumps({'action': 'batch', 'chunk': 32, 'items': items}))
