"""Order the 1,000 words into 5-word steps.

Rules
  * a definition may only use words from EARLIER steps
  * each word needs at least one "teaching example" that uses only words from earlier steps
    or the same step; its other examples are scheduled for review from the step where
    all their words are known
  * the first six steps are a fixed starter block whose examples use only starter words
Priority: frequent words and words that unlock many others go first.
"""
import glob, json, itertools, os
from lint import load
from vocab import analyse

STEP_SIZE = 5
rows = load(sorted(glob.glob('src/*.txt')))
meta = {e['uk']: e for e in json.load(open('result.json'))['entries']}

def deps(text, w):
    used, unk, _ = analyse(text)
    assert not unk, (w, unk)
    return set(used) - {w}

D = {w: deps(r['definition'], w) if r['definition'] else set() for w, r in rows.items()}
EX = {w: [deps(x, w) for x in r['examples']] for w, r in rows.items()}

unlocks = {w: 0 for w in rows}
for w in rows:
    for d in D[w].union(*EX[w]):
        unlocks[d] += 1

def rank(w):
    r = meta[w]['rank']
    return r if r else 1200

def priority(w):
    return rank(w) - 4 * unlocks[w]

STARTER = [['I', 'am', 'a', 'man', 'woman'], ['you', 'are', 'he', 'she', 'is'],
           ['boy', 'girl', 'child', 'this', 'that'], ['house', 'dog', 'cat', 'it', 'big'],
           ['the', 'small', 'we', 'they', 'and'], ['have', 'not', 'yes', 'no', 'what']]
STARTER_SET = {w for s in STARTER for w in s}


def closure(c, prior, chosen, left, room):
    """Smallest set of new words (including c) that lets c be taught in this step, or None.
    prior = words from earlier steps; chosen = words already in this step."""
    best = None
    def grow(need, todo):
        nonlocal best
        if len(need) > room or (best and len(need) >= len(best)):
            return
        if not todo:
            best = set(need)
            return
        x, rest = todo[0], todo[1:]
        have = prior | chosen | need
        for ex in sorted(EX[x], key=lambda e: len(e - have)):
            missing = ex - have
            if any(m not in left or not D[m] <= prior for m in missing):
                continue
            grow(need | missing, rest + sorted(missing))
    if not D[c] <= prior:
        return None
    grow({c}, [c])
    return best


PINNED = 'order_pinned.json'  # the published order; see README ("Pinned order")


def pinned():
    """The published step order, checked against the rules. Audio, pictures and films are made per
    step, so once a course is live its order must not move when an example sentence is edited."""
    steps = json.load(open(PINNED))
    flat = [w for s in steps for w in s]
    assert sorted(flat) == sorted(rows) and len(flat) == len(set(flat)), 'pinned order must list every word once'
    known = set()
    for s in steps:
        assert len(s) == STEP_SIZE, s
        here = known | set(s)
        for w in s:
            assert D[w] <= known, (w, 'definition uses', sorted(D[w] - known))
            assert any(e <= here for e in EX[w]), (w, 'has no teaching example at its step')
        known = here
    return steps, set(), known, set()


def plan(fresh=False):
    if not fresh and os.path.exists(PINNED):
        return pinned()
    seen = set()
    for step in STARTER:
        seen |= set(step)
        for w in step:
            assert not D[w] and any(e <= seen for e in EX[w]), w
    known, steps = set(STARTER_SET), [list(s) for s in STARTER]
    left = set(rows) - STARTER_SET
    while left:
        chosen = set()
        order = sorted(left, key=lambda w: (priority(w), w))  # name breaks ties, so every build gives the same order
        while len(chosen) < STEP_SIZE:
            added = False
            for c in order:
                if c in chosen:
                    continue
                need = closure(c, known, chosen, left - chosen, STEP_SIZE - len(chosen))
                if need:
                    chosen |= need
                    added = True
                    break
            if not added:
                break
        if len(chosen) < STEP_SIZE and len(left) > len(chosen):
            return steps, left, known, chosen
        steps.append(sorted(chosen, key=lambda w: (priority(w), w)))
        known |= chosen
        left -= chosen
    return steps, left, known, set()


if __name__ == '__main__':
    steps, left, known, partial = plan()
    print('steps', len(steps), 'left', len(left), 'partial step', sorted(partial))
    for i, s in enumerate(steps[6:30], 7):
        print(i, s)
    if left:
        k = known | partial
        blocked = []
        for w in sorted(left - partial, key=priority):
            miss = [sorted(e - k) for e in EX[w]]
            blocked.append((w, sorted(D[w] - k), min(miss, key=len)))
        print('BLOCKED (word, def needs, best example needs):')
        for b in blocked[:60]:
            print(b)
        json.dump(blocked, open('blocked.json', 'w'))
