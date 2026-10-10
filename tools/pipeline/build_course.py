"""Build course.json and course_words.csv from the source files and the step plan."""
import csv, json
import order
from vocab import analyse

MODES = {'P': 'picture', 'A': 'action', 'D': 'demo', 'F': 'definition'}
steps, left, _, _ = order.plan()
assert not left
pos = {w: i + 1 for i, s in enumerate(steps) for w in s}
meta = order.meta


def uses(text):
    used, unk, _ = analyse(text)
    assert not unk
    out = []
    for u in used:
        if u not in out:
            out.append(u)
    return out


words = []
for step_no, step in enumerate(steps, 1):
    for w in step:
        r = order.rows[w]
        m = meta[w]
        ex_out = []
        for text in r['examples']:
            u = uses(text)
            avail = max([pos[x] for x in u if x != w] + [step_no])
            ex_out.append({'text': text, 'uses': u, 'available_from_step': avail,
                           'role': 'teach' if avail == step_no else 'review'})
        # teaching examples first
        ex_out.sort(key=lambda e: (e['role'] != 'teach', e['available_from_step']))
        words.append({
            'id': len(words) + 1,
            'word': w,
            'us_spelling': m['us'],
            'pos': r['pos'],
            'step': step_no,
            'teach_mode': MODES[r['mode']],
            'definition': r['definition'] or None,
            'definition_uses': [x for x in uses(r['definition']) if x != w] if r['definition'] else [],
            'examples': ex_out,
            'grouped_forms': [f.strip() for f in m['forms'].split(',')] if m['forms'] else [],
            'source': m['source'],
            'ngsl_rank': m['rank'],
        })

step_list = []
for i, s in enumerate(steps, 1):
    modes = [MODES[order.rows[w]['mode']] for w in s]
    step_list.append({'step': i, 'type': 'vocabulary',
                      'phase': 'starter' if i <= len(order.STARTER) else 'main',
                      'words': list(s),
                      'defined_words': sum(m == 'definition' for m in modes)})

course = {
    'meta': {
        'title': 'Basic 1000 bootstrap course',
        'word_count': len(words),
        'step_count': len(step_list),
        'step_size': order.STEP_SIZE,
        'teach_modes': {
            'picture': 'shown with an image; no text definition',
            'action': 'shown with a movement or short video; no text definition',
            'demo': 'grammar or function word, taught through its examples; no text definition',
            'definition': 'explained with a Basic English definition',
        },
        'rules': [
            'Every definition uses only words from earlier steps.',
            'Every word has at least one teaching example that uses only words from earlier steps or the same step.',
            'Other examples are review examples, usable from available_from_step onward.',
            'Free forms count as the base word: -s/-es, -ed, -ing, -er, -est, -ly, un-, irregular forms, '
            'grouped pronoun forms, and the listed free compounds (someone, something, cannot ...).',
        ],
    },
    'steps': step_list,
    'words': words,
}
json.dump(course, open('out/course.json', 'w'), indent=1, ensure_ascii=False)

with open('out/course_words.csv', 'w', newline='', encoding='utf-8') as f:
    wr = csv.writer(f)
    wr.writerow(['id', 'step', 'word', 'us_spelling', 'pos', 'teach_mode', 'definition',
                 'example_1', 'example_1_role', 'example_1_from_step',
                 'example_2', 'example_2_role', 'example_2_from_step',
                 'definition_uses', 'grouped_forms', 'source', 'ngsl_rank'])
    for e in words:
        ex = e['examples'] + [{'text': '', 'role': '', 'available_from_step': ''}] * (2 - len(e['examples']))
        wr.writerow([e['id'], e['step'], e['word'], e['us_spelling'], e['pos'], e['teach_mode'],
                     e['definition'] or '',
                     ex[0]['text'], ex[0]['role'], ex[0]['available_from_step'],
                     ex[1]['text'], ex[1]['role'], ex[1]['available_from_step'],
                     ' '.join(e['definition_uses']), ', '.join(e['grouped_forms']),
                     e['source'], e['ngsl_rank'] or ''])
print('wrote', len(words), 'words in', len(step_list), 'steps')
