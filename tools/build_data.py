"""Rebuild data-1.txt .. data-4.txt (the files the site loads) from content/course.json.

Usage: python3 tools/build_data.py
Each line: word|pos|mode|step|definition|example1|from_step|example2|from_step|grouped_forms|us_spelling
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODE = {'picture': 'P', 'action': 'A', 'demo': 'D', 'definition': 'F'}

words = json.load(open(os.path.join(ROOT, 'content', 'course.json')))['words']
lines = []
for w in words:
    ex = w['examples']
    parts = [w['word'], w['pos'], MODE[w['teach_mode']], str(w['step']), w['definition'] or '',
             ex[0]['text'], str(ex[0]['available_from_step']), ex[1]['text'], str(ex[1]['available_from_step']),
             ', '.join(w['grouped_forms']), w['us_spelling']]
    assert all('|' not in p and '\n' not in p for p in parts), w['word']
    lines.append('|'.join(parts) + '\n')
for k in range(4):
    with open(os.path.join(ROOT, f'data-{k + 1}.txt'), 'w', encoding='utf-8') as f:
        f.write(''.join(lines[k * 250:(k + 1) * 250]))
print('wrote data-1.txt .. data-4.txt from', len(words), 'words')
