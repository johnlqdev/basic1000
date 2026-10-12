"""List the slow clips a range of steps needs, as a tts "slow" request body.

  python3 tools/slow_items.py 5        # steps 1-5
  python3 tools/slow_items.py 6 10     # steps 6-10

Every word (kind "word") and both example sentences of every word (kind "sentence"), in the same
voice as the normal clip (see voice_for in tools/audio_items.py). The normal clips must exist first.
Words also need their sound groups in pron.js, or the page shows no slow button for them; their IPA
is sent along ("ipa"), so the voice server can report words where what it hears does not match.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audio_items import voice_for, norm  # noqa: E402

def pron_ipa():
    """headword -> IPA from pron.js"""
    out = {}
    for line in open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pron.js'), encoding='utf-8'):
        m = re.match(r'\s*"?([A-Za-z]+)"?: (\[\[.*\]\]),\s*$', line)
        if m:
            out[m.group(1)] = ''.join(g[1] for g in json.loads(m.group(2)))
    return out


IPA = pron_ipa()
lo, hi = (1, int(sys.argv[1])) if len(sys.argv) == 2 else (int(sys.argv[1]), int(sys.argv[2]))
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
items, seen = [], set()
for n in range(1, 5):
    for line in open(os.path.join(root, f'data-{n}.txt')):
        p = line.rstrip('\n').split('|')
        if len(p) < 9 or not (lo <= int(p[3]) <= hi):
            continue
        for text, kind in [(p[0], 'word'), (p[5], 'sentence'), (p[7], 'sentence')]:
            voice = 'man' if kind == 'word' else voice_for(text)
            k = (voice, norm(text))
            if k not in seen:
                seen.add(k)
                it = {'text': norm(text), 'kind': kind, 'voice': voice}
                if kind == 'word' and p[0] in IPA:
                    it['ipa'] = IPA[p[0]]
                items.append(it)
print(json.dumps({'action': 'slow', 'items': items}))
