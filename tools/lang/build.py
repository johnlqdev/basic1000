"""Build the mother-language files the site loads, from content/lang/.

    python3 tools/lang/build.py           # check, then write lang/index.json and lang/<code>.json
    python3 tools/lang/build.py --check   # check only

Sources (content/lang/):
  languages.json   {"default": code, "languages": [{"code", "name" (in that language), "english"}]}
  <code>.tsv       one line per headword: word<TAB>translation  (lines starting with # are comments)

A translation gives the sense the word's examples teach; several senses are separated by "; ",
the one used in the first example first. Words only, never sentences.

To add a language: write content/lang/<code>.tsv for all 1,000 words, add it to languages.json,
run this script. The site needs no change.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'content', 'lang')
OUT = os.path.join(ROOT, 'lang')


def load_tsv(path, words):
    out, errors = {}, []
    for n, line in enumerate(open(path, encoding='utf-8'), 1):
        line = line.rstrip('\n')
        if not line.strip() or line.startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) != 2 or not parts[1].strip():
            errors.append(f'{os.path.basename(path)}:{n}: expected "word<TAB>translation"')
            continue
        w, t = parts[0].strip(), ' '.join(parts[1].split())
        if w in out:
            errors.append(f'{os.path.basename(path)}:{n}: "{w}" appears twice')
        if w not in words:
            errors.append(f'{os.path.basename(path)}:{n}: "{w}" is not one of the 1,000 words')
        out[w] = t
    missing = [w for w in words if w not in out]
    if missing:
        errors.append(f'{os.path.basename(path)}: {len(missing)} word(s) without a translation: {", ".join(missing[:20])}')
    return out, errors


def main():
    check_only = '--check' in sys.argv
    words = [w['word'] for w in json.load(open(os.path.join(ROOT, 'content', 'course.json')))['words']]
    reg = json.load(open(os.path.join(SRC, 'languages.json'), encoding='utf-8'))
    codes = [l['code'] for l in reg['languages']]
    errors = []
    if reg.get('default') not in codes + [None, '']:
        errors.append(f'default language "{reg.get("default")}" is not in the list')
    data = {}
    for lang in reg['languages']:
        path = os.path.join(SRC, lang['code'] + '.tsv')
        if not os.path.exists(path):
            errors.append(f'{lang["code"]}: content/lang/{lang["code"]}.tsv is missing')
            continue
        data[lang['code']], errs = load_tsv(path, set(words))
        errors += errs
    if errors:
        print(f'{len(errors)} problem(s):')
        for e in errors:
            print(' -', e)
        sys.exit(1)
    if not check_only:
        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8') as f:
            json.dump({'default': reg.get('default') or '', 'languages': reg['languages']}, f, ensure_ascii=False, indent=1)
        for lang in reg['languages']:
            words_out = {w: data[lang['code']][w] for w in words}
            with open(os.path.join(OUT, lang['code'] + '.json'), 'w', encoding='utf-8') as f:
                json.dump({'code': lang['code'], 'name': lang['name'], 'english': lang['english'], 'words': words_out},
                          f, ensure_ascii=False, separators=(',', ':'))
    print(f'OK: {len(codes)} language(s) ({", ".join(codes)}), each with all {len(words)} words'
          + ('' if check_only else ' -> lang/'))


if __name__ == '__main__':
    main()
