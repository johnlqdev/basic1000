"""Validate course.json against the bootstrap rules.

Usage:  python3 check_course.py [course.json]
Exit code 0 means every rule passes. Run it after any edit to definitions, examples or order.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from vocab import analyse  # noqa: E402

path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'course.json')
course = json.load(open(path))
words = course['words']
size = course['meta']['step_size']
errors = []

# 1. exactly the headword set, each once, steps full and in order
names = [w['word'] for w in words]
if len(names) != len(set(names)):
    errors.append('duplicate headwords')
pos = {w['word']: w['step'] for w in words}
for s in course['steps']:
    if len(s['words']) != size:
        errors.append(f"step {s['step']} has {len(s['words'])} words")
    for w in s['words']:
        if pos.get(w) != s['step']:
            errors.append(f"{w}: step list and word entry disagree")

for w in words:
    name, step = w['word'], w['step']
    # 2. definitions: only earlier steps, never the word itself
    if w['teach_mode'] == 'definition':
        if not w['definition']:
            errors.append(f'{name}: definition missing')
        else:
            used, unknown, _ = analyse(w['definition'])
            if unknown:
                errors.append(f'{name}: definition uses words outside the list: {unknown}')
            if name in used:
                errors.append(f'{name}: definition uses the word itself')
            late = sorted({u for u in used if u != name and pos.get(u, 0) >= step})
            if late:
                errors.append(f'{name} (step {step}): definition uses words not yet learned: {late}')
    elif w['definition']:
        errors.append(f'{name}: {w["teach_mode"]} word should have no definition')

    # 3. examples: known words only; at least one teaching example
    teach = 0
    for ex in w['examples']:
        used, unknown, _ = analyse(ex['text'])
        if unknown:
            errors.append(f'{name}: example uses words outside the list: {unknown}')
            continue
        if name not in used:
            errors.append(f'{name}: example does not contain the word: "{ex["text"]}"')
        avail = max([pos[u] for u in used if u != name] + [step])
        if avail != ex['available_from_step']:
            errors.append(f'{name}: available_from_step should be {avail} for "{ex["text"]}"')
        if avail == step:
            teach += 1
    if not teach:
        errors.append(f'{name} (step {step}): no example usable at its own step')

if errors:
    print(f'{len(errors)} problem(s):')
    for e in errors:
        print(' -', e)
    sys.exit(1)
print(f'OK: {len(words)} words in {len(course["steps"])} steps pass every rule.')
