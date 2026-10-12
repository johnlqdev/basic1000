"""Build pron.js: American IPA for every headword, split into sound groups.

    python3 tools/pron/build_pron.py CMUDICT [--review]

CMUDICT is cmudict.dict from https://github.com/cmusphinx/cmudict (BSD licence). Each word's first
pronunciation is turned into IPA (General American), and its letters are lined up with its sounds
by a small search over known spellings of each sound (tools/pron/spellings.py). Silent letters join
the group before them. The primary stress mark (ˈ) goes before the stressed syllable's first sound
(words of two or more syllables only).

tools/pron/overrides.json holds hand-made entries ([[letters, IPA], ...]); they win over CMU.
--review prints every word with its groups and marks the doubtful ones (no CMU entry, unusual
letter-sound pairs, several CMU pronunciations) for a person to check.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spellings import COST, SILENT, ONSETS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ARPA = {
    'AA': 'ɑ', 'AE': 'æ', 'AH': 'ʌ', 'AO': 'ɔ', 'AW': 'aʊ', 'AY': 'aɪ', 'EH': 'ɛ', 'ER': 'ɝ', 'EY': 'eɪ',
    'IH': 'ɪ', 'IY': 'i', 'OW': 'oʊ', 'OY': 'ɔɪ', 'UH': 'ʊ', 'UW': 'u',
    'B': 'b', 'CH': 'tʃ', 'D': 'd', 'DH': 'ð', 'F': 'f', 'G': 'ɡ', 'HH': 'h', 'JH': 'dʒ', 'K': 'k', 'L': 'l',
    'M': 'm', 'N': 'n', 'NG': 'ŋ', 'P': 'p', 'R': 'r', 'S': 's', 'SH': 'ʃ', 'T': 't', 'TH': 'θ', 'V': 'v',
    'W': 'w', 'Y': 'j', 'Z': 'z', 'ZH': 'ʒ'}
VOWELS = {'ɑ', 'æ', 'ʌ', 'ə', 'ɔ', 'aʊ', 'aɪ', 'ɛ', 'ɝ', 'ɚ', 'eɪ', 'ɪ', 'i', 'oʊ', 'ɔɪ', 'ʊ', 'u'}


def words():
    out = []
    for n in range(1, 5):
        for line in open(os.path.join(ROOT, f'data-{n}.txt')):
            p = line.rstrip('\n').split('|')
            if len(p) >= 9:
                out.append((p[0], int(p[3])))
    return out


def load_cmu(path):
    d = {}
    for line in open(path, encoding='utf-8'):
        line = line.split('#')[0].strip()
        if not line:
            continue
        w, *ph = line.split()
        d.setdefault(re.sub(r'\(\d+\)$', '', w), []).append(ph)
    return d


def to_ipa(arpa):
    """[(ipa phoneme, stress or None)]"""
    out = []
    for a in arpa:
        base, st = re.match(r'([A-Z]+)(\d?)', a).groups()
        ipa = ARPA[base]
        st = int(st) if st else None
        if base == 'AH' and st == 0:
            ipa = 'ə'
        if base == 'ER' and st == 0:
            ipa = 'ɚ'
        out.append((ipa, st))
    return out


def align(word, phones):
    """Line the letters up with the phonemes. Returns [(letters, [phonemes])] or None."""
    w, n, m = word.lower(), len(word), len(phones)
    INF = float('inf')
    best = [[INF] * (m + 1) for _ in range(n + 1)]
    back = [[None] * (m + 1) for _ in range(n + 1)]
    best[0][0] = 0
    for i in range(n + 1):
        for j in range(m + 1):
            c0 = best[i][j]
            if c0 == INF:
                continue
            for li in range(1, 5):
                if i + li > n:
                    break
                g = w[i:i + li]
                for pj in range(0, 3):
                    if j + pj > m:
                        break
                    ph = tuple(phones[j:j + pj])
                    if pj == 0:
                        c = SILENT.get(g)
                        if c is None:
                            continue
                    else:
                        c = COST.get((g, ph))
                        if c is None:
                            if li == 1 and pj == 1:
                                c = 9  # an unusual pairing, allowed but flagged
                            else:
                                continue
                    if c0 + c < best[i + li][j + pj]:
                        best[i + li][j + pj] = c0 + c
                        back[i + li][j + pj] = (i, j)
    if best[n][m] == INF:
        return None, INF, 0
    groups, i, j, odd = [], n, m, 0
    while (i, j) != (0, 0):
        pi, pj = back[i][j]
        g, ph = word[pi:i], tuple(phones[pj:j])
        if ph and (g.lower(), ph) not in COST:
            odd += 1  # an unusual letter-sound pair
        groups.append((g, list(ph)))
        i, j = pi, pj
    groups.reverse()
    # silent letters join the group before them (or after, at the start)
    merged = []
    for g, ph in groups:
        if not ph and merged:
            merged[-1] = (merged[-1][0] + g, merged[-1][1])
        elif not ph:
            merged.append((g, ph))
        elif merged and not merged[-1][1]:
            merged[-1] = (merged[-1][0] + g, ph)
        else:
            merged.append((g, ph))
    return merged, best[n][m], odd


def stress_index(ipa):
    """index of the first phoneme of the primary-stressed syllable, or None for one syllable"""
    vowels = [k for k, (p, s) in enumerate(ipa) if s is not None]
    if len(vowels) < 2:
        return None
    v = next((k for k, (p, s) in enumerate(ipa) if s == 1), None)
    if v is None:
        return None
    start = v
    while start > 0 and ipa[start - 1][1] is None:
        cluster = ''.join(p for p, _ in ipa[start - 1:v])
        if cluster in ONSETS:
            start -= 1
        else:
            break
    return start


def build(cmu_path, review=False):
    cmu = load_cmu(cmu_path)
    over = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'overrides.json')))
    out, notes = {}, []
    for w, step in words():
        if w in over:
            out[w] = over[w]
            notes.append((w, step, 'hand', ''))
            continue
        prons = cmu.get(w.lower())
        if not prons:
            notes.append((w, step, 'MISSING', ''))
            continue
        # the first CMU pronunciation, unless it cannot be lined up with the spelling and a later one can
        cands = []
        for k, pr in enumerate(prons[:4]):
            ip = to_ipa(pr)
            g, c, o = align(w, [p for p, _ in ip])
            if g is not None:
                cands.append(((o, k), k, ip, g, o))  # fewest unusual letter-sound pairs, then CMU's order
        if not cands:
            notes.append((w, step, 'NOALIGN', ' '.join(p for p, _ in to_ipa(prons[0]))))
            continue
        _, pick, ipa, groups, odd = min(cands, key=lambda x: x[0])
        phones = [p for p, _ in ipa]
        cost = 0
        si = stress_index(ipa)
        res, k = [], 0
        for g, ph in groups:
            s = ''.join(ph)
            if si is not None and k <= si < k + len(ph) and si == k:
                s = 'ˈ' + s
            elif si is not None and k < si < k + len(ph):
                s = ''.join(ph[:si - k]) + 'ˈ' + ''.join(ph[si - k:])
            res.append([g, s])
            k += len(ph)
        out[w] = res
        flag = []
        if odd:
            flag.append(f'ODD{odd}')
        if pick:
            flag.append(f'variant{pick + 1}')
        if len(prons) > 1:
            alts = sorted({''.join(p for p, _ in to_ipa(x)) for x in prons} - {''.join(phones)})
            if alts:
                flag.append('alt:' + ','.join(alts[:3]))
        notes.append((w, step, ' '.join(flag), ''))
    return out, notes


def write_js(out, path):
    lines = []
    for w, groups in out.items():
        key = w if re.fullmatch(r'[A-Za-z_]\w*', w) else json.dumps(w)
        lines.append(f'  {key}: {json.dumps(groups, ensure_ascii=False)},')
    head = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'header.js')).read()
    with open(path, 'w') as f:
        f.write(head + 'window.BASIC_PRON = {\n' + '\n'.join(lines) + '\n};\n')


if __name__ == '__main__':
    out, notes = build(sys.argv[1], '--review' in sys.argv)
    if '--review' in sys.argv:
        for w, step, flag, extra in notes:
            g = out.get(w)
            shown = ' '.join(f'{a}={b}' for a, b in g) if g else extra
            print(f'{step:>3} {w:<14} {shown:<50} {flag}')
    write_js(out, os.path.join(ROOT, 'pron.js'))
    bad = [n for n in notes if n[2] in ('MISSING', 'NOALIGN')]
    print(f'{len(out)} words written to pron.js; {len(bad)} need a hand entry: {[n[0] for n in bad]}', file=sys.stderr)
