"""Helpers for writing lessons (see lessons.py for what a lesson holds)."""

TOP = 114     # y of a table top (things on the table)
GROUND = 140  # y of the ground line


def L(t, **kw):  # a spoken line
    return dict(t=t, **kw)


def C(id, k, x, **kw):  # a figure or thing in a shot
    return dict(id=id, k=k, x=x, **kw)


def B(at, w, r=None, tag=None, x=None):  # a state of the word board
    out = {'at': at, 'w': w}
    if r:
        out['r'] = {str(i): v for i, v in r.items()}
    if tag:
        out['tag'] = {str(i): v for i, v in tag.items()}
    if x:
        out['x'] = x
    return out


def S(lines, cast=None, board=None, **kw):  # a shot
    out = {'lines': lines}
    if cast:
        out['cast'] = cast
    if board:
        out['board'] = board
    out.update(kw)
    return out


def pick(ask, opts, right, why, before='', after='', answer=None):
    a = answer or (' '.join(x for x in (before, right, after) if x) if (before or after) else None)
    out = {'kind': 'pick', 'ask': ask, 'opts': opts, 'right': right, 'why': why, 'before': before, 'after': after}
    if a:
        out['answer'] = a
    return out


def build(ask, tiles, right, why):
    return {'kind': 'build', 'ask': ask, 'tiles': tiles, 'right': right, 'why': why, 'answer': ' '.join(right)}


def fix(words, wrong, opts, right, why, ask='One word is wrong. Touch it.'):
    full = list(words)
    full[wrong] = right
    return {'kind': 'fix', 'ask': ask, 'words': words, 'wrong': wrong, 'opts': opts, 'right': right, 'why': why, 'answer': ' '.join(full)}


def tap(ask, words, right, why):
    return {'kind': 'tap', 'ask': ask, 'words': words, 'right': right, 'why': why, 'answer': ' '.join(words)}


PEOPLE = [
    {'s': 'I', 'be': 'am', 'rest': 'a man'},
    {'s': 'you', 'be': 'are', 'rest': 'a woman'},
    {'s': 'he', 'be': 'is', 'rest': 'a boy'},
    {'s': 'she', 'be': 'is', 'rest': 'a girl'},
    {'s': 'it', 'be': 'is', 'rest': 'a dog'},
    {'s': 'we', 'be': 'are', 'rest': 'children'},
    {'s': 'they', 'be': 'are', 'rest': 'cats'},
]
