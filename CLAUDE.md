# Basic 1000 — rule book

Standing rules for all work on this project. Read this first, and follow it for every piece of new
content (words, examples, grammar, videos, audio). The owner sets these rules; add new ones here
when the owner gives them, with the date.

## Content

1. **First example = plain form.** (2026-10-14) The first example sentence of every word uses the
   word exactly as it is written in the list: "I make a cake.", not "I made a cake." / "She makes a
   cake."; "A cow gives milk.", not "Cows give milk.". No past tense, no -s, no -ing, no plural for
   the headword itself. The first example must also be usable at the word's own step. Other words in
   the sentence may take any form. Enforced by `content/check_course.py` (rule 4).
2. **Only known words.** A definition uses only words from earlier steps; an example uses only words
   from earlier steps or the same step (`content/check_course.py`). Grammar lessons use only the
   1,000 words, plus terms defined by the node or its ancestors (`tools/grammar/build.py --check`).
3. **The step order is pinned** (`tools/pipeline/order_pinned.json`). Audio, pictures and films are
   made per step, so editing a sentence must never move words between steps.
4. **Edit the pipeline source, not only course.json.** Sentences live in `tools/pipeline/src/b*.txt`;
   rebuild with `tools/pipeline/build_course.py`, copy `out/course.json` to `content/`, then run
   `python3 tools/build_data.py`.
5. **Every quiz question has exactly one right answer.** After changing words or examples, run the
   quiz-check steps (`tools/quiz/`, see the quiz-check skill) until nothing is pending.
6. **Videos follow the first example.** A word's scene in `figures.js` acts out its first example and
   shows the same sentence. If the sentence changes, change the scene.
7. **Modules are linked.** Every word shown in grammar (examples, rules, answers) links to its
   Basic 1000 word page and counts as a visit.
8. **Mother-language annotations.** (2026-10-14) Every word has a short, intuitive translation in
   every listed language (German and French as options; the default is English only, no
   translation shown — learn English through English), in the meaning its example
   sentences teach (several senses: "; ", the first example's sense first). Words only, never
   sentences, and never shown in quiz questions. Sources: `content/lang/<code>.tsv` plus
   `content/lang/languages.json`; build with `python3 tools/lang/build.py` (writes `lang/`). A new
   word needs its translation in every language; if a word's first example changes meaning, check
   its translations. Adding a language = one new `.tsv` + one line in `languages.json`.

## Audio

- Voices: Daniel (`man`) by default; Sarah (`woman`) only when a woman is speaking
  (`voice_for` in `tools/audio_items.py`, `voiceFor` in `audio.js`).
- A single word is read as "Word." (`spoken()` in the tts function), so its last sound is not lost.
- Every new sentence needs a normal clip and, for course examples, a slow clip. Always stop the GPU
  pod afterwards.
- If clips are made again under the same name, raise `FRESH` in `audio.js` (clips are cached for a
  year).

## Safety and secrets

- Never print or paste API keys, tokens or passwords. The admin token lives in the Supabase vault
  (`tts_admin_token`). Never put the Supabase service role key in the site; only the publishable key.
- The owner adds secrets in the Supabase dashboard (RUNPOD_API_KEY, DROPBOX_*).
- Dropbox: write only inside `basic1000-backup/`. Never touch the other folders in the app folder.

## Shipping

- Commit as "Basic 1000" <noreply@anthropic.com>. Pushing does not deploy: create a Vercel
  production deployment for the commit and wait until it is READY.
- Before shipping content: `python3 content/check_course.py`, `python3 tools/grammar/build.py --check`,
  `python3 tools/lang/build.py --check`.
