"""Basic 1000 vocabulary checker.

Maps any word in a sentence back to one of the 1,000 headwords using the course rules:
  * grouped forms (me/my -> I, more/most -> much, better/best -> good ...)
  * irregular verb and plural forms (went -> go, children -> child ...)
  * free endings: -s/-es, -ed, -ing, -er (doer and comparison), -est, -ly, and the prefix un-
  * free compounds of two listed words (someone, everything, football)
Anything it cannot map is reported as outside the vocabulary.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
_wl = os.path.join(HERE, 'words1000.json')
if os.path.exists(_wl):
    WORDS = json.load(open(_wl))
else:  # shipped version: headwords come from course.json
    WORDS = [e['word'] for e in json.load(open(os.path.join(HERE, 'course.json')))['words']]
HEAD = {w.lower(): w for w in WORDS}          # 'i' -> 'I'

GROUPED = {
    'me': 'I', 'my': 'I', 'myself': 'I',
    'him': 'he', 'his': 'he', 'himself': 'he',
    'her': 'she', 'hers': 'she', 'herself': 'she',
    'its': 'it', 'itself': 'it',
    'us': 'we', 'our': 'we', 'ours': 'we', 'ourselves': 'we',
    'them': 'they', 'their': 'they', 'theirs': 'they', 'themselves': 'they',
    'your': 'you', 'yours': 'you', 'yourself': 'you', 'yourselves': 'you',
    'whom': 'who', 'whose': 'who', 'these': 'this', 'those': 'that', 'an': 'a',
    'more': 'much', 'most': 'much', 'less': 'little', 'least': 'little',
    'better': 'good', 'best': 'good', 'worse': 'bad', 'worst': 'bad', 'furthest': 'far',
    'color': 'colour', 'gray': 'grey', 'behavior': 'behaviour', 'harbor': 'harbour',
    'humor': 'humour', 'organization': 'organisation', 'center': 'centre',
}

IRREGULAR = {
    'be': 'was were been being', 'have': 'has had having', 'do': 'does did done doing',
    'go': 'goes went gone', 'say': 'said says', 'make': 'made', 'take': 'took taken',
    'give': 'gave given', 'come': 'came', 'see': 'saw seen', 'get': 'got gotten',
    'know': 'knew known', 'tell': 'told', 'find': 'found', 'feel': 'felt', 'keep': 'kept',
    'run': 'ran', 'sit': 'sat', 'stand': 'stood', 'bring': 'brought', 'buy': 'bought',
    'begin': 'began begun', 'become': 'became', 'break': 'broke broken', 'choose': 'chose chosen',
    'draw': 'drew drawn', 'drink': 'drank drunk', 'drive': 'drove driven', 'eat': 'ate eaten',
    'fall': 'fell fallen', 'fight': 'fought', 'fly': 'flew flown', 'forget': 'forgot forgotten',
    'grow': 'grew grown', 'hang': 'hung', 'hear': 'heard', 'hold': 'held', 'lead': 'led',
    'lie': 'lay lain lying', 'lose': 'lost', 'mean': 'meant', 'meet': 'met', 'pay': 'paid',
    'rise': 'rose risen', 'sell': 'sold', 'send': 'sent', 'shake': 'shook shaken',
    'sleep': 'slept', 'speak': 'spoke spoken', 'spend': 'spent', 'stick': 'stuck',
    'swim': 'swam swum', 'teach': 'taught', 'throw': 'threw thrown', 'understand': 'understood',
    'wear': 'wore worn', 'win': 'won', 'write': 'wrote written', 'bite': 'bitten',
    'blow': 'blew blown', 'build': 'built', 'burn': 'burnt', 'catch': 'caught', 'bend': 'bent',
    'light': 'lit', 'ring': 'rang rung', 'show': 'shown', 'die': 'dying', 'leave': 'left',
    'think': 'thought', 'awake': 'woke woken',
    'child': 'children', 'man': 'men', 'woman': 'women', 'foot': 'feet', 'tooth': 'teeth',
    'knife': 'knives', 'leaf': 'leaves', 'life': 'lives', 'wife': 'wives', 'half': 'halves',
    'shelf': 'shelves', 'person': 'people',
}
IRREG = {}
for head, forms in IRREGULAR.items():
    for f in forms.split():
        IRREG.setdefault(f, head)

# Free compounds: two listed words joined, with a meaning clear from the parts
COMPOUNDS = {w: (a, b) for w, a, b in [
    ('anyone', 'any', 'one'), ('anything', 'any', 'thing'), ('anybody', 'any', 'body'),
    ('anywhere', 'any', 'where'), ('everyone', 'every', 'one'), ('everything', 'every', 'thing'),
    ('everybody', 'every', 'body'), ('everywhere', 'every', 'where'), ('someone', 'some', 'one'),
    ('something', 'some', 'thing'), ('somebody', 'some', 'body'), ('somewhere', 'some', 'where'),
    ('nothing', 'no', 'thing'), ('nobody', 'no', 'body'), ('nowhere', 'no', 'where'),
    ('cannot', 'can', 'not'), ('inside', 'in', 'side'), ('onto', 'on', 'to'),
    ('birthday', 'birth', 'day'), ('tonight', 'to', 'night'), ('railway', 'rail', 'way'),
    ('bathroom', 'bath', 'room')]}

CONTRACTIONS = [("can't", 'can not'), ("won't", 'will not'), ("n't", ' not'), ("'m", ' am'),
                ("'re", ' are'), ("'ll", ' will'), ("'ve", ' have'), ("'d", ' would'), ("'s", '')]


def _direct(w):
    if w in HEAD:
        return HEAD[w]
    if w in GROUPED:
        return GROUPED[w]
    return None


def _strip(w):
    """Candidate base forms after removing one free ending."""
    out = []
    def add(x):
        if len(x) >= 2:
            out.append(x)
    for suf, reps in [('ies', ['y']), ('es', ['', 'e']), ('s', ['']),
                      ('ied', ['y']), ('ed', ['', 'e']), ('ing', ['', 'e']),
                      ('ier', ['y']), ('er', ['', 'e']), ('iest', ['y']), ('est', ['', 'e']),
                      ('ily', ['y']), ('bly', ['ble']), ('ly', ['', 'e']), ('ally', ['al', ''])]:
        if w.endswith(suf) and len(w) > len(suf) + 1:
            stem = w[:-len(suf)]
            for r in reps:
                add(stem + r)
            # doubled final consonant: stopped, running, bigger
            if suf in ('ed', 'ing', 'er', 'est') and len(stem) > 2 and stem[-1] == stem[-2]:
                add(stem[:-1])
    return out


# real words that only look like a listed word plus an ending
FALSE_FRIENDS = {'forest', 'outer', 'other', 'bitten', 'mister', 'singer', 'finger', 'master', 'water',
                 'winter', 'number', 'letter', 'matter', 'butter', 'paper', 'corner', 'wonder', 'sister',
                 'mother', 'father', 'brother', 'daughter', 'never', 'ever', 'over', 'under', 'after',
                 'river', 'flower', 'power', 'tower', 'shower', 'later', 'manager', 'owner'}


def lemma(word, depth=0):
    """Return (headword, rule) or (None, None)."""
    w = word.lower()
    if depth == 0 and w in FALSE_FRIENDS and w not in HEAD:
        return None, None
    h = _direct(w)
    if h:
        return h, 'word'
    if w in IRREG and IRREG[w].lower() in HEAD:
        return HEAD[IRREG[w].lower()], 'irregular'
    if depth < 2:
        # prefer the longest base that matches (bites -> bite, not bit; uses -> use, not us)
        for base in sorted(_strip(w), key=len, reverse=True):
            h, _ = lemma(base, depth + 1)
            if h:
                return h, 'ending'
        if w.startswith('un') and len(w) > 4:
            h, _ = lemma(w[2:], depth + 1)
            if h:
                return h, 'un-'
    if depth == 0:
        base = w[:-1] if w.endswith('s') and w[:-1] in COMPOUNDS else w
        if base in COMPOUNDS:
            return COMPOUNDS[base], 'compound'
    return None, None


def tokens(text):
    t = text.replace('’', "'")
    for a, b in CONTRACTIONS:
        t = re.sub(re.escape(a), b, t, flags=re.I)
    return re.findall(r"[A-Za-z]+|\d+", t)


def analyse(text):
    """Return (headwords used, unknown tokens, compounds used)."""
    used, unknown, compounds = [], [], []
    for tok in tokens(text):
        if tok.isdigit():
            unknown.append(tok)
            continue
        h, rule = lemma(tok)
        if h is None:
            unknown.append(tok)
        elif rule == 'compound':
            compounds.append(tok)
            used.extend(h)
        else:
            used.append(h)
    return used, unknown, compounds


if __name__ == '__main__':
    import sys
    for s in sys.argv[1:]:
        print(s, analyse(s))
