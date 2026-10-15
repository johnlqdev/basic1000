"""Check the grammar curriculum and build grammar-data.js for the site.

    python3 tools/grammar/build.py            # check, then write grammar-data.js and the audio job list
    python3 tools/grammar/build.py --check    # check only

The curriculum (content/grammar/curriculum.py) is a list of topics ("nodes"). Each node names the
nodes it needs first, so together they form a dependency tree (a graph without loops). The list is
kept in a learning order: every node comes after all the nodes it needs.

Rules checked here:
  * ids are unique; every "needs" id exists and comes earlier in the list (so there are no loops);
  * every text uses only the 1,000 words (any form the course allows), plus
      - grammar terms ("noun", "verb", ...) defined by the node itself or by a node it needs,
        directly or further back, and
      - words the node or an earlier needed node "teaches" (although, either ...);
    example sentences, board words and exercise sentences may use the taught words but not terms;
  * every node in the FULL_BANDS has a complete lesson (content/grammar/lessons*.py), and each
    exercise is well formed (the right answer is among the options, and so on);
  * a line spoken by a woman or girl in a film uses Sarah's voice.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'content'))
sys.path.insert(0, os.path.join(ROOT, 'content', 'grammar'))
import vocab  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from audio_items import voice_for  # noqa: E402  (same rule as voiceFor in audio.js)
from curriculum import NODES, BANDS  # noqa: E402
from lessons import LESSONS  # noqa: E402

FULL_BANDS = ('start', 'elementary')  # every node in these bands must have a complete lesson
WOMEN = {'woman', 'girl'}
# letters and word endings, written as spelling in rules ("add s", "ends in ing"): not vocabulary
LETTERS = set('abcdefghijklmnopqrstuvwxyz') | {'es', 'ed', 'ing', 'er', 'est', 'ly', 'ch', 'sh'}


def words_of(text):
    return vocab.tokens(text)


def term_words(terms):
    out = set()
    for t in terms:
        for w in re.findall(r"[A-Za-z]+", t.lower()):
            out.add(w)
            out.add(w + 's')
            out.add(w + 'es')
    return out


def main():
    problems = []
    ids = [n['id'] for n in NODES]
    pos = {}
    for i, n in enumerate(NODES):
        if n['id'] in pos:
            problems.append(f"{n['id']}: id used twice")
        pos[n['id']] = i
        if n['band'] not in BANDS:
            problems.append(f"{n['id']}: unknown band {n['band']}")
        for d in n.get('needs', []):
            if d not in pos:
                problems.append(f"{n['id']}: needs {d!r}, which is missing or comes later in the list")
    # everything a node may rely on: its own and all earlier needed nodes' terms and taught words
    anc = {}
    for n in NODES:
        a = set()
        for d in n.get('needs', []):
            if d in anc:
                a |= anc[d] | {d}
        anc[n['id']] = a
    by_id = {n['id']: n for n in NODES}

    def allowed(nid, with_terms=True):
        nodes = [by_id[nid]] + [by_id[a] for a in anc[nid] if a in by_id]
        ok = set()
        for m in nodes:
            ok |= {w.lower() for w in m.get('teaches', [])}
            if with_terms:
                ok |= term_words(m.get('terms', {}).keys())
        return ok

    def check(nid, where, text, with_terms=True):
        ok = allowed(nid, with_terms) | (LETTERS if with_terms else set())
        bad = sorted({w for w in words_of(text) if not w.isdigit() and vocab.lemma(w)[0] is None and w.lower() not in ok})
        bad += [w for w in words_of(text) if w.isdigit()]
        if bad:
            problems.append(f"{nid} {where}: {', '.join(bad)}  |  {text[:90]}")

    for n in NODES:
        nid = n['id']
        check(nid, 'title', n['title'])
        check(nid, 'goal', n['goal'])
        for t, d in n.get('terms', {}).items():
            check(nid, f'term {t}', d)
        for k, p in enumerate(n.get('points', [])):
            check(nid, f'point {k + 1}', p)
        for k, e in enumerate(n.get('examples', [])):
            check(nid, f'example {k + 1}', e, with_terms=False)
        if len(n.get('points', [])) < 1 or len(n.get('examples', [])) < 2:
            problems.append(f"{nid}: needs at least 1 point and 2 examples")

    # lessons
    for n in NODES:
        if n['band'] in FULL_BANDS and n['id'] not in LESSONS:
            problems.append(f"{n['id']}: in band {n['band']} but has no lesson")
    for nid, les in LESSONS.items():
        if nid not in by_id:
            problems.append(f"lesson {nid}: no such node")
            continue
        for s, shot in enumerate(les.get('film', [])):
            cast = {c['id']: c for c in shot.get('cast', [])}
            for k, line in enumerate(shot.get('lines', [])):
                spoken_by = cast.get(line.get('by'), {}).get('k')
                check(nid, f'film {s + 1}.{k + 1}', line['t'], with_terms=not line.get('by'))
                if spoken_by in WOMEN and line.get('v') != 'woman':
                    problems.append(f"{nid} film {s + 1}.{k + 1}: spoken by a {spoken_by}, so it needs v: 'woman'")
                if line.get('by') and line['by'] not in cast:
                    problems.append(f"{nid} film {s + 1}.{k + 1}: speaker {line['by']!r} is not in the shot")
            for b in shot.get('board', []):
                check(nid, f'film {s + 1} board', ' '.join(b['w']), with_terms=False)
                for tag in b.get('tag', {}).values():
                    check(nid, f'film {s + 1} tag', tag)
        rule = les.get('rule', {})
        for k, p in enumerate(rule.get('points', [])):
            check(nid, f'rule {k + 1}', p)
        for k, row in enumerate(rule.get('table', [])):
            check(nid, f'rule table {k + 1}', ' '.join(row))
        for k, e in enumerate(rule.get('examples', [])):
            check(nid, f'rule example {k + 1}', e['t'], with_terms=False)
        for k, t in enumerate(les.get('tasks', [])):
            for f in ('ask', 'why'):
                if t.get(f):
                    check(nid, f'task {k + 1} {f}', t[f])
            for f in ('before', 'after', 'right', 'answer'):
                if isinstance(t.get(f), str):
                    check(nid, f'task {k + 1} {f}', t[f], with_terms=False)
            for f in ('tiles', 'words', 'opts'):
                if t.get(f):
                    check(nid, f'task {k + 1} {f}', ' '.join(t[f]), with_terms=False)
        if les.get('machine'):
            for ms in machine_sentences(les['machine']):
                check(nid, 'machine', ms, with_terms=False)
        kinds = [t.get('kind') for t in les.get('tasks', [])]
        if len(kinds) < 6 or any(k not in ('pick', 'build', 'fix', 'tap') for k in kinds):
            problems.append(f"lesson {nid}: needs 6 exercises of known kinds, has {kinds}")
        for k, t in enumerate(les.get('tasks', [])):
            if t.get('kind') == 'pick' and t.get('right') not in t.get('opts', []):
                problems.append(f"lesson {nid} task {k + 1}: the right answer is not one of the options")
            if t.get('kind') == 'build' and sorted(t['tiles']) != sorted(t['right']):
                problems.append(f"lesson {nid} task {k + 1}: tiles and right order do not match")
            if t.get('kind') == 'fix' and t.get('right') not in t.get('opts', []):
                problems.append(f"lesson {nid} task {k + 1}: the right word is not one of the options")
            if t.get('kind') == 'tap' and any(i >= len(t['words']) for i in t['right']):
                problems.append(f"lesson {nid} task {k + 1}: a right index is past the last word")
        for s_i, shot in enumerate(les.get('film', [])):
            n_lines = len(shot.get('lines', []))
            for b in shot.get('board', []):
                if b.get('at', 0) >= n_lines:
                    problems.append(f"lesson {nid} film {s_i + 1}: a board state comes at line {b.get('at')} but the shot has {n_lines} lines")
                for key in list(b.get('r', {})) + list(b.get('tag', {})):
                    if int(key) >= len(b['w']):
                        problems.append(f"lesson {nid} film {s_i + 1}: a role or tag points past the last word")
        if not les.get('film') or not les.get('tasks') or not les.get('rule'):
            problems.append(f"lesson {nid}: needs film, rule and tasks")

    if problems:
        print(f"{len(problems)} problems:")
        for p in problems:
            print('  ' + p)
        sys.exit(1)
    print(f"{len(NODES)} nodes, {len(LESSONS)} lessons: all good")
    if '--check' in sys.argv:
        return
    data = {'bands': BANDS, 'nodes': NODES, 'lessons': LESSONS}
    with open(os.path.join(ROOT, 'grammar-data.js'), 'w', encoding='utf-8') as f:
        f.write('// Made by tools/grammar/build.py from content/grammar/. Do not edit by hand.\n')
        f.write('window.BASIC_GRAMMAR_DATA = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
    write_audio_jobs()
    print('wrote grammar-data.js')


def spoken(les):
    """Every sentence a lesson can say, as (voice, text). Voice: 'man' (Daniel) by default; 'woman'
    (Sarah) when the line says so (v: 'woman') or, like everywhere on the site, when the sentence is
    one only a woman can say ("I am a girl."). grammar.js picks the voice the same way."""
    pick = lambda d, text: d.get('v') or voice_for(text)
    out = []
    for shot in les.get('film', []):
        for line in shot.get('lines', []):
            out.append((pick(line, line['t']), line['t']))
    for e in les.get('rule', {}).get('examples', []):
        out.append((pick(e, e['t']), e['t']))
    for t in les.get('tasks', []):
        if t.get('answer'):
            out.append((pick(t, t['answer']), t['answer']))
    m = les.get('machine')
    if m:
        for s in machine_sentences(m):
            out.append((voice_for(s), s))
    return out


def machine_sentences(m):
    """All sentences the sentence machine can show (mirrors machineTiles/answer in grammar.js)."""
    out = []
    cap = lambda w: w[:1].upper() + w[1:]
    subj = lambda w, first: 'I' if w == 'I' else (cap(w) if first else w)
    for p in m['people']:
        for form in m['forms']:
            if form == 'question':
                out.append(f"{cap(p['be'])} {subj(p['s'], False)} {p['rest']}?")
                s = 'you' if p['s'] == 'I' else 'I' if p['s'] == 'you' else p['s']
                many = s in ('you', 'we', 'they')
                be = (('am' if s == 'I' else 'are' if many else 'is') if p['be'] in ('am', 'is', 'are')
                      else ('were' if many else 'was') if p['be'] in ('was', 'were') else p['be'])
                out.append(f"Yes, {subj(s, False)} {be}.")
                out.append(f"No, {subj(s, False)} {be} not.")
            elif form == 'not':
                out.append(f"{subj(p['s'], True)} {p['be']} not {p['rest']}.")
            else:
                out.append(f"{subj(p['s'], True)} {p['be']} {p['rest']}.")
    return out


# A sentence that starts with a word (or a list of words) being talked about ("“We” is you and other
# people.") is read with a comma after it ("“We”, is you ..."): the voice then stresses the word and pauses before the
# verb. The comma is only spoken, never shown; the clip keeps the name of the shown sentence.
TALKED_ABOUT = re.compile(r'(?:^|(?<=[.?!] ))(“[^”]+”(?:(?:, | and | or )“[^”]+”)*)( )(?=[A-Za-z])(?!(?:and|or) )')


def say_text(t):
    return TALKED_ABOUT.sub(r'\1,\2', t)


def write_audio_jobs():
    items, seen = [], set()
    for nid, les in LESSONS.items():
        for v, t in spoken(les):
            t = re.sub(r'\s+', ' ', t).strip()
            if (v, t) not in seen:
                seen.add((v, t))
                item = {'text': t, 'voice': v}
                if say_text(t) != t:
                    item['say'] = say_text(t)
                items.append(item)
    path = os.path.join(ROOT, 'content', 'jobs', 'grammar_audio.json')
    with open(path, 'w') as f:
        json.dump({'action': 'batch', 'chunk': 16, 'items': items}, f, ensure_ascii=False, indent=0)
    print(f'{len(items)} sentences to record -> content/jobs/grammar_audio.json')


if __name__ == '__main__':
    main()
