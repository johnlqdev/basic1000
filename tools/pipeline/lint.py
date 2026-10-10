import glob, sys, json
from vocab import analyse, HEAD

MODES = {'P': 'picture', 'A': 'action', 'D': 'demo', 'F': 'definition'}

def load(paths):
    rows = {}
    for p in paths:
        for n, line in enumerate(open(p), 1):
            line = line.rstrip('\n')
            if not line.strip():
                continue
            parts = line.split('|')
            if len(parts) != 6:
                print(f'{p}:{n} wrong field count: {line}')
                continue
            w, pos, mode, d, e1, e2 = [x.strip() for x in parts]
            rows[w] = dict(word=w, pos=pos, mode=mode, definition=d, examples=[e1, e2], src=f'{p}:{n}')
    return rows

if __name__ == '__main__':
    paths = sys.argv[1:] or sorted(glob.glob('src/*.txt'))
    rows = load(paths)
    problems = 0
    for w, r in rows.items():
        msgs = []
        if w.lower() not in HEAD:
            msgs.append('not a headword')
        if r['mode'] not in MODES:
            msgs.append('bad mode')
        if r['mode'] == 'F' and not r['definition']:
            msgs.append('missing definition')
        if r['mode'] != 'F' and r['definition']:
            msgs.append('seed has definition')
        if r['definition']:
            used, unk, _ = analyse(r['definition'])
            if unk:
                msgs.append(f'def unknown: {unk}')
            if w in used:
                msgs.append('def uses headword')
        for ex in r['examples']:
            used, unk, _ = analyse(ex)
            if unk:
                msgs.append(f'ex unknown: {unk} in "{ex}"')
            if w not in used:
                msgs.append(f'ex lacks headword: "{ex}"')
        if msgs:
            problems += 1
            print(w, '|', '; '.join(msgs))
    print(f'{len(rows)} rows, {problems} with problems')
